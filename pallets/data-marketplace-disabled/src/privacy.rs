//! Privacy verification utilities for the ABENA Data Marketplace.
//!
//! Verifies k-anonymity, l-diversity, and differential privacy guarantees.
//! Risk level is computed with fixed-point math (no f64) for no_std.

#![cfg_attr(not(feature = "std"), no_std)]

use crate::types::PrivacyGuarantee;

/// Privacy verification utilities
pub struct PrivacyVerifier;

impl PrivacyVerifier {
    /// Verify privacy guarantees are met
    pub fn verify_guarantees(guarantees: &PrivacyGuarantee, dataset_size: u32) -> bool {
        if let Some(k) = guarantees.k_anonymity {
            if dataset_size < k.saturating_mul(10) {
                return false;
            }
        }

        if let Some(l) = guarantees.l_diversity {
            if l < 2 {
                return false;
            }
        }

        if let Some(epsilon) = guarantees.differential_privacy_epsilon {
            if epsilon > 1000 {
                return false;
            }
        }

        true
    }

    /// Calculate re-identification risk (fixed-point: no f64 on-chain).
    /// Risk score = 1_000_000 / (k * l); thresholds: &lt;1000 VeryLow, &lt;10000 Low, &lt;100000 Medium, else High.
    pub fn calculate_risk(
        k_anonymity: Option<u32>,
        l_diversity: Option<u32>,
        _dataset_size: u32,
    ) -> RiskLevel {
        let k = k_anonymity.unwrap_or(1).max(1);
        let l = l_diversity.unwrap_or(1).max(1);
        let product = k.saturating_mul(l);
        let risk_score_micro = if product == 0 {
            u32::MAX
        } else {
            1_000_000u32.saturating_div(product)
        };

        if risk_score_micro < 1000 {
            RiskLevel::VeryLow
        } else if risk_score_micro < 10_000 {
            RiskLevel::Low
        } else if risk_score_micro < 100_000 {
            RiskLevel::Medium
        } else {
            RiskLevel::High
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RiskLevel {
    VeryLow,
    Low,
    Medium,
    High,
}
