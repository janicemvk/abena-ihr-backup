#![cfg_attr(not(feature = "std"), no_std)]
pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;

    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum AlertType {
        CriticalLabValue,
        DrugInteraction,
        MissedMedication,
        ConsentExpiring,
        AbnormalVital,
        EcbomeAnomaly,
        QuantumFlaggedPattern,
        DataAccessUnauthorized,
        RewardMilestone,
    }

    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum AlertSeverity { Low, Medium, High, Critical }

    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum AlertStatus { Active, Acknowledged, Resolved, Dismissed }

    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct Alert<T: Config> {
        pub alert_id: u64,
        pub patient: T::AccountId,
        pub alert_type: AlertType,
        pub severity: AlertSeverity,
        pub status: AlertStatus,
        pub module_id: Option<u32>,
        pub created_at: BlockNumberFor<T>,
        pub resolved_at: Option<BlockNumberFor<T>>,
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        #[pallet::constant]
        type MaxAlertsPerPatient: Get<u32>;
        type OracleOrigin: EnsureOrigin<Self::RuntimeOrigin>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::storage]
    #[pallet::getter(fn alerts)]
    pub type Alerts<T: Config> = StorageMap<
        _, Blake2_128Concat, u64, Alert<T>, OptionQuery,
    >;

    #[pallet::storage]
    #[pallet::getter(fn patient_alerts)]
    pub type PatientAlerts<T: Config> = StorageMap<
        _, Blake2_128Concat, T::AccountId,
        BoundedVec<u64, T::MaxAlertsPerPatient>, ValueQuery,
    >;

    #[pallet::storage]
    #[pallet::getter(fn alert_count)]
    pub type AlertCount<T: Config> = StorageValue<_, u64, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        AlertCreated { alert_id: u64, patient: T::AccountId, alert_type: AlertType, severity: AlertSeverity },
        AlertAcknowledged { alert_id: u64, patient: T::AccountId },
        AlertResolved { alert_id: u64 },
    }

    #[pallet::error]
    pub enum Error<T> {
        TooManyAlerts,
        AlertNotFound,
        NotPatient,
        AlreadyResolved,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Oracle creates a clinical alert for a patient.
        #[pallet::call_index(0)]
        #[pallet::weight(Weight::from_parts(10_000_000, 0).saturating_add(T::DbWeight::get().writes(2)))]
        pub fn create_alert(
            origin: OriginFor<T>,
            patient: T::AccountId,
            alert_type: AlertType,
            severity: AlertSeverity,
            module_id: Option<u32>,
        ) -> DispatchResult {
            T::OracleOrigin::ensure_origin(origin)?;
            let block = frame_system::Pallet::<T>::block_number();
            let alert_id = AlertCount::<T>::get();

            let alert = Alert {
                alert_id,
                patient: patient.clone(),
                alert_type: alert_type.clone(),
                severity: severity.clone(),
                status: AlertStatus::Active,
                module_id,
                created_at: block,
                resolved_at: None,
            };

            Alerts::<T>::insert(alert_id, alert);
            PatientAlerts::<T>::try_mutate(&patient, |alerts| {
                alerts.try_push(alert_id).map_err(|_| Error::<T>::TooManyAlerts)
            })?;
            AlertCount::<T>::put(alert_id + 1);
            Self::deposit_event(Event::AlertCreated { alert_id, patient, alert_type, severity });
            Ok(())
        }

        /// Patient acknowledges an alert.
        #[pallet::call_index(1)]
        #[pallet::weight(Weight::from_parts(5_000_000, 0).saturating_add(T::DbWeight::get().writes(1)))]
        pub fn acknowledge_alert(
            origin: OriginFor<T>,
            alert_id: u64,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;
            Alerts::<T>::try_mutate(alert_id, |maybe_alert| {
                let alert = maybe_alert.as_mut().ok_or(Error::<T>::AlertNotFound)?;
                ensure!(alert.patient == patient, Error::<T>::NotPatient);
                alert.status = AlertStatus::Acknowledged;
                Ok::<(), DispatchError>(())
            })?;
            Self::deposit_event(Event::AlertAcknowledged { alert_id, patient });
            Ok(())
        }

        /// Oracle resolves an alert.
        #[pallet::call_index(2)]
        #[pallet::weight(Weight::from_parts(5_000_000, 0).saturating_add(T::DbWeight::get().writes(1)))]
        pub fn resolve_alert(
            origin: OriginFor<T>,
            alert_id: u64,
        ) -> DispatchResult {
            T::OracleOrigin::ensure_origin(origin)?;
            let block = frame_system::Pallet::<T>::block_number();
            Alerts::<T>::try_mutate(alert_id, |maybe_alert| {
                let alert = maybe_alert.as_mut().ok_or(Error::<T>::AlertNotFound)?;
                ensure!(alert.status != AlertStatus::Resolved, Error::<T>::AlreadyResolved);
                alert.status = AlertStatus::Resolved;
                alert.resolved_at = Some(block);
                Ok::<(), DispatchError>(())
            })?;
            Self::deposit_event(Event::AlertResolved { alert_id });
            Ok(())
        }
    }
}
