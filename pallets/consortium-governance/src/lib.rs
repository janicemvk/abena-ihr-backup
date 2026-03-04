//! # ABENA Consortium Governance Pallet
//!
//! Weighted voting by healthcare organizations. Consortium members (hospitals, insurers,
//! pharma, etc.) each have a voting weight. Proposals pass when approval threshold is met.
//!
//! ## Proposal lifecycle
//!
//! ```text
//!   Proposer (consortium rep) ──► propose(call, priority) ──► Open
//!       priority: Normal (7-day, 67%) | Emergency (24h, 75%)
//!                                                  │
//!   Reps vote during voting period ──► vote(id, aye)
//!                                                  │
//!   Anyone ──► close_and_execute(id) ──► Approved → dispatch(call)
//!                                       Rejected → mark closed
//! ```

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::{pallet_prelude::*, traits::EnsureOrigin};
use sp_runtime::traits::Dispatchable;
use scale_info::TypeInfo;
use sp_runtime::{
    traits::{Get, Saturating},
    BoundedVec, Permill, RuntimeDebug,
};

pub mod weights;

#[cfg(any(test, feature = "runtime-benchmarks"))]
mod mock;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;

pub use pallet::*;
pub use weights::WeightInfo;

/// Healthcare organization type for weighted voting.
#[derive(Clone, Copy, PartialEq, Eq, Encode, Decode, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[cfg_attr(feature = "std", derive(serde::Serialize, serde::Deserialize))]
pub enum OrgType {
    Hospital,
    Insurer,
    Pharma,
    Laboratory,
    ResearchInstitution,
    GovernmentHealthAgency,
    Other,
}

/// Consortium member: a healthcare organization with voting rights.
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct HealthcareOrg<T: frame_system::Config> {
    /// Organization type (Hospital, Insurer, etc.)
    pub org_type: OrgType,
    /// Voting weight (e.g. 1–100)
    pub voting_weight: u32,
    /// Representative accounts that may vote on behalf of this org
    pub representatives: BoundedVec<T::AccountId, frame_support::traits::ConstU32<8>>,
}

/// Proposal status.
#[derive(Clone, Copy, PartialEq, Eq, Encode, Decode, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum ProposalStatus {
    Open,
    Approved,
    Rejected,
    Executed,
}

/// Proposal priority: determines voting period and approval threshold.
#[derive(Clone, Copy, PartialEq, Eq, Encode, Decode, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[cfg_attr(feature = "std", derive(serde::Serialize, serde::Deserialize))]
pub enum ProposalPriority {
    /// Normal proposals: longer voting period (e.g. 7 days), standard threshold (e.g. 67%).
    Normal,
    /// Emergency proposals: shorter voting period (e.g. 24 hours), higher threshold (e.g. 75%).
    Emergency,
}

/// Max encoded size for a proposal call (2KB; most calls are < 512 bytes).
pub type MaxProposalCallLen = frame_support::traits::ConstU32<2048>;

/// Governance proposal. Call is stored as encoded bytes to avoid MaxEncodedLen on RuntimeCall.
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct GovernanceProposal<T: frame_system::Config> {
    pub proposer: T::AccountId,
    /// Encoded RuntimeCall
    pub call: BoundedVec<u8, MaxProposalCallLen>,
    pub created_at: frame_system::pallet_prelude::BlockNumberFor<T>,
    pub voting_ends_at: frame_system::pallet_prelude::BlockNumberFor<T>,
    pub status: ProposalStatus,
    /// Normal = longer period, standard threshold; Emergency = 24h, 75% threshold
    pub priority: ProposalPriority,
}

#[frame_support::pallet]
pub mod pallet {
    use super::*;
    use frame_support::traits::ConstU32;
    use frame_system::pallet_prelude::{BlockNumberFor, OriginFor, *};

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type WeightInfo: crate::WeightInfo;
        /// Origin that may register/remove consortium members
        type RegisterOrigin: EnsureOrigin<Self::RuntimeOrigin>;
        /// Voting period in blocks for normal proposals (e.g. 7 days)
        #[pallet::constant]
        type VotingPeriod: Get<u32>;
        /// Emergency voting period in blocks (e.g. 24 hours)
        #[pallet::constant]
        type EmergencyVotingPeriod: Get<u32>;
        /// Approval threshold for normal proposals (e.g. 67%)
        #[pallet::constant]
        type ApprovalThreshold: Get<Permill>;
        /// Approval threshold for emergency proposals (e.g. 75%)
        #[pallet::constant]
        type EmergencyApprovalThreshold: Get<Permill>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Consortium members: org hash → HealthcareOrg
    #[pallet::storage]
    #[pallet::getter(fn consortium_members)]
    pub type ConsortiumMembers<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::Hash,
        HealthcareOrg<T>,
        OptionQuery,
    >;

