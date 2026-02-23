//! # Governance Pallet
//!
//! A pallet for clinical guideline updates, protocol approval voting,
//! stakeholder consensus mechanisms, and emergency intervention procedures.

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Encode, Decode, MaxEncodedLen};
use scale_info::TypeInfo;
use sp_runtime::RuntimeDebug;
use frame_system::pallet_prelude::BlockNumberFor;
use frame_support::weights::Weight;
use sp_runtime::BoundedVec;
use frame_support::traits::ConstU32;


#[cfg(test)]
mod mock;

#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;
pub mod weights;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::{
        pallet_prelude::*,
        traits::ConstU32,
    };
    use frame_system::pallet_prelude::*;
    use scale_info::TypeInfo;
    use sp_std::vec::Vec;
    use sp_core::H256;
    use codec::MaxEncodedLen;
    use sp_runtime::BoundedVec;
    use super::{ProposalId, GuidelineProposal, ProtocolProposal, Vote, InterventionId, EmergencyIntervention, ProposalStatus, EmergencyInterventionType};
    use crate::WeightInfo;

    /// Configuration trait for the pallet.
    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// Weight information for extrinsics
        type WeightInfo: crate::WeightInfo;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Clinical guideline proposals
    #[pallet::storage]
    pub type GuidelineProposals<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        ProposalId,
        GuidelineProposal<T>,
        OptionQuery,
    >;

    /// Protocol approval proposals
    #[pallet::storage]
    pub type ProtocolProposals<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        ProposalId,
        ProtocolProposal<T>,
        OptionQuery,
    >;

    /// Votes for proposals
    /// Maps (proposal_id, voter) to vote
    #[pallet::storage]
    pub type Votes<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        ProposalId,
        Blake2_128Concat,
        T::AccountId,
        Vote,
        OptionQuery,
    >;

    /// Emergency interventions
    #[pallet::storage]
    pub type EmergencyInterventions<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        InterventionId,
        EmergencyIntervention<T>,
        OptionQuery,
    >;

    /// Events emitted by this pallet
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// Guideline proposal was created
        GuidelineProposalCreated {
            proposal_id: ProposalId,
            proposer: T::AccountId,
        },
        /// Protocol proposal was created
        ProtocolProposalCreated {
            proposal_id: ProposalId,
            proposer: T::AccountId,
        },
        /// Vote was cast
        VoteCast {
            proposal_id: ProposalId,
            voter: T::AccountId,
            vote: Vote,
        },
        /// Proposal was approved
        ProposalApproved {
            proposal_id: ProposalId,
        },
        /// Proposal was rejected
        ProposalRejected {
            proposal_id: ProposalId,
        },
        /// Emergency intervention was executed
        EmergencyInterventionExecuted {
            intervention_id: InterventionId,
            executor: T::AccountId,
        },
    }

    /// Errors that can occur in this pallet
    #[pallet::error]
    pub enum Error<T> {
        /// Proposal not found
        ProposalNotFound,
        /// Vote already cast
        VoteAlreadyCast,
        /// Proposal voting period ended
        VotingPeriodEnded,
        /// Unauthorized to create proposal
        Unauthorized,
        /// Emergency intervention not authorized
        InterventionNotAuthorized,
        /// Content too large for BoundedVec
        ContentTooLarge,
    }

    /// Hooks for the pallet
    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    /// Extrinsics for the pallet
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create a clinical guideline proposal
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::create_guideline_proposal())]
        pub fn create_guideline_proposal(
            origin: OriginFor<T>,
            proposal_id: ProposalId,
            guideline_content: Vec<u8>,
            voting_period: BlockNumberFor<T>,
        ) -> DispatchResult {
            let proposer = ensure_signed(origin)?;

            // Check authorization (simplified - in production, check stakeholder status)
            let guideline_content = BoundedVec::try_from(guideline_content)
                .map_err(|_| Error::<T>::ContentTooLarge)?;
            
            let proposal = GuidelineProposal {
                proposal_id,
                proposer: proposer.clone(),
                guideline_content,
                voting_period,
                created_at: <frame_system::Pallet<T>>::block_number(),
                status: ProposalStatus::Active,
            };

            GuidelineProposals::<T>::insert(&proposal_id, proposal);

            Self::deposit_event(Event::GuidelineProposalCreated {
                proposal_id,
                proposer,
            });

            Ok(())
        }

        /// Create a protocol approval proposal
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::create_protocol_proposal())]
        pub fn create_protocol_proposal(
            origin: OriginFor<T>,
            proposal_id: ProposalId,
            protocol_content: Vec<u8>,
            voting_period: BlockNumberFor<T>,
        ) -> DispatchResult {
            let proposer = ensure_signed(origin)?;

            let protocol_content = BoundedVec::try_from(protocol_content)
                .map_err(|_| Error::<T>::ContentTooLarge)?;

            let proposal = ProtocolProposal {
                proposal_id,
                proposer: proposer.clone(),
                protocol_content,
                voting_period,
                created_at: <frame_system::Pallet<T>>::block_number(),
                status: ProposalStatus::Active,
            };

            ProtocolProposals::<T>::insert(&proposal_id, proposal);

            Self::deposit_event(Event::ProtocolProposalCreated {
                proposal_id,
                proposer,
            });

            Ok(())
        }

        /// Cast a vote on a proposal
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::cast_vote())]
        pub fn cast_vote(
            origin: OriginFor<T>,
            proposal_id: ProposalId,
            vote: Vote,
        ) -> DispatchResult {
            let voter = ensure_signed(origin)?;

            // Check if proposal exists (check both types)
            let guideline_exists = GuidelineProposals::<T>::contains_key(&proposal_id);
            let protocol_exists = ProtocolProposals::<T>::contains_key(&proposal_id);
            
            ensure!(
                guideline_exists || protocol_exists,
                Error::<T>::ProposalNotFound
            );

            // Check if vote already cast
            ensure!(
                !Votes::<T>::contains_key(&proposal_id, &voter),
                Error::<T>::VoteAlreadyCast
            );

            // Check voting period (simplified check)
            if guideline_exists {
                let proposal = GuidelineProposals::<T>::get(&proposal_id).unwrap();
                let current_block = <frame_system::Pallet<T>>::block_number();
                ensure!(
                    current_block < proposal.created_at + proposal.voting_period,
                    Error::<T>::VotingPeriodEnded
                );
            }

            Votes::<T>::insert(&proposal_id, &voter, vote.clone());

            Self::deposit_event(Event::VoteCast {
                proposal_id,
                voter,
                vote,
            });

            Ok(())
        }

        /// Execute emergency intervention
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::execute_emergency_intervention())]
        pub fn execute_emergency_intervention(
            origin: OriginFor<T>,
            intervention_id: InterventionId,
            intervention_type: EmergencyInterventionType,
            reason: Vec<u8>,
        ) -> DispatchResult {
            let executor = ensure_signed(origin)?;

            // Check authorization (simplified - in production, verify emergency authority)
            // Convert reason to BoundedVec
            let reason_bounded = BoundedVec::try_from(reason)
                .map_err(|_| Error::<T>::ContentTooLarge)?;

            let intervention = EmergencyIntervention {
                intervention_id,
                executor: executor.clone(),
                intervention_type,
                reason: reason_bounded,
                executed_at: <frame_system::Pallet<T>>::block_number(),
            };

            EmergencyInterventions::<T>::insert(&intervention_id, intervention);

            Self::deposit_event(Event::EmergencyInterventionExecuted {
                intervention_id,
                executor,
            });

            Ok(())
        }
    }
}

