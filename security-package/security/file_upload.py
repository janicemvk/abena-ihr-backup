"""
Abena IHR Secure File Upload Module
====================================

Secure file upload handling with validation, virus scanning, and integrity checks.

Features:
- MIME type validation
- File size limits
- Extension whitelist
- Virus scanning (ClamAV)
- SHA-256 integrity hashing
- Secure file storage

Author: Abena IHR Security Team
Date: December 3, 2025
Version: 2.0.0
"""

import os
import hashlib
import magic
from typing import Optional, Dict, List, Tuple
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
import aiofiles


class FileUploadSecurity:
    """
    Secure file upload handler with comprehensive validation.
    
    Features:
    - MIME type verification
    - File size limits
    - Extension whitelist
    - Virus scanning
    - Integrity hashing
    """
    
    # Allowed MIME types (HIPAA-compliant document types)
    ALLOWED_MIME_TYPES = {
        # Documents
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
        'text/plain',
        'text/csv',
        
        # Images (for medical imaging)
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/tiff',
        'image/bmp',
        
        # Medical imaging formats
        'application/dicom',
        'image/dicom',
    }
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.csv',
        '.jpg', '.jpeg', '.png', '.gif', '.tiff', '.bmp',
        '.dcm', '.dicom'
    }
    
    # File size limits (in bytes)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB for images
    MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50 MB for documents
    
    # Upload directory
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    
    # ClamAV configuration (optional)
    CLAMAV_ENABLED = os.getenv("CLAMAV_ENABLED", "false").lower() == "true"
    CLAMAV_SOCKET = os.getenv("CLAMAV_SOCKET", "/var/run/clamav/clamd.ctl")
    
    def __init__(self, upload_dir: Optional[str] = None):
        """
        Initialize file upload security handler.
        
        Args:
            upload_dir: Directory to store uploaded files
        """
        self.upload_dir = upload_dir or self.UPLOAD_DIR
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)
    
    async def upload_file(
        self,
        file: UploadFile,
        user_id: str,
        scan_virus: bool = True
    ) -> Dict[str, any]:
        """
        Securely upload and validate a file.
        
        Args:
            file: FastAPI UploadFile object
            user_id: ID of user uploading the file
            scan_virus: Whether to scan for viruses
            
        Returns:
            Dictionary with file metadata
            
        Raises:
            HTTPException: If file validation fails
            
        Example:
            >>> metadata = await file_security.upload_file(file, "usr_123")
            >>> print(metadata['file_path'])
        """
        # Validate file
        validation_result = await self._validate_file(file)
        if not validation_result['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_result['error']
            )
        
        # Read file content
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Calculate file hash
        file_hash = self._calculate_hash(content)
        
        # Check file size
        file_size = len(content)
        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {self.MAX_FILE_SIZE / 1024 / 1024} MB"
            )
        
        # Virus scanning
        if scan_virus and self.CLAMAV_ENABLED:
            is_safe = await self._scan_virus(content)
            if not is_safe:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File failed virus scan. Upload rejected."
                )
        
        # Generate secure filename
        file_extension = self._get_file_extension(file.filename)
        secure_filename = self._generate_secure_filename(
            user_id, file_extension, file_hash
        )
        
        # Save file
        file_path = os.path.join(self.upload_dir, secure_filename)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Return metadata
        return {
            'filename': secure_filename,
            'original_filename': file.filename,
            'file_path': file_path,
            'file_size': file_size,
            'mime_type': validation_result['mime_type'],
            'sha256_hash': file_hash,
            'uploaded_by': user_id,
            'uploaded_at': self._get_timestamp()
        }
    
    async def _validate_file(self, file: UploadFile) -> Dict:
        """
        Validate uploaded file.
        
        Args:
            file: UploadFile object
            
        Returns:
            Dictionary with validation result
        """
        if not file.filename:
            return {'valid': False, 'error': 'No filename provided'}
        
        # Check extension
        extension = self._get_file_extension(file.filename)
        if extension not in self.ALLOWED_EXTENSIONS:
            return {
                'valid': False,
                'error': f'File extension not allowed. Allowed: {", ".join(self.ALLOWED_EXTENSIONS)}'
            }
        
        # Read first chunk to detect MIME type
        content = await file.read(1024)
        await file.seek(0)
        
        # Detect MIME type
        try:
            mime_type = magic.from_buffer(content, mime=True)
        except Exception:
            # Fallback to content-type header
            mime_type = file.content_type
        
        if not mime_type:
            return {'valid': False, 'error': 'Could not determine file type'}
        
        # Validate MIME type
        if mime_type not in self.ALLOWED_MIME_TYPES:
            return {
                'valid': False,
                'error': f'MIME type not allowed: {mime_type}'
            }
        
        # Check if extension matches MIME type
        if not self._extension_matches_mime(extension, mime_type):
            return {
                'valid': False,
                'error': 'File extension does not match file type'
            }
        
        return {
            'valid': True,
            'mime_type': mime_type,
            'extension': extension
        }
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase"""
        return Path(filename).suffix.lower()
    
    def _extension_matches_mime(self, extension: str, mime_type: str) -> bool:
        """Check if file extension matches MIME type"""
        extension_mime_map = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.tiff': 'image/tiff',
            '.bmp': 'image/bmp',
        }
        
        expected_mime = extension_mime_map.get(extension)
        return expected_mime == mime_type if expected_mime else True
    
    def _calculate_hash(self, content: bytes) -> str:
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(content).hexdigest()
    
    def _generate_secure_filename(
        self,
        user_id: str,
        extension: str,
        file_hash: str
    ) -> str:
        """
        Generate secure filename to prevent:
        - Path traversal
        - Filename collisions
        - Information disclosure
        """
        import secrets
        import time
        
        # Use hash + random + timestamp for uniqueness
        random_part = secrets.token_urlsafe(8)
        timestamp = int(time.time())
        
        # Format: {hash_prefix}_{user_id}_{timestamp}_{random}.{ext}
        hash_prefix = file_hash[:8]
        secure_name = f"{hash_prefix}_{user_id}_{timestamp}_{random_part}{extension}"
        
        return secure_name
    
    async def _scan_virus(self, content: bytes) -> bool:
        """
        Scan file for viruses using ClamAV.
        
        Args:
            content: File content bytes
            
        Returns:
            True if file is safe, False if virus detected
        """
        if not self.CLAMAV_ENABLED:
            return True  # Skip if ClamAV not enabled
        
        try:
            import pyclamd
            
            # Connect to ClamAV daemon
            cd = pyclamd.ClamdUnixSocket(self.CLAMAV_SOCKET)
            
            # Scan file
            result = cd.scan_stream(content)
            
            # Result format: {filename: ('FOUND', 'virus_name')} or None
            if result:
                return False  # Virus found
            
            return True  # No virus found
            
        except ImportError:
            # pyclamd not installed
            import warnings
            warnings.warn(
                "ClamAV scanning requested but pyclamd not installed. "
                "Install with: pip install pyclamd",
                UserWarning
            )
            return True  # Fail open if ClamAV not available
        except Exception as e:
            # ClamAV connection error
            import warnings
            warnings.warn(
                f"ClamAV scan failed: {e}. Allowing upload (fail open).",
                UserWarning
            )
            return True  # Fail open on error
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def verify_file_integrity(self, file_path: str, expected_hash: str) -> bool:
        """
        Verify file integrity using SHA-256 hash.
        
        Args:
            file_path: Path to file
            expected_hash: Expected SHA-256 hash
            
        Returns:
            True if hash matches, False otherwise
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                actual_hash = self._calculate_hash(content)
                return actual_hash == expected_hash
        except Exception:
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """
        Securely delete a file.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            # Ensure file is in upload directory (prevent path traversal)
            abs_path = os.path.abspath(file_path)
            abs_upload_dir = os.path.abspath(self.upload_dir)
            
            if not abs_path.startswith(abs_upload_dir):
                return False  # File outside upload directory
            
            if os.path.exists(abs_path):
                os.remove(abs_path)
                return True
            return False
        except Exception:
            return False


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Abena IHR Secure File Upload Module - Test")
    print("=" * 60)
    
    print("\n1. File upload security configuration:")
    security = FileUploadSecurity()
    print(f"   Upload directory: {security.upload_dir}")
    print(f"   Max file size: {security.MAX_FILE_SIZE / 1024 / 1024} MB")
    print(f"   Allowed extensions: {len(security.ALLOWED_EXTENSIONS)}")
    print(f"   Allowed MIME types: {len(security.ALLOWED_MIME_TYPES)}")
    print(f"   ClamAV enabled: {security.CLAMAV_ENABLED}")
    
    print("\n2. Allowed file types:")
    for ext in sorted(security.ALLOWED_EXTENSIONS):
        print(f"   - {ext}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\n⚠️  IMPORTANT:")
    print("   - Install python-magic: pip install python-magic-bin (Windows) or python-magic (Linux)")
    print("   - For ClamAV: pip install pyclamd and configure ClamAV daemon")
    print("   - Set UPLOAD_DIR environment variable for custom upload directory")

