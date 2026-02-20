#!/usr/bin/env python3
"""
Environment Variable Loader for Abena IHR Intelligence Layer
This script loads environment variables from .env file for development.
"""

import os
from pathlib import Path

def load_env_file(env_file: str = ".env"):
    """Load environment variables from .env file"""
    if not os.path.exists(env_file):
        print(f"⚠️  .env file not found: {env_file}")
        print("   Run 'python setup_config.py' to create one")
        return False
    
    print(f"📁 Loading environment variables from {env_file}")
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse key=value pairs
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Set environment variable
                os.environ[key] = value
                print(f"   ✅ {key} = {'*' * len(value) if 'password' in key.lower() or 'key' in key.lower() else value}")
    
    print(f"✅ Loaded {len([k for k in os.environ.keys() if k.startswith(('DATABASE_', 'REDIS_', 'SMTP_', 'SLACK_', 'API_', 'LOG_', 'ALERT_', 'MONITORING_', 'DATA_QUALITY_', 'SECURITY_', 'CORS_'))])} configuration variables")
    return True

def main():
    """Main function to load environment variables"""
    print("🌍 Abena IHR Intelligence Layer - Environment Loader")
    print("=" * 55)
    
    success = load_env_file()
    
    if success:
        print("\n🎉 Environment variables loaded successfully!")
        print("\n📚 You can now run:")
        print("   python api_server.py")
        print("   python example_usage.py")
        print("   python test_config.py")
    else:
        print("\n❌ Failed to load environment variables")
        print("   Please run 'python setup_config.py' first")

if __name__ == "__main__":
    main() 