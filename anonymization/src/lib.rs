//! ABENA k-anonymity anonymization and data pricing for patient records.
//!
//! Used off-chain (e.g. in data-preparation pipelines or off-chain workers) to
//! generalize quasi-identifiers (age, gender, zip) and produce k-anonymous datasets
//! before data is made available under a data license. Not used inside the runtime
//! (which uses bounded storage and no_std).
//!
//! Also provides `DataPricing` with `f64` multiplier for off-chain compensation
//! calculations; the runtime uses fixed-point in the data-separation pallet.

use std::collections::HashMap;

// -----------------------------------------------------------------------------
// Data pricing (off-chain: uses f64)
// -----------------------------------------------------------------------------

/// Data type for pricing (matches pallet data-separation DataType).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum DataType {
    BasicVitals,
    LabResults,
    GeneticData,
    LongitudinalData,
    QuantumAnalyzed,
    RareDisease,
}

/// Base prices in ABENA Coins per record (matches pallet defaults).
#[derive(Clone, Debug)]
pub struct DataPricing {
    pub basic_vitals: u128,
    pub lab_results: u128,
    pub genetic_data: u128,
    pub longitudinal_data: u128,
    pub quantum_analyzed_data: u128,
    pub rare_disease_data: u128,
}

impl Default for DataPricing {
    fn default() -> Self {
        Self {
            basic_vitals: 10,
            lab_results: 50,
            genetic_data: 500,
            longitudinal_data: 200,
            quantum_analyzed_data: 1_000,
            rare_disease_data: 5_000,
        }
    }
}

impl DataPricing {
    /// Compensation = base_price * rarity_multiplier (e.g. 1.0 = normal, 1.5 = 50% premium).
    pub fn calculate_compensation(&self, data_type: DataType, rarity_multiplier: f64) -> u128 {
        let base = match data_type {
            DataType::BasicVitals => self.basic_vitals,
            DataType::LabResults => self.lab_results,
            DataType::GeneticData => self.genetic_data,
            DataType::LongitudinalData => self.longitudinal_data,
            DataType::QuantumAnalyzed => self.quantum_analyzed_data,
            DataType::RareDisease => self.rare_disease_data,
        };
        (base as f64 * rarity_multiplier) as u128
    }
}

// -----------------------------------------------------------------------------
// K-anonymity
// -----------------------------------------------------------------------------

#[derive(Clone, Debug)]
pub struct PatientRecord {
    /// Will be removed in anonymized output (direct identifier).
    pub patient_id: String,
    pub age: u32,
    pub gender: String,
    pub zip_code: String,
    /// Sensitive attribute.
    pub diagnosis: String,
    pub lab_values: Vec<f64>,
}

#[derive(Clone, Debug, Hash, Eq, PartialEq)]
pub struct QuasiIdentifier {
    pub age_range: String,
    pub gender: String,
    pub zip_prefix: String,
}

#[derive(Clone, Debug)]
pub struct AnonymizedRecord {
    pub quasi_identifier: QuasiIdentifier,
    pub diagnosis: String,
    pub lab_values: Vec<f64>,
    /// How many patients in this group (for k-anonymity).
    pub record_count: usize,
}

pub struct KAnonymizer {
    k: u32,
}

impl KAnonymizer {
    pub fn new(k: u32) -> Self {
        Self { k }
    }

    /// Generalize age into decade ranges (e.g. 34 -> "30-39").
    fn generalize_age(&self, age: u32) -> String {
        let lower_bound = (age / 10) * 10;
        let upper_bound = lower_bound + 9;
        format!("{}-{}", lower_bound, upper_bound)
    }

    /// Generalize zip code to 3-digit prefix (e.g. "97341" -> "973**").
    fn generalize_zip(&self, zip: &str) -> String {
        if zip.len() >= 3 {
            format!("{}**", &zip[..3])
        } else {
            "***".to_string()
        }
    }

    /// Create quasi-identifier from patient record.
    fn create_quasi_identifier(&self, record: &PatientRecord) -> QuasiIdentifier {
        QuasiIdentifier {
            age_range: self.generalize_age(record.age),
            gender: record.gender.clone(),
            zip_prefix: self.generalize_zip(&record.zip_code),
        }
    }

    /// Anonymize dataset with k-anonymity: group by quasi-identifiers, keep only groups of size >= k.
    pub fn anonymize(&self, records: Vec<PatientRecord>) -> Result<Vec<AnonymizedRecord>, String> {
        let mut groups: HashMap<QuasiIdentifier, Vec<PatientRecord>> = HashMap::new();

        for record in records {
            let qi = self.create_quasi_identifier(&record);
            groups.entry(qi).or_default().push(record);
        }

        let mut anonymized = Vec::new();
        let mut suppressed_count = 0;

        for (quasi_id, group_records) in groups {
            if group_records.len() >= self.k as usize {
                let count = group_records.len();
                for record in group_records {
                    anonymized.push(AnonymizedRecord {
                        quasi_identifier: quasi_id.clone(),
                        diagnosis: record.diagnosis,
                        lab_values: record.lab_values,
                        record_count: count,
                    });
                }
            } else {
                suppressed_count += group_records.len();
            }
        }

        if anonymized.is_empty() {
            return Err("No records meet k-anonymity threshold".to_string());
        }

        Ok(anonymized)
    }

    /// Verify k-anonymity property: every quasi-identifier group has at least k records.
    pub fn verify_k_anonymity(&self, records: &[AnonymizedRecord]) -> bool {
        let mut counts: HashMap<QuasiIdentifier, usize> = HashMap::new();

        for record in records {
            *counts.entry(record.quasi_identifier.clone()).or_insert(0) += 1;
        }

        counts.values().all(|&count| count >= self.k as usize)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_k_anonymity() {
        let records = vec![
            PatientRecord {
                patient_id: "001".to_string(),
                age: 34,
                gender: "Male".to_string(),
                zip_code: "97341".to_string(),
                diagnosis: "Diabetes".to_string(),
                lab_values: vec![120.5, 7.2],
            },
            PatientRecord {
                patient_id: "002".to_string(),
                age: 35,
                gender: "Male".to_string(),
                zip_code: "97342".to_string(),
                diagnosis: "Hypertension".to_string(),
                lab_values: vec![140.0, 5.5],
            },
            PatientRecord {
                patient_id: "003".to_string(),
                age: 36,
                gender: "Male".to_string(),
                zip_code: "97343".to_string(),
                diagnosis: "Diabetes".to_string(),
                lab_values: vec![115.0, 7.8],
            },
        ];

        let anonymizer = KAnonymizer::new(2);
        let anonymized = anonymizer.anonymize(records).unwrap();

        assert!(anonymizer.verify_k_anonymity(&anonymized));

        for record in &anonymized {
            assert_eq!(record.quasi_identifier.age_range, "30-39");
            assert_eq!(record.quasi_identifier.zip_prefix, "973**");
        }
    }

    #[test]
    fn test_data_pricing() {
        let pricing = DataPricing::default();
        assert_eq!(pricing.calculate_compensation(DataType::BasicVitals, 1.0), 10);
        assert_eq!(pricing.calculate_compensation(DataType::RareDisease, 1.0), 5_000);
        assert_eq!(pricing.calculate_compensation(DataType::LabResults, 2.0), 100);
    }
}
