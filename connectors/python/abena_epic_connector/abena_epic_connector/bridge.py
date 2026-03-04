"""
ABENAEpicBridge - Sync Epic patients to ABENA blockchain and link identifiers
"""

import json
import os
from pathlib import Path
from typing import Optional

from .epic_client import EpicFHIRClient
from .abena_client import ABENABlockchainClient, convert_fhir_to_abena


class ABENAEpicBridge:
    """
    Bridge between Epic FHIR and ABENA blockchain.
    - Fetches patient from Epic by MRN
    - Converts to ABENA format
    - Registers on blockchain (requires signer)
    - Links Epic MRN to ABENA DID
    """

    def __init__(self, epic_fhir_endpoint: str, abena_endpoint: str, epic_token: Optional[str] = None):
        self.epic = EpicFHIRClient(epic_fhir_endpoint, access_token=epic_token)
        self.abena = ABENABlockchainClient(abena_endpoint)
        self._links_path = Path(os.environ.get("ABENA_LINKS_PATH", "./abena-epic-links.json"))
        self._links: dict[str, str] = {}
        self._load_links()

    def _load_links(self) -> None:
        if self._links_path.exists():
            try:
                self._links = json.loads(self._links_path.read_text())
            except Exception:
                self._links = {}

    def _save_links(self) -> None:
        self._links_path.parent.mkdir(parents=True, exist_ok=True)
        self._links_path.write_text(json.dumps(self._links, indent=2))

    def link_identifiers(self, epic_mrn: str, abena_did: str) -> None:
        """Store Epic MRN -> ABENA DID mapping."""
        self._links[epic_mrn] = abena_did
        self._save_links()

    def lookup_did(self, epic_mrn: str) -> Optional[str]:
        """Resolve ABENA DID from Epic MRN."""
        return self._links.get(epic_mrn)

    def sync_patient_to_blockchain(
        self,
        patient_mrn: str,
        signer_ss58: str,
        emergency_contact_ss58: Optional[str] = None,
    ) -> Optional[str]:
        """
        Sync a single patient from Epic to ABENA.

        1. Fetch from Epic FHIR API
        2. Convert to ABENA format
        3. Register on blockchain (returns DID = signer for now)
        4. Link Epic MRN to ABENA DID

        Returns ABENA DID (patient account ss58) or None on failure.
        """
        epic_patient = self.epic.get_patient(mrn=patient_mrn)
        if not epic_patient:
            return None

        abena_patient = convert_fhir_to_abena(epic_patient)

        tx_hash = self.abena.register_patient(
            signer_ss58=signer_ss58,
            public_key=abena_patient["public_key"],
            metadata_hash=abena_patient["metadata_hash"],
            emergency_contact_ss58=emergency_contact_ss58 or abena_patient.get("emergency_contact"),
        )  # Returns signer_ss58 as DID

        self.link_identifiers(epic_mrn=patient_mrn, abena_did=tx_hash)
        return tx_hash

    def bidirectional_sync(self) -> None:
        """
        Placeholder for bidirectional sync:
        - Epic -> ABENA: New records (observations, encounters)
        - ABENA -> Epic: Quantum insights, external data
        """
        pass
