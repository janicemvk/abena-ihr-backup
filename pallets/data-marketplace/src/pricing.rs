//! Data pricing and compensation calculations for the ABENA Data Marketplace.
//!
//! Uses fixed-point math (no f64) for on-chain compatibility.

#![cfg_attr(not(feature = "std"), no_std)]

use crate::types::DataTier;

/// Data pricing calculations (ABENA Coins)
pub struct DataPricing;

impl DataPricing {
    /// Base prices (in ABENA Coins)
    pub const BASIC_VITALS: u128 = 10;
    pub const LAB_RESULTS: u128 = 50;
    pub const GENETIC_DATA: u128 = 500;
    pub const LONGITUDINAL_DATA: u128 = 200;
    pub const QUANTUM_ANALYZED: u128 = 1000;
    pub const RARE_DISEASE: u128 = 5000;

    /// Fixed-point scale: 1_000_000 = 1.0
    const MICRO: u128 = 1_000_000;

    /// Calculate compensation based on data tier and rarity (fixed-point: no f64).
    /// Multipliers: rare_condition 5x, quantum_analysis 2x, longitudinal 1 + 0.5 * duration_years.
    pub fn calculate_compensation(
        data_tier: &DataTier,
        has_rare_condition: bool,
        has_quantum_analysis: bool,
        duration_years: u32,
    ) -> u128 {
        let base_price = match data_tier {
            DataTier::ClinicalData => Self::LAB_RESULTS,
            DataTier::GenomicData => Self::GENETIC_DATA,
            DataTier::QuantumAnalyzedData => Self::QUANTUM_ANALYZED,
            _ => Self::BASIC_VITALS,
        };

        let mut multiplier_micro = Self::MICRO;

        if has_rare_condition {
            multiplier_micro = multiplier_micro.saturating_mul(5);
        }
        if has_quantum_analysis {
            multiplier_micro = multiplier_micro.saturating_mul(2);
        }
        if duration_years > 1 {
            let longitudinal_micro = Self::MICRO
                .saturating_add((duration_years as u128).saturating_mul(500_000));
            multiplier_micro = multiplier_micro.saturating_mul(longitudinal_micro);
        }

        base_price
            .saturating_mul(multiplier_micro)
            .saturating_div(Self::MICRO)
    }
}
