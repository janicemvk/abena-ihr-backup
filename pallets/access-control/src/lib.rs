//! # Access Control Pallet
//!
//! A pallet for patient authorization (free reads), institutional permissions,
//! emergency access protocols, and audit logging.

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
    use super::{PermissionId, PatientAuthorization, InstitutionalPermission, EmergencyAccess, AuditLog, PermissionType, AccessLevel, EmergencyAccessReason};
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

    /// Patient authorizations
    /// Maps (patient_account, resource_id) to authorization
    #[pallet::storage]
    pub type PatientAuthorizations<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        H256,
        PatientAuthorization<T>,
        OptionQuery,
    >;

    /// Institutional permissions
    /// Maps (institution_account, resource_id) to permission
    #[pallet::storage]
    pub type InstitutionalPermissions<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        H256,
        InstitutionalPermission<T>,
        OptionQuery,
    >;

    /// Emergency access records
    /// Maps (requester_account, resource_id) to emergency access record
    #[pallet::storage]
    pub type EmergencyAccessRecords<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        H256,
        EmergencyAccess<T>,
        OptionQuery,
    >;

    /// Audit log
    /// Maps log_id to audit log entry
    #[pallet::storage]
    pub type AuditLogs<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        u64,
        AuditLog<T>,
        OptionQuery,
    >;

    /// Next audit log ID
    #[pallet::storage]
    pub type NextAuditLogId<T: Config> = StorageValue<_, u64, ValueQuery>;

    /// Events emitted by this pallet
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// Patient authorization granted
        PatientAuthorizationGranted {
            patient: T::AccountId,
            resource_id: H256,
            permission_type: PermissionType,
        },
        /// Patient authorization revoked
        PatientAuthorizationRevoked {
            patient: T::AccountId,
            resource_id: H256,
        },
        /// Institutional permission granted
        InstitutionalPermissionGranted {
            institution: T::AccountId,
            resource_id: H256,
            access_level: AccessLevel,
        },
        /// Institutional permission revoked
        InstitutionalPermissionRevoked {
            institution: T::AccountId,
            resource_id: H256,
        },
        /// Emergency access granted
        EmergencyAccessGranted {
            requester: T::AccountId,
            resource_id: H256,
            reason: EmergencyAccessReason,
            authorized_by: T::AccountId,
        },
        /// Emergency access revoked
        EmergencyAccessRevoked {
            requester: T::AccountId,
            resource_id: H256,
        },
        /// Audit log entry created
        AuditLogCreated {
            log_id: u64,
            account: T::AccountId,
            action: Vec<u8>,
        },
    }

    /// Errors that can occur in this pallet
    #[pallet::error]
    pub enum Error<T> {
        /// Authorization not found
        AuthorizationNotFound,
        /// Permission not found
        PermissionNotFound,
        /// Unauthorized access attempt
        Unauthorized,
        /// Emergency access not authorized
        EmergencyAccessNotAuthorized,
        /// Invalid permission type
        InvalidPermissionType,
        /// Content too large
        ContentTooLarge,
    }

    /// Hooks for the pallet
    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    /// Extrinsics for the pallet
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Grant patient authorization (free reads for patients)
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::grant_patient_authorization())]
        pub fn grant_patient_authorization(
            origin: OriginFor<T>,
            resource_id: H256,
            permission_type: PermissionType,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            let authorization = PatientAuthorization {
                patient: patient.clone(),
                resource_id,
                permission_type,
                granted_at: <frame_system::Pallet<T>>::block_number(),
                expires_at: None, // Free reads don't expire
            };

            PatientAuthorizations::<T>::insert(&patient, &resource_id, authorization.clone());

            Self::log_audit(
                &patient,
                b"grant_patient_authorization".to_vec(),
                Some(resource_id),
            )?;

            Self::deposit_event(Event::PatientAuthorizationGranted {
                patient,
                resource_id,
                permission_type,
            });

            Ok(())
        }

        /// Revoke patient authorization
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::revoke_patient_authorization())]
        pub fn revoke_patient_authorization(
            origin: OriginFor<T>,
            resource_id: H256,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            ensure!(
                PatientAuthorizations::<T>::contains_key(&patient, &resource_id),
                Error::<T>::AuthorizationNotFound
            );

            PatientAuthorizations::<T>::remove(&patient, &resource_id);

            Self::log_audit(
                &patient,
                b"revoke_patient_authorization".to_vec(),
                Some(resource_id),
            )?;

            Self::deposit_event(Event::PatientAuthorizationRevoked {
                patient,
                resource_id,
            });

            Ok(())
        }

        /// Grant institutional permission
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::grant_institutional_permission())]
        pub fn grant_institutional_permission(
            origin: OriginFor<T>,
            institution: T::AccountId,
            resource_id: H256,
            access_level: AccessLevel,
            expires_at: Option<BlockNumberFor<T>>,
        ) -> DispatchResult {
            let granter = ensure_signed(origin)?;

            let permission = InstitutionalPermission {
                institution: institution.clone(),
                resource_id,
                access_level,
                granted_by: granter.clone(),
                granted_at: <frame_system::Pallet<T>>::block_number(),
                expires_at,
            };

            InstitutionalPermissions::<T>::insert(&institution, &resource_id, permission.clone());

            Self::log_audit(
                &granter,
                b"grant_institutional_permission".to_vec(),
                Some(resource_id),
            )?;

            Self::deposit_event(Event::InstitutionalPermissionGranted {
                institution,
                resource_id,
                access_level,
            });

            Ok(())
        }

        /// Revoke institutional permission
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::revoke_institutional_permission())]
        pub fn revoke_institutional_permission(
            origin: OriginFor<T>,
            institution: T::AccountId,
            resource_id: H256,
        ) -> DispatchResult {
            let revoker = ensure_signed(origin)?;

            ensure!(
                InstitutionalPermissions::<T>::contains_key(&institution, &resource_id),
                Error::<T>::PermissionNotFound
            );

            InstitutionalPermissions::<T>::remove(&institution, &resource_id);

            Self::log_audit(
                &revoker,
                b"revoke_institutional_permission".to_vec(),
                Some(resource_id),
            )?;

            Self::deposit_event(Event::InstitutionalPermissionRevoked {
                institution,
                resource_id,
            });

            Ok(())
        }

        /// Grant emergency access
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::grant_emergency_access())]
        pub fn grant_emergency_access(
            origin: OriginFor<T>,
            requester: T::AccountId,
            resource_id: H256,
            reason: EmergencyAccessReason,
            duration_blocks: BlockNumberFor<T>,
        ) -> DispatchResult {
            let authorizer = ensure_signed(origin)?;

            // Check if authorizer has emergency access authority (simplified check)
            // In production, verify against emergency authority list

            let current_block = <frame_system::Pallet<T>>::block_number();
            let emergency_access = EmergencyAccess {
                requester: requester.clone(),
                resource_id,
                reason: reason.clone(),
                authorized_by: authorizer.clone(),
                granted_at: current_block,
                expires_at: current_block + duration_blocks,
            };

            EmergencyAccessRecords::<T>::insert(&requester, &resource_id, emergency_access.clone());

            Self::log_audit(
                &authorizer,
                b"grant_emergency_access".to_vec(),
                Some(resource_id),
            )?;

            Self::deposit_event(Event::EmergencyAccessGranted {
                requester,
                resource_id,
                reason,
                authorized_by: authorizer,
            });

            Ok(())
        }

        /// Revoke emergency access
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::revoke_emergency_access())]
        pub fn revoke_emergency_access(
            origin: OriginFor<T>,
            requester: T::AccountId,
            resource_id: H256,
        ) -> DispatchResult {
            let revoker = ensure_signed(origin)?;

            ensure!(
                EmergencyAccessRecords::<T>::contains_key(&requester, &resource_id),
                Error::<T>::AuthorizationNotFound
            );

            EmergencyAccessRecords::<T>::remove(&requester, &resource_id);

            Self::log_audit(
                &revoker,
                b"revoke_emergency_access".to_vec(),
                Some(resource_id),
            )?;

            Self::deposit_event(Event::EmergencyAccessRevoked {
                requester,
                resource_id,
            });

            Ok(())
        }

        /// Check if account has read access (free for patients)
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::check_read_access())]
        pub fn check_read_access(
            account: &T::AccountId,
            resource_id: H256,
        ) -> Result<bool, Error<T>> {
            // Patients get free reads
            if PatientAuthorizations::<T>::contains_key(account, &resource_id) {
                return Ok(true);
            }

            // Check institutional permissions
            if let Some(permission) = InstitutionalPermissions::<T>::get(account, &resource_id) {
                let current_block = <frame_system::Pallet<T>>::block_number();
                
                // Check if expired
                if let Some(expires_at) = permission.expires_at {
                    if current_block > expires_at {
                        return Ok(false);
                    }
                }

                // Check access level
                match permission.access_level {
                    AccessLevel::Read | AccessLevel::Write | AccessLevel::Full => {
                        return Ok(true);
                    },
                    _ => return Ok(false),
                }
            }

            // Check emergency access
            if let Some(emergency) = EmergencyAccessRecords::<T>::get(account, &resource_id) {
                let current_block = <frame_system::Pallet<T>>::block_number();
                if current_block <= emergency.expires_at {
                    return Ok(true);
                }
            }

            Ok(false)
        }
    }

    impl<T: Config> Pallet<T> {
        /// Log audit entry
        fn log_audit(
            account: &T::AccountId,
            action: Vec<u8>,
            resource_id: Option<H256>,
        ) -> DispatchResult {
            let log_id = NextAuditLogId::<T>::get();
            NextAuditLogId::<T>::put(log_id + 1);

            let action_bounded = BoundedVec::try_from(action)
                .map_err(|_| Error::<T>::ContentTooLarge)?;

            let audit_log = AuditLog {
                log_id,
                account: account.clone(),
                action: action_bounded,
                resource_id,
                timestamp: <frame_system::Pallet<T>>::block_number(),
            };

            AuditLogs::<T>::insert(&log_id, audit_log.clone());

            Self::deposit_event(Event::AuditLogCreated {
                log_id,
                account: account.clone(),
                action: action_bounded.to_vec(),
            });

            Ok(())
        }
    }
}

