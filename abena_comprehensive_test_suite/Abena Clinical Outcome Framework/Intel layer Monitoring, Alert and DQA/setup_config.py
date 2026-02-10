#!/usr/bin/env python3
"""
Configuration Setup Script for Abena IHR Intelligence Layer
This script helps you configure your environment variables interactively.
"""

import os
import sys
import getpass
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🔧 Abena IHR Intelligence Layer Configuration Setup")
    print("=" * 60)
    print()

def get_input(prompt: str, default: str = "", password: bool = False) -> str:
    """Get user input with optional default value"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    if password:
        value = getpass.getpass(prompt)
    else:
        value = input(prompt)
    
    return value if value.strip() else default

def setup_database_config():
    """Setup database configuration"""
    print("📊 Database Configuration")
    print("-" * 30)
    
    db_host = get_input("Database host", "localhost")
    db_port = get_input("Database port", "5432")
    db_name = get_input("Database name", "abena_ihr")
    db_user = get_input("Database user", "user")
    db_password = getpass.getpass("Database password: ")
    
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    return {
        "DATABASE_URL": database_url,
        "DB_POOL_SIZE": get_input("Database pool size", "10"),
        "DB_MAX_OVERFLOW": get_input("Database max overflow", "20"),
        "DB_POOL_TIMEOUT": get_input("Database pool timeout", "30")
    }

def setup_redis_config():
    """Setup Redis configuration"""
    print("\n🔴 Redis Configuration")
    print("-" * 25)
    
    redis_host = get_input("Redis host", "localhost")
    redis_port = get_input("Redis port", "6379")
    redis_password = getpass.getpass("Redis password (leave empty if none): ")
    
    if redis_password:
        redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}"
    else:
        redis_url = f"redis://{redis_host}:{redis_port}"
    
    return {
        "REDIS_URL": redis_url,
        "REDIS_MAX_CONNECTIONS": get_input("Redis max connections", "20"),
        "REDIS_SOCKET_TIMEOUT": get_input("Redis socket timeout", "5"),
        "REDIS_SOCKET_CONNECT_TIMEOUT": get_input("Redis socket connect timeout", "5")
    }

def setup_email_config():
    """Setup email notification configuration"""
    print("\n📧 Email Notification Configuration")
    print("-" * 40)
    
    print("Do you want to configure email notifications? (y/n) [y]: ", end="")
    enable_email = input().strip().lower()
    if enable_email == "":
        enable_email = "y"
    
    if enable_email != "y":
        print("Skipping email notification configuration.")
        return {
            "SMTP_SERVER": "",
            "SMTP_PORT": "",
            "SMTP_USERNAME": "",
            "SMTP_PASSWORD": "",
            "FROM_EMAIL": "",
            "TO_EMAILS": ""
        }
    
    smtp_server = get_input("SMTP server", "smtp.gmail.com")
    smtp_port = get_input("SMTP port", "587")
    smtp_username = get_input("SMTP username", "alerts@abena-ihr.com")
    smtp_password = getpass.getpass("SMTP password/app password: ")
    from_email = get_input("From email", smtp_username)
    
    print("\nEnter recipient email addresses (comma-separated):")
    to_emails = get_input("To emails", "admin@abena-ihr.com,ops@abena-ihr.com")
    
    return {
        "SMTP_SERVER": smtp_server,
        "SMTP_PORT": smtp_port,
        "SMTP_USERNAME": smtp_username,
        "SMTP_PASSWORD": smtp_password,
        "FROM_EMAIL": from_email,
        "TO_EMAILS": to_emails
    }

def setup_slack_config():
    """Setup Slack notification configuration"""
    print("\n💬 Slack Notification Configuration")
    print("-" * 38)
    
    print("Do you want to configure Slack notifications? (y/n) [y]: ", end="")
    enable_slack = input().strip().lower()
    if enable_slack == "":
        enable_slack = "y"
    
    if enable_slack != "y":
        print("Skipping Slack notification configuration.")
        return {
            "SLACK_WEBHOOK_URL": ""
        }
    
    print("To get your Slack webhook URL:")
    print("1. Go to https://api.slack.com/apps")
    print("2. Create a new app or select existing one")
    print("3. Go to 'Incoming Webhooks'")
    print("4. Create a new webhook")
    print("5. Copy the webhook URL")
    print()
    
    webhook_url = get_input("Slack webhook URL", "")
    
    return {
        "SLACK_WEBHOOK_URL": webhook_url
    }

def setup_security_config():
    """Setup security configuration"""
    print("\n🔒 Security Configuration")
    print("-" * 25)
    
    api_key = getpass.getpass("API key (for authentication): ")
    cors_origins = get_input("CORS origins (comma-separated)", "http://localhost:3000,http://localhost:8080")
    
    return {
        "API_KEY_VALUE": api_key,
        "CORS_ORIGINS": cors_origins
    }

def setup_monitoring_config():
    """Setup monitoring configuration"""
    print("\n📈 Monitoring Configuration")
    print("-" * 30)
    
    return {
        "HEALTH_CHECK_INTERVAL_SECONDS": get_input("Health check interval (seconds)", "60"),
        "FAILURE_DETECTION_INTERVAL_SECONDS": get_input("Failure detection interval (seconds)", "300"),
        "SYSTEM_HEALTH_THRESHOLD": get_input("System health threshold (0-100)", "50"),
        "HIGH_ERROR_RATE_THRESHOLD": get_input("High error rate threshold (0-1)", "0.05"),
        "SLOW_RESPONSE_TIME_THRESHOLD": get_input("Slow response time threshold (seconds)", "30.0"),
        "LOW_DATA_QUALITY_THRESHOLD": get_input("Low data quality threshold (0-1)", "0.7")
    }

def setup_logging_config():
    """Setup logging configuration"""
    print("\n📝 Logging Configuration")
    print("-" * 25)
    
    log_level = get_input("Log level", "INFO")
    log_file = get_input("Log file path", "logs/intelligence_layer.log")
    
    return {
        "LOG_LEVEL": log_level,
        "LOG_FILE": log_file
    }

def write_env_file(config: dict, env_file: str = ".env"):
    """Write configuration to .env file"""
    print(f"\n💾 Writing configuration to {env_file}...")
    
    with open(env_file, 'w') as f:
        f.write("# Abena IHR Intelligence Layer Environment Configuration\n")
        f.write("# Generated by setup_config.py\n\n")
        
        for key, value in config.items():
            if value:  # Only write non-empty values
                f.write(f"{key}={value}\n")
    
    print(f"✅ Configuration written to {env_file}")

def validate_config(config: dict) -> list:
    """Validate configuration and return issues"""
    issues = []
    
    # Check required fields
    required_fields = ["DATABASE_URL", "REDIS_URL"]
    for field in required_fields:
        if not config.get(field):
            issues.append(f"Missing required field: {field}")
    
    # Check email configuration only if email is enabled
    if config.get("SMTP_SERVER") and config.get("SMTP_USERNAME"):
        if not config.get("SMTP_PASSWORD"):
            issues.append("SMTP_PASSWORD is required for email notifications")
        elif "your_app_password" in config.get("SMTP_PASSWORD", ""):
            issues.append("Please set a real SMTP password")
    
    # Check Slack configuration only if Slack is enabled
    if config.get("SLACK_WEBHOOK_URL"):
        if "YOUR/SLACK/WEBHOOK" in config.get("SLACK_WEBHOOK_URL", ""):
            issues.append("Please set a real Slack webhook URL")
    
    return issues

def main():
    """Main configuration setup function"""
    print_banner()
    
    print("This script will help you configure your Abena IHR Intelligence Layer environment.")
    print("You can press Enter to use the default values shown in brackets.")
    print()
    
    # Collect all configuration
    config = {}
    
    # Database configuration
    config.update(setup_database_config())
    
    # Redis configuration
    config.update(setup_redis_config())
    
    # Email configuration
    config.update(setup_email_config())
    
    # Slack configuration
    config.update(setup_slack_config())
    
    # Security configuration
    config.update(setup_security_config())
    
    # Monitoring configuration
    config.update(setup_monitoring_config())
    
    # Logging configuration
    config.update(setup_logging_config())
    
    # Validate configuration
    print("\n🔍 Validating configuration...")
    issues = validate_config(config)
    
    if issues:
        print("❌ Configuration issues found:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nPlease fix these issues and run the setup again.")
        return False
    
    print("✅ Configuration validation passed!")
    
    # Write configuration file
    write_env_file(config)
    
    print("\n🎉 Configuration setup completed!")
    print("\n📚 Next steps:")
    print("   1. Review the generated .env file")
    print("   2. Start the services: ./start.sh")
    print("   3. Test the API: curl http://localhost:8000/health")
    print("   4. Access the dashboard: http://localhost:8000/dashboard")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Configuration setup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during configuration setup: {e}")
        sys.exit(1) 