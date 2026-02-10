#!/usr/bin/env python3
"""
Basic Usage Example for Abena IHR Security Module

This example demonstrates the core functionality of the security module,
including data processing, encryption, masking, and compliance validation.
"""

import asyncio
import logging
from datetime import datetime, timezone

from abena_ihr_security.sdk import (
    AbenaSecurityClient,
    AbenaSecurityConfig,
    SecurityContext,
    AuditEvent,
    AuditAction,
    AuditResourceType,
    AbenaSecurityException,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_patient_data():
    """Helper function to get sample patient data"""
    return {
        "id": "patient_001",
        "name": "John Doe",
        "ssn": "123-45-6789",
        "date_of_birth": "1985-03-15",
        "phone": "555-123-4567",
        "email": "john.doe@example.com",
        "address": "123 Main St, Anytown, USA",
        "medications": ["Aspirin", "Lisinopril"],
        "allergies": ["Penicillin"],
        "diagnoses": ["Hypertension", "Diabetes Type 2"],
    }


def get_security_context(user_role: str):
    """Helper function to get a sample security context"""
    return SecurityContext(
        user_id=f"user_{user_role}_001",
        user_role=user_role,
        action="read",
        resource_type="patient",
        resource_id="patient_001",
        source_ip="192.168.1.100",
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) " "AppleWebKit/537.36"),
        session_id="session_123",
        permissions=["read_patient", "write_observations"],
        requested_fields=["name", "date_of_birth", "medications", "allergies"],
    )


async def demonstrate_encryption(client: AbenaSecurityClient):
    """Demonstrate encryption and decryption"""
    print("\n--- Encrypting Data ---")
    sensitive_data = "SSN: 123-45-6789"
    key_id = "patient_data_key_001"
    encrypted_data = await client.encrypt_data(sensitive_data, key_id)
    print("Successfully encrypted data.")

    print("\n--- Decrypting Data ---")
    decrypted_data = await client.decrypt_data(encrypted_data, key_id)
    print(f"Successfully decrypted data: {decrypted_data.decode()}")
    assert decrypted_data.decode() == sensitive_data


async def demonstrate_data_masking(client: AbenaSecurityClient):
    """Demonstrate data masking for different user roles"""
    print("\n--- Demonstrating Data Masking ---")
    patient_data = get_patient_data()

    # Mask for a nurse
    print("\n1. Masking data for a 'nurse'...")
    nurse_masked_data = await client.mask_data(patient_data, "nurse")
    print("Masked data for nurse:")
    for key, value in nurse_masked_data.items():
        print(f"  {key}: {value}")

    # Mask for a researcher
    print("\n2. Masking data for a 'researcher'...")
    researcher_masked_data = await client.mask_data(patient_data, "researcher")
    print("Masked data for researcher:")
    for key, value in researcher_masked_data.items():
        print(f"  {key}: {value}")


async def demonstrate_audit_logging(client: AbenaSecurityClient):
    """Demonstrate logging an audit event"""
    print("\n--- Demonstrating Audit Logging ---")
    audit_event = AuditEvent(
        event_id="event-001",
        user_id="dr_smith_001",
        user_role="doctor",
        action=AuditAction.READ,
        resource_type=AuditResourceType.PATIENT,
        resource_id="patient_123",
        source_ip="192.168.1.50",
        status="success",
        timestamp=datetime.now(timezone.utc),
        details={"query_params": "include_meds=true"},
    )
    event_id = await client.log_audit_event(audit_event)
    print(f"Successfully logged audit event with ID: {event_id}")


async def demonstrate_compliance_check(client: AbenaSecurityClient):
    """Demonstrate a compliance check"""
    print("\n--- Demonstrating Compliance Check ---")
    security_context = get_security_context("nurse")
    compliance_result = await client.validate_compliance(security_context)

    if compliance_result.compliant:
        print("Compliance check passed.")
    else:
        print("Compliance check failed. Violations:")
        for violation in compliance_result.violations:
            print(f"  - {violation}")


async def demonstrate_configuration(client: AbenaSecurityClient):
    """Demonstrate configuration management"""
    print("\n--- Demonstrating Configuration Management ---")
    # Get configuration for an integration
    integration_name = "Epic_EMR"
    config = await client.get_configuration(integration_name)
    print(f"Configuration for '{integration_name}':")
    for key, value in config.items():
        print(f"  {key}: {value}")

    # Get configuration with secrets (requires appropriate permissions)
    try:
        secret_config = await client.get_configuration(
            integration_name, include_secrets=True
        )
        print(f"\nConfiguration for '{integration_name}' (with secrets):")
        for key, value in secret_config.items():
            print(f"  {key}: {value}")
    except AbenaSecurityException as e:
        print(f"\nCould not retrieve secrets: {e}")


async def demonstrate_business_rules(client: AbenaSecurityClient):
    """Demonstrate applying business rules"""
    print("\n--- Demonstrating Business Rules ---")
    patient_data = get_patient_data()

    # Apply validation rules
    print("\n1. Applying 'validation' rules...")
    validation_result = await client.apply_business_rules(patient_data, "validation")
    print("Validation result:")
    print(f"  Rules applied: {validation_result['rules_applied']}")
    print(f"  Errors: {validation_result['errors']}")

    # Apply transformation rules
    print("\n2. Applying 'transformation' rules...")
    transformation_result = await client.apply_business_rules(
        patient_data, "transformation"
    )
    print("Transformation result:")
    print(f"  Original name: {patient_data['name']}")
    print(f"  Transformed name: " f"{transformation_result['processed_data']['name']}")


