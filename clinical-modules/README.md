# Clinical Modules

Off-chain clinical assessment and decision-support modules (e.g. symptom checker, drug interactions, integrative protocols). Each module is identified by a stable ID and can be referenced from on-chain metadata or events.

**Naming:** `module-{ID}-{slug}/` (e.g. `module-001-symptom-checker`, `module-002-drug-interactions`, … `module-150-integrative-protocols`).

**Role:**
- Run in Tier 1 (application/off-chain); results hashed or summarized on-chain via Health Record Hash / Treatment Protocol pallets.
- Inputs/outputs stay off-chain; only pointers, hashes, or attestations go on-chain.

**Examples (placeholders):**
- `module-001-symptom-checker` – symptom triage
- `module-002-drug-interactions` – drug–drug and drug–herb checks
- `module-150-integrative-protocols` – multi-modality integrative care protocols

Add concrete modules under this directory as they are implemented.
