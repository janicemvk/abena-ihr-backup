"""
Abena IHR Input Validation Module
==================================

Comprehensive input validation and sanitization to prevent:
- SQL injection attacks
- XSS (Cross-Site Scripting) attacks
- Command injection attacks
- Path traversal attacks
- Data type validation

Features:
- String sanitization
- Email validation
- Phone number validation
- SSN validation
- Date validation
- Pydantic model integration

Author: Abena IHR Security Team
Date: December 3, 2025
Version: 2.0.0
"""

import re
import bleach
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


class InputValidator:
    """
    Input validation and sanitization utilities.
    
    Prevents common injection attacks and validates data formats.
    """
    
    # SQL injection patterns to block
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(\b(UNION|OR|AND)\s+\d+)",
        r"(--|\#|\/\*|\*\/)",
        r"(\b(CHAR|ASCII|SUBSTRING|CONCAT)\s*\()",
        r"(\b(WAITFOR|DELAY)\s+DELAY)",
        r"(\b(XP_|SP_)\w+)",
        r"(\b(LOAD_FILE|INTO\s+OUTFILE|INTO\s+DUMPFILE)\b)",
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$(){}[\]<>]",
        r"(\b(cat|ls|pwd|whoami|id|uname|ps|kill|rm|mv|cp)\b)",
        r"(\$(\(|`))",
        r"(\b(nc|netcat|wget|curl|python|perl|ruby|bash|sh)\b)",
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"\.\.%2F",
        r"\.\.%5C",
        r"\.\.%252F",
        r"\.\.%255C",
    ]
    
    # Allowed HTML tags (for sanitization)
    ALLOWED_TAGS = []  # No HTML tags allowed by default
    ALLOWED_ATTRIBUTES = {}
    
    # Phone number regex (US format)
    PHONE_REGEX = re.compile(
        r'^(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'
    )
    
    # SSN regex (US format)
    SSN_REGEX = re.compile(r'^\d{3}-?\d{2}-?\d{4}$')
    
    # Date formats
    DATE_FORMATS = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y-%m-%d %H:%M:%S',
        '%m/%d/%Y %H:%M:%S',
    ]
    
    @staticmethod
    def sanitize_string(
        input_str: str,
        max_length: Optional[int] = None,
        allow_html: bool = False
    ) -> str:
        """
        Sanitize string input to prevent XSS and injection attacks.
        
        Args:
            input_str: String to sanitize
            max_length: Maximum allowed length
            allow_html: Whether to allow HTML tags (not recommended)
            
        Returns:
            Sanitized string
            
        Example:
            >>> safe = InputValidator.sanitize_string("<script>alert('xss')</script>")
            >>> "script" not in safe.lower()
            True
        """
        if not isinstance(input_str, str):
            input_str = str(input_str)
        
        # Remove null bytes
        input_str = input_str.replace('\x00', '')
        
        # Strip whitespace
        input_str = input_str.strip()
        
        # Check for SQL injection
        if InputValidator._contains_sql_injection(input_str):
            raise ValueError("Input contains potentially dangerous SQL patterns")
        
        # Check for command injection
        if InputValidator._contains_command_injection(input_str):
            raise ValueError("Input contains potentially dangerous command patterns")
        
        # Check for path traversal
        if InputValidator._contains_path_traversal(input_str):
            raise ValueError("Input contains potentially dangerous path patterns")
        
        # Sanitize HTML/XSS
        if allow_html:
            input_str = bleach.clean(
                input_str,
                tags=InputValidator.ALLOWED_TAGS,
                attributes=InputValidator.ALLOWED_ATTRIBUTES,
                strip=True
            )
        else:
            # Remove all HTML tags
            input_str = bleach.clean(input_str, tags=[], strip=True)
        
        # Apply length limit
        if max_length and len(input_str) > max_length:
            input_str = input_str[:max_length]
        
        return input_str
    
    @staticmethod
    def _contains_sql_injection(input_str: str) -> bool:
        """Check if string contains SQL injection patterns"""
        input_upper = input_str.upper()
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_upper, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def _contains_command_injection(input_str: str) -> bool:
        """Check if string contains command injection patterns"""
        for pattern in InputValidator.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, input_str, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def _contains_path_traversal(input_str: str) -> bool:
        """Check if string contains path traversal patterns"""
        for pattern in InputValidator.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, input_str, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Example:
            >>> is_valid, msg = InputValidator.validate_email("user@example.com")
            >>> is_valid
            True
        """
        if not email:
            return False, "Email cannot be empty"
        
        # Basic email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        # Check length
        if len(email) > 254:  # RFC 5321 limit
            return False, "Email address too long (max 254 characters)"
        
        # Check for dangerous characters
        if InputValidator._contains_sql_injection(email):
            return False, "Email contains potentially dangerous patterns"
        
        return True, None
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """
        Validate phone number format (US format).
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not phone:
            return False, "Phone number cannot be empty"
        
        # Remove common formatting
        cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
        
        # Check if it matches pattern
        if not InputValidator.PHONE_REGEX.match(phone):
            return False, "Invalid phone number format. Expected: (XXX) XXX-XXXX or XXX-XXX-XXXX"
        
        return True, None
    
    @staticmethod
    def validate_ssn(ssn: str) -> Tuple[bool, Optional[str]]:
        """
        Validate SSN format (US format).
        
        Args:
            ssn: SSN to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not ssn:
            return False, "SSN cannot be empty"
        
        # Check format
        if not InputValidator.SSN_REGEX.match(ssn):
            return False, "Invalid SSN format. Expected: XXX-XX-XXXX"
        
        # Check for invalid SSNs
        # 000-XX-XXXX, XXX-00-XXXX, XXX-XX-0000, 123-45-6789 (test number)
        parts = ssn.replace('-', '')
        if len(parts) == 9:
            if parts[:3] == '000' or parts[3:5] == '00' or parts[5:] == '0000':
                return False, "Invalid SSN (contains all zeros)"
            if ssn == '123-45-6789':
                return False, "Invalid SSN (test number)"
        
        return True, None
    
    @staticmethod
    def validate_date(
        date_str: str,
        date_formats: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[datetime], Optional[str]]:
        """
        Validate and parse date string.
        
        Args:
            date_str: Date string to validate
            date_formats: Optional list of date formats to try
            
        Returns:
            Tuple of (is_valid, datetime_object, error_message)
        """
        if not date_str:
            return False, None, "Date cannot be empty"
        
        formats = date_formats or InputValidator.DATE_FORMATS
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return True, dt, None
            except ValueError:
                continue
        
        return False, None, f"Invalid date format. Supported formats: {', '.join(formats)}"
    
    @staticmethod
    def validate_positive_integer(value: Any) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Validate positive integer.
        
        Args:
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, integer_value, error_message)
        """
        try:
            int_value = int(value)
            if int_value < 0:
                return False, None, "Value must be positive"
            return True, int_value, None
        except (ValueError, TypeError):
            return False, None, "Value must be a valid integer"
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str]]:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return False, "URL cannot be empty"
        
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        
        if not url_pattern.match(url):
            return False, "Invalid URL format"
        
        # Check for dangerous patterns
        if InputValidator._contains_path_traversal(url):
            return False, "URL contains potentially dangerous path patterns"
        
        return True, None