async def main():
    """Main function to run all demonstrations"""
    logger.info("Starting Abena IHR Security Module Basic Usage Example")

    # 1. Initialize Configuration
    logger.info("1. Initializing configuration...")
    config = AbenaSecurityConfig(
        database_url="sqlite:///example.db",
        redis_url="redis://localhost:6379",
        master_key_path="/tmp/example_master.key",
        debug_mode=True,
        test_mode=True,
    )

    # 2. Create Security Client
    logger.info("2. Creating security client...")
    client = AbenaSecurityClient(config)

    try:
        # 3. Initialize Client
        logger.info("3. Initializing client...")
        await client.initialize()
        logger.info("✓ Client initialized successfully")

        # 4. Create Test Data
        logger.info("4. Creating test patient data...")
        patient_data = {
            "id": "patient_001",
            "name": "John Doe",
            "ssn": "123-45-6789",
            "date_of_birth": "1985-03-15",
            "phone": "555-123-4567",
            "email": "john.doe@example.com",
            "address": "123 Main St, Anytown, USA",
            "medications": ["Aspirin", "Lisinopril"],
            "allergies": ["Penicillin"],
            "diagnoses": ["Hypertension", "Diabetes Type 2"],
        }

        # 5. Create Security Context
        logger.info("5. Creating security context...")
        security_context = SecurityContext(
            user_id="nurse_001",
            user_role="nurse",
            action="read",
            resource_type="patient",
            resource_id="patient_001",
            source_ip="192.168.1.100",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " "AppleWebKit/537.36"
            ),
            session_id="session_123",
            permissions=["read_patient", "write_observations"],
            requested_fields=[
                "name",
                "date_of_birth",
                "medications",
                "allergies",
            ],
        )

        # 6. Process Data with Security
        logger.info("6. Processing data with security...")
        try:
            result = await client.process_data_with_security(
                patient_data, security_context, "read"
            )
            logger.info("✓ Data processed successfully")
            logger.info(
                f"  - Compliance status: "
                f"{result.get('compliance_status', 'unknown')}"
            )
            logger.info(f"  - Security flags: {result.get('security_flags', [])}")
            logger.info(f"  - Processing time: {result.get('processing_time', 0)}s")
        except Exception as e:
            logger.error(f"✗ Data processing failed: {e}")

        # 7. Test Encryption/Decryption
        logger.info("7. Testing encryption/decryption...")
        try:
            await demonstrate_encryption(client)
        except Exception as e:
            logger.error(f"✗ Encryption/decryption failed: {e}")

        # 8. Test Data Masking
        logger.info("8. Testing data masking...")
        try:
            await demonstrate_data_masking(client)
        except Exception as e:
            logger.error(f"✗ Data masking failed: {e}")

        # 9. Test Audit Logging
        logger.info("9. Testing audit logging...")
        try:
            await demonstrate_audit_logging(client)
        except Exception as e:
            logger.error(f"✗ Audit logging failed: {e}")

        # 10. Test Compliance Validation
        logger.info("10. Testing compliance validation...")
        try:
            await demonstrate_compliance_check(client)
        except Exception as e:
            logger.error(f"✗ Compliance validation failed: {e}")

        # 11. Test Configuration Management
        logger.info("11. Testing configuration management...")
        try:
            await demonstrate_configuration(client)
        except Exception as e:
            logger.error(f"✗ Configuration retrieval failed: {e}")

        # 12. Test Business Rules
        logger.info("12. Testing business rules...")
        try:
            await demonstrate_business_rules(client)
        except Exception as e:
            logger.error(f"✗ Business rules failed: {e}")

        # 13. Test Compliance Dashboard
        logger.info("13. Testing compliance dashboard...")
        try:
            dashboard = await client.get_compliance_dashboard()
            logger.info(
                "  - HIPAA Compliance Score: %s%%",
                dashboard.get("compliance_summary", {}).get(
                    "hipaa_compliance_score", "N/A"
                ),
            )

            logger.info(
                "  - Total Violations: %s",
                dashboard.get("compliance_summary", {}).get("total_violations", "N/A"),
            )

            logger.info(
                "  - Total Events: %s",
                dashboard.get("audit_summary", {}).get("total_events", "N/A"),
            )
        except Exception as e:
            logger.error(f"✗ Compliance dashboard failed: {e}")

        # 14. Test Error Handling
        logger.info("14. Testing error handling...")
        try:
            # Test with invalid key
            await client.encrypt_data("test_data", "nonexistent_key")
        except Exception as e:
            logger.info("✓ Error handling working correctly")
            logger.info(f"  - Expected error: {type(e).__name__}")
            logger.info(f"  - Error message: {str(e)}")

        logger.info("✓ All tests completed successfully!")

    except Exception as e:
        logger.error(f"✗ Example failed: {e}")
        raise

    finally:
        # 15. Cleanup
        logger.info("15. Cleaning up...")
        await client.close()
        logger.info("✓ Cleanup completed")


def print_separator():
    """Print a separator line"""
    print("=" * 80)


if __name__ == "__main__":
    print_separator()
    print("ABENA IHR SECURITY MODULE - BASIC USAGE EXAMPLE")
    print_separator()

    try:
        asyncio.run(main())
        print_separator()
        print("✓ Example completed successfully!")
        print_separator()
    except Exception as e:
        print_separator()
        print(f"✗ Example failed: {e}")
        print_separator()
        exit(1)
