//! # ABENA Permissioned Validators Pallet
//!
//! Controls who can produce blocks on the ABENA healthcare network. Supports four
//! network modes—Public, Permissioned, Consortium, and Hybrid—and maintains a
//! whitelist of approved validators and registered healthcare institutions.
//!
//! ## Network Modes
//!
//! | Mode          | Who validates                              | Use case                        |
//! |---------------|--------------------------------------------|---------------------------------|
//! | Public        | Anyone (standard Aura/GRANDPA)             | Development / testnet           |
//! | Permissioned  | Only whitelisted `AccountId`s              | Enterprise healthcare           |
//! | Consortium    | Federated nodes per hospital network       | Hospital federation             |
//! | Hybrid        | Per-call override; some extrinsics locked  | Mixed public-private deployment |
//!
//! ## Validator Lifecycle
//! ```text
//!   Root ──► add_validator ──► Approved
//!                              │
//!                              ▼
//!                         remove_validator ──► Removed
//! ```
//!
//! ## Institution Lifecycle
//! ```text
//!   Anyone ──► register_institution ──► Pending
//!                                       │
//!                       approve_institution ──► Approved
//!                       revoke_institution  ──► Revoked
//! ```

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::dispatch::DispatchResult;
use sp_runtime::DispatchError;
use frame_support::traits::ConstU32;
use scale_info::TypeInfo;
use sp_runtime::{BoundedVec, RuntimeDebug};

#[cfg(test)]
mod mock;

#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;
pub mod weights;

// ── Public re-exports of types used in the runtime config ──────────────────
pub use pallet::*;
pub use weights::WeightInfo;

// ── Standalone types (outside the pallet mod so they can be referenced in ──
// ── runtime parameter_types! without importing the inner pallet module)   ──

/// The four operational modes for the ABENA network.
#[derive(Clone, Copy, PartialEq, Eq, Encode, Decode, RuntimeDebug, TypeInfo, MaxEncodedLen, serde::Serialize, serde::Deserialize)]
pub enum NetworkMode {
    /// Open to any validator — equivalent to a standard Substrate chain.
    Public,
    /// Only `AccountId`s in the `ApprovedValidators` map may produce blocks.
    Permissioned,
    /// Federated mode: validators are grouped by `consortium_id`; a sub-set of
    /// the federation signs each block (e.g., a hospital network).
    Consortium,
    /// Some on-chain functions are unrestricted while others require a
    /// validator that matches the calling pallet's assigned mode.
    Hybrid,
}

impl Default for NetworkMode {
    fn default() -> Self {
        NetworkMode::Public
    }
}

/// Healthcare institution categories recognised by the network.
#[derive(Clone, Copy, PartialEq, Eq, Encode, Decode, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[cfg_attr(feature = "std", derive(serde::Serialize, serde::Deserialize))]
pub enum InstitutionType {
    Hospital,
    Clinic,
    Laboratory,
    Pharmacy,
    InsuranceProvider,
    ResearchInstitution,
    GovernmentHealthAgency,
}

/// Approval state for validators and institutions.
#[derive(Clone, Copy, PartialEq, Eq, Encode, Decode, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[cfg_attr(feature = "std", derive(serde::Serialize, serde::Deserialize))]
pub enum ApprovalStatus {
    Pending,
    Approved,
    Revoked,
}

/// Role a validator plays in the network.
#[derive(Clone, Copy, PartialEq, Eq, Encode, Decode, RuntimeDebug, TypeInfo, MaxEncodedLen, serde::Serialize, serde::Deserialize)]
pub enum ValidatorRole {
    /// Full block-producing authority.
    BlockProducer,
    /// Finalisation only (GRANDPA voter but not Aura author).
    Finalizer,
    /// Member of a consortium sub-group.
    ConsortiumMember,
    /// Cross-chain bridge operator.
    BridgeOperator,
}

/// On-chain record for an approved validator node.
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub struct ValidatorInfo<AccountId, BlockNumber> {
    /// The validator's `AccountId` (authority key).
    pub account: AccountId,
    /// Human-readable institution name (max 64 bytes).
    pub institution_name: BoundedVec<u8, ConstU32<64>>,
    /// Which role this validator performs.
    pub role: ValidatorRole,
    /// Whether the validator is currently active.
    pub status: ApprovalStatus,
    /// Block at which the validator was added.
    pub added_at: BlockNumber,
    /// Optional consortium group identifier (0 = no consortium).
    pub consortium_id: u32,
}

