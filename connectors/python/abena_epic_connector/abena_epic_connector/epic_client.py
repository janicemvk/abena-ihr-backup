"""
Epic FHIR API client - fetch Patient by MRN
"""

import requests
from typing import Optional, Dict, Any


class EpicFHIRClient:
    """Client for Epic FHIR R4 API. Requires OAuth2 token for production."""

    def __init__(self, epic_fhir_endpoint: str, access_token: Optional[str] = None):
        self.base_url = epic_fhir_endpoint.rstrip("/")
        self.access_token = access_token

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/fhir+json", "Content-Type": "application/fhir+json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def get_patient(self, mrn: str) -> Optional[Dict[str, Any]]:
        """
        Fetch Patient by MRN (Medical Record Number).
        Uses FHIR Patient search: Patient?identifier=urn:oid:2.16.840.1.113883.4.1|{mrn}
        """
        url = f"{self.base_url}/Patient"
        params = {"identifier": f"urn:oid:2.16.840.1.113883.4.1|{mrn}"}
        try:
            resp = requests.get(url, params=params, headers=self._headers(), timeout=30)
            resp.raise_for_status()
            data = resp.json()
            entries = data.get("entry", [])
            if entries:
                return entries[0].get("resource")
            return None
        except requests.RequestException:
            return None