/// Weight information for extrinsics
pub trait WeightInfo {
    fn grant_patient_authorization() -> Weight;
    fn revoke_patient_authorization() -> Weight;
    fn grant_institutional_permission() -> Weight;
    fn revoke_institutional_permission() -> Weight;
    fn grant_emergency_access() -> Weight;
    fn revoke_emergency_access() -> Weight;
    fn check_read_access() -> Weight;
}

/// Permission ID type
pub type PermissionId = u64;

/// Permission type
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum PermissionType {
    /// Read permission
    Read,
    /// Write permission
    Write,
    /// Full access permission
    Full,
}

/// Access level
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum AccessLevel {
    /// Read-only access
    Read,
    /// Write access
    Write,
    /// Full access
    Full,
}

/// Patient authorization
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct PatientAuthorization<T: frame_system::Config> {
    /// Patient account
    pub patient: T::AccountId,
    /// Resource identifier
    pub resource_id: sp_core::H256,
    /// Permission type (patients get free reads)
    pub permission_type: PermissionType,
    /// Block when authorization was granted
    pub granted_at: BlockNumberFor<T>,
    /// Block when authorization expires (None = never expires)
    pub expires_at: Option<BlockNumberFor<T>>,
}

/// Institutional permission
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct InstitutionalPermission<T: frame_system::Config> {
    /// Institution account
    pub institution: T::AccountId,
    /// Resource identifier
    pub resource_id: sp_core::H256,
    /// Access level
    pub access_level: AccessLevel,
    /// Account that granted the permission
    pub granted_by: T::AccountId,
    /// Block when permission was granted
    pub granted_at: BlockNumberFor<T>,
    /// Block when permission expires (None = never expires)
    pub expires_at: Option<BlockNumberFor<T>>,
}

