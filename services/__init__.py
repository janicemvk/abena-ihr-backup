"""Services module for Quantum Healthcare Service"""

from .abena_ihr_client import AbenaIHRClient, ihr_client
from .ecbome_client import ECBomeClient, ecbome_client, ECDomeClient, ecdome_client

__all__ = [
    'AbenaIHRClient',
    'ihr_client',
    'ECBomeClient',
    'ecbome_client',
    'ECDomeClient',  # Backward compatibility
    'ecdome_client'  # Backward compatibility
]



