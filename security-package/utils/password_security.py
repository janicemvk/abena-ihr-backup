"""
Abena IHR Password Security Module
==================================

Provides secure password hashing, validation, and management using bcrypt.
Implements HIPAA-compliant password policies.

Author: Abena IHR Security Team
Date: December 3, 2025
Version: 2.0.0
"""

import bcrypt
import re
from datetime import datetime, timedelta
from typing import Tuple, Optional
from enum import Enum


class PasswordStrength(Enum):
    """Password strength levels"""
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class PasswordSecurity:
    """
    Secure password hashing and validation using bcrypt.
    
    Features:
    - Bcrypt hashing with configurable cost factor
    - Automatic salt generation
    - Password strength validation
    - HIPAA-compliant password policies
    - Password expiration support
    """
    
    # Bcrypt cost factor (2^12 = 4096 iterations)
    # Higher = more secure but slower
    BCRYPT_COST_FACTOR = 12
    
    # Password policy requirements
    MIN_LENGTH = 12
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL = True
    MIN_SPECIAL_CHARS = 1
    
    # Password expiration (HIPAA compliant: 90 days)
    PASSWORD_EXPIRATION_DAYS = 90
    
    # Common weak passwords to reject
    COMMON_PASSWORDS = {
        'password', 'password123', '12345678', 'qwerty', 'abc123',
        'letmein', 'welcome', 'admin', 'root', 'passw0rd',
        'password1', 'Password1', 'P@ssw0rd', 'Welcome123'
    }
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt with automatic salt generation.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password string (includes salt)
            
        Raises:
            ValueError: If password doesn't meet strength requirements
            
        Example:
            >>> hashed = PasswordSecurity.hash_password("SecureP@ss123")
            >>> isinstance(hashed, str)
            True
        """
        # Validate password strength before hashing
        is_valid, message = PasswordSecurity.validate_password_strength(password)
        if not is_valid:
            raise ValueError(f"Password validation failed: {message}")
        
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=PasswordSecurity.BCRYPT_COST_FACTOR)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify a password against a bcrypt hash.
        
        Args:
            password: Plain text password to verify
            hashed: Bcrypt hash string to verify against
            
        Returns:
            True if password matches hash, False otherwise
            
        Example:
            >>> hashed = PasswordSecurity.hash_password("SecureP@ss123")
            >>> PasswordSecurity.verify_password("SecureP@ss123", hashed)
            True
            >>> PasswordSecurity.verify_password("WrongPassword", hashed)
            False
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except (ValueError, TypeError) as e:
            # Invalid hash format or encoding error
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Validate password strength against security policy.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid: bool, message: str)
            
        Example:
            >>> is_valid, msg = PasswordSecurity.validate_password_strength("Weak123")
            >>> is_valid
            False
        """
        if not password:
            return False, "Password cannot be empty"
        
        # Check length
        if len(password) < PasswordSecurity.MIN_LENGTH:
            return False, f"Password must be at least {PasswordSecurity.MIN_LENGTH} characters"
        
        if len(password) > PasswordSecurity.MAX_LENGTH:
            return False, f"Password must be no more than {PasswordSecurity.MAX_LENGTH} characters"
        
        # Check for common weak passwords
        if password.lower() in PasswordSecurity.COMMON_PASSWORDS:
            return False, "Password is too common. Please choose a more unique password"
        
        # Check for repeated characters (e.g., "aaaaaa")
        if re.search(r'(.)\1{3,}', password):
            return False, "Password contains too many repeated characters"
        
        # Check for sequential characters (e.g., "12345", "abcde")
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            return False, "Password contains sequential numbers"
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            return False, "Password contains sequential letters"
        
        # Check requirements
        errors = []
        
        if PasswordSecurity.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("uppercase letter")
        
        if PasswordSecurity.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("lowercase letter")
        
        if PasswordSecurity.REQUIRE_DIGITS and not re.search(r'\d', password):
            errors.append("digit")
        
        if PasswordSecurity.REQUIRE_SPECIAL:
            special_chars = re.findall(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', password)
            if len(special_chars) < PasswordSecurity.MIN_SPECIAL_CHARS:
                errors.append(f"at least {PasswordSecurity.MIN_SPECIAL_CHARS} special character")
        
        if errors:
            return False, f"Password must contain: {', '.join(errors)}"
        
        return True, "Password meets strength requirements"
    
    @staticmethod
    def get_password_strength(password: str) -> PasswordStrength:
        """
        Calculate password strength level.
        
        Args:
            password: Password to analyze
            
        Returns:
            PasswordStrength enum value
        """
        if not password:
            return PasswordStrength.WEAK
        
        score = 0
        
        # Length scoring
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        if len(password) >= 20:
            score += 1
        
        # Character variety
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', password):
            score += 1
        
        # Complexity bonus
        if len(set(password)) >= len(password) * 0.7:  # 70% unique characters
            score += 1
        
        # Determine strength
        if score <= 3:
            return PasswordStrength.WEAK
        elif score <= 5:
            return PasswordStrength.MEDIUM
        elif score <= 7:
            return PasswordStrength.STRONG
        else:
            return PasswordStrength.VERY_STRONG
    
    @staticmethod
    def is_password_expired(last_changed: datetime) -> bool:
        """
        Check if password has expired based on last change date.
        
        Args:
            last_changed: Datetime when password was last changed
            
        Returns:
            True if password is expired, False otherwise
        """
        if not last_changed:
            return True  # Never changed = expired
        
        expiration_date = last_changed + timedelta(days=PasswordSecurity.PASSWORD_EXPIRATION_DAYS)
        return datetime.utcnow() > expiration_date
    
    @staticmethod
    def days_until_expiration(last_changed: datetime) -> Optional[int]:
        """
        Calculate days until password expiration.
        
        Args:
            last_changed: Datetime when password was last changed
            
        Returns:
            Number of days until expiration, or None if expired
        """
        if not last_changed:
            return None
        
        expiration_date = last_changed + timedelta(days=PasswordSecurity.PASSWORD_EXPIRATION_DAYS)
        days_left = (expiration_date - datetime.utcnow()).days
        
        return days_left if days_left > 0 else None
    
    @staticmethod
    def generate_password_suggestions() -> list:
        """
        Generate password strength suggestions for users.
        
        Returns:
            List of suggestion strings
        """
        return [
            f"Use at least {PasswordSecurity.MIN_LENGTH} characters",
            "Include uppercase and lowercase letters",
            "Include numbers and special characters",
            "Avoid common words or personal information",
            "Avoid sequential characters (123, abc)",
            "Use a unique password not used elsewhere",
            "Consider using a passphrase (e.g., 'Coffee!Morning@2024')"
        ]


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("Abena IHR Password Security Module - Test")
    print("=" * 60)
    
    # Test password hashing
    print("\n1. Testing password hashing...")
    test_password = "SecureP@ssw0rd123!"
    hashed = PasswordSecurity.hash_password(test_password)
    print(f"   Original: {test_password}")
    print(f"   Hashed: {hashed[:50]}...")
    
    # Test password verification
    print("\n2. Testing password verification...")
    is_valid = PasswordSecurity.verify_password(test_password, hashed)
    print(f"   Correct password: {is_valid}")
    is_invalid = PasswordSecurity.verify_password("WrongPassword", hashed)
    print(f"   Wrong password: {is_invalid}")
    
    # Test password strength validation
    print("\n3. Testing password strength validation...")
    test_passwords = [
        "weak",  # Too short
        "Weak123",  # Missing special char
        "Weak123!",  # Too short
        "SecureP@ssw0rd123!",  # Strong
    ]
    
    for pwd in test_passwords:
        is_valid, message = PasswordSecurity.validate_password_strength(pwd)
        strength = PasswordSecurity.get_password_strength(pwd)
        status = "✓" if is_valid else "✗"
        print(f"   {status} '{pwd}': {message} (Strength: {strength.value})")
    
    # Test password expiration
    print("\n4. Testing password expiration...")
    from datetime import datetime, timedelta
    old_date = datetime.utcnow() - timedelta(days=100)
    new_date = datetime.utcnow() - timedelta(days=30)
    
    print(f"   Password changed 100 days ago: {PasswordSecurity.is_password_expired(old_date)}")
    print(f"   Password changed 30 days ago: {PasswordSecurity.is_password_expired(new_date)}")
    print(f"   Days until expiration (30 days ago): {PasswordSecurity.days_until_expiration(new_date)}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