/// Emergency access reason
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum EmergencyAccessReason {
    /// Life-threatening emergency
    LifeThreatening,
    /// Medical emergency
    MedicalEmergency,
    /// Legal requirement
    LegalRequirement,
    /// Other emergency reason
    Other(BoundedVec<u8, ConstU32<256>>),
}

/// Emergency access record
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct EmergencyAccess<T: frame_system::Config> {
    /// Requester account
    pub requester: T::AccountId,
    /// Resource identifier
    pub resource_id: sp_core::H256,
    /// Reason for emergency access
    pub reason: EmergencyAccessReason,
    /// Account that authorized emergency access
    pub authorized_by: T::AccountId,
    /// Block when emergency access was granted
    pub granted_at: BlockNumberFor<T>,
    /// Block when emergency access expires
    pub expires_at: BlockNumberFor<T>,
}

/// Audit log entry
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct AuditLog<T: frame_system::Config> {
    /// Log entry identifier
    pub log_id: u64,
    /// Account that performed the action
    pub account: T::AccountId,
    /// Action performed
    pub action: BoundedVec<u8, ConstU32<256>>,
    /// Resource identifier (if applicable)
    pub resource_id: Option<sp_core::H256>,
    /// Block when action was performed
    pub timestamp: BlockNumberFor<T>,
}

