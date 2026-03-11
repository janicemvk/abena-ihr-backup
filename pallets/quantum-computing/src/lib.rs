//! # ABENA Quantum Results Pallet
//!
//! Attests and stores quantum computation results (e.g. from IBM Quantum) for the
//! ABENA IHR. Supports algorithm types VQE, QML, QAOA; links results to patient
//! records via hashes; timestamps all analyses. Integration points can represent
//! IBM Quantum or other providers; signature verification can be extended for
//! IBM cryptographic attestations.

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
    use sp_core::H256;
    use sp_std::vec::Vec;
    /// Configuration trait for the pallet.
    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// The pallet ID
        type PalletId: Get<frame_support::PalletId>;
        /// Weight information for extrinsics
        type WeightInfo: crate::WeightInfo;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Quantum computing jobs submitted to the system
    #[pallet::storage]
    #[pallet::getter(fn quantum_jobs)]
    pub type QuantumJobs<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        JobId,
        QuantumJob<T>,
        OptionQuery,
   >;

    /// Quantum computing results
    #[pallet::storage]
    #[pallet::getter(fn quantum_results)]
    pub type QuantumResults<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        JobId,
        QuantumResult<T>,
        OptionQuery,
   >;

    /// Job counter for generating unique job IDs
    #[pallet::storage]
    pub type JobCounter<T: Config> = StorageValue<_, u64, ValueQuery>;

    /// Integration points for external quantum computing services
    #[pallet::storage]
    #[pallet::getter(fn integration_points)]
    pub type IntegrationPoints<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        IntegrationPointId,
        IntegrationPoint<T>,
        OptionQuery,
   >;

    /// Mapping of jobs to integration points
    #[pallet::storage]
    pub type JobIntegrationMapping<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        JobId,
        IntegrationPointId,
        OptionQuery,
    >;

    /// Events emitted by this pallet
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// A new quantum computing job was submitted
        QuantumJobSubmitted {
            job_id: JobId,
            submitter: T::AccountId,
            job_type: QuantumJobType,
        },
        /// Quantum computing job was completed
        QuantumJobCompleted {
            job_id: JobId,
            result_hash: Hash,
        },
        /// Quantum computing result was stored
        QuantumResultStored {
            job_id: JobId,
            result_hash: Hash,
        },
        /// Integration point was registered
        IntegrationPointRegistered {
            point_id: IntegrationPointId,
            provider: T::AccountId,
        },
        /// Integration point was updated
        IntegrationPointUpdated {
            point_id: IntegrationPointId,
        },
    }

    /// Errors that can occur in this pallet
    #[pallet::error]
    pub enum Error<T> {
        /// Job not found
        JobNotFound,
        /// Invalid job parameters
        InvalidJobParameters,
        /// Integration point not found
        IntegrationPointNotFound,
        /// Job already exists
        JobAlreadyExists,
        /// Result already stored
        ResultAlreadyStored,
        /// Data too large for BoundedVec
        DataTooLarge,
        /// Invalid result data
        InvalidResultData,
    }

    /// Hooks for the pallet
    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    /// Extrinsics for the pallet
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Submit a quantum computing job (ABENA: optionally link to patient/record)
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::submit_job())]
        pub fn submit_job(
            origin: OriginFor<T>,
            job_type: QuantumJobType,
            parameters: Vec<u8>,
            integration_point_id: Option<IntegrationPointId>,
            patient: Option<T::AccountId>,
            health_record_hash: Option<H256>,
        ) -> DispatchResult {
            let submitter = ensure_signed(origin)?;

            // Generate new job ID
            let job_id = Self::generate_job_id();

            // Ensure job doesn't already exist
            ensure!(
                !QuantumJobs::<T>::contains_key(&job_id),
                Error::<T>::JobAlreadyExists
            );

            // Validate integration point if provided
            if let Some(point_id) = integration_point_id {
                ensure!(
                    IntegrationPoints::<T>::contains_key(&point_id),
                    Error::<T>::IntegrationPointNotFound
                );
                JobIntegrationMapping::<T>::insert(&job_id, point_id);
            }

            // Convert parameters to BoundedVec
            let parameters_bounded = BoundedVec::try_from(parameters)
                .map_err(|_| Error::<T>::DataTooLarge)?;

            // Create job (ABENA: store patient/record link when provided)
            let job = QuantumJob {
                id: job_id,
                submitter: submitter.clone(),
                job_type: job_type.clone(),
                parameters: parameters_bounded,
                status: JobStatus::Pending,
                created_at: <frame_system::Pallet<T>>::block_number(),
                updated_at: <frame_system::Pallet<T>>::block_number(),
                patient,
                health_record_hash,
            };

            QuantumJobs::<T>::insert(&job_id, job);

            Self::deposit_event(Event::QuantumJobSubmitted {
                job_id,
                submitter,
                job_type,
            });

            Ok(())
        }

        /// Store quantum computing result
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::store_result())]
        pub fn store_result(
            origin: OriginFor<T>,
            job_id: JobId,
            result_data: Vec<u8>,
            result_hash: Hash,
        ) -> DispatchResult {
            let _submitter = ensure_signed(origin)?;

            // Ensure job exists
            let mut job = QuantumJobs::<T>::get(&job_id)
                .ok_or(Error::<T>::JobNotFound)?;

            // Ensure result doesn't already exist
            ensure!(
                !QuantumResults::<T>::contains_key(&job_id),
                Error::<T>::ResultAlreadyStored
            );

            // Validate result data (basic validation)
            ensure!(
                !result_data.is_empty(),
                Error::<T>::InvalidResultData
            );

            // Update job status
            job.status = JobStatus::Completed;
            job.updated_at = <frame_system::Pallet<T>>::block_number();
            let patient = job.patient.clone();
            let health_record_hash = job.health_record_hash;
            QuantumJobs::<T>::insert(&job_id, job);

            // Convert result_data to BoundedVec
            let result_data_bounded = BoundedVec::try_from(result_data)
                .map_err(|_| Error::<T>::DataTooLarge)?;

            // Store result
            let result = QuantumResult {
                job_id,
                result_data: result_data_bounded,
                result_hash,
                stored_at: <frame_system::Pallet<T>>::block_number(),
                patient,
                health_record_hash,
            };

            QuantumResults::<T>::insert(&job_id, result.clone());

            Self::deposit_event(Event::QuantumResultStored {
                job_id,
                result_hash,
            });

            Self::deposit_event(Event::QuantumJobCompleted {
                job_id,
                result_hash,
            });

            Ok(())
        }

        /// Register an integration point for external quantum computing services
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::register_integration_point())]
        pub fn register_integration_point(
            origin: OriginFor<T>,
            point_id: IntegrationPointId,
            provider_name: Vec<u8>,
            endpoint: Vec<u8>,
            capabilities: Vec<QuantumCapability>,
        ) -> DispatchResult {
            let provider = ensure_signed(origin)?;

            // Convert to BoundedVec
            let provider_name_bounded = BoundedVec::try_from(provider_name)
                .map_err(|_| Error::<T>::DataTooLarge)?;
            let endpoint_bounded = BoundedVec::try_from(endpoint)
                .map_err(|_| Error::<T>::DataTooLarge)?;
            let capabilities_bounded = BoundedVec::try_from(capabilities)
                .map_err(|_| Error::<T>::DataTooLarge)?;

            // Create integration point
            let integration_point = IntegrationPoint {
                id: point_id.clone(),
                provider: provider.clone(),
                provider_name: provider_name_bounded,
                endpoint: endpoint_bounded,
                capabilities: capabilities_bounded,
                registered_at: <frame_system::Pallet<T>>::block_number(),
                active: true,
            };

            IntegrationPoints::<T>::insert(&point_id, integration_point);

            Self::deposit_event(Event::IntegrationPointRegistered {
                point_id,
                provider,
            });

            Ok(())
        }

        /// Update an integration point
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::update_integration_point())]
        pub fn update_integration_point(
            origin: OriginFor<T>,
            point_id: IntegrationPointId,
            endpoint: Option<Vec<u8>>,
            capabilities: Option<Vec<QuantumCapability>>,
            active: Option<bool>,
        ) -> DispatchResult {
            let updater = ensure_signed(origin)?;

            let mut integration_point = IntegrationPoints::<T>::get(&point_id)
                .ok_or(Error::<T>::IntegrationPointNotFound)?;

            // Only the provider can update
            ensure!(
                integration_point.provider == updater,
                Error::<T>::IntegrationPointNotFound
            );

            if let Some(endpoint) = endpoint {
                let endpoint_bounded = BoundedVec::try_from(endpoint)
                    .map_err(|_| Error::<T>::DataTooLarge)?;
                integration_point.endpoint = endpoint_bounded;
            }

            if let Some(capabilities) = capabilities {
                let capabilities_bounded = BoundedVec::try_from(capabilities)
                    .map_err(|_| Error::<T>::DataTooLarge)?;
                integration_point.capabilities = capabilities_bounded;
            }

            if let Some(active) = active {
                integration_point.active = active;
            }

            IntegrationPoints::<T>::insert(&point_id, integration_point);

            Self::deposit_event(Event::IntegrationPointUpdated { point_id });

            Ok(())
        }

        /// Query quantum computing result
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::query_result())]
        pub fn query_result(
            origin: OriginFor<T>,
            job_id: JobId,
        ) -> DispatchResult {
            let _querier = ensure_signed(origin)?;

            let result = QuantumResults::<T>::get(&job_id)
                .ok_or(Error::<T>::JobNotFound)?;

            // Result is available in storage, this extrinsic just validates access
            Ok(())
        }
    }


