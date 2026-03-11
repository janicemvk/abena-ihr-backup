//! # ABENA Health Record Hash Pallet
//!
//! Stores **cryptographic hashes** of medical records only (NOT full records) for
//! an immutable audit trail without exposing PHI on-chain. Full records live
//! off-chain (IPFS/encrypted DB); blockchain proves existence and integrity.
//!
//! **Features**: SHA-3 hashes, version chain (previous_version), multi-signature
//! access, access log, grant/revoke access, emergency override, link to quantum
//! results. HIPAA audit trail and FDA 21 CFR Part 11 oriented.

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Encode, Decode, DecodeWithMemTracking, MaxEncodedLen};
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
    use codec::{Encode, Decode, DecodeWithMemTracking, MaxEncodedLen};
    use sp_runtime::traits::Hash;
    use sp_runtime::{RuntimeDebug, SaturatedConversion};

    /// Configuration trait for the pallet.
    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// Weight information for extrinsics
        type WeightInfo: crate::WeightInfo;
    }

    /// Therapeutic modality (aligns with patient-identity / integrative care).
    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum TherapeuticModality {
        WesternMedicine,
        TraditionalChineseMedicine,
        Ayurveda,
        Homeopathy,
        Naturopathy,
        Integrative,
        Other,
    }

    /// Access record for audit trail (who accessed when, success/fail).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct AccessRecord<T: Config> {
        pub accessor: T::AccountId,
        pub block: BlockNumberFor<T>,
        pub granted: bool,
        pub emergency_override: bool,
    }

    /// Record type (spec: clinical note, lab, prescription, etc.).
    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum RecordTypeSpec {
        ClinicalNote,
        LabResult,
        Prescription,
        ImagingReport,
        QuantumAnalysis,
        TreatmentPlan,
        ConsentForm,
        IntegrativeAssessment,
    }

    /// Full record hash entry (spec: SHA-3 hash, IPFS CID, version chain, encryption key hash).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct RecordHash<T: Config> {
        pub record_id: T::Hash,
        pub patient_id: T::AccountId,
        pub record_hash: [u8; 32],
        pub ipfs_cid: Option<BoundedVec<u8, ConstU32<256>>>,
        pub record_type: RecordTypeSpec,
        pub therapeutic_modality: TherapeuticModality,
        pub created_at: u64,
        pub updated_at: u64,
        pub version: u32,
        pub previous_version: Option<T::Hash>,
        pub provider_signature: BoundedVec<u8, ConstU32<512>>,
        pub encryption_key_hash: [u8; 32],
        pub active: bool,
    }

    /// Multi-sig requirement: required signers and current signatures.
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct MultiSigRequirement<T: Config> {
        pub required_signatures: u8,
        pub approved_signers: BoundedVec<T::AccountId, ConstU32<16>>,
        pub current_signatures: BoundedVec<(T::AccountId, BoundedVec<u8, ConstU32<128>>), ConstU32<16>>,
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Health record hashes
    /// Maps (patient_id, record_id) to record hash entry
    #[pallet::storage]
    #[pallet::getter(fn record_hashes)]
    pub type RecordHashes<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        RecordId,
        RecordHashEntry<T>,
        OptionQuery,
    >;

    /// Record version history
    /// Maps (patient_id, record_id) to version list
    #[pallet::storage]
    pub type RecordVersions<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        RecordId,
        BoundedVec<RecordVersion<T>, ConstU32<100>>,
        ValueQuery,
    >;

    /// Multi-signature access controls
    /// Maps (patient_id, record_id) to required signatures
    #[pallet::storage]
    pub type MultiSigRequirements<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        RecordId,
        MultiSigConfig<T>,
        OptionQuery,
    >;

    /// Audit log entries
    /// Maps (patient_id, record_id) to audit log
    #[pallet::storage]
    pub type AuditLogs<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        RecordId,
        BoundedVec<AuditLogEntry<T>, ConstU32<1000>>,
        ValueQuery,
    >;

    // ---------- Spec storage (record_id = T::Hash) ----------

    /// Record hashes by record_id (immutable audit trail).
    #[pallet::storage]
    #[pallet::getter(fn record_hash_by_id)]
    pub type RecordHashStore<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::Hash,
        RecordHash<T>,
        OptionQuery,
    >;

    /// Patient's record IDs (for right to access: list all hashes for a patient).
    #[pallet::storage]
    #[pallet::getter(fn patient_record_ids)]
    pub type PatientRecordIds<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        BoundedVec<T::Hash, ConstU32<1000>>,
        ValueQuery,
    >;

    /// Access log: (record_id, accessor) -> list of access events.
    #[pallet::storage]
    #[pallet::getter(fn access_log)]
    pub type AccessLog<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::Hash,
        Blake2_128Concat,
        T::AccountId,
        BoundedVec<AccessRecord<T>, ConstU32<100>>,
        ValueQuery,
    >;

    /// Multi-signature requirements per record.
    #[pallet::storage]
    #[pallet::getter(fn multisig_permissions)]
    pub type MultiSigPermissions<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::Hash,
        MultiSigRequirement<T>,
        OptionQuery,
    >;

    /// Temporary access grants: (record_id, accessor) -> expiry block.
    #[pallet::storage]
    #[pallet::getter(fn access_grant_expiry)]
    pub type AccessGrants<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::Hash,
        Blake2_128Concat,
        T::AccountId,
        BlockNumberFor<T>,
        OptionQuery,
    >;

    /// Link to quantum result (record_id -> quantum result id / hash).
    #[pallet::storage]
    #[pallet::getter(fn quantum_result_link)]
    pub type QuantumResultLinks<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::Hash,
        T::Hash,
        OptionQuery,
    >;

    /// Emergency override used (record_id -> block) for breach/audit.
    #[pallet::storage]
    pub type EmergencyOverrideLog<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::Hash,
        Blake2_128Concat,
        T::AccountId,
        BlockNumberFor<T>,
        OptionQuery,
    >;

    /// Events emitted by this pallet
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// Record hash was recorded
        RecordHashRecorded {
            patient: T::AccountId,
            record_id: RecordId,
            record_hash: H256,
            provider: T::AccountId,
        },
        /// Record hash was updated
        RecordHashUpdated {
            patient: T::AccountId,
            record_id: RecordId,
            new_hash: H256,
            version: u32,
        },
        /// Multi-signature requirement was set
        MultiSigRequirementSet {
            patient: T::AccountId,
            record_id: RecordId,
            required_signatures: u32,
        },
        /// Audit log entry was created
        AuditLogCreated {
            patient: T::AccountId,
            record_id: RecordId,
            action: AuditAction,
        },
        /// New record hash created (spec)
        RecordHashCreated {
            record_id: T::Hash,
            patient: T::AccountId,
            record_type: RecordTypeSpec,
            version: u32,
        },
        /// Record hash updated (new version)
        RecordHashUpdatedSpec {
            record_id: T::Hash,
            patient: T::AccountId,
            version: u32,
            previous_version: T::Hash,
        },
        /// Access granted to record
        RecordAccessGranted {
            record_id: T::Hash,
            accessor: T::AccountId,
            expiry_block: BlockNumberFor<T>,
        },
        /// Access revoked
        RecordAccessRevoked {
            record_id: T::Hash,
            accessor: T::AccountId,
        },
        /// Record accessed (logged)
        RecordAccessed {
            record_id: T::Hash,
            accessor: T::AccountId,
            granted: bool,
            emergency: bool,
        },
        /// Integrity verification requested
        RecordIntegrityVerified {
            record_id: T::Hash,
            verifier: T::AccountId,
            matches: bool,
        },
        /// Linked to quantum result
        LinkedToQuantumResult {
            record_id: T::Hash,
            quantum_result_id: T::Hash,
        },
        /// Multi-sig requirement set
        MultiSigRequirementCreated {
            record_id: T::Hash,
            required_signatures: u8,
        },
        /// Emergency access override used
        EmergencyAccessOverride {
            record_id: T::Hash,
            accessor: T::AccountId,
            block: BlockNumberFor<T>,
        },
        /// Record marked inactive (right to be forgotten; audit preserved)
        RecordMarkedInactive {
            record_id: T::Hash,
            patient: T::AccountId,
        },
    }

    /// Errors that can occur in this pallet
    #[pallet::error]
    pub enum Error<T> {
        /// Record not found
        RecordNotFound,
        /// Invalid hash format
        InvalidHash,
        /// Insufficient signatures for multi-sig requirement
        InsufficientSignatures,
        /// Unauthorized access
        Unauthorized,
        /// Too many signers (exceeds BoundedVec limit)
        TooManySigners,
        /// Record already exists
        RecordAlreadyExists,
        /// Access denied (no grant or expired)
        AccessDenied,
        /// Invalid record hash length (must be 32 bytes)
        InvalidHashLength,
        /// Grant not found or already revoked
        GrantNotFound,
        /// Multi-sig not satisfied
        MultiSigNotSatisfied,
        /// Emergency override not authorized
        EmergencyOverrideDenied,
        /// Record inactive (right to be forgotten)
        RecordInactive,
    }

    /// Hooks for the pallet
    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    /// Extrinsics for the pallet
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Record a health record hash
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::record_hash())]
        pub fn record_hash(
            origin: OriginFor<T>,
            patient: T::AccountId,
            record_id: RecordId,
            record_hash: H256,
            record_type: RecordType,
            ipfs_cid: Option<Vec<u8>>,
        ) -> DispatchResult {
            let provider = ensure_signed(origin)?;

            // Check authorization (simplified - in production, check consent)
            // For now, allow provider to record hash

            let ipfs_cid_bounded = ipfs_cid.map(|cid| {
                BoundedVec::try_from(cid).unwrap_or_default()
            });
            
            let entry = RecordHashEntry {
                record_hash,
                record_type,
                provider: provider.clone(),
                created_at: <frame_system::Pallet<T>>::block_number(),
                ipfs_cid: ipfs_cid_bounded,
                version: 1,
            };

            RecordHashes::<T>::insert(&patient, &record_id, entry.clone());

            // Initialize version history
            let version = RecordVersion {
                hash: record_hash,
                version: 1,
                created_at: <frame_system::Pallet<T>>::block_number(),
                provider: provider.clone(),
            };
            RecordVersions::<T>::mutate(&patient, &record_id, |versions| {
                let _ = versions.try_push(version);
            });

            // Create audit log entry
            Self::add_audit_log(
                &patient,
                &record_id,
                AuditAction::RecordCreated,
                &provider,
            );

            Self::deposit_event(Event::RecordHashRecorded {
                patient,
                record_id,
                record_hash,
                provider,
            });

            Ok(())
        }

        /// Update a health record hash (creates new version)
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::update_hash())]
        pub fn update_hash(
            origin: OriginFor<T>,
            patient: T::AccountId,
            record_id: RecordId,
            new_hash: H256,
            ipfs_cid: Option<Vec<u8>>,
        ) -> DispatchResult {
            let provider = ensure_signed(origin)?;

            let mut entry = RecordHashes::<T>::get(&patient, &record_id)
                .ok_or(Error::<T>::RecordNotFound)?;

            // Check multi-signature requirements if set
            if let Some(multi_sig) = MultiSigRequirements::<T>::get(&patient, &record_id) {
                // In production, verify signatures here
                // For now, simplified check
            }

            // Increment version
            entry.version += 1;
            entry.record_hash = new_hash;
            entry.ipfs_cid = ipfs_cid.map(|cid| {
                BoundedVec::try_from(cid).unwrap_or_default()
            });
            entry.created_at = <frame_system::Pallet<T>>::block_number();

            RecordHashes::<T>::insert(&patient, &record_id, entry.clone());

            // Add to version history
            let version = RecordVersion {
                hash: new_hash,
                version: entry.version,
                created_at: <frame_system::Pallet<T>>::block_number(),
                provider: provider.clone(),
            };
            RecordVersions::<T>::mutate(&patient, &record_id, |versions| {
                let _ = versions.try_push(version);
            });

            // Create audit log entry
            Self::add_audit_log(
                &patient,
                &record_id,
                AuditAction::RecordUpdated,
                &provider,
            );

            Self::deposit_event(Event::RecordHashUpdated {
                patient,
                record_id,
                new_hash,
                version: entry.version,
            });

            Ok(())
        }

        /// Set multi-signature requirement for a record
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::set_multi_sig())]
        pub fn set_multi_sig_requirement(
            origin: OriginFor<T>,
            patient: T::AccountId,
            record_id: RecordId,
            required_signatures: u32,
            authorized_signers: Vec<T::AccountId>,
        ) -> DispatchResult {
            let _caller = ensure_signed(origin)?;

            // Only patient or authorized provider can set multi-sig
            // Simplified check for now

            // Convert authorized_signers to BoundedVec
            let authorized_signers_bounded = BoundedVec::try_from(authorized_signers)
                .map_err(|_| Error::<T>::TooManySigners)?;

            let config = MultiSigConfig {
                required_signatures,
                authorized_signers: authorized_signers_bounded,
            };

            MultiSigRequirements::<T>::insert(&patient, &record_id, config);

            Self::deposit_event(Event::MultiSigRequirementSet {
                patient,
                record_id,
                required_signatures,
            });

            Ok(())
        }

        // ---------- Spec dispatchables ----------

        /// Create a new record hash (first version). Record ID = hash of (patient + nonce + content_hash) or caller-provided.
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::create_record_hash())]
        pub fn create_record_hash(
            origin: OriginFor<T>,
            record_id: T::Hash,
            patient_id: T::AccountId,
            record_hash: [u8; 32],
            ipfs_cid: Option<BoundedVec<u8, ConstU32<256>>>,
            record_type: RecordTypeSpec,
            therapeutic_modality: TherapeuticModality,
            provider_signature: BoundedVec<u8, ConstU32<512>>,
            encryption_key_hash: [u8; 32],
        ) -> DispatchResult {
            let provider = ensure_signed(origin)?;

            ensure!(RecordHashStore::<T>::get(&record_id).is_none(), Error::<T>::RecordAlreadyExists);

            let now = <frame_system::Pallet<T>>::block_number();
            let now_u64 = now.saturated_into();

            let entry = RecordHash::<T> {
                record_id,
                patient_id: patient_id.clone(),
                record_hash,
                ipfs_cid,
                record_type,
                therapeutic_modality,
                created_at: now_u64,
                updated_at: now_u64,
                version: 1,
                previous_version: None,
                provider_signature,
                encryption_key_hash,
                active: true,
            };

            RecordHashStore::<T>::insert(&record_id, &entry);
            PatientRecordIds::<T>::mutate(&patient_id, |ids| {
                let _ = ids.try_push(record_id);
            });

            Self::deposit_event(Event::RecordHashCreated {
                record_id,
                patient: patient_id,
                record_type,
                version: 1,
            });
            Ok(())
        }

        /// Update record hash (new version; preserves previous_version link).
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::update_record_hash())]
        pub fn update_record_hash(
            origin: OriginFor<T>,
            record_id: T::Hash,
            record_hash: [u8; 32],
            ipfs_cid: Option<BoundedVec<u8, ConstU32<256>>>,
            provider_signature: BoundedVec<u8, ConstU32<512>>,
        ) -> DispatchResult {
            let _provider = ensure_signed(origin)?;

            let mut entry = RecordHashStore::<T>::get(&record_id).ok_or(Error::<T>::RecordNotFound)?;
            ensure!(entry.active, Error::<T>::RecordInactive);

            let now = <frame_system::Pallet<T>>::block_number();
            let now_u64 = now.saturated_into();
            let prev_hash = <T as frame_system::Config>::Hashing::hash_of(&entry.record_hash);

            entry.previous_version = Some(prev_hash);
            entry.record_hash = record_hash;
            entry.updated_at = now_u64;
            entry.version = entry.version.saturating_add(1);
            entry.ipfs_cid = ipfs_cid;
            entry.provider_signature = provider_signature;

            RecordHashStore::<T>::insert(&record_id, &entry);

            Self::deposit_event(Event::RecordHashUpdatedSpec {
                record_id,
                patient: entry.patient_id,
                version: entry.version,
                previous_version: prev_hash,
            });
            Ok(())
        }

        /// Grant temporary access to a record (patient or authorized).
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::grant_record_access())]
        pub fn grant_record_access(
            origin: OriginFor<T>,
            record_id: T::Hash,
            accessor: T::AccountId,
            expiry_block: BlockNumberFor<T>,
        ) -> DispatchResult {
            let granter = ensure_signed(origin)?;

            let entry = RecordHashStore::<T>::get(&record_id).ok_or(Error::<T>::RecordNotFound)?;
            ensure!(entry.active, Error::<T>::RecordInactive);
            ensure!(granter == entry.patient_id, Error::<T>::Unauthorized);

            let now = <frame_system::Pallet<T>>::block_number();
            ensure!(expiry_block > now, Error::<T>::AccessDenied);

            AccessGrants::<T>::insert(&record_id, &accessor, expiry_block);

            Self::deposit_event(Event::RecordAccessGranted {
                record_id,
                accessor,
                expiry_block,
            });
            Ok(())
        }

        /// Revoke access to a record.
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::revoke_record_access())]
        pub fn revoke_record_access(
            origin: OriginFor<T>,
            record_id: T::Hash,
            accessor: T::AccountId,
        ) -> DispatchResult {
            let revoker = ensure_signed(origin)?;

            let entry = RecordHashStore::<T>::get(&record_id).ok_or(Error::<T>::RecordNotFound)?;
            ensure!(revoker == entry.patient_id, Error::<T>::Unauthorized);

            AccessGrants::<T>::remove(&record_id, &accessor);

            Self::deposit_event(Event::RecordAccessRevoked {
                record_id,
                accessor,
            });
            Ok(())
        }

        /// Access record (logs attempt; verifies grant or multi-sig).
        #[pallet::call_index(7)]
        #[pallet::weight(T::WeightInfo::access_record())]
        pub fn access_record(
            origin: OriginFor<T>,
            record_id: T::Hash,
        ) -> DispatchResult {
            let accessor = ensure_signed(origin)?;

            let entry = RecordHashStore::<T>::get(&record_id).ok_or(Error::<T>::RecordNotFound)?;
            ensure!(entry.active, Error::<T>::RecordInactive);

            let granted = if accessor == entry.patient_id {
                true
            } else if let Some(expiry) = AccessGrants::<T>::get(&record_id, &accessor) {
                let now = <frame_system::Pallet<T>>::block_number();
                now <= expiry
            } else if let Some(ms) = MultiSigPermissions::<T>::get(&record_id) {
                ms.current_signatures.len() as u8 >= ms.required_signatures
            } else {
                false
            };

            let rec = AccessRecord::<T> {
                accessor: accessor.clone(),
                block: <frame_system::Pallet<T>>::block_number(),
                granted,
                emergency_override: false,
            };
            AccessLog::<T>::mutate(&record_id, &accessor, |log| {
                let _ = log.try_push(rec);
            });

            // Always emit an event and return Ok so the log entry is never rolled back.
            // Callers determine whether access was granted via the event's `granted` field
            // or by inspecting the last entry in AccessLog.
            Self::deposit_event(Event::RecordAccessed {
                record_id,
                accessor,
                granted,
                emergency: false,
            });
            Ok(())
        }

        /// Verify record integrity (compare supplied hash with stored).
        #[pallet::call_index(8)]
        #[pallet::weight(T::WeightInfo::verify_record_integrity())]
        pub fn verify_record_integrity(
            origin: OriginFor<T>,
            record_id: T::Hash,
            supplied_hash: [u8; 32],
        ) -> DispatchResult {
            let verifier = ensure_signed(origin)?;

            let entry = RecordHashStore::<T>::get(&record_id).ok_or(Error::<T>::RecordNotFound)?;
            let matches = entry.record_hash == supplied_hash;

            Self::deposit_event(Event::RecordIntegrityVerified {
                record_id,
                verifier,
                matches,
            });
            Ok(())
        }

        /// Link record to a quantum analysis result.
        #[pallet::call_index(9)]
        #[pallet::weight(T::WeightInfo::link_to_quantum_result())]
        pub fn link_to_quantum_result(
            origin: OriginFor<T>,
            record_id: T::Hash,
            quantum_result_id: T::Hash,
        ) -> DispatchResult {
            let _caller = ensure_signed(origin)?;

            let entry = RecordHashStore::<T>::get(&record_id).ok_or(Error::<T>::RecordNotFound)?;
            ensure!(entry.active, Error::<T>::RecordInactive);

            QuantumResultLinks::<T>::insert(&record_id, &quantum_result_id);

            Self::deposit_event(Event::LinkedToQuantumResult {
                record_id,
                quantum_result_id,
            });
            Ok(())
        }

        /// Create multi-signature requirement for a record.
        #[pallet::call_index(10)]
        #[pallet::weight(T::WeightInfo::create_multisig_requirement())]
        pub fn create_multisig_requirement(
            origin: OriginFor<T>,
            record_id: T::Hash,
            required_signatures: u8,
            approved_signers: BoundedVec<T::AccountId, ConstU32<16>>,
        ) -> DispatchResult {
            let caller = ensure_signed(origin)?;

            let entry = RecordHashStore::<T>::get(&record_id).ok_or(Error::<T>::RecordNotFound)?;
            ensure!(caller == entry.patient_id, Error::<T>::Unauthorized);
            ensure!(required_signatures as usize <= approved_signers.len(), Error::<T>::InsufficientSignatures);

            let req = MultiSigRequirement::<T> {
                required_signatures,
                approved_signers: approved_signers.clone(),
                current_signatures: BoundedVec::default(),
            };
            MultiSigPermissions::<T>::insert(&record_id, req);

            Self::deposit_event(Event::MultiSigRequirementCreated {
                record_id,
                required_signatures,
            });
            Ok(())
        }

        /// Sign for record access (multi-sig).
        #[pallet::call_index(11)]
        #[pallet::weight(T::WeightInfo::sign_record_access())]
        pub fn sign_record_access(
            origin: OriginFor<T>,
            record_id: T::Hash,
            signature: BoundedVec<u8, ConstU32<128>>,
        ) -> DispatchResult {
            let signer = ensure_signed(origin)?;

            let mut ms = MultiSigPermissions::<T>::get(&record_id).ok_or(Error::<T>::RecordNotFound)?;
            let approved = ms.approved_signers.iter().any(|a| a == &signer);
            ensure!(approved, Error::<T>::Unauthorized);
            let already = ms.current_signatures.iter().any(|(a, _)| a == &signer);
            ensure!(!already, Error::<T>::InsufficientSignatures);

            ms.current_signatures.try_push((signer.clone(), signature))
                .map_err(|_| Error::<T>::TooManySigners)?;
            MultiSigPermissions::<T>::insert(&record_id, ms);
            Ok(())
        }

        /// Emergency access override (break-glass). Root only.
        #[pallet::call_index(12)]
        #[pallet::weight(T::WeightInfo::emergency_access_override())]
        pub fn emergency_access_override(
            origin: OriginFor<T>,
            record_id: T::Hash,
            accessor: T::AccountId,
        ) -> DispatchResult {
            frame_system::ensure_root(origin)?;

            let entry = RecordHashStore::<T>::get(&record_id).ok_or(Error::<T>::RecordNotFound)?;
            ensure!(entry.active, Error::<T>::RecordInactive);

            let now = <frame_system::Pallet<T>>::block_number();
            EmergencyOverrideLog::<T>::insert(&record_id, &accessor, now);

            let rec = AccessRecord::<T> {
                accessor: accessor.clone(),
                block: now,
                granted: true,
                emergency_override: true,
            };
            AccessLog::<T>::mutate(&record_id, &accessor, |log| {
                let _ = log.try_push(rec);
            });

            Self::deposit_event(Event::EmergencyAccessOverride {
                record_id,
                accessor,
                block: now,
            });
            Ok(())
        }

        /// Mark record inactive (right to be forgotten; audit trail preserved).
        #[pallet::call_index(13)]
        #[pallet::weight(T::WeightInfo::mark_record_inactive())]
        pub fn mark_record_inactive(
            origin: OriginFor<T>,
            record_id: T::Hash,
        ) -> DispatchResult {
            let caller = ensure_signed(origin)?;

            let mut entry = RecordHashStore::<T>::get(&record_id).ok_or(Error::<T>::RecordNotFound)?;
            ensure!(caller == entry.patient_id, Error::<T>::Unauthorized);

            entry.active = false;
            RecordHashStore::<T>::insert(&record_id, &entry);

            Self::deposit_event(Event::RecordMarkedInactive {
                record_id,
                patient: entry.patient_id,
            });
            Ok(())
        }
    }

    /// Helper functions
    impl<T: Config> Pallet<T> {
        /// Add audit log entry
        fn add_audit_log(
            patient: &T::AccountId,
            record_id: &RecordId,
            action: AuditAction,
            actor: &T::AccountId,
        ) {
            let log_entry = AuditLogEntry {
                action: action.clone(),
                actor: actor.clone(),
                timestamp: <frame_system::Pallet<T>>::block_number(),
            };

            AuditLogs::<T>::mutate(patient, record_id, |logs| {
                let _ = logs.try_push(log_entry);
            });

            Self::deposit_event(Event::AuditLogCreated {
                patient: patient.clone(),
                record_id: record_id.clone(),
                action: action.clone(),
            });
        }
    }

