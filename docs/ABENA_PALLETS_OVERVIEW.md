# ABENA Pallets Overview

All custom Substrate pallets in the ABENA Integrative Health Record (IHR) blockchain are **complete and customized for ABENA**. This document summarizes each pallet’s role and main features.

---

## 1. Patient Identity (`pallet-patient-identity`)

**Role:** Core identity layer for the ABENA IHR.

- **DIDs** – Decentralized identifiers (patient account, public key, metadata hash)
- **Modality consent** – Per-modality consent (Western, TCM, Ayurveda, Homeopathy, Naturopathy)
- **Provider access** – Grant/revoke provider access with expiry and access level
- **Emergency override** – Emergency access with optional emergency contact
- **Deactivation** – Deactivate patient identity

**ABENA customization:** Therapeutic modalities aligned with integrative care; consent and access designed for multi-provider workflows.

---

## 2. Health Record Hash (`pallet-health-record-hash`)

**Role:** Store only hashes of medical records (no full content); immutable audit and IPFS links.

- **SHA-3** – Hashes should be SHA-3 (Keccak-256); documented and used consistently
- **Record hashes** – `RecordHashEntry`: hash, type, provider, version, optional IPFS CID
- **Version history** – `RecordVersions` for immutable version list
- **Multi-sig** – `MultiSigRequirements` and `MultiSigConfig` (patient + provider signers)
- **Audit log** – `AuditLogs` and `AuditLogEntry` for actions

**ABENA customization:** Record types (clinical, lab, imaging, medication, etc.); IPFS for off-chain storage; multi-sig for sensitive records.

---

## 3. Patient Health Records (`pallet-patient-health-records`)

**Role:** Encrypted on-chain health record metadata and access control.

- **Encrypted storage** – `EncryptedHealthRecord` with quantum-resistant algorithm options
- **Access permissions** – `AccessPermissions` by patient and authorized account
- **Encryption metadata** – Algorithm and parameters (e.g. Kyber, Dilithium)
- **Create/update** – Create record, update record, grant/revoke access

**ABENA customization:** Quantum-resistant encryption options; integrates with hashes (Health Record Hash) and identity (Patient Identity) for full IHR flow.

---

## 4. Quantum Computing / Quantum Results (`pallet-quantum-computing`)

**Role:** Attest and store quantum computation results; link to patient records.

- **Job types** – VQE, QML, QAOA, Simulation, Optimization, MachineLearning, Cryptography, DrugDiscovery, ProteinFolding
- **Jobs & results** – `QuantumJob`, `QuantumResult` with timestamps
- **Patient/record link** – Optional `patient` and `health_record_hash` on jobs and results
- **Integration points** – Register external providers (e.g. IBM Quantum)
- **Submit / store / query** – Submit job (with optional patient/hash), store result, query result

**ABENA customization:** VQE/QML/QAOA; optional link to patient and health record hash; timestamps for audit; ready for IBM attestation extension.

---

## 5. ABENA Coin (`pallet-abena-coin`)

**Role:** Fungible token for gamification and wellness incentives.

- **Token** – Mint, burn, transfer; `TotalSupply`, `Balances`
- **Rewards** – `RewardType`: HealthRecordCreated, HealthRecordUpdated, DataShared, QuantumContribution, PlatformParticipation, **WellnessGoalReached**, **CarePlanAdherence**
- **Achievements** – `AchievementType`: HealthRecordCreator, ActiveUser, DataContributor, QuantumResearcher, **WellnessStreak**, **IntegrativeCareComplete**
- **Reward history** – Per-account, per reward type
- **Achievement unlocks** – Claim achievement and receive reward

**ABENA customization:** Wellness and care-plan reward/achievement types; rewards aligned with IHR and integrative care.

---

## 6. Treatment Protocol (`pallet-treatment-protocol`)

**Role:** On-chain treatment protocols and guidelines for multi-modality care.