/// Trait for submitting a validator-addition proposal to consortium governance.
/// The runtime implements this to bridge permissioned-validators and consortium-governance:
/// builds the encoded `add_validator` call and forwards to `ConsortiumGovernance::propose`.
pub trait ValidatorProposalSubmitter<T: frame_system::Config> {
    fn submit_validator_proposal(
        origin: T::RuntimeOrigin,
        candidate: T::AccountId,
        institution_name: sp_std::vec::Vec<u8>,
        role: ValidatorRole,
        consortium_id: u32,
    ) -> DispatchResult;
}

/// No-op implementation for runtimes or tests that do not use consortium-based validator voting.
impl<T: frame_system::Config> ValidatorProposalSubmitter<T> for () {
    fn submit_validator_proposal(
        _origin: T::RuntimeOrigin,
        _candidate: T::AccountId,
        _institution_name: sp_std::vec::Vec<u8>,
        _role: ValidatorRole,
        _consortium_id: u32,
    ) -> DispatchResult {
        Err(DispatchError::Other(
            "ValidatorProposalSubmitter not configured",
        ))
    }
}

/// On-chain record for a registered healthcare institution.
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub struct InstitutionInfo<AccountId, BlockNumber> {
    /// Representative account for the institution.
    pub account: AccountId,
    /// Human-readable name (max 64 bytes).
    pub name: BoundedVec<u8, ConstU32<64>>,
    /// Category of the institution.
    pub institution_type: InstitutionType,
    /// SHA-256 hash of the off-chain contact / compliance document.
    pub contact_hash: [u8; 32],
    /// Registration status.
    pub status: ApprovalStatus,
    /// Block at which the institution was registered.
    pub registered_at: BlockNumber,
}

// ── Pallet ─────────────────────────────────────────────────────────────────

#[frame_support::pallet]
pub mod pallet {
    use super::*;
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;

    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;

        /// Origin that may change the network mode and manage validators
        /// (typically `EnsureRoot` or a governance collective).
        type AdminOrigin: EnsureOrigin<Self::RuntimeOrigin>;

        /// Maximum number of validators that may be whitelisted simultaneously.
        #[pallet::constant]
        type MaxValidators: Get<u32>;

        /// Maximum number of institutions that may be registered.
        #[pallet::constant]
        type MaxInstitutions: Get<u32>;

        /// Weight information for extrinsics.
        type WeightInfo: WeightInfo;

        /// Optional: submit validator-addition proposals to consortium governance.
        /// Set to `()` for no-op (extrinsic will fail). Set to runtime impl for governance-based voting.
        type ValidatorProposalSubmitter: ValidatorProposalSubmitter<Self>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // ── Storage ──────────────────────────────────────────────────────────

    /// Current operational mode of the network.
    #[pallet::storage]
    #[pallet::getter(fn network_mode)]
    pub type CurrentNetworkMode<T: Config> =
        StorageValue<_, NetworkMode, ValueQuery>;

    /// Lookup: `AccountId` → `ValidatorInfo`.
    #[pallet::storage]
    #[pallet::getter(fn validator_info)]
    pub type ApprovedValidators<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        ValidatorInfo<T::AccountId, BlockNumberFor<T>>,
        OptionQuery,
    >;

    /// Ordered list of approved validator `AccountId`s for fast iteration.
    #[pallet::storage]
    #[pallet::getter(fn validator_list)]
    pub type ValidatorList<T: Config> =
        StorageValue<_, BoundedVec<T::AccountId, T::MaxValidators>, ValueQuery>;

    /// Lookup: `AccountId` → `InstitutionInfo`.
    #[pallet::storage]
    #[pallet::getter(fn institution_info)]
    pub type RegisteredInstitutions<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        InstitutionInfo<T::AccountId, BlockNumberFor<T>>,
        OptionQuery,
    >;

    /// Ordered list of registered institution `AccountId`s.
    #[pallet::storage]
    #[pallet::getter(fn institution_list)]
    pub type InstitutionList<T: Config> =
        StorageValue<_, BoundedVec<T::AccountId, T::MaxInstitutions>, ValueQuery>;

    // ── Genesis ──────────────────────────────────────────────────────────

