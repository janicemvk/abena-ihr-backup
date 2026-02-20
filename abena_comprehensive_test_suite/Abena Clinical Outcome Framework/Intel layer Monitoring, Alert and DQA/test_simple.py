#!/usr/bin/env python3
"""
Simple test script to verify configuration loading
"""

import os
from dotenv import load_dotenv

def test_config():
    print("🔧 Testing Configuration Loading")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Test key configuration values
    config_values = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "REDIS_URL": os.getenv("REDIS_URL"),
        "API_HOST": os.getenv("API_HOST"),
        "API_PORT": os.getenv("API_PORT"),
        "SLACK_WEBHOOK_URL": os.getenv("SLACK_WEBHOOK_URL"),
        "API_KEY_VALUE": os.getenv("API_KEY_VALUE"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL")
    }
    
    print("📊 Configuration Values:")
    for key, value in config_values.items():
        if value:
            # Mask sensitive values
            if "PASSWORD" in key or "KEY" in key:
                masked_value = value[:10] + "***" if len(value) > 10 else "***"
                print(f"   {key}: {masked_value}")
            elif "WEBHOOK" in key:
                print(f"   {key}: {value[:30]}...")
            else:
                print(f"   {key}: {value}")
        else:
            print(f"   {key}: ❌ NOT SET")
    
    # Check if essential values are present
    essential_keys = ["DATABASE_URL", "REDIS_URL", "API_KEY_VALUE"]
    missing_keys = [key for key in essential_keys if not config_values[key]]
    
    if missing_keys:
        print(f"\n❌ Missing essential configuration: {missing_keys}")
        return False
    else:
        print(f"\n✅ All essential configuration values are set!")
        return True

if __name__ == "__main__":
    try:
        success = test_config()
        if success:
            print("\n🎉 Configuration test passed!")
        else:
            print("\n❌ Configuration test failed!")
    except Exception as e:
        print(f"\n❌ Error during configuration test: {e}") 