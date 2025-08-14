#!/usr/bin/env python3
"""
Configuration Test Script for Abena IHR Intelligence Layer
This script tests the configuration system and validates all settings.
"""

import os
import sys
import logging
from config import config

def test_configuration():
    """Test the configuration system"""
    print("🔧 Testing Abena IHR Intelligence Layer Configuration")
    print("=" * 60)
    
    # Test basic configuration loading
    print("\n📋 Configuration Status:")
    print("-" * 25)
    
    # Database configuration
    print(f"Database URL: {'✅ Set' if config.database.url else '❌ Not set'}")
    if config.database.url:
        print(f"  Pool Size: {config.database.pool_size}")
        print(f"  Max Overflow: {config.database.max_overflow}")
        print(f"  Pool Timeout: {config.database.pool_timeout}")
    
    # Redis configuration
    print(f"Redis URL: {'✅ Set' if config.redis.url else '❌ Not set'}")
    if config.redis.url:
        print(f"  Max Connections: {config.redis.max_connections}")
        print(f"  Socket Timeout: {config.redis.socket_timeout}")
    
    # API configuration
    print(f"API Configuration:")
    print(f"  Host: {config.api.host}")
    print(f"  Port: {config.api.port}")
    print(f"  Prometheus Port: {config.api.prometheus_port}")
    
    # Email configuration
    print(f"Email Notifications: {'✅ Configured' if config.is_email_configured() else '❌ Not configured'}")
    if config.is_email_configured():
        print(f"  SMTP Server: {config.email.smtp_server}")
        print(f"  SMTP Port: {config.email.smtp_port}")
        print(f"  Username: {config.email.username}")
        print(f"  From Email: {config.email.from_email}")
        print(f"  To Emails: {', '.join(config.email.to_emails)}")
    
    # Slack configuration
    print(f"Slack Notifications: {'✅ Configured' if config.is_slack_configured() else '❌ Not configured'}")
    if config.is_slack_configured():
        print(f"  Webhook URL: {config.slack.webhook_url[:50]}...")
    
    # Security configuration
    print(f"Security: {'✅ Configured' if config.is_secure() else '❌ Not configured'}")
    if config.is_secure():
        print(f"  API Key Header: {config.security.api_key_header}")
        print(f"  CORS Origins: {', '.join(config.security.cors_origins)}")
    
    # Alert configuration
    print(f"\n🚨 Alert Configuration:")
    print(f"  Default Cooldown: {config.alerts.default_cooldown_minutes} minutes")
    print(f"  High Error Rate Threshold: {config.alerts.high_error_rate_threshold}")
    print(f"  Slow Response Time Threshold: {config.alerts.slow_response_time_threshold} seconds")
    print(f"  Low Data Quality Threshold: {config.alerts.low_data_quality_threshold}")
    
    # Monitoring configuration
    print(f"\n📈 Monitoring Configuration:")
    print(f"  Health Check Interval: {config.monitoring.health_check_interval_seconds} seconds")
    print(f"  Failure Detection Interval: {config.monitoring.failure_detection_interval_seconds} seconds")
    print(f"  System Health Threshold: {config.monitoring.system_health_threshold}")
    
    # Data quality configuration
    print(f"\n🔍 Data Quality Configuration:")
    print(f"  Anomaly Detection Contamination: {config.data_quality.anomaly_detection_contamination}")
    print(f"  Quality Analysis Batch Size: {config.data_quality.quality_analysis_batch_size}")
    
    # Logging configuration
    print(f"\n📝 Logging Configuration:")
    print(f"  Level: {config.logging.level}")
    print(f"  File: {config.logging.file}")
    
    # Validate configuration
    print(f"\n🔍 Configuration Validation:")
    print("-" * 30)
    
    issues = config.validate()
    if issues:
        print("❌ Configuration issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Configuration validation passed!")
        return True

def test_environment_variables():
    """Test environment variable loading"""
    print(f"\n🌍 Environment Variables:")
    print("-" * 30)
    
    # Test if .env file exists
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ .env file found: {env_file}")
        
        # Read and display some key variables
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        print(f"  Total configuration lines: {len(lines)}")
        
        # Check for key variables
        key_vars = ['DATABASE_URL', 'REDIS_URL', 'SMTP_PASSWORD', 'SLACK_WEBHOOK_URL', 'API_KEY_VALUE']
        for var in key_vars:
            value = os.getenv(var)
            if value:
                if 'password' in var.lower() or 'key' in var.lower():
                    print(f"  {var}: {'✅ Set' if value != 'your_app_password' and 'YOUR' not in value else '❌ Default value'}")
                else:
                    print(f"  {var}: ✅ Set")
            else:
                print(f"  {var}: ❌ Not set")
    else:
        print(f"❌ .env file not found: {env_file}")
        print("  Run 'python setup_config.py' to create one")

def main():
    """Main test function"""
    try:
        # Test configuration
        config_valid = test_configuration()
        
        # Test environment variables
        test_environment_variables()
        
        print(f"\n{'='*60}")
        if config_valid:
            print("🎉 Configuration test completed successfully!")
            print("\n📚 Next steps:")
            print("   1. Start the services: ./start.sh")
            print("   2. Test the API: curl http://localhost:8000/health")
            print("   3. Access the dashboard: http://localhost:8000/dashboard")
        else:
            print("❌ Configuration test failed!")
            print("\n🔧 To fix configuration issues:")
            print("   1. Run: python setup_config.py")
            print("   2. Edit the .env file manually")
            print("   3. Run this test again")
        
        return config_valid
        
    except Exception as e:
        print(f"\n❌ Error during configuration test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 