    /// Reverse: representative AccountId → org hash
    #[pallet::storage]
    #[pallet::getter(fn representative_org)]
    pub type RepresentativeToOrg<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, T::Hash, OptionQuery>;

    /// Proposals by ID (incrementing index)
    #[pallet::storage]
    #[pallet::getter(fn proposals)]
    pub type Proposals<T: Config> =
        StorageMap<_, Blake2_128Concat, u64, GovernanceProposal<T>, OptionQuery>;

    /// Votes: (proposal_id, voter) → aye
    #[pallet::storage]
    #[pallet::getter(fn votes)]
    pub type Votes<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        u64,
        Blake2_128Concat,
        T::AccountId,
        bool,
        OptionQuery,
    >;

    /// Next proposal ID
    #[pallet::storage]
    #[pallet::getter(fn next_proposal_id)]
    pub type NextProposalId<T: Config> = StorageValue<_, u64, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ConsortiumMemberRegistered { org_id: T::Hash, org_type: OrgType },
        ConsortiumMemberRemoved { org_id: T::Hash },
        Proposed { proposal_id: u64, proposer: T::AccountId },
        Voted { proposal_id: u64, voter: T::AccountId, aye: bool },
        Closed { proposal_id: u64, approved: bool },
        Executed { proposal_id: u64 },
    }

    #[pallet::error]
    pub enum Error<T> {
        AlreadyMember,
        NotMember,
        NotRepresentative,
        AlreadyVoted,
        ProposalNotFound,
        ProposalNotOpen,
        VotingNotEnded,
        ProposalNotApproved,
        ProposalAlreadyExecuted,
        RepresentativesEmpty,
        TooManyRepresentatives,
        InvalidWeight,
        ProposalCallTooLarge,
        ProposalDecodeFailed,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Register a consortium member. Only `RegisterOrigin` (e.g. Root).
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::register_consortium_member())]
        pub fn register_consortium_member(
            origin: OriginFor<T>,
            org_id: T::Hash,
            org_type: OrgType,
            voting_weight: u32,
            representatives: BoundedVec<T::AccountId, ConstU32<8>>,
        ) -> DispatchResult {
            T::RegisterOrigin::ensure_origin(origin)?;
            ensure!(!representatives.is_empty(), Error::<T>::RepresentativesEmpty);
            ensure!(voting_weight > 0, Error::<T>::InvalidWeight);
            ensure!(!ConsortiumMembers::<T>::contains_key(&org_id), Error::<T>::AlreadyMember);

            let org = HealthcareOrg::<T> {
                org_type,
                voting_weight,
                representatives: representatives.clone(),
            };
            ConsortiumMembers::<T>::insert(&org_id, &org);
            for rep in representatives {
                RepresentativeToOrg::<T>::insert(&rep, &org_id);
            }
            Self::deposit_event(Event::ConsortiumMemberRegistered {
                org_id,
                org_type,
            });
            Ok(())
        }

        /// Remove a consortium member.
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::register_consortium_member())]
        pub fn remove_consortium_member(
            origin: OriginFor<T>,
            org_id: T::Hash,
        ) -> DispatchResult {
            T::RegisterOrigin::ensure_origin(origin)?;
            let org = ConsortiumMembers::<T>::get(&org_id).ok_or(Error::<T>::NotMember)?;
            for rep in &org.representatives {
                RepresentativeToOrg::<T>::remove(rep);
            }
            ConsortiumMembers::<T>::remove(&org_id);
            Self::deposit_event(Event::ConsortiumMemberRemoved { org_id });
            Ok(())
        }

        /// Propose a call for consortium vote. Caller must be a representative.
        /// `call_encoded` is the encoded RuntimeCall (client-side encoding avoids cycle).
        /// `priority`: Normal = 7-day voting, 67% threshold; Emergency = 24-hour voting, 75% threshold.
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::propose())]
        pub fn propose(
            origin: OriginFor<T>,
            call_encoded: BoundedVec<u8, MaxProposalCallLen>,
            priority: ProposalPriority,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(
                RepresentativeToOrg::<T>::contains_key(&who),
                Error::<T>::NotRepresentative
            );
            ensure!(!call_encoded.is_empty(), Error::<T>::ProposalDecodeFailed);

            let now = frame_system::Pallet::<T>::block_number();
            let voting_period = match priority {
                ProposalPriority::Normal => T::VotingPeriod::get(),
                ProposalPriority::Emergency => T::EmergencyVotingPeriod::get(),
            };
            let voting_ends_at = now.saturating_add(BlockNumberFor::<T>::from(voting_period));

            let id = NextProposalId::<T>::get();
            NextProposalId::<T>::put(id.saturating_add(1));

            let proposal = GovernanceProposal::<T> {
                proposer: who.clone(),
                call: call_encoded,
                created_at: now,
                voting_ends_at,
                status: ProposalStatus::Open,
                priority,
            };
            Proposals::<T>::insert(id, proposal);

            Self::deposit_event(Event::Proposed { proposal_id: id, proposer: who });
            Ok(())
        }

        /// Cast a vote. Caller must be a representative.
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::vote())]
        pub fn vote(origin: OriginFor<T>, proposal_id: u64, aye: bool) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let _org_id = RepresentativeToOrg::<T>::get(&who).ok_or(Error::<T>::NotRepresentative)?;

            let proposal =
                Proposals::<T>::get(&proposal_id).ok_or(Error::<T>::ProposalNotFound)?;
            ensure!(matches!(proposal.status, ProposalStatus::Open), Error::<T>::ProposalNotOpen);
            ensure!(!Votes::<T>::contains_key(proposal_id, &who), Error::<T>::AlreadyVoted);

            Votes::<T>::insert(proposal_id, &who, aye);
            Self::deposit_event(Event::Voted { proposal_id, voter: who, aye });
            Ok(())
        }

        /// Close voting and optionally execute if approved.
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::close_and_execute())]
        pub fn close_and_execute(origin: OriginFor<T>, proposal_id: u64) -> DispatchResult {
            ensure_signed(origin)?;

            let now = frame_system::Pallet::<T>::block_number();
            let mut proposal =
                Proposals::<T>::get(&proposal_id).ok_or(Error::<T>::ProposalNotFound)?;
            ensure!(matches!(proposal.status, ProposalStatus::Open), Error::<T>::ProposalNotOpen);
            ensure!(now >= proposal.voting_ends_at, Error::<T>::VotingNotEnded);

            let (aye_weight, _nay_weight, _total_weight) = Self::tally_votes(proposal_id)?;
            let total_possible: u64 = ConsortiumMembers::<T>::iter()
                .map(|(_, org)| org.voting_weight as u64)
                .sum();
            ensure!(total_possible > 0, Error::<T>::ProposalNotFound);

            let threshold = match proposal.priority {
                ProposalPriority::Normal => T::ApprovalThreshold::get(),
                ProposalPriority::Emergency => T::EmergencyApprovalThreshold::get(),
            };
            let aye_permill = Permill::from_rational(aye_weight, total_possible);
            let approved = aye_permill >= threshold;

            proposal.status = if approved {
                ProposalStatus::Approved
            } else {
                ProposalStatus::Rejected
            };
            Proposals::<T>::insert(proposal_id, &proposal);

            Self::deposit_event(Event::Closed {
                proposal_id,
                approved,
            });

            if approved {
                proposal.status = ProposalStatus::Executed;
                Proposals::<T>::insert(proposal_id, &proposal);

                let call = <T::RuntimeCall as Decode>::decode(&mut &proposal.call[..])
                    .map_err(|_| Error::<T>::ProposalDecodeFailed)?;
                let result = call.dispatch(frame_system::RawOrigin::Root.into());
                if result.is_ok() {
                    Self::deposit_event(Event::Executed { proposal_id });
                }
            }
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        fn tally_votes(proposal_id: u64) -> Result<(u64, u64, u64), Error<T>> {
            let mut aye: u64 = 0;
            let mut nay: u64 = 0;
            for (voter, aye_vote) in Votes::<T>::iter_prefix(proposal_id) {
                let org_id = RepresentativeToOrg::<T>::get(&voter).ok_or(Error::<T>::NotMember)?;
                let org = ConsortiumMembers::<T>::get(&org_id).ok_or(Error::<T>::NotMember)?;
                let w = org.voting_weight as u64;
                if aye_vote {
                    aye = aye.saturating_add(w);
                } else {
                    nay = nay.saturating_add(w);
                }
            }
            let total = aye.saturating_add(nay);
            Ok((aye, nay, total))
        }
    }
}
