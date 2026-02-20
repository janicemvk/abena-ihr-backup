"""
Generate secure secret key for Abena IHR System
"""

import secrets
import string

def generate_secret_key(length=50):
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*()-_=+[]{}|;:,.<>?'
    secret_key = ''.join(secrets.choice(alphabet) for i in range(length))
    return secret_key

def generate_database_password(length=16):
    """Generate a secure database password"""
    alphabet = string.ascii_letters + string.digits + '@#$%^&*'
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

if __name__ == "__main__":
    print("Generating secure keys for Abena IHR System...")
    print("=" * 50)
    
    secret_key = generate_secret_key()
    db_password = generate_database_password()
    
    print(f"SECRET_KEY={secret_key}")
    print(f"DATABASE_PASSWORD={db_password}")
    print()
    print("Copy these values to your .env file!")
    print("=" * 50) 