/// Weight information for extrinsics
pub trait WeightInfo {
    fn record_hash() -> Weight;
    fn update_hash() -> Weight;
    fn set_multi_sig() -> Weight;
    fn create_record_hash() -> Weight;
    fn update_record_hash() -> Weight;
    fn grant_record_access() -> Weight;
    fn revoke_record_access() -> Weight;
    fn access_record() -> Weight;
    fn verify_record_integrity() -> Weight;
    fn link_to_quantum_result() -> Weight;
    fn create_multisig_requirement() -> Weight;
    fn sign_record_access() -> Weight;
    fn emergency_access_override() -> Weight;
    fn mark_record_inactive() -> Weight;
}

/// Record ID type
pub type RecordId = u64;

/// Record hash entry (hash should be SHA-3/Keccak-256 for ABENA consistency)
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct RecordHashEntry<T: frame_system::Config> {
    /// Cryptographic hash of the record (ABENA: use SHA-3 Keccak-256)
    pub record_hash: sp_core::H256,
    /// Type of record
    pub record_type: RecordType,
    /// Provider who created/updated the record
    pub provider: T::AccountId,
    /// Block number when created/updated
    pub created_at: BlockNumberFor<T>,
    /// IPFS CID if record is stored off-chain
    pub ipfs_cid: Option<BoundedVec<u8, ConstU32<256>>>,
    /// Version number
    pub version: u32,
}