# Pydantic models for common validations
class SanitizedString(str):
    """Pydantic field type for sanitized strings"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            v = str(v)
        return InputValidator.sanitize_string(v)


class ValidatedEmail(EmailStr):
    """Pydantic field type for validated emails"""
    
    @classmethod
    def __get_validators__(cls):
        yield from super().__get_validators__()
        yield cls.validate_security
    
    @classmethod
    def validate_security(cls, v):
        is_valid, error = InputValidator.validate_email(v)
        if not is_valid:
            raise ValueError(error)
        return v


class PatientInput(BaseModel):
    """Example Pydantic model with input validation"""
    first_name: SanitizedString = Field(..., max_length=100)
    last_name: SanitizedString = Field(..., max_length=100)
    email: ValidatedEmail
    phone: str = Field(..., pattern=InputValidator.PHONE_REGEX.pattern)
    date_of_birth: str
    ssn: Optional[str] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone_format(cls, v):
        is_valid, error = InputValidator.validate_phone(v)
        if not is_valid:
            raise ValueError(error)
        return v
    
    @field_validator('date_of_birth')
    @classmethod
    def validate_dob(cls, v):
        is_valid, dt, error = InputValidator.validate_date(v)
        if not is_valid:
            raise ValueError(error)
        return v
    
    @field_validator('ssn')
    @classmethod
    def validate_ssn_format(cls, v):
        if v:
            is_valid, error = InputValidator.validate_ssn(v)
            if not is_valid:
                raise ValueError(error)
        return v


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Abena IHR Input Validation Module - Test")
    print("=" * 60)
    
    # Test string sanitization
    print("\n1. Testing string sanitization...")
    test_inputs = [
        "Normal text",
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        "../../etc/passwd",
        "normal@email.com"
    ]
    
    for test_input in test_inputs:
        try:
            sanitized = InputValidator.sanitize_string(test_input)
            print(f"   ✓ '{test_input[:30]}...' -> '{sanitized[:30]}...'")
        except ValueError as e:
            print(f"   ✗ '{test_input[:30]}...' -> BLOCKED: {e}")
    
    # Test email validation
    print("\n2. Testing email validation...")
    emails = [
        "user@example.com",
        "invalid-email",
        "user@domain",
        "a" * 255 + "@example.com"
    ]
    
    for email in emails:
        is_valid, error = InputValidator.validate_email(email)
        status = "✓" if is_valid else "✗"
        print(f"   {status} {email}: {error or 'Valid'}")
    
    # Test phone validation
    print("\n3. Testing phone validation...")
    phones = [
        "(555) 123-4567",
        "555-123-4567",
        "5551234567",
        "123"
    ]
    
    for phone in phones:
        is_valid, error = InputValidator.validate_phone(phone)
        status = "✓" if is_valid else "✗"
        print(f"   {status} {phone}: {error or 'Valid'}")
    
    # Test SSN validation
    print("\n4. Testing SSN validation...")
    ssns = [
        "123-45-6789",
        "000-12-3456",
        "123-00-4567",
        "123-45-0000"
    ]
    
    for ssn in ssns:
        is_valid, error = InputValidator.validate_ssn(ssn)
        status = "✓" if is_valid else "✗"
        print(f"   {status} {ssn}: {error or 'Valid'}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

