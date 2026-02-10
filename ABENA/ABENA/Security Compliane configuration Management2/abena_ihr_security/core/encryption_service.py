"""
Encryption Service

Provides encryption and decryption capabilities for sensitive data.
"""

import logging
from typing import Union

logger = logging.getLogger(__name__)


class EncryptionService:
    """Service for data encryption and decryption"""

    def __init__(self):
        """Initialize encryption service"""
        logger.info("EncryptionService initialized")

    def encrypt_data(self, data: Union[str, bytes], key_id: str) -> bytes:
        """
        Encrypt data using the specified key

        Args:
            data: Data to encrypt
            key_id: ID of the encryption key to use

        Returns:
            Encrypted data
        """
        try:
            # Mock encryption for testing
            if isinstance(data, str):
                data = data.encode("utf-8")

            # In a real implementation, this would use actual encryption
            encrypted = b"encrypted_" + data

            logger.info(f"Data encrypted successfully with key: {key_id}")
            return encrypted

        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise

    def decrypt_data(self, encrypted_data: bytes, key_id: str) -> bytes:
        """
        Decrypt data using the specified key

        Args:
            encrypted_data: Data to decrypt
            key_id: ID of the encryption key to use

        Returns:
            Decrypted data
        """
        try:
            # Mock decryption for testing
            if encrypted_data.startswith(b"encrypted_"):
                decrypted = encrypted_data[10:]  # Remove "encrypted_" prefix
            else:
                decrypted = encrypted_data

            logger.info(f"Data decrypted successfully with key: {key_id}")
            return decrypted

        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
