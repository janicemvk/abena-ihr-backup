//! Weights for ABENA runtime

use frame_support::weights::Weight;

/// Weight functions needed for the runtime.
pub trait WeightInfo {
    fn db_read() -> Weight;
    fn db_write() -> Weight;
}

/// Weight functions for `pallet_balances`.
impl WeightInfo for () {
    fn db_read() -> Weight {
        Weight::from_parts(25_000_000, 0)
    }

    fn db_write() -> Weight {
        Weight::from_parts(100_000_000, 0)
    }
}

pub struct RuntimeDbWeight;
impl WeightInfo for RuntimeDbWeight {
    fn db_read() -> Weight {
        Weight::from_parts(25_000_000, 0)
    }

    fn db_write() -> Weight {
        Weight::from_parts(100_000_000, 0)
    }
}

