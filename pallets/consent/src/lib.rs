#![cfg_attr(not(feature = "std"), no_std)]
pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;

    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum ConsentScope {
        ViewClinicalData,
        ViewResearchData,
        ShareAnonymized,
        ShareIdentified,
        TelehealthAccess,
        LabResultAccess,
        MedicationAccess,
    }

    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum ConsentStatus { Granted, Revoked, Pending, Expired }

    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct ConsentRecord<T: Config> {
        pub patient: T::AccountId,
        pub provider: T::AccountId,
        pub scope: ConsentScope,
        pub status: ConsentStatus,
        pub granted_at: BlockNumberFor<T>,
        pub expires_at: Option<BlockNumberFor<T>>,
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        #[pallet::constant]
        type MaxConsentsPerPatient: Get<u32>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::storage]
    #[pallet::getter(fn consent)]
    pub type Consents<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat, T::AccountId,
        Blake2_128Concat, T::AccountId,
        BoundedVec<ConsentRecord<T>, T::MaxConsentsPerPatient>,
        ValueQuery,
    >;

    #[pallet::storage]
    #[pallet::getter(fn consent_count)]
    pub type ConsentCount<T: Config> = StorageValue<_, u64, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ConsentGranted { patient: T::AccountId, provider: T::AccountId, scope: ConsentScope },
        ConsentRevoked { patient: T::AccountId, provider: T::AccountId, scope: ConsentScope },
    }

    #[pallet::error]
    pub enum Error<T> { TooManyConsents, ConsentNotFound, NotPatient }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::call_index(0)]
        #[pallet::weight(Weight::from_parts(10_000_000, 0).saturating_add(T::DbWeight::get().writes(1)))]
        pub fn grant_consent(
            origin: OriginFor<T>,
            provider: T::AccountId,
            scope: ConsentScope,
            expires_at: Option<BlockNumberFor<T>>,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;
            let block = frame_system::Pallet::<T>::block_number();
            let record = ConsentRecord {
                patient: patient.clone(), provider: provider.clone(),
                scope: scope.clone(), status: ConsentStatus::Granted,
                granted_at: block, expires_at,
            };
            Consents::<T>::try_mutate(&patient, &provider, |consents| {
                consents.try_push(record).map_err(|_| Error::<T>::TooManyConsents)
            })?;
            ConsentCount::<T>::mutate(|c| *c += 1);
            Self::deposit_event(Event::ConsentGranted { patient, provider, scope });
            Ok(())
        }

        #[pallet::call_index(1)]
        #[pallet::weight(Weight::from_parts(10_000_000, 0).saturating_add(T::DbWeight::get().writes(1)))]
        pub fn revoke_consent(
            origin: OriginFor<T>,
            provider: T::AccountId,
            scope: ConsentScope,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;
            Consents::<T>::try_mutate(&patient, &provider, |consents| {
                for record in consents.iter_mut() {
                    if record.scope == scope {
                        record.status = ConsentStatus::Revoked;
                        return Ok(());
                    }
                }
                Err(Error::<T>::ConsentNotFound)
            })?;
            Self::deposit_event(Event::ConsentRevoked { patient, provider, scope });
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        pub fn has_consent(patient: &T::AccountId, provider: &T::AccountId, scope: &ConsentScope) -> bool {
            let consents = Consents::<T>::get(patient, provider);
            let block = frame_system::Pallet::<T>::block_number();
            consents.iter().any(|c| {
                &c.scope == scope &&
                c.status == ConsentStatus::Granted &&
                c.expires_at.map_or(true, |exp| exp > block)
            })
        }
    }
}
