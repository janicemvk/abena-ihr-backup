//! K-anonymity and differential privacy utilities for the ABENA Data Marketplace.
//!
//! Provides quasi-identifier generalization (age, ZIP, gender) and k-anonymity
//! verification (k=5 minimum). Differential privacy placeholder for off-chain use.

#![cfg_attr(not(feature = "std"), no_std)]

use sp_std::collections::btree_map::BTreeMap;
use sp_std::vec::Vec;

/// K-anonymity implementation for quasi-identifier generalization
pub struct KAnonymizer {
    pub k: u32,
}

impl KAnonymizer {
    pub fn new(k: u32) -> Self {
        Self { k }
    }

    /// Generalize age into decade ranges
    pub fn generalize_age(age: u32) -> AgeRange {
        match age {
            0..=9 => AgeRange::Range0to9,
            10..=19 => AgeRange::Range10to19,
            20..=29 => AgeRange::Range20to29,
            30..=39 => AgeRange::Range30to39,
            40..=49 => AgeRange::Range40to49,
            50..=59 => AgeRange::Range50to59,
            60..=69 => AgeRange::Range60to69,
            70..=79 => AgeRange::Range70to79,
            80..=89 => AgeRange::Range80to89,
            _ => AgeRange::Range90Plus,
        }
    }

    /// Generalize ZIP code to 3-digit prefix (no_std: slice of bytes, e.g. b"12345" -> Prefix([b'1',b'2',b'3']))
    pub fn generalize_zip(zip: &[u8]) -> ZipPrefix {
        if zip.len() >= 3 {
            let mut prefix = [0u8; 3];
            prefix[..3].copy_from_slice(&zip[..3]);
            ZipPrefix::Prefix(prefix)
        } else {
            ZipPrefix::Unknown
        }
    }

    /// Check if groups meet k-anonymity threshold (k=5 minimum when using default)
    pub fn verify_k_anonymity(&self, groups: &BTreeMap<QuasiIdentifier, u32>) -> bool {
        groups.values().all(|&count| count >= self.k)
    }
}

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub enum AgeRange {
    Range0to9,
    Range10to19,
    Range20to29,
    Range30to39,
    Range40to49,
    Range50to59,
    Range60to69,
    Range70to79,
    Range80to89,
    Range90Plus,
}

/// ZIP prefix: 3 bytes for no_std (no String)
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub enum ZipPrefix {
    Prefix([u8; 3]),
    Unknown,
}

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub struct QuasiIdentifier {
    pub age_range: AgeRange,
    pub gender: Gender,
    pub zip_prefix: ZipPrefix,
}

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub enum Gender {
    Male,
    Female,
    Other,
}

/// Differential privacy (epsilon). On-chain we store epsilon in fixed-point (e.g. epsilon_micro = epsilon * 1_000_000).
/// Actual noise addition is done off-chain; this struct holds configuration.
pub struct DifferentialPrivacy {
    /// Epsilon in micro-units (epsilon * 1_000_000) to avoid f64 on-chain
    pub epsilon_micro: u32,
}

impl DifferentialPrivacy {
    pub fn new(epsilon_micro: u32) -> Self {
        Self { epsilon_micro }
    }

    /// Placeholder: on-chain we do not add noise (no f64). Use off-chain worker for Laplace noise.
    #[cfg(feature = "std")]
    pub fn add_noise(&self, value: f64) -> f64 {
        let _ = self.epsilon_micro;
        value
    }
}
