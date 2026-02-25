//! # ABENA Quantum Results Pallet
//!
//! Provides cryptographic attestation of quantum computation results from IBM Quantum,
//! creating an immutable audit trail for AI-assisted medical diagnostics.
//!
//! ## Purpose
//!
//! - Store attestations of quantum algorithm executions (VQE, QML, QAOA)
//! - Link quantum results to patient records via cryptographic hashes (pseudonymized)
//! - Verify IBM Quantum platform signatures for proof of execution
//! - Track quantum job metadata (algorithm type, parameters, execution time)
//! - Version control for algorithm improvements
//! - Generate quantum computation certificates for regulatory compliance (FDA 21 CFR Part 11, HIPAA)

#![cfg_attr(not(feature = "std"), no_std)]

#[cfg(test)]
mod mock;

#[cfg(test)]
mod tests;

pub mod offchain;
pub mod weights;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::offchain::SubmitTransaction;
    use frame_system::pallet_prelude::*;
    use sp_core::offchain::{Duration, HttpRequestStatus};
    use sp_runtime::traits::{Hash, Verify, Zero};
    use sp_runtime::transaction_validity::{
        InvalidTransaction, TransactionSource, TransactionValidity, ValidTransaction,
    };
    use sp_std::vec::Vec;

    use crate::weights::WeightInfo;

    /// Maximum length for IBM job ID bytes
    pub type JobIdMaxLen = ConstU32<64>;
    /// Maximum length for IBM signature
    pub type SignatureMaxLen = ConstU32<512>;
    /// Maximum length for linked clinical module identifier
    pub type ClinicalModuleMaxLen = ConstU32<64>;
    /// Max job IDs per patient
    pub type MaxJobsPerPatient = ConstU32<128>;

    /// Quantum algorithm type
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum QuantumAlgorithm {
        VQE,              // Variational Quantum Eigensolver
        QML,              // Quantum Machine Learning
        QAOA,             // Quantum Approximate Optimization
        QuantumSampling,
        GroversSearch,
        Custom,
    }

    /// Quantum attestation: immutable record of a quantum computation (FDA 21 CFR Part 11 audit trail).
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct QuantumAttestation<T: Config> {
        pub job_id: BoundedVec<u8, JobIdMaxLen>,
        pub patient_pseudonym: T::Hash,
        pub algorithm_type: QuantumAlgorithm,
        pub algorithm_version: u32,
        pub parameters_hash: T::Hash,
        pub result_hash: T::Hash,
        pub ibm_signature: BoundedVec<u8, SignatureMaxLen>,
        pub execution_timestamp: u64,
        pub circuit_depth: u32,
        pub qubit_count: u8,
        pub shots: u32,
        pub verified: bool,
        pub linked_clinical_module: Option<BoundedVec<u8, ClinicalModuleMaxLen>>,
        pub created_at: BlockNumberFor<T>,
    }

    /// Algorithm metadata for version control and compliance.
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct AlgorithmMetadata<T: Config> {
        pub algorithm_hash: T::Hash,
        pub algorithm_type: QuantumAlgorithm,
        pub version: u32,
        pub description: BoundedVec<u8, ConstU32<256>>,
        pub registered_at: BlockNumberFor<T>,
        pub owner: T::AccountId,
    }

    /// IBM Quantum backend (e.g. ibm_brisbane, ibm_kyoto).
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct IBMBackendInfo<T: Config> {
        pub backend_id: BoundedVec<u8, ConstU32<32>>,
        pub name: BoundedVec<u8, ConstU32<64>>,
        pub available: bool,
        pub qubit_count: u16,
        pub calibration_data_hash: Option<T::Hash>,
        pub registered_at: BlockNumberFor<T>,
    }

    /// Job completion status from IBM API.
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum JobCompletionStatus {
        Pending,
        Running,
        Completed,
        Failed,
    }

    /// Context needed by off-chain worker to submit attestation after IBM job completes.
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct PendingAttestationContext<T: Config> {
        pub patient_pseudonym: T::Hash,
        pub algorithm_type: QuantumAlgorithm,
        pub algorithm_version: u32,
        pub parameters_hash: T::Hash,
        pub execution_timestamp: u64,
        pub circuit_depth: u32,
        pub qubit_count: u8,
        pub shots: u32,
        pub linked_clinical_module: Option<BoundedVec<u8, ClinicalModuleMaxLen>>,
    }

    /// Pending job awaiting verification (in queue). Includes job_id for IBM API and optional context for attestation.
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct PendingJob<T: Config> {
        pub job_id: BoundedVec<u8, JobIdMaxLen>,
        pub job_id_hash: T::Hash,
        pub backend_id: BoundedVec<u8, ConstU32<32>>,
        pub status: JobCompletionStatus,
        pub submitted_at: BlockNumberFor<T>,
        pub attestation_context: Option<PendingAttestationContext<T>>,
    }

    /// Circuit transpilation and hardware metadata.
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct CircuitMetadata<T: Config> {
        pub job_id_hash: T::Hash,
        pub backend_id: BoundedVec<u8, ConstU32<32>>,
        pub transpilation_depth: u32,
        pub gate_fidelity_micro: u32,   // e.g. 999000 = 99.9%
        pub error_rate_micro: u32,      // per 1_000_000
        pub calibration_data_hash: Option<T::Hash>,
        pub created_at: BlockNumberFor<T>,
    }

    /// Result quality and error mitigation metrics.
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct QualityMetrics<T: Config> {
        pub job_id_hash: T::Hash,
        pub measurement_error_mitigation: BoundedVec<u8, ConstU32<64>>, // e.g. "m3" or "none"
        pub readout_error_rate_micro: u32,
        pub circuit_optimization_level: u8, // 0-3
        pub confidence_score_micro: u32,    // 0-1_000_000
        pub created_at: BlockNumberFor<T>,
    }

    /// Max jobs in a batch
    pub type MaxBatchSize = ConstU32<32>;
    /// Max backends in registry
    pub type MaxBackends = ConstU32<16>;
    /// Max pending jobs in queue
    pub type MaxQueueLen = ConstU32<64>;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::config]
    pub trait Config: frame_system::Config + frame_system::offchain::SendTransactionTypes<Call<Self>> {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type WeightInfo: crate::weights::WeightInfo;
        /// Run off-chain worker every N blocks (e.g. 10).
        #[pallet::constant]
        type OffchainWorkerInterval: Get<BlockNumberFor<Self>>;
    }

    /// Map from job_id (bounded bytes) to attestation. Key = hash(job_id) for fixed-size key.
    #[pallet::storage]
    #[pallet::getter(fn quantum_results)]
    pub type QuantumResults<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::Hash,
        QuantumAttestation<T>,
        OptionQuery,
    >;

    /// Job ID bytes -> hash (for lookup when we only have raw job_id).
    #[pallet::storage]
    pub(super) type JobIdToHash<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        BoundedVec<u8, JobIdMaxLen>,
        T::Hash,
        OptionQuery,
    >;

    /// Patient (account or pseudonym hash) -> list of attestation hashes (job_id hashes).
    #[pallet::storage]
    #[pallet::getter(fn patient_quantum_results)]
    pub type PatientQuantumResults<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::Hash,
        BoundedVec<T::Hash, MaxJobsPerPatient>,
        ValueQuery,
    >;

    /// Algorithm registry: algorithm_hash -> metadata (version control).
    #[pallet::storage]
    #[pallet::getter(fn algorithm_registry)]
    pub type AlgorithmRegistry<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::Hash,
        AlgorithmMetadata<T>,
        OptionQuery,
    >;

    /// IBM Quantum public keys for signature verification (key_id -> raw public key bytes).
    #[pallet::storage]
    #[pallet::getter(fn ibm_quantum_keys)]
    pub type IBMQuantumKeys<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        BoundedVec<u8, ConstU32<32>>,
        BoundedVec<u8, ConstU32<128>>,
        OptionQuery,
    >;

    /// Available IBM Quantum backends (ibm_brisbane, ibm_kyoto, etc.).
    #[pallet::storage]
    #[pallet::getter(fn ibm_backend_registry)]
    pub type IBMBackendRegistry<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        BoundedVec<u8, ConstU32<32>>,
        IBMBackendInfo<T>,
        OptionQuery,
    >;

    /// Pending jobs awaiting verification (ordered queue).
    #[pallet::storage]
    #[pallet::getter(fn quantum_job_queue)]
    pub type QuantumJobQueue<T: Config> = StorageValue<
        _,
        BoundedVec<PendingJob<T>, MaxQueueLen>,
        ValueQuery,
    >;

    /// Circuit metadata per job (transpilation, gate fidelity, calibration).
    #[pallet::storage]
    #[pallet::getter(fn circuit_metadata)]
    pub type CircuitMetadataMap<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::Hash,
        CircuitMetadata<T>,
        OptionQuery,
    >;

    /// Quality metrics per job (readout error, confidence score).
    #[pallet::storage]
    #[pallet::getter(fn quality_metrics)]
    pub type QualityMetricsMap<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::Hash,
        QualityMetrics<T>,
        OptionQuery,
    >;

    /// Batch: clinical_analysis_id -> list of job hashes (multiple jobs for one analysis).
    #[pallet::storage]
    #[pallet::getter(fn batch_jobs)]
    pub type BatchJobs<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::Hash,
        BoundedVec<T::Hash, MaxBatchSize>,
        OptionQuery,
    >;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        AlgorithmRegistered { algorithm_hash: T::Hash, algorithm_type: QuantumAlgorithm, version: u32 },
        QuantumResultAttested {
            job_id_hash: T::Hash,
            algorithm_type: QuantumAlgorithm,
            patient_pseudonym: T::Hash,
            verified: bool,
        },
        IBMSignatureVerified { job_id_hash: T::Hash, valid: bool },
        LinkedToPatient { job_id_hash: T::Hash, patient_pseudonym: T::Hash },
        ComplianceCertificateRequested { job_id_hash: T::Hash, requester: T::AccountId },
        AlgorithmVersionUpdated { algorithm_hash: T::Hash, new_version: u32 },
        IBMKeyRegistered { key_id: BoundedVec<u8, ConstU32<32>> },
        BackendRegistered { backend_id: BoundedVec<u8, ConstU32<32>>, name: BoundedVec<u8, ConstU32<64>> },
        BatchSubmitted { analysis_id: T::Hash, job_count: u32 },
        JobCompletionVerified { job_id_hash: T::Hash, status: JobCompletionStatus },
        ResultConfidenceCalculated { job_id_hash: T::Hash, confidence_micro: u32 },
        BatchLinked { analysis_id: T::Hash, patient_pseudonym: T::Hash, job_count: u32 },
    }

    #[pallet::error]
    pub enum Error<T> {
        JobAlreadyAttested,
        JobIdTooLong,
        SignatureTooLong,
        AlgorithmNotRegistered,
        InvalidSignature,
        PatientNotAuthorized,
        AttestationNotFound,
        TooManyJobsForPatient,
        DuplicateJobId,
        InvalidAlgorithmHash,
        /// Quantum job failed (IBM API reported failure)
        JobFailed,
        /// Backend not available or not registered
        BackendUnavailable,
        /// Result verification failed (signature or consistency)
        ResultVerificationFailed,
        /// Queue full
        QueueFull,
        /// Batch too large
        BatchTooLarge,
    }

    #[pallet::validate_unsigned]
    impl<T: Config> ValidateUnsigned for Pallet<T> {
        type Call = Call<T>;
        fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
            if let Call::submit_attestation_unsigned {
                job_id: ref jid, ..
            } = call
            {
                let job_id_b = match BoundedVec::<u8, JobIdMaxLen>::try_from(jid.clone()) {
                    Ok(b) => b,
                    Err(_) => return InvalidTransaction::BadProof.into(),
                };
                let job_id_hash = T::Hashing::hash_of(&job_id_b.encode());
                let in_queue = QuantumJobQueue::<T>::get()
                    .iter()
                    .any(|p| p.job_id_hash == job_id_hash && p.attestation_context.is_some());
                if !in_queue {
                    return InvalidTransaction::Custom(0).into(); // JobNotInQueue
                }
                ValidTransaction::with_tag_prefix("QuantumResults")
                    .longevity(64)
                    .propagate(true)
                    .build()
                    .map_err(Into::into)
            } else {
                InvalidTransaction::Call.into()
            }
        }
    }

    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {
        fn offchain_worker(block_number: BlockNumberFor<T>) {
            Self::offchain_worker_impl(block_number);

            use sp_io::offchain;

            if block_number % T::OffchainWorkerInterval::get() != Zero::zero() {
                return;
            }
            let queue = QuantumJobQueue::<T>::get();
            if queue.is_empty() {
                return;
            }
            // API token: node operator sets via offchain::local_storage_set(PERSENT, b"ibm_quantum_api_token", token_bytes)
            // and we could add header via http_request_add_header for Authorization (not done here for minimal impl).
            for pending in queue.iter() {
                if pending.status != JobCompletionStatus::Pending
                    && pending.status != JobCompletionStatus::Running
                {
                    continue;
                }
                let Some(ref ctx) = pending.attestation_context else { continue };
                let job_id_str = sp_std::str::from_utf8(pending.job_id.as_slice()).unwrap_or("");
                if job_id_str.is_empty() {
                    continue;
                }
                let base = b"https://api.quantum-computing.ibm.com/api/v2/jobs/";
                let mut url_buf = [0u8; 128];
                let blen = base.len().min(url_buf.len());
                url_buf[..blen].copy_from_slice(&base[..blen]);
                let jlen = pending.job_id.len().min(url_buf.len().saturating_sub(blen));
                url_buf[blen..blen + jlen].copy_from_slice(&pending.job_id[..jlen]);
                let url = sp_std::str::from_utf8(&url_buf[..blen + jlen]).unwrap_or("");
                let request = match offchain::http_request_start("GET", url, &[]) {
                    Ok(id) => id,
                    Err(_) => continue,
                };
                let timeout = offchain::timestamp().add(Duration::from_millis(8000));
                let ids = [request];
                let statuses = offchain::http_response_wait(&ids, Some(timeout));
                let status = match statuses.first() {
                    Some(s) => s,
                    None => continue,
                };
                if *status == HttpRequestStatus::Finished(200) {
                        let mut body = Vec::new();
                        let mut buf = [0u8; 4096];
                        loop {
                            match offchain::http_response_read_body(request, &mut buf, Some(timeout)) {
                                Ok(0) => break,
                                Ok(n) => body.extend_from_slice(&buf[..n as usize]),
                                Err(_) => break,
                            }
                        }
                        let body_str = sp_std::str::from_utf8(&body).unwrap_or("");
                        let completed = body_str.contains("\"status\":\"COMPLETED\"")
                            || body_str.contains("\"status\": \"COMPLETED\"");
                        let failed = body_str.contains("\"status\":\"FAILED\"")
                            || body_str.contains("\"status\": \"FAILED\"");
                        if failed {
                            QuantumJobQueue::<T>::mutate(|q| {
                                q.retain(|p| p.job_id_hash != pending.job_id_hash);
                            });
                            continue;
                        }
                        if !completed {
                            continue;
                        }
                        let result_hash = T::Hashing::hash_of(&body);
                        let sig: BoundedVec<u8, SignatureMaxLen> = BoundedVec::default();
                        let clinical_b = ctx.linked_clinical_module.clone();
                        let call = Call::submit_attestation_unsigned {
                            job_id: pending.job_id.to_vec(),
                            patient_pseudonym: ctx.patient_pseudonym,
                            algorithm_type: ctx.algorithm_type.clone(),
                            algorithm_version: ctx.algorithm_version,
                            parameters_hash: ctx.parameters_hash,
                            result_hash,
                            ibm_signature: sig.to_vec(),
                            execution_timestamp: ctx.execution_timestamp,
                            circuit_depth: ctx.circuit_depth,
                            qubit_count: ctx.qubit_count,
                            shots: ctx.shots,
                            linked_clinical_module: clinical_b.map(|b| b.to_vec()),
                        };
                        let _ = SubmitTransaction::<T, Call<T>>::submit_unsigned_transaction(call.into());
                        QuantumJobQueue::<T>::mutate(|q| {
                            q.retain(|p| p.job_id_hash != pending.job_id_hash);
                        });
                }
            }
        }
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Register quantum algorithm metadata (version control).
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::register_algorithm())]
        pub fn register_algorithm(
            origin: OriginFor<T>,
            algorithm_hash: T::Hash,
            algorithm_type: QuantumAlgorithm,
            version: u32,
            description: Vec<u8>,
        ) -> DispatchResult {
            let owner = ensure_signed(origin)?;
            let desc_bounded = BoundedVec::try_from(description).map_err(|_| Error::<T>::JobIdTooLong)?;
            let meta = AlgorithmMetadata {
                algorithm_hash,
                algorithm_type: algorithm_type.clone(),
                version,
                description: desc_bounded,
                registered_at: <frame_system::Pallet<T>>::block_number(),
                owner: owner.clone(),
            };
            AlgorithmRegistry::<T>::insert(algorithm_hash, meta);
            Self::deposit_event(Event::AlgorithmRegistered {
                algorithm_hash,
                algorithm_type,
                version,
            });
            Ok(())
        }

        /// Submit quantum computation attestation (single-shot or batch; one call per job).
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::attest_quantum_result())]
        pub fn attest_quantum_result(
            origin: OriginFor<T>,
            job_id: Vec<u8>,
            patient_pseudonym: T::Hash,
            algorithm_type: QuantumAlgorithm,
            algorithm_version: u32,
            parameters_hash: T::Hash,
            result_hash: T::Hash,
            ibm_signature: Vec<u8>,
            execution_timestamp: u64,
            circuit_depth: u32,
            qubit_count: u8,
            shots: u32,
            linked_clinical_module: Option<Vec<u8>>,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;

            let job_id_b = BoundedVec::try_from(job_id).map_err(|_| Error::<T>::JobIdTooLong)?;
            let sig_b = BoundedVec::try_from(ibm_signature).map_err(|_| Error::<T>::SignatureTooLong)?;
            let clinical_b = linked_clinical_module
                .map(|v| BoundedVec::try_from(v).map_err(|_| Error::<T>::JobIdTooLong))
                .transpose()?;

            let job_id_hash = T::Hashing::hash_of(&job_id_b.encode());
            ensure!(!QuantumResults::<T>::contains_key(&job_id_hash), Error::<T>::DuplicateJobId);

            let verified = Self::verify_ibm_signature_internal(&job_id_b, &result_hash, &sig_b);

            let attestation = QuantumAttestation {
                job_id: job_id_b.clone(),
                patient_pseudonym,
                algorithm_type: algorithm_type.clone(),
                algorithm_version,
                parameters_hash,
                result_hash,
                ibm_signature: sig_b,
                execution_timestamp,
                circuit_depth,
                qubit_count,
                shots,
                verified,
                linked_clinical_module: clinical_b,
                created_at: <frame_system::Pallet<T>>::block_number(),
            };

            QuantumResults::<T>::insert(job_id_hash, &attestation);
            JobIdToHash::<T>::insert(&job_id_b, job_id_hash);

            PatientQuantumResults::<T>::mutate(patient_pseudonym, |list| {
                if list.len() < <MaxJobsPerPatient as frame_support::traits::Get<u32>>::get() as usize {
                    let _ = list.try_push(job_id_hash);
                }
            });

            Self::deposit_event(Event::QuantumResultAttested {
                job_id_hash,
                algorithm_type,
                patient_pseudonym,
                verified,
            });
            Ok(())
        }

        /// Verify IBM Quantum signature for an attested job (and optionally update verified flag).
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::verify_ibm_signature())]
        pub fn verify_ibm_signature(origin: OriginFor<T>, job_id_hash: T::Hash) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            let attestation = QuantumResults::<T>::get(&job_id_hash).ok_or(Error::<T>::AttestationNotFound)?;
            let valid = Self::verify_ibm_signature_internal(
                &attestation.job_id,
                &attestation.result_hash,
                &attestation.ibm_signature,
            );
            if valid {
                QuantumResults::<T>::mutate(&job_id_hash, |a| {
                    if let Some(ref mut att) = a {
                        att.verified = true;
                    }
                });
            }
            Self::deposit_event(Event::IBMSignatureVerified { job_id_hash, valid });
            Ok(())
        }

        /// Link attestation to patient (by pseudonym). Already stored at attestation time; this can update linkage.
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::link_to_patient())]
        pub fn link_to_patient(
            origin: OriginFor<T>,
            job_id_hash: T::Hash,
            patient_pseudonym: T::Hash,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            ensure!(QuantumResults::<T>::contains_key(&job_id_hash), Error::<T>::AttestationNotFound);
            QuantumResults::<T>::mutate(&job_id_hash, |a| {
                if let Some(ref mut att) = a {
                    att.patient_pseudonym = patient_pseudonym;
                }
            });
            PatientQuantumResults::<T>::mutate(patient_pseudonym, |list| {
                if list.len() < <MaxJobsPerPatient as frame_support::traits::Get<u32>>::get() as usize {
                    let _ = list.try_push(job_id_hash);
                }
            });
            Self::deposit_event(Event::LinkedToPatient { job_id_hash, patient_pseudonym });
            Ok(())
        }

        /// Request generation of compliance certificate (emits event; actual document is off-chain).
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::generate_compliance_certificate())]
        pub fn generate_compliance_certificate(
            origin: OriginFor<T>,
            job_id_hash: T::Hash,
        ) -> DispatchResult {
            let requester = ensure_signed(origin)?;
            ensure!(QuantumResults::<T>::contains_key(&job_id_hash), Error::<T>::AttestationNotFound);
            Self::deposit_event(Event::ComplianceCertificateRequested {
                job_id_hash,
                requester,
            });
            Ok(())
        }

        /// Update algorithm version in registry.
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::update_algorithm_version())]
        pub fn update_algorithm_version(
            origin: OriginFor<T>,
            algorithm_hash: T::Hash,
            new_version: u32,
            description: Vec<u8>,
        ) -> DispatchResult {
            let owner = ensure_signed(origin)?;
            AlgorithmRegistry::<T>::try_mutate(algorithm_hash, |opt| {
                let meta = opt.as_mut().ok_or(Error::<T>::AlgorithmNotRegistered)?;
                ensure!(meta.owner == owner, Error::<T>::PatientNotAuthorized);
                meta.version = new_version;
                let desc_bounded = BoundedVec::try_from(description).map_err(|_| Error::<T>::JobIdTooLong)?;
                meta.description = desc_bounded;
                Ok::<(), DispatchError>(())
            })?;
            Self::deposit_event(Event::AlgorithmVersionUpdated {
                algorithm_hash,
                new_version,
            });
            Ok(())
        }

        /// Register an IBM Quantum public key for signature verification.
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::register_ibm_key())]
        pub fn register_ibm_key(
            origin: OriginFor<T>,
            key_id: Vec<u8>,
            public_key: Vec<u8>,
        ) -> DispatchResult {
            frame_system::ensure_root(origin)?;
            let kid = BoundedVec::try_from(key_id).map_err(|_| Error::<T>::JobIdTooLong)?;
            let pk = BoundedVec::try_from(public_key).map_err(|_| Error::<T>::SignatureTooLong)?;
            IBMQuantumKeys::<T>::insert(kid.clone(), pk);
            Self::deposit_event(Event::IBMKeyRegistered { key_id: kid });
            Ok(())
        }

        /// Register an IBM Quantum backend (e.g. ibm_brisbane, ibm_kyoto).
        #[pallet::call_index(7)]
        #[pallet::weight(T::WeightInfo::register_ibm_backend())]
        pub fn register_ibm_backend(
            origin: OriginFor<T>,
            backend_id: Vec<u8>,
            name: Vec<u8>,
            qubit_count: u16,
            calibration_data_hash: Option<T::Hash>,
        ) -> DispatchResult {
            frame_system::ensure_root(origin)?;
            let bid = BoundedVec::try_from(backend_id).map_err(|_| Error::<T>::JobIdTooLong)?;
            let name_b = BoundedVec::try_from(name).map_err(|_| Error::<T>::JobIdTooLong)?;
            let info = IBMBackendInfo {
                backend_id: bid.clone(),
                name: name_b.clone(),
                available: true,
                qubit_count,
                calibration_data_hash,
                registered_at: <frame_system::Pallet<T>>::block_number(),
            };
            IBMBackendRegistry::<T>::insert(&bid, info);
            Self::deposit_event(Event::BackendRegistered { backend_id: bid, name: name_b });
            Ok(())
        }

        /// Submit multiple related quantum jobs (batch) for one clinical analysis.
        #[pallet::call_index(8)]
        #[pallet::weight(T::WeightInfo::submit_batch_job())]
        pub fn submit_batch_job(
            origin: OriginFor<T>,
            analysis_id: T::Hash,
            job_id_hashes: Vec<T::Hash>,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            let bounded = BoundedVec::try_from(job_id_hashes).map_err(|_| Error::<T>::BatchTooLarge)?;
            for jh in bounded.iter() {
                ensure!(QuantumResults::<T>::contains_key(jh), Error::<T>::AttestationNotFound);
            }
            BatchJobs::<T>::insert(analysis_id, bounded.clone());
            Self::deposit_event(Event::BatchSubmitted {
                analysis_id,
                job_count: bounded.len() as u32,
            });
            Ok(())
        }

        /// Verify job completion status (e.g. from IBM API); update queue/attestation.
        #[pallet::call_index(9)]
        #[pallet::weight(T::WeightInfo::verify_job_completion())]
        pub fn verify_job_completion(
            origin: OriginFor<T>,
            job_id_hash: T::Hash,
            status: JobCompletionStatus,
            backend_id: Vec<u8>,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            let bid = BoundedVec::try_from(backend_id).map_err(|_| Error::<T>::JobIdTooLong)?;
            ensure!(
                IBMBackendRegistry::<T>::contains_key(&bid),
                Error::<T>::BackendUnavailable
            );
            if status == JobCompletionStatus::Failed {
                return Err(Error::<T>::JobFailed.into());
            }
            let backend_available = IBMBackendRegistry::<T>::get(&bid)
                .map(|b| b.available)
                .unwrap_or(false);
            ensure!(backend_available, Error::<T>::BackendUnavailable);
            QuantumJobQueue::<T>::mutate(|q| {
                if let Some(pos) = q.iter().position(|p| p.job_id_hash == job_id_hash) {
                    q[pos].status = status.clone();
                }
            });
            Self::deposit_event(Event::JobCompletionVerified { job_id_hash, status });
            Ok(())
        }

        /// Calculate and store result confidence score for a job (from quality metrics).
        #[pallet::call_index(10)]
        #[pallet::weight(T::WeightInfo::calculate_result_confidence())]
        pub fn calculate_result_confidence(
            origin: OriginFor<T>,
            job_id_hash: T::Hash,
            readout_error_rate_micro: u32,
            gate_fidelity_micro: u32,
            mitigation_factor_micro: u32, // 0-1_000_000
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            ensure!(QuantumResults::<T>::contains_key(&job_id_hash), Error::<T>::AttestationNotFound);
            let confidence_micro = Self::compute_confidence_internal(
                readout_error_rate_micro,
                gate_fidelity_micro,
                mitigation_factor_micro,
            );
            QualityMetricsMap::<T>::mutate(job_id_hash, |opt| {
                if let Some(ref mut q) = opt {
                    q.readout_error_rate_micro = readout_error_rate_micro;
                    q.confidence_score_micro = confidence_micro;
                } else {
                    *opt = Some(QualityMetrics {
                        job_id_hash,
                        measurement_error_mitigation: BoundedVec::default(),
                        readout_error_rate_micro,
                        circuit_optimization_level: 0,
                        confidence_score_micro: confidence_micro,
                        created_at: <frame_system::Pallet<T>>::block_number(),
                    });
                }
            });
            Self::deposit_event(Event::ResultConfidenceCalculated {
                job_id_hash,
                confidence_micro,
            });
            Ok(())
        }

        /// Store circuit metadata (transpilation, gate fidelity, calibration) for a job.
        #[pallet::call_index(11)]
        #[pallet::weight(T::WeightInfo::register_algorithm())]
        pub fn store_circuit_metadata(
            origin: OriginFor<T>,
            job_id_hash: T::Hash,
            backend_id: Vec<u8>,
            transpilation_depth: u32,
            gate_fidelity_micro: u32,
            error_rate_micro: u32,
            calibration_data_hash: Option<T::Hash>,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            ensure!(QuantumResults::<T>::contains_key(&job_id_hash), Error::<T>::AttestationNotFound);
            let bid = BoundedVec::try_from(backend_id).map_err(|_| Error::<T>::JobIdTooLong)?;
            let meta = CircuitMetadata {
                job_id_hash,
                backend_id: bid,
                transpilation_depth,
                gate_fidelity_micro,
                error_rate_micro,
                calibration_data_hash,
                created_at: <frame_system::Pallet<T>>::block_number(),
            };
            CircuitMetadataMap::<T>::insert(job_id_hash, meta);
            Ok(())
        }

        /// Enqueue a quantum job for off-chain worker to poll IBM and submit attestation when completed.
        #[pallet::call_index(12)]
        #[pallet::weight(T::WeightInfo::register_algorithm())]
        pub fn enqueue_quantum_job(
            origin: OriginFor<T>,
            job_id: Vec<u8>,
            backend_id: Vec<u8>,
            patient_pseudonym: T::Hash,
            algorithm_type: QuantumAlgorithm,
            algorithm_version: u32,
            parameters_hash: T::Hash,
            execution_timestamp: u64,
            circuit_depth: u32,
            qubit_count: u8,
            shots: u32,
            linked_clinical_module: Option<Vec<u8>>,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            let job_id_b = BoundedVec::try_from(job_id).map_err(|_| Error::<T>::JobIdTooLong)?;
            let bid = BoundedVec::try_from(backend_id).map_err(|_| Error::<T>::JobIdTooLong)?;
            ensure!(
                IBMBackendRegistry::<T>::contains_key(&bid),
                Error::<T>::BackendUnavailable
            );
            let job_id_hash = T::Hashing::hash_of(&job_id_b.encode());
            ensure!(
                !QuantumResults::<T>::contains_key(&job_id_hash),
                Error::<T>::DuplicateJobId
            );
            let clinical_b = linked_clinical_module
                .map(|v| BoundedVec::try_from(v).map_err(|_| Error::<T>::JobIdTooLong))
                .transpose()?;
            let context = PendingAttestationContext {
                patient_pseudonym,
                algorithm_type: algorithm_type.clone(),
                algorithm_version,
                parameters_hash,
                execution_timestamp,
                circuit_depth,
                qubit_count,
                shots,
                linked_clinical_module: clinical_b,
            };
            let pending = PendingJob {
                job_id: job_id_b.clone(),
                job_id_hash,
                backend_id: bid,
                status: JobCompletionStatus::Pending,
                submitted_at: <frame_system::Pallet<T>>::block_number(),
                attestation_context: Some(context),
            };
            QuantumJobQueue::<T>::mutate(|q| {
                if q.len() < <MaxQueueLen as frame_support::traits::Get<u32>>::get() as usize {
                    let _ = q.try_push(pending);
                }
            });
            Ok(())
        }

        /// Submit attestation from off-chain worker (unsigned). Valid only when job is in queue with context.
        #[pallet::call_index(13)]
        #[pallet::weight(T::WeightInfo::attest_quantum_result())]
        pub fn submit_attestation_unsigned(
            origin: OriginFor<T>,
            job_id: Vec<u8>,
            patient_pseudonym: T::Hash,
            algorithm_type: QuantumAlgorithm,
            algorithm_version: u32,
            parameters_hash: T::Hash,
            result_hash: T::Hash,
            ibm_signature: Vec<u8>,
            execution_timestamp: u64,
            circuit_depth: u32,
            qubit_count: u8,
            shots: u32,
            linked_clinical_module: Option<Vec<u8>>,
        ) -> DispatchResult {
            ensure_none(origin)?;

            let job_id_b = BoundedVec::try_from(job_id).map_err(|_| Error::<T>::JobIdTooLong)?;
            let sig_b = BoundedVec::try_from(ibm_signature).map_err(|_| Error::<T>::SignatureTooLong)?;
            let clinical_b = linked_clinical_module
                .map(|v| BoundedVec::try_from(v).map_err(|_| Error::<T>::JobIdTooLong))
                .transpose()?;
            let job_id_hash = T::Hashing::hash_of(&job_id_b.encode());

            let verified = Self::verify_ibm_signature_internal(&job_id_b, &result_hash, &sig_b);
            let attestation = QuantumAttestation {
                job_id: job_id_b.clone(),
                patient_pseudonym,
                algorithm_type: algorithm_type.clone(),
                algorithm_version,
                parameters_hash,
                result_hash,
                ibm_signature: sig_b,
                execution_timestamp,
                circuit_depth,
                qubit_count,
                shots,
                verified,
                linked_clinical_module: clinical_b,
                created_at: <frame_system::Pallet<T>>::block_number(),
            };
            QuantumResults::<T>::insert(job_id_hash, &attestation);
            JobIdToHash::<T>::insert(&job_id_b, job_id_hash);
            PatientQuantumResults::<T>::mutate(patient_pseudonym, |list| {
                if list.len() < <MaxJobsPerPatient as frame_support::traits::Get<u32>>::get() as usize {
                    let _ = list.try_push(job_id_hash);
                }
            });
            QuantumJobQueue::<T>::mutate(|q| {
                q.retain(|p| p.job_id_hash != job_id_hash);
            });
            Self::deposit_event(Event::QuantumResultAttested {
                job_id_hash,
                algorithm_type,
                patient_pseudonym,
                verified,
            });
            Ok(())
        }

        /// Link multiple jobs (batch) to one patient analysis / pseudonym.
        #[pallet::call_index(14)]
        #[pallet::weight(T::WeightInfo::link_batch_results())]
        pub fn link_batch_results(
            origin: OriginFor<T>,
            analysis_id: T::Hash,
            patient_pseudonym: T::Hash,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            let job_hashes = BatchJobs::<T>::get(&analysis_id).ok_or(Error::<T>::AttestationNotFound)?;
            for jh in job_hashes.iter() {
                QuantumResults::<T>::mutate(jh, |a| {
                    if let Some(ref mut att) = a {
                        att.patient_pseudonym = patient_pseudonym;
                    }
                });
                PatientQuantumResults::<T>::mutate(patient_pseudonym, |list| {
                    if list.len() < <MaxJobsPerPatient as frame_support::traits::Get<u32>>::get() as usize {
                        let _ = list.try_push(*jh);
                    }
                });
            }
            Self::deposit_event(Event::BatchLinked {
                analysis_id,
                patient_pseudonym,
                job_count: job_hashes.len() as u32,
            });
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        /// Verify IBM signature: Ed25519 when key is 32 bytes and signature 64 bytes; else placeholder.
        fn verify_ibm_signature_internal(
            job_id: &BoundedVec<u8, JobIdMaxLen>,
            result_hash: &T::Hash,
            signature: &BoundedVec<u8, SignatureMaxLen>,
        ) -> bool {
            if signature.is_empty() {
                return false;
            }
            let message = (job_id.encode(), result_hash.encode()).encode();
            for (key_id, pk) in IBMQuantumKeys::<T>::iter() {
                if pk.len() == 32 && signature.len() == 64 {
                    if let (Ok(public), Ok(sig)) = (
                        sp_core::ed25519::Public::try_from(pk.as_ref()),
                        sp_core::ed25519::Signature::try_from(signature.as_ref()),
                    ) {
                        if sig.verify(&*message, &public) {
                            return true;
                        }
                    }
                }
            }
            false
        }

        /// Compute confidence score (fixed-point micro): based on error rates and mitigation.
        fn compute_confidence_internal(
            readout_error_micro: u32,
            gate_fidelity_micro: u32,
            mitigation_factor_micro: u32,
        ) -> u32 {
            let err = readout_error_micro.saturating_add(1_000_000_u32.saturating_sub(gate_fidelity_micro));
            let reduced = err.saturating_mul(mitigation_factor_micro).saturating_div(1_000_000);
            1_000_000_u32.saturating_sub(reduced.min(1_000_000))
        }

        /// Query all quantum result (job) hashes for a patient pseudonym.
        pub fn query_patient_quantum_history(patient_pseudonym: T::Hash) -> sp_std::vec::Vec<T::Hash> {
            PatientQuantumResults::<T>::get(patient_pseudonym)
                .iter()
                .cloned()
                .collect()
        }
    }
}

pub use pallet::*;
