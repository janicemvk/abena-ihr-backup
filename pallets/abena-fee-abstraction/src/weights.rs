use frame_support::weights::Weight;

pub trait WeightInfo {
    fn sponsor_patient() -> Weight;
    fn remove_sponsorship() -> Weight;
}

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);
impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
    fn sponsor_patient() -> Weight {
        Weight::from_parts(20_000_000, 0)
    }
    fn remove_sponsorship() -> Weight {
        Weight::from_parts(15_000_000, 0)
    }
}
