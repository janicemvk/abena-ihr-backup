//! # ABENA Modules Registry Pallet
//!
//! Registers all 30 clinical analysis modules on-chain with metadata.
//! Each module has a name, category, version, and active status.

#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::{
        pallet_prelude::*,
        traits::Get,
    };
    use frame_system::pallet_prelude::*;
    use sp_std::vec::Vec;

    // ── Module Categories ─────────────────────────────────────────────────────
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum ModuleCategory {
        CoreDemographic,
        MentalHealth,
        SleepArchitecture,
        Nutrition,
        PainManagement,
        Cannabinoid,
        Genetic,
        Cardiovascular,
        Endocrine,
        Immunology,
        Neurology,
        Integrative,
        Environmental,
        Reproductive,
        Fitness,
        Spiritual,
    }

    // ── Module Status ─────────────────────────────────────────────────────────
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum ModuleStatus {
        Active,
        Inactive,
        Beta,
        Deprecated,
    }

    // ── Module Metadata ───────────────────────────────────────────────────────
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct ModuleMetadata<T: Config> {
        pub module_id: u32,
        pub name: BoundedVec<u8, T::MaxNameLength>,
        pub category: ModuleCategory,
        pub version: u32,
        pub status: ModuleStatus,
        pub registered_at: BlockNumberFor<T>,
    }

    // ── Config ────────────────────────────────────────────────────────────────
    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        #[pallet::constant]
        type MaxNameLength: Get<u32>;
        #[pallet::constant]
        type MaxModules: Get<u32>;
        type AdminOrigin: EnsureOrigin<Self::RuntimeOrigin>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // ── Storage ───────────────────────────────────────────────────────────────
    #[pallet::storage]
    #[pallet::getter(fn modules)]
    pub type Modules<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        u32,
        ModuleMetadata<T>,
        OptionQuery,
    >;

    #[pallet::storage]
    #[pallet::getter(fn module_count)]
    pub type ModuleCount<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn initialized)]
    pub type Initialized<T: Config> = StorageValue<_, bool, ValueQuery>;

    // ── Genesis ───────────────────────────────────────────────────────────────
    #[pallet::genesis_config]
    #[derive(frame_support::DefaultNoBound)]
    pub struct GenesisConfig<T: Config> {
        pub _phantom: PhantomData<T>,
    }

    #[pallet::genesis_build]
    impl<T: Config> BuildGenesisConfig for GenesisConfig<T> {
        fn build(&self) {
            // Modules registered via initialize_modules extrinsic after chain start
        }
    }

    // ── Events ────────────────────────────────────────────────────────────────
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ModuleRegistered { module_id: u32, name: Vec<u8> },
        ModuleUpdated { module_id: u32 },
        ModulesInitialized { count: u32 },
    }

    // ── Errors ────────────────────────────────────────────────────────────────
    #[pallet::error]
    pub enum Error<T> {
        ModuleNotFound,
        ModuleAlreadyExists,
        AlreadyInitialized,
        NameTooLong,
        TooManyModules,
    }

    // ── Calls ─────────────────────────────────────────────────────────────────
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Initialize all 30 ABENA clinical modules on-chain.
        /// Can only be called once by admin.
        #[pallet::call_index(0)]
        #[pallet::weight(Weight::from_parts(10_000_000, 0).saturating_add(T::DbWeight::get().writes(31)))]
        pub fn initialize_modules(origin: OriginFor<T>) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;
            ensure!(!Initialized::<T>::get(), Error::<T>::AlreadyInitialized);

            let modules_data: Vec<(&str, ModuleCategory)> = sp_std::vec![
                // Layer 1 — Universal Core
                ("Demographics",                 ModuleCategory::CoreDemographic),
                ("Social_Determinants_of_Health",ModuleCategory::CoreDemographic),
                ("Clinical_Outcomes",            ModuleCategory::CoreDemographic),
                ("Genetic_Genomic_Data",         ModuleCategory::Genetic),
                ("IOT_Wearable",                 ModuleCategory::CoreDemographic),
                ("Reproductive_Sexual_Health",   ModuleCategory::Reproductive),
                ("Mental_Health",                ModuleCategory::MentalHealth),
                ("Sleep_Architecture",           ModuleCategory::SleepArchitecture),
                ("Nutrition",                    ModuleCategory::Nutrition),
                ("Fitness_Physical_Activity",    ModuleCategory::Fitness),
                // Layer 2 — Condition-Triggered
                ("Cannabinoid",                  ModuleCategory::Cannabinoid),
                ("Pain_Management",              ModuleCategory::PainManagement),
                ("Psychedelic",                  ModuleCategory::MentalHealth),
                ("Pharmacogenomics",             ModuleCategory::Genetic),
                ("Vitamins_Supplements",         ModuleCategory::Nutrition),
                ("Toxicome",                     ModuleCategory::MentalHealth),
                // Layer 3 — Specialty Clinical
                ("Cardiovascular",               ModuleCategory::Cardiovascular),
                ("Endocrine_Metabolic",          ModuleCategory::Endocrine),
                ("Immunology_Autoimmune",        ModuleCategory::Immunology),
                ("Neurology_Cognitive",          ModuleCategory::Neurology),
                ("Gastrointestinal",             ModuleCategory::Nutrition),
                ("Respiratory_Pulmonary",        ModuleCategory::Cardiovascular),
                ("Musculoskeletal",              ModuleCategory::PainManagement),
                ("Dermatology",                  ModuleCategory::Immunology),
                // Layer 4 — Integrative
                ("Traditional_Chinese_Medicine", ModuleCategory::Integrative),
                ("Ayurveda",                     ModuleCategory::Integrative),
                ("Homeopathy",                   ModuleCategory::Integrative),
                ("Spiritual_Health",             ModuleCategory::Spiritual),
                // Layer 5 — Environmental
                ("Water",                        ModuleCategory::Environmental),
                ("Life_Environmental_Data",      ModuleCategory::Environmental),
            ];

            let block = frame_system::Pallet::<T>::block_number();
            let mut count = 0u32;

            for (idx, (name, category)) in modules_data.iter().enumerate() {
                let module_id = idx as u32;
                let bounded_name = BoundedVec::try_from(name.as_bytes().to_vec())
                    .map_err(|_| Error::<T>::NameTooLong)?;

                let metadata = ModuleMetadata {
                    module_id,
                    name: bounded_name.clone(),
                    category: category.clone(),
                    version: 1,
                    status: ModuleStatus::Active,
                    registered_at: block,
                };

                Modules::<T>::insert(module_id, metadata);
                count += 1;
            }

            ModuleCount::<T>::put(count);
            Initialized::<T>::put(true);
            Self::deposit_event(Event::ModulesInitialized { count });
            Ok(())
        }

        /// Update module status (admin only)
        #[pallet::call_index(1)]
        #[pallet::weight(Weight::from_parts(5_000_000, 0).saturating_add(T::DbWeight::get().writes(1)))]
        pub fn update_module_status(
            origin: OriginFor<T>,
            module_id: u32,
            status: ModuleStatus,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;
            Modules::<T>::try_mutate(module_id, |maybe_module| {
                let module = maybe_module.as_mut().ok_or(Error::<T>::ModuleNotFound)?;
                module.status = status;
                Ok::<(), DispatchError>(())
            })?;
            Self::deposit_event(Event::ModuleUpdated { module_id });
            Ok(())
        }
    }

    // ── Helper ────────────────────────────────────────────────────────────────
    impl<T: Config> Pallet<T> {
        pub fn get_active_modules() -> Vec<u32> {
            Modules::<T>::iter()
                .filter(|(_, m)| m.status == ModuleStatus::Active)
                .map(|(id, _)| id)
                .collect()
        }
    }
}