    #[pallet::genesis_config]
    #[derive(frame_support::DefaultNoBound)]
    pub struct GenesisConfig<T: Config> {
        /// Initial network mode (defaults to `Public`).
        pub initial_mode: NetworkMode,
        /// Validators to pre-approve at genesis `(account, institution_name, role, consortium_id)`.
        pub initial_validators: sp_std::vec::Vec<(T::AccountId, sp_std::vec::Vec<u8>, ValidatorRole, u32)>,
    }

    #[pallet::genesis_build]
    impl<T: Config> BuildGenesisConfig for GenesisConfig<T> {
        fn build(&self) {
            CurrentNetworkMode::<T>::put(self.initial_mode);

            for (account, name_bytes, role, consortium_id) in &self.initial_validators {
                let name: BoundedVec<u8, ConstU32<64>> =
                    BoundedVec::try_from(name_bytes.clone())
                        .expect("genesis validator institution name must be ≤ 64 bytes");

                let info = ValidatorInfo {
                    account: account.clone(),
                    institution_name: name,
                    role: *role,
                    status: ApprovalStatus::Approved,
                    added_at: frame_system::Pallet::<T>::block_number(),
                    consortium_id: *consortium_id,
                };
                ApprovedValidators::<T>::insert(account, info);

                ValidatorList::<T>::mutate(|list| {
                    let _ = list.try_push(account.clone());
                });
            }
        }
    }