/// Record type
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum RecordType {
    /// Clinical encounter
    ClinicalEncounter,
    /// Lab results
    LabResults,
    /// Imaging study
    Imaging,
    /// Medication record
    Medication,
    /// Diagnosis
    Diagnosis,
    /// Vital signs
    Vitals,
    /// Treatment plan
    TreatmentPlan,
    /// Genomic data (e.g. sequencing, variants, pharmacogenomics)
    Genomic,
    /// Longitudinal health history (aggregate timeline / summary)
    Longitudinal,
    /// Other
    Other(BoundedVec<u8, ConstU32<256>>),
}

/// Record version
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct RecordVersion<T: frame_system::Config> {
    /// Hash of this version
    pub hash: sp_core::H256,
    /// Version number
    pub version: u32,
    /// Block number when version was created
    pub created_at: BlockNumberFor<T>,
    /// Provider who created this version
    pub provider: T::AccountId,
}

/// Multi-signature configuration
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct MultiSigConfig<T: frame_system::Config> {
    /// Number of signatures required
    pub required_signatures: u32,
    /// List of authorized signers
    pub authorized_signers: BoundedVec<T::AccountId, ConstU32<100>>,
}

/// Audit action types
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum AuditAction {
    /// Record was created
    RecordCreated,
    /// Record was updated
    RecordUpdated,
    /// Record was accessed
    RecordAccessed,
    /// Record was deleted
    RecordDeleted,
    /// Access was granted
    AccessGranted,
    /// Access was revoked
    AccessRevoked,
}

/// Audit log entry
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct AuditLogEntry<T: frame_system::Config> {
    /// Action performed
    pub action: AuditAction,
    /// Account that performed the action
    pub actor: T::AccountId,
    /// Block number when action occurred
    pub timestamp: BlockNumberFor<T>,
}
}

pub use pallet::*;
