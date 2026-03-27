#![cfg_attr(not(feature = "std"), no_std)]
pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;

    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum VaultDataType {
        ClinicalRecord,
        LabResult,
        GeneticData,
        ImagingHash,
        MedicationRecord,
        WearableData,
        CannabinoidRecord,
        EcbomeMarker,
    }

    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum AccessLevel { PatientOnly, PatientAndProvider, Research, Public }

    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct VaultEntry<T: Config> {
        pub entry_id: u64,
        pub patient: T::AccountId,
        pub data_type: VaultDataType,
        pub data_hash: BoundedVec<u8, T::MaxHashLength>,
        pub module_id: u32,
        pub access_level: AccessLevel,
        pub created_at: BlockNumberFor<T>,
        pub updated_at: BlockNumberFor<T>,
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        #[pallet::constant]
        type MaxHashLength: Get<u32>;
        #[pallet::constant]
        type MaxEntriesPerPatient: Get<u32>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::storage]
    #[pallet::getter(fn vault)]
    pub type Vault<T: Config> = StorageMap<
        _, Blake2_128Concat, u64, VaultEntry<T>, OptionQuery,
    >;

    #[pallet::storage]
    #[pallet::getter(fn patient_entries)]
    pub type PatientEntries<T: Config> = StorageMap<
        _, Blake2_128Concat, T::AccountId,
        BoundedVec<u64, T::MaxEntriesPerPatient>, ValueQuery,
    >;

    #[pallet::storage]
    #[pallet::getter(fn entry_count)]
    pub type EntryCount<T: Config> = StorageValue<_, u64, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        DataStored { entry_id: u64, patient: T::AccountId, data_type: VaultDataType },
        DataUpdated { entry_id: u64, patient: T::AccountId },
        AccessLevelChanged { entry_id: u64, new_level: AccessLevel },
    }

    #[pallet::error]
    pub enum Error<T> {
        TooManyEntries,
        EntryNotFound,
        NotOwner,
        HashTooLong,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Store a hashed health data record in the patient vault.
        #[pallet::call_index(0)]
        #[pallet::weight(Weight::from_parts(10_000_000, 0).saturating_add(T::DbWeight::get().writes(2)))]
        pub fn store_data(
            origin: OriginFor<T>,
            data_type: VaultDataType,
            data_hash: sp_std::vec::Vec<u8>,
            module_id: u32,
            access_level: AccessLevel,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;
            let block = frame_system::Pallet::<T>::block_number();
            let entry_id = EntryCount::<T>::get();

            let bounded_hash = BoundedVec::try_from(data_hash)
                .map_err(|_| Error::<T>::HashTooLong)?;

            let entry = VaultEntry {
                entry_id,
                patient: patient.clone(),
                data_type: data_type.clone(),
                data_hash: bounded_hash,
                module_id,
                access_level,
                created_at: block,
                updated_at: block,
            };

            Vault::<T>::insert(entry_id, entry);
            PatientEntries::<T>::try_mutate(&patient, |entries| {
                entries.try_push(entry_id).map_err(|_| Error::<T>::TooManyEntries)
            })?;
            EntryCount::<T>::put(entry_id + 1);
            Self::deposit_event(Event::DataStored { entry_id, patient, data_type });
            Ok(())
        }

        /// Update access level for a vault entry (patient only).
        #[pallet::call_index(1)]
        #[pallet::weight(Weight::from_parts(5_000_000, 0).saturating_add(T::DbWeight::get().writes(1)))]
        pub fn set_access_level(
            origin: OriginFor<T>,
            entry_id: u64,
            access_level: AccessLevel,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;
            Vault::<T>::try_mutate(entry_id, |maybe_entry| {
                let entry = maybe_entry.as_mut().ok_or(Error::<T>::EntryNotFound)?;
                ensure!(entry.patient == patient, Error::<T>::NotOwner);
                entry.access_level = access_level.clone();
                Ok::<(), DispatchError>(())
            })?;
            Self::deposit_event(Event::AccessLevelChanged { entry_id, new_level: access_level });
            Ok(())
        }
    }
}