- **Protocols** – `TreatmentProtocol`: patient, provider, treatments, guideline, status
- **Modalities** – Western, TCM, Ayurveda, Integrative, Other
- **Guidelines** – `ClinicalGuideline` registration and reference
- **Compliance / contraindication** – Helpers for compliance and contraindication checks
- **Create / validate / update** – Create protocol, validate, update, register guideline

**ABENA customization:** Modalities and guideline lifecycle for integrative care plans.

---

## 7. Interoperability (`pallet-interoperability`)

**Role:** FHIR, cross-chain, insurance, pharmacy/lab for the IHR.

- **FHIR** – `FHIRResources`, `FHIRResourceMapping` by patient and resource type
- **Cross-chain** – `CrossChainExchanges` for exchange records
- **Insurance** – `InsuranceClaims`, `InsuranceClaim` verification
- **Pharmacy / lab** – `PharmacyIntegrations`, `LabIntegrations` with endpoints

**ABENA customization:** Oriented to integrative care workflows and external systems (pharmacy, lab, payers).

---

## 8. Governance (`pallet-governance`)

**Role:** On-chain governance for guidelines and protocols.

- **Guideline proposals** – `GuidelineProposals`, `GuidelineProposal` with voting
- **Protocol proposals** – `ProtocolProposals`, `ProtocolProposal` with voting
- **Votes** – Approve, Reject, Abstain
- **Emergency interventions** – `EmergencyInterventions`, `EmergencyIntervention` (e.g. suspend, override, emergency access)

**ABENA customization:** Clinical guideline and treatment protocol lifecycle; emergency actions for care safety.

---

## 9. Fee Management (`pallet-fee-management`)

**Role:** Subscriptions, rate limits, and validator rewards.

- **Account types** – Patient, Provider, Institution
- **Rate limits** – Time window and max requests per account type
- **Usage** – Usage records and rate-limit checks
- **Validator rewards** – Distribution of rewards to validators

**ABENA customization:** Account-type-based limits and subscriptions for the IHR ecosystem.

---

## 10. Access Control (`pallet-access-control`)

**Role:** Patient-centric authorization and audit.

- **Patient authorization** – Free reads for own data; grant/revoke
- **Institutional permissions** – Access level and expiry
- **Emergency access** – Reason, authorizer, expiry
- **Audit log** – Immutable log of actions

**ABENA customization:** Patient-first model; emergency and institutional access for care coordination.

---

## 11. Account Management (`pallet-account-management`)

**Role:** Tiered accounts and credentials.

- **Tiers** – Patient, Provider, Institution
- **Credentials** – Submit and verify (e.g. license, certification, accreditation)
- **Deposits** – Make and withdraw deposits for providers/institutions
- **Registration** – Register account with tier; update tier (root)

**ABENA customization:** Three tiers and credential types aligned with healthcare roles.

---

## Summary

| # | Pallet              | ABENA focus |
|---|---------------------|------------|
| 1 | Patient Identity    | DIDs, modality consent, provider access, emergency |
| 2 | Health Record Hash  | SHA-3 hashes, audit, multi-sig, IPFS |
| 3 | Patient Health Records | Encrypted records, quantum-resistant options |
| 4 | Quantum Computing   | VQE/QML/QAOA, patient/record link, timestamps |
| 5 | ABENA Coin          | Gamification, wellness/care-plan rewards & achievements |
| 6 | Treatment Protocol  | Multi-modality protocols, guidelines, compliance |
| 7 | Interoperability    | FHIR, cross-chain, insurance, pharmacy/lab |
| 8 | Governance          | Guidelines, protocol voting, emergency intervention |
| 9 | Fee Management      | Subscriptions, rate limits, validator rewards |
| 10 | Access Control     | Patient auth, institutional, emergency, audit |
| 11 | Account Management  | Patient/Provider/Institution, credentials, deposits |

All pallets have **ABENA-focused module docs** and **Cargo.toml descriptions**. Core domain pallets (1–8) include ABENA-specific types, events, or behavior where applicable.
