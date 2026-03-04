"""
ABENA blockchain client - register patients via RPC
"""

import hashlib
import json
from typing import Optional, List, Any

try:
    import jsonrpcclient
except ImportError:
    jsonrpcclient = None

try:
    import websockets
except ImportError:
    websockets = None


def _blake2b_256(data: bytes) -> bytes:
    return hashlib.blake2b(data, digest_size=32).digest()


def _metadata_hash(metadata: dict) -> bytes:
    """32-byte hash of patient metadata for on-chain storage."""
    return _blake2b_256(json.dumps(metadata, sort_keys=True).encode())


def convert_fhir_to_abena(epic_patient: dict) -> dict:
    """
    Convert FHIR Patient to ABENA format.
    Returns dict with: metadata, metadata_hash, public_key, emergency_contact.
    """
    identifiers = epic_patient.get("identifier", [])
    mrn = None
    for id_ in identifiers:
        sys = str(id_.get("system", ""))
        if "4.1" in sys or "mrn" in str(id_.get("type", {})).lower():
            mrn = id_.get("value")
            break
    if not mrn:
        mrn = next((id_.get("value") for id_ in identifiers if id_.get("value")), "")

    names = epic_patient.get("name", [{}])
    name = names[0] if names else {}
    given = name.get("given", [])
    family = name.get("family", "")

    metadata = {
        "mrn": mrn,
        "given": given,
        "family": family,
        "birthDate": epic_patient.get("birthDate"),
        "gender": epic_patient.get("gender"),
    }
    metadata_hash_bytes = _metadata_hash(metadata)

    public_key = hashlib.sha256(f"abena:{mrn}".encode()).digest()
    if len(public_key) != 32:
        public_key = (public_key + b"\x00" * 32)[:32]

    return {
        "metadata": metadata,
        "metadata_hash": metadata_hash_bytes,
        "public_key": public_key,
        "emergency_contact": None,
    }


class ABENABlockchainClient:
    """
    ABENA Substrate node RPC client.
    In production, submits register_patient via author_submitExtrinsic.
    """

    def __init__(self, abena_endpoint: str):
        url = abena_endpoint
        if url.startswith("http://"):
            self.ws_url = "ws://" + url[7:]
        elif url.startswith("https://"):
            self.ws_url = "wss://" + url[8:]
        elif not url.startswith("ws"):
            self.ws_url = "wss://" + url
        else:
            self.ws_url = url

    async def _rpc(self, method: str, params: Optional[List[Any]] = None) -> dict:
        if websockets is None:
            raise RuntimeError("pip install websockets")
        async with websockets.connect(self.ws_url) as ws:
            payload = {"jsonrpc": "2.0", "id": 1, "method": method}
            if params:
                payload["params"] = params
            await ws.send(json.dumps(payload))
            raw = await ws.recv()
            return json.loads(raw)

    def register_patient(
        self,
        signer_ss58: str,
        public_key: bytes,
        metadata_hash: bytes,
        emergency_contact_ss58: Optional[str] = None,
    ) -> str:
        """
        Register patient on ABENA.
        Returns the patient DID (signer account ss58).
        In production: build + sign extrinsic, submit via author_submitExtrinsic.
        """
        return signer_ss58
