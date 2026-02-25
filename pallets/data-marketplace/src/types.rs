//! Data structures for the ABENA Data Marketplace pallet.

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Decode, Encode, MaxEncodedLen};
use scale_info::TypeInfo;
use sp_runtime::RuntimeDebug;
use sp_std::vec::Vec;

/// Therapeutic modalities for consent tracking
#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum TherapeuticModality {
    WesternMedicine,
    TraditionalChineseMedicine,
    Ayurveda,
    Homeopathy,
    Naturopathy,
    Integrative,
}

/// Data tiers for privacy classification
#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum DataTier {
    /// Direct identifiers - NEVER shared (name, SSN, address, email, phone)
    DirectIdentifiers,
    /// Quasi-identifiers - Transformed before sharing (age, gender, zip, dates)
    QuasiIdentifiers,
    /// Clinical data - Shareable with consent (diagnoses, labs, treatments)
    ClinicalData,
    /// Genomic data - Highly sensitive, requires special consent
    GenomicData,
    /// Quantum-analyzed data - Premium data with AI insights
    QuantumAnalyzedData,
}

/// Anonymization levels and techniques
#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum AnonymizationLevel {
    /// K-anonymity with specified k value
    KAnonymity(u32),
    /// L-diversity with specified l value
    LDiversity(u32),
    /// Differential privacy with epsilon parameter
    DifferentialPrivacy(u32), // Stored as epsilon * 1000 (e.g., 0.1 = 100)
    /// Full anonymization (all techniques)
    Full,
}

/// Purpose for data licensing
#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum LicensePurpose {
    DrugDevelopment,
    ClinicalTrial,
    InsuranceActuary,
    AgriculturalResearch,
    CannabisResearch,
    AcademicResearch,
    PublicHealth,
    QualityImprovement,
}

/// Privacy guarantee specifications
#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub struct PrivacyGuarantee {
    pub k_anonymity: Option<u32>,
    pub l_diversity: Option<u32>,
    pub differential_privacy_epsilon: Option<u32>, // * 1000
    pub no_reidentification_clause: bool,
}

/// Data field types that can be requested
#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum DataField {
    Age,
    Gender,
    ZipCode,
    Diagnosis,
    LabResults,
    Medications,
    Vitals,
    Genomics,
    QuantumAnalysis,
    TreatmentOutcomes,
}

/// Clinical condition filter
#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum ClinicalCondition {
    Diabetes,
    Hypertension,
    Cancer,
    CardiovascularDisease,
    RespiratoryDisease,
    MentalHealth,
    AutoimmuneDisease,
    InfectiousDisease,
    ChronicPain,
    Other,
}

/// Demographic filter for data queries
#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub struct DemographicFilter {
    pub age_min: Option<u32>,
    pub age_max: Option<u32>,
    pub gender: Option<Gender>,
    pub geographic_region: Option<GeographicRegion>,
}

#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum Gender {
    Male,
    Female,
    Other,
    Any,
}

#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum GeographicRegion {
    NorthAmerica,
    Europe,
    Asia,
    Africa,
    SouthAmerica,
    Oceania,
}

/// Data violation types
#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum DataViolation {
    UnauthorizedReidentification,
    PurposeMisuse,
    UnauthorizedRedistribution,
    PrivacyGuaranteeViolation,
    ContractualBreach,
}

/// Commercial entity status
#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum EntityStatus {
    Pending,
    Approved,
    Suspended,
    Banned,
}

/// Entity type for commercial entities
#[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum EntityType {
    PharmaceuticalCompany,
    BiotechCompany,
    InsuranceCompany,
    ResearchInstitution,
    AcademicInstitution,
    HealthcareProvider,
    TechnologyCompany,
}
