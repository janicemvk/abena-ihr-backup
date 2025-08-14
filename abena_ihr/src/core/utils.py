"""
Core Utilities

This module contains utility functions and helpers used across
the Abena IHR Clinical Outcomes Management System.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date, timedelta
import hashlib
import uuid
from pathlib import Path
import os
from urllib.parse import urlparse


# Configure logging
logger = logging.getLogger(__name__)


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


def hash_data(data: str) -> str:
    """Generate SHA-256 hash of data."""
    return hashlib.sha256(data.encode()).hexdigest()


def safe_json_dumps(obj: Any) -> str:
    """Safely serialize object to JSON string."""
    try:
        return json.dumps(obj, default=str, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error serializing object to JSON: {e}")
        return "{}"


def safe_json_loads(json_str: str) -> Any:
    """Safely deserialize JSON string to object."""
    try:
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Error deserializing JSON: {e}")
        return {}


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.isoformat() if dt else None


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse ISO datetime string."""
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except Exception as e:
        logger.error(f"Error parsing datetime: {e}")
        return None


def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date."""
    today = date.today()
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    return age


def validate_email(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    import re
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    return filename


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return Path(filename).suffix.lower()


def is_valid_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Check if file has allowed extension."""
    ext = get_file_extension(filename)
    return ext in allowed_extensions


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def retry_operation(func, max_attempts: int = 3, delay: float = 1.0):
    """Retry operation with exponential backoff."""
    import time
    
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            logger.warning(f"Operation failed, attempt {attempt + 1}/{max_attempts}: {e}")
            time.sleep(delay * (2 ** attempt))


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    """Flatten nested list."""
    return [item for sublist in nested_list for item in sublist]


def remove_duplicates(lst: List[Any]) -> List[Any]:
    """Remove duplicates from list while preserving order."""
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]


def get_environment_variable(key: str, default: Any = None) -> Any:
    """Get environment variable with optional default."""
    value = os.getenv(key, default)
    if value is None:
        logger.warning(f"Environment variable {key} not set, using default: {default}")
    return value


def mask_sensitive_data(data: str, mask_char: str = '*') -> str:
    """Mask sensitive data for logging."""
    if len(data) <= 4:
        return mask_char * len(data)
    return data[:2] + mask_char * (len(data) - 4) + data[-2:]


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate required fields in data dictionary."""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    return missing_fields


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def create_backup_filename(original_filename: str) -> str:
    """Create backup filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(original_filename)
    return f"{name}_backup_{timestamp}{ext}"


def is_within_date_range(check_date: date, start_date: date, end_date: date) -> bool:
    """Check if date is within specified range."""
    return start_date <= check_date <= end_date


def get_date_range_days(start_date: date, end_date: date) -> int:
    """Get number of days between two dates."""
    return (end_date - start_date).days


def format_duration(seconds: float) -> str:
    """Format duration in human readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def create_patient_id() -> str:
    """Generate a unique patient ID."""
    return f"PAT-{generate_uuid()[:8].upper()}"


def validate_patient_data(data: Dict[str, Any]) -> List[str]:
    """Validate patient data and return list of validation errors."""
    errors = []
    
    # Check required fields
    required_fields = ['first_name', 'last_name', 'date_of_birth']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate email if provided
    if 'email' in data and data['email']:
        if not validate_email(data['email']):
            errors.append("Invalid email format")
    
    # Validate date of birth
    if 'date_of_birth' in data and data['date_of_birth']:
        try:
            if isinstance(data['date_of_birth'], str):
                datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
        except ValueError:
            errors.append("Invalid date of birth format (use YYYY-MM-DD)")
    
    return errors


def calculate_prediction_confidence(prediction_score: float, model_accuracy: float = 0.85) -> float:
    """Calculate confidence level for a prediction based on score and model accuracy."""
    # Simple confidence calculation based on prediction score and model accuracy
    base_confidence = min(prediction_score, 1.0) * model_accuracy
    # Add some uncertainty based on how close to 0.5 the prediction is
    uncertainty = abs(prediction_score - 0.5) * 0.2
    confidence = base_confidence + uncertainty
    return min(confidence, 1.0) 