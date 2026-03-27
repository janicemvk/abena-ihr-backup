#![cfg_attr(not(feature = "std"), no_std)]
pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;
    use sp_std::vec::Vec;

    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum AuditAction {
        DataAccessed,
        DataModified,
        DataDeleted,
        ConsentGranted,
        ConsentRevoked,
        RewardIssued,
        LoginAttempt,
        ExportRequested,
    }

    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum AuditResult { Success, Failure, Denied }

    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct AuditEntry<T: Config> {
        pub entry_id: u64,
        pub actor: T::AccountId,
        pub action: AuditAction,
        pub result: AuditResult,
        pub block_number: BlockNumberFor<T>,
        pub module_id: Option<u32>,
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        #[pallet::constant]
        type MaxEntriesPerBlock: Get<u32>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::storage]
    #[pallet::getter(fn audit_log)]
    pub type AuditLog<T: Config> = StorageMap<
        _, Blake2_128Concat, u64, AuditEntry<T>, OptionQuery,
    >;

    #[pallet::storage]
    #[pallet::getter(fn entry_count)]
    pub type EntryCount<T: Config> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn actor_log)]
    pub type ActorLog<T: Config> = StorageMap<
        _, Blake2_128Concat, T::AccountId,
        BoundedVec<u64, T::MaxEntriesPerBlock>, ValueQuery,
    >;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        AuditEntryCreated { entry_id: u64, actor: T::AccountId, action: AuditAction },
    }

    #[pallet::error]
    pub enum Error<T> { TooManyEntries }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Record an audit entry. Called by oracles and system pallets.
        #[pallet::call_index(0)]
        #[pallet::weight(Weight::from_parts(5_000_000, 0).saturating_add(T::DbWeight::get().writes(2)))]
        pub fn record_action(
            origin: OriginFor<T>,
            action: AuditAction,
            result: AuditResult,
            module_id: Option<u32>,
        ) -> DispatchResult {
            let actor = ensure_signed(origin)?;
            let block = frame_system::Pallet::<T>::block_number();
            let entry_id = EntryCount::<T>::get();

            let entry = AuditEntry {
                entry_id,
                actor: actor.clone(),
                action: action.clone(),
                result,
                block_number: block,
                module_id,
            };

            AuditLog::<T>::insert(entry_id, entry);
            ActorLog::<T>::try_mutate(&actor, |log| {
                log.try_push(entry_id).map_err(|_| Error::<T>::TooManyEntries)
            })?;
            EntryCount::<T>::put(entry_id + 1);
            Self::deposit_event(Event::AuditEntryCreated { entry_id, actor, action });
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        pub fn log(actor: T::AccountId, action: AuditAction, result: AuditResult, module_id: Option<u32>) {
            let block = frame_system::Pallet::<T>::block_number();
            let entry_id = EntryCount::<T>::get();
            let entry = AuditEntry { entry_id, actor, action, result, block_number: block, module_id };
            AuditLog::<T>::insert(entry_id, entry);
            EntryCount::<T>::put(entry_id + 1);
        }
    }
}