    // ── Events ───────────────────────────────────────────────────────────

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// The network mode was changed.
        NetworkModeChanged {
            old_mode: NetworkMode,
            new_mode: NetworkMode,
        },
        /// A validator was added to the whitelist.
        ValidatorAdded {
            validator: T::AccountId,
            institution_name: BoundedVec<u8, ConstU32<64>>,
            role: ValidatorRole,
            consortium_id: u32,
        },
        /// A validator was removed from the whitelist.
        ValidatorRemoved {
            validator: T::AccountId,
        },
        /// A validator's role or consortium was updated.
        ValidatorUpdated {
            validator: T::AccountId,
            new_role: ValidatorRole,
            new_consortium_id: u32,
        },
        /// A healthcare institution submitted a registration request.
        InstitutionRegistered {
            institution: T::AccountId,
            name: BoundedVec<u8, ConstU32<64>>,
            institution_type: InstitutionType,
        },
        /// An institution's registration was approved by an admin.
        InstitutionApproved {
            institution: T::AccountId,
        },
        /// An institution's registration was revoked.
        InstitutionRevoked {
            institution: T::AccountId,
        },
        /// A validator-addition proposal was submitted to consortium governance.
        ValidatorProposalSubmitted {
            candidate: T::AccountId,
            institution_name: BoundedVec<u8, ConstU32<64>>,
            role: ValidatorRole,
            consortium_id: u32,
        },
    }

    // ── Errors ───────────────────────────────────────────────────────────

    #[pallet::error]
    pub enum Error<T> {
        /// The validator is already in the whitelist.
        ValidatorAlreadyExists,
        /// No validator with that `AccountId` was found.
        ValidatorNotFound,
        /// The validator whitelist is at capacity (`MaxValidators`).
        ValidatorListFull,
        /// The institution is already registered.
        InstitutionAlreadyRegistered,
        /// No institution with that `AccountId` was found.
        InstitutionNotFound,
        /// The institution list is at capacity (`MaxInstitutions`).
        InstitutionListFull,
        /// The provided name is too long (max 64 bytes).
        NameTooLong,
        /// Cannot remove a validator that is not in `Approved` status.
        ValidatorNotApproved,
        /// The institution must be in `Pending` state to be approved.
        InstitutionNotPending,
        /// The network mode is already set to the requested value.
        ModeUnchanged,
    }

    // ── Extrinsics ───────────────────────────────────────────────────────

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Switch the network to a different operational mode.
        ///
        /// Requires `AdminOrigin` (typically `Root` or a governance body).
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::set_network_mode())]
        pub fn set_network_mode(
            origin: OriginFor<T>,
            new_mode: NetworkMode,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            let old_mode = CurrentNetworkMode::<T>::get();
            ensure!(old_mode != new_mode, Error::<T>::ModeUnchanged);

            CurrentNetworkMode::<T>::put(new_mode);

            Self::deposit_event(Event::NetworkModeChanged { old_mode, new_mode });
            Ok(())
        }

        /// Whitelist a validator node for block production.
        ///
        /// Requires `AdminOrigin`. The `institution_name` is the human-readable
        /// name of the owning healthcare organisation (≤ 64 bytes UTF-8).
        /// Set `consortium_id` to `0` if not part of a Consortium group.
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::add_validator())]
        pub fn add_validator(
            origin: OriginFor<T>,
            validator: T::AccountId,
            institution_name: sp_std::vec::Vec<u8>,
            role: ValidatorRole,
            consortium_id: u32,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            ensure!(
                !ApprovedValidators::<T>::contains_key(&validator),
                Error::<T>::ValidatorAlreadyExists
            );

            let name: BoundedVec<u8, ConstU32<64>> =
                BoundedVec::try_from(institution_name).map_err(|_| Error::<T>::NameTooLong)?;

            let info = ValidatorInfo {
                account: validator.clone(),
                institution_name: name.clone(),
                role,
                status: ApprovalStatus::Approved,
                added_at: frame_system::Pallet::<T>::block_number(),
                consortium_id,
            };
            ApprovedValidators::<T>::insert(&validator, info);

            ValidatorList::<T>::try_mutate(|list| {
                list.try_push(validator.clone()).map_err(|_| Error::<T>::ValidatorListFull)
            })?;

            Self::deposit_event(Event::ValidatorAdded {
                validator,
                institution_name: name,
                role,
                consortium_id,
            });
            Ok(())
        }

        /// Propose adding a new validator via consortium governance.
        ///
        /// Caller must be a consortium representative. The proposal is submitted to
        /// `ConsortiumGovernance::propose`; if approved after the voting period,
        /// `add_validator` is dispatched with `Root` origin and the candidate is added.
        ///
        /// Requires `ValidatorProposalSubmitter` to be configured (e.g. wired to
        /// consortium-governance in the runtime).
        #[pallet::call_index(7)]
        #[pallet::weight(T::WeightInfo::propose_new_validator())]
        pub fn propose_new_validator(
            origin: OriginFor<T>,
            candidate: T::AccountId,
            institution_name: sp_std::vec::Vec<u8>,
            role: ValidatorRole,
            consortium_id: u32,
        ) -> DispatchResult {
            ensure_signed(origin.clone())?;

            ensure!(
                !ApprovedValidators::<T>::contains_key(&candidate),
                Error::<T>::ValidatorAlreadyExists
            );

            let bounded_name: BoundedVec<u8, ConstU32<64>> =
                BoundedVec::try_from(institution_name.clone()).map_err(|_| Error::<T>::NameTooLong)?;

            T::ValidatorProposalSubmitter::submit_validator_proposal(
                origin,
                candidate.clone(),
                institution_name,
                role,
                consortium_id,
            )?;

            Self::deposit_event(Event::ValidatorProposalSubmitted {
                candidate,
                institution_name: bounded_name,
                role,
                consortium_id,
            });
            Ok(())
        }

        /// Remove a validator from the whitelist.
        ///
        /// Requires `AdminOrigin`. The validator's `ValidatorInfo` is deleted and
        /// its `AccountId` is removed from `ValidatorList`.
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::remove_validator())]
        pub fn remove_validator(
            origin: OriginFor<T>,
            validator: T::AccountId,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            ensure!(
                ApprovedValidators::<T>::contains_key(&validator),
                Error::<T>::ValidatorNotFound
            );

            ApprovedValidators::<T>::remove(&validator);
            ValidatorList::<T>::mutate(|list| {
                list.retain(|v| v != &validator);
            });

            Self::deposit_event(Event::ValidatorRemoved { validator });
            Ok(())
        }

        /// Update the role and/or consortium group of an existing validator.
        ///
        /// Requires `AdminOrigin`.
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::update_validator())]
        pub fn update_validator(
            origin: OriginFor<T>,
            validator: T::AccountId,
            new_role: ValidatorRole,
            new_consortium_id: u32,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            ApprovedValidators::<T>::try_mutate(&validator, |maybe_info| {
                let info = maybe_info.as_mut().ok_or(Error::<T>::ValidatorNotFound)?;
                info.role = new_role;
                info.consortium_id = new_consortium_id;
                Ok::<_, Error<T>>(())
            })?;

            Self::deposit_event(Event::ValidatorUpdated {
                validator,
                new_role,
                new_consortium_id,
            });
            Ok(())
        }

        /// Register a healthcare institution on-chain.
        ///
        /// Any signed account may submit a registration; an admin must approve it
        /// via `approve_institution` before it is considered active. The
        /// `contact_hash` is the SHA-256 of the off-chain compliance document.
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::register_institution())]
        pub fn register_institution(
            origin: OriginFor<T>,
            name: sp_std::vec::Vec<u8>,
            institution_type: InstitutionType,
            contact_hash: [u8; 32],
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(
                !RegisteredInstitutions::<T>::contains_key(&who),
                Error::<T>::InstitutionAlreadyRegistered
            );

            let bounded_name: BoundedVec<u8, ConstU32<64>> =
                BoundedVec::try_from(name).map_err(|_| Error::<T>::NameTooLong)?;

            let info = InstitutionInfo {
                account: who.clone(),
                name: bounded_name.clone(),
                institution_type,
                contact_hash,
                status: ApprovalStatus::Pending,
                registered_at: frame_system::Pallet::<T>::block_number(),
            };
            RegisteredInstitutions::<T>::insert(&who, info);

            InstitutionList::<T>::try_mutate(|list| {
                list.try_push(who.clone()).map_err(|_| Error::<T>::InstitutionListFull)
            })?;

            Self::deposit_event(Event::InstitutionRegistered {
                institution: who,
                name: bounded_name,
                institution_type,
            });
            Ok(())
        }

        /// Approve a previously registered institution.
        ///
        /// Requires `AdminOrigin`. The institution must currently be `Pending`.
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::approve_institution())]
        pub fn approve_institution(
            origin: OriginFor<T>,
            institution: T::AccountId,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            RegisteredInstitutions::<T>::try_mutate(&institution, |maybe_info| {
                let info = maybe_info.as_mut().ok_or(Error::<T>::InstitutionNotFound)?;
                ensure!(
                    info.status == ApprovalStatus::Pending,
                    Error::<T>::InstitutionNotPending
                );
                info.status = ApprovalStatus::Approved;
                Ok::<_, DispatchError>(())
            })?;

            Self::deposit_event(Event::InstitutionApproved { institution });
            Ok(())
        }

        /// Revoke an institution's approved status.
        ///
        /// Requires `AdminOrigin`. Works on both `Pending` and `Approved`
        /// institutions. The record is retained for audit purposes.
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::revoke_institution())]
        pub fn revoke_institution(
            origin: OriginFor<T>,
            institution: T::AccountId,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            RegisteredInstitutions::<T>::try_mutate(&institution, |maybe_info| {
                let info = maybe_info.as_mut().ok_or(Error::<T>::InstitutionNotFound)?;
                info.status = ApprovalStatus::Revoked;
                Ok::<_, DispatchError>(())
            })?;

            Self::deposit_event(Event::InstitutionRevoked { institution });
            Ok(())
        }
    }

    // ── Helper / query functions ──────────────────────────────────────────

    impl<T: Config> Pallet<T> {
        /// Returns `true` if `who` is an approved, non-revoked validator.
        pub fn is_approved_validator(who: &T::AccountId) -> bool {
            ApprovedValidators::<T>::get(who)
                .map(|v| v.status == ApprovalStatus::Approved)
                .unwrap_or(false)
        }

        /// Returns the list of all currently approved validator `AccountId`s.
        pub fn approved_validator_accounts() -> sp_std::vec::Vec<T::AccountId> {
            ValidatorList::<T>::get()
                .into_iter()
                .filter(|a| Self::is_approved_validator(a))
                .collect()
        }

        /// Returns `true` if the network is in a mode that restricts block
        /// production to whitelisted validators.
        pub fn is_permissioned() -> bool {
            matches!(
                CurrentNetworkMode::<T>::get(),
                NetworkMode::Permissioned | NetworkMode::Consortium | NetworkMode::Hybrid
            )
        }

        /// Returns all validators belonging to a specific consortium group.
        pub fn consortium_validators(
            consortium_id: u32,
        ) -> sp_std::vec::Vec<T::AccountId> {
            ValidatorList::<T>::get()
                .into_iter()
                .filter(|a| {
                    ApprovedValidators::<T>::get(a)
                        .map(|v| {
                            v.consortium_id == consortium_id
                                && v.status == ApprovalStatus::Approved
                        })
                        .unwrap_or(false)
                })
                .collect()
        }
    }
}
