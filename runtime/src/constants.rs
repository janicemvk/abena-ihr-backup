//! Constants for ABENA runtime

use frame_support::weights::Weight;

/// Time and blocks.
pub mod time {
    use super::*;

    /// Since BABE is probabilistic this is the average expected block time that
    /// we are targeting. Blocks will be produced at a minimum duration defined
    /// by `SLOT_DURATION`, but some slots will not be allocated to any
    /// authority and hence no block will be produced. We expect to have this
    /// block time on average following the defined slot duration and the value
    /// of `c` configured for BABE (where `1 - c` represents the probability of
    /// a slot being empty).
    /// This value is only used in benchmarks that are used for runtime weight
    /// estimation.
    pub const MILLISECS_PER_BLOCK: u64 = 6000;

    pub const SLOT_DURATION: u64 = MILLISECS_PER_BLOCK;

    // These time units are defined in number of blocks.
    pub const MINUTES: u32 = 60_000 / (MILLISECS_PER_BLOCK as u32);
    pub const HOURS: u32 = MINUTES * 60;
    pub const DAYS: u32 = HOURS * 24;
}

/// Fee-related.
pub mod fee {
    use super::*;

    /// The fee to be paid for making a transaction; the per-byte portion.
    pub const fn transaction_byte_fee() -> u128 {
        1
    }
}

/// Weight-related.
pub mod weight {
    use super::*;

    /// Maximum block weight.
    pub const MAXIMUM_BLOCK_WEIGHT: Weight = Weight::from_parts(2_000_000_000_000, u64::MAX);
}

