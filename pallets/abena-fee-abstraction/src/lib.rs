//! ABENA Fee Abstraction Pallet
//!
//! Gasless model for patients: sponsors (institutions, insurers) can pay
//! transaction fees on behalf of patients. Stores sponsor-patient mappings
//! for use by the transaction payment logic.

#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type AdminOrigin: EnsureOrigin<Self::RuntimeOrigin>;
        type WeightInfo: crate::WeightInfo;
    }

    /// Maps patient account -> sponsor account (who pays their fees)
    #[pallet::storage]
    #[pallet::getter(fn get_sponsor)]
    pub type SponsoredPatients<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, T::AccountId, OptionQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// Patient sponsored for gasless transactions
        PatientSponsored { patient: T::AccountId, sponsor: T::AccountId },
        /// Sponsorship removed
        SponsorshipRemoved { patient: T::AccountId },
    }

    #[pallet::error]
    pub enum Error<T> {
        /// Patient already sponsored
        AlreadySponsored,
        /// Patient not sponsored
        NotSponsored,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Register a patient for fee abstraction (sponsor pays their fees).
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::sponsor_patient())]
        pub fn sponsor_patient(
            origin: OriginFor<T>,
            patient: T::AccountId,
            sponsor: T::AccountId,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;
            ensure!(!SponsoredPatients::<T>::contains_key(&patient), Error::<T>::AlreadySponsored);

            SponsoredPatients::<T>::insert(&patient, &sponsor);

            Self::deposit_event(Event::PatientSponsored { patient, sponsor });

            Ok(())
        }

        /// Remove sponsorship for a patient.
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::remove_sponsorship())]
        pub fn remove_sponsorship(origin: OriginFor<T>, patient: T::AccountId) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;
            ensure!(SponsoredPatients::<T>::contains_key(&patient), Error::<T>::NotSponsored);

            SponsoredPatients::<T>::remove(&patient);

            Self::deposit_event(Event::SponsorshipRemoved { patient });

            Ok(())
        }
    }

}

pub trait WeightInfo {
    fn sponsor_patient() -> frame_support::weights::Weight;
    fn remove_sponsorship() -> frame_support::weights::Weight;
}

pub mod weights {
    use frame_support::weights::Weight;

    pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

    impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
        fn sponsor_patient() -> Weight {
            Weight::from_parts(30_000_000, 0)
        }
        fn remove_sponsorship() -> Weight {
            Weight::from_parts(25_000_000, 0)
        }
    }
}