/// Internal functions
    impl<T: Config> Pallet<T> {
        /// Generate a new unique job ID
        fn generate_job_id() -> JobId {
            let current = JobCounter::<T>::get();
            let new_id = current + 1;
            JobCounter::<T>::put(new_id);
            new_id
        }
    }

/// Weight information for extrinsics
pub trait WeightInfo {
    fn submit_job() -> Weight;
    fn store_result() -> Weight;
    fn register_integration_point() -> Weight;
    fn update_integration_point() -> Weight;
    fn query_result() -> Weight;
}

/// Job ID type
pub type JobId = u64;

/// Hash type for results
pub type Hash = sp_core::H256;

/// Integration point ID type
pub type IntegrationPointId = u32;

/// Quantum computing job structure (ABENA: optional link to patient/record)
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct QuantumJob<T: frame_system::Config> {
    /// Unique job identifier
    pub id: JobId,
    /// Account that submitted the job
    pub submitter: T::AccountId,
    /// Type of quantum computing job (VQE, QML, QAOA, etc.)
    pub job_type: QuantumJobType,
    /// Job parameters (encoded)
    pub parameters: BoundedVec<u8, ConstU32<4096>>,
    /// Current status of the job
    pub status: JobStatus,
    /// Block number when job was created
    pub created_at: BlockNumberFor<T>,
    /// Block number when job was last updated
    pub updated_at: BlockNumberFor<T>,
    /// Optional: patient account when job is tied to a health record (ABENA)
    pub patient: Option<T::AccountId>,
    /// Optional: health record hash this job relates to (ABENA)
    pub health_record_hash: Option<sp_core::H256>,
}