/// Weight information for extrinsics
pub trait WeightInfo {
    fn create_guideline_proposal() -> Weight;
    fn create_protocol_proposal() -> Weight;
    fn cast_vote() -> Weight;
    fn execute_emergency_intervention() -> Weight;
}

/// Proposal ID type
pub type ProposalId = u64;

/// Intervention ID type
pub type InterventionId = u64;

/// Clinical guideline proposal
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
#[scale_info(skip_type_params(T))]
#[scale_info(skip_type_params(T))]
pub struct GuidelineProposal<T: frame_system::Config> {
    /// Proposal identifier
    pub proposal_id: ProposalId,
    /// Account that created the proposal
    pub proposer: T::AccountId,
    /// Guideline content (encoded)
    pub guideline_content: BoundedVec<u8, ConstU32<8192>>,
    /// Voting period in blocks
    pub voting_period: BlockNumberFor<T>,
    /// Block number when proposal was created
    pub created_at: BlockNumberFor<T>,
    /// Current proposal status
    pub status: ProposalStatus,
}

/// Protocol proposal
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
#[scale_info(skip_type_params(T))]
#[scale_info(skip_type_params(T))]
pub struct ProtocolProposal<T: frame_system::Config> {
    /// Proposal identifier
    pub proposal_id: ProposalId,
    /// Account that created the proposal
    pub proposer: T::AccountId,
    /// Protocol content (encoded)
    pub protocol_content: BoundedVec<u8, ConstU32<8192>>,
    /// Voting period in blocks
    pub voting_period: BlockNumberFor<T>,
    /// Block number when proposal was created
    pub created_at: BlockNumberFor<T>,
    /// Current proposal status
    pub status: ProposalStatus,
}

/// Vote
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum Vote {
    /// Approve
    Approve,
    /// Reject
    Reject,
    /// Abstain
    Abstain,
}

/// Proposal status
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum ProposalStatus {
    /// Proposal is active and accepting votes
    Active,
    /// Proposal was approved
    Approved,
    /// Proposal was rejected
    Rejected,
    /// Proposal expired
    Expired,
}

/// Emergency intervention type
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum EmergencyInterventionType {
    /// Suspend protocol
    SuspendProtocol,
    /// Override treatment
    OverrideTreatment,
    /// Emergency access grant
    EmergencyAccess,
    /// Other emergency action
    Other(BoundedVec<u8, ConstU32<256>>),
}

/// Emergency intervention
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
#[scale_info(skip_type_params(T))]
#[scale_info(skip_type_params(T))]
pub struct EmergencyIntervention<T: frame_system::Config> {
    /// Intervention identifier
    pub intervention_id: InterventionId,
    /// Account that executed the intervention
    pub executor: T::AccountId,
    /// Type of intervention
    pub intervention_type: EmergencyInterventionType,
    /// Reason for intervention
    pub reason: BoundedVec<u8, ConstU32<1024>>,
    /// Block number when intervention was executed
    pub executed_at: BlockNumberFor<T>,
}