/// Quantum computing result structure (ABENA: links to patient record)
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct QuantumResult<T: frame_system::Config> {
    /// Associated job ID
    pub job_id: JobId,
    /// Result data (may be encrypted or hashed)
    pub result_data: BoundedVec<u8, ConstU32<8192>>,
    /// Hash of the result for verification
    pub result_hash: Hash,
    /// Block number when result was stored (timestamp for ABENA audit)
    pub stored_at: BlockNumberFor<T>,
    /// Optional: patient account when result is tied to a health record (ABENA)
    pub patient: Option<T::AccountId>,
    /// Optional: health record hash this result relates to (ABENA)
    pub health_record_hash: Option<sp_core::H256>,
}

/// Integration point for external quantum computing services
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct IntegrationPoint<T: frame_system::Config> {
    /// Unique integration point identifier
    pub id: IntegrationPointId,
    /// Account of the provider
    pub provider: T::AccountId,
    /// Name of the provider
    pub provider_name: BoundedVec<u8, ConstU32<128>>,
    /// Endpoint URL or identifier
    pub endpoint: BoundedVec<u8, ConstU32<256>>,
    /// Capabilities offered by this integration point
    pub capabilities: BoundedVec<QuantumCapability, ConstU32<20>>,
    /// Block number when registered
    pub registered_at: BlockNumberFor<T>,
    /// Whether the integration point is active
    pub active: bool,
}

/// Types of quantum computing jobs (ABENA: includes standard algorithm classes)
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum QuantumJobType {
    /// Variational Quantum Eigensolver (VQE) - e.g. molecular/chemistry
    VQE,
    /// Quantum Machine Learning (QML)
    QML,
    /// Quantum Approximate Optimization Algorithm (QAOA)
    QAOA,
    /// Generic quantum simulation
    Simulation,
    /// Quantum optimization (other than QAOA)
    Optimization,
    /// Quantum machine learning (alias; use QML for consistency)
    MachineLearning,
    /// Quantum cryptography
    Cryptography,
    /// Drug discovery simulation
    DrugDiscovery,
    /// Protein folding simulation
    ProteinFolding,
}

/// Status of a quantum computing job
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum JobStatus {
    /// Job is pending execution
    Pending,
    /// Job is currently running
    Running,
    /// Job has completed successfully
    Completed,
    /// Job failed
    Failed,
    /// Job was cancelled
    Cancelled,
}

/// Capabilities of a quantum computing integration point
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum QuantumCapability {
    /// Supports quantum simulation
    Simulation,
    /// Supports quantum optimization
    Optimization,
    /// Supports quantum machine learning
    MachineLearning,
    /// Supports quantum cryptography
    Cryptography,
    /// Supports NISQ (Noisy Intermediate-Scale Quantum) devices
    NISQ,
    /// Supports fault-tolerant quantum computing
    FaultTolerant,
}
}

pub use pallet::*;
