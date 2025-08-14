#!/usr/bin/env python3
"""
Advanced Workflow Example for Abena IHR Security Module

This example demonstrates advanced scenarios including:
- Complex data processing workflows
- Multi-step compliance validation
- Advanced audit logging
- Error recovery and retry logic
- Performance monitoring
- Security best practices
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from abena_ihr_security.sdk import (
    AbenaSecurityClient,
    AbenaSecurityConfig,
    SecurityContext,
    AuditEvent,
    AuditAction,
    AuditResourceType,
)
from abena_ihr_security.sdk.exceptions import (
    AbenaSecurityException,
    ComplianceException,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of data processing operation"""

    success: bool
    data: Dict[str, Any]
    compliance_status: str
    security_flags: List[str]
    processing_time: float
    audit_event_id: Optional[str] = None
    error_message: Optional[str] = None


class AdvancedSecurityWorkflow:
    """Advanced security workflow manager"""

    def __init__(self, config: AbenaSecurityConfig):
        self.config = config
        self.client: Optional[AbenaSecurityClient] = None
        self.processing_stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "total_processing_time": 0.0,
            "compliance_violations": 0,
        }

    async def initialize(self):
        """Initialize the workflow manager"""
        logger.info("Initializing Advanced Security Workflow...")

        self.client = AbenaSecurityClient(self.config)
        await self.client.initialize()

        logger.info("✓ Advanced Security Workflow initialized")

    async def close(self):
        """Close the workflow manager"""
        if self.client:
            await self.client.close()
        logger.info("✓ Advanced Security Workflow closed")

    async def process_patient_batch(
        self,
        patients: List[Dict[str, Any]],
        user_context: SecurityContext,
        operation: str = "read",
    ) -> List[ProcessingResult]:
        """Process a batch of patients with comprehensive security"""
        logger.info(f"Processing batch of {len(patients)} patients...")

        results = []
        batch_start_time = time.time()

        for i, patient in enumerate(patients):
            try:
                logger.info(
                    f"Processing patient {i+1}/{len(patients)}:"
                    f"{patient.get('id', 'unknown')}"
                )

                # Step 1: Pre-processing validation
                validation_result = await self._validate_patient_data(patient)
                if not validation_result.success:
                    results.append(validation_result)
                    continue

                # Step 2: Apply business rules
                rules_result = await self._apply_business_rules(patient, "validation")
                if not rules_result.success:
                    results.append(rules_result)
                    continue

                # Step 3: Process with security
                security_result = await self._process_with_security(
                    patient, user_context, operation
                )
                if not security_result.success:
                    results.append(security_result)
                    continue

                # Step 4: Apply data masking based on user role
                masking_result = await self._apply_role_based_masking(
                    security_result.data, user_context.user_role
                )

                # Step 5: Log comprehensive audit event
                audit_result = await self._log_comprehensive_audit(
                    patient, user_context, operation, masking_result
                )

                # Step 6: Validate compliance
                compliance_result = await self._validate_compliance(user_context)

                # Create final result
                final_result = ProcessingResult(
                    success=True,
                    data=masking_result.data,
                    compliance_status=compliance_result.compliance_status,
                    security_flags=(masking_result.security_flags + ["audit_logged"]),
                    processing_time=time.time() - batch_start_time,
                    audit_event_id=audit_result.audit_event_id,
                )

                results.append(final_result)
                self.processing_stats["successful_operations"] += 1

            except Exception as e:
                logger.error(
                    f"Error processing patient " f"{patient.get('id', 'unknown')}: {e}"
                )

                error_result = ProcessingResult(
                    success=False,
                    data=patient,
                    compliance_status="error",
                    security_flags=["error"],
                    processing_time=time.time() - batch_start_time,
                    error_message=str(e),
                )

                results.append(error_result)
                self.processing_stats["failed_operations"] += 1

        self.processing_stats["total_operations"] += len(patients)
        self.processing_stats["total_processing_time"] += time.time() - batch_start_time

        logger.info(f"✓ Batch processing completed: {len(results)} results")
        return results

    async def _validate_patient_data(self, patient: Dict[str, Any]) -> ProcessingResult:
        """Validate patient data before processing"""
        try:
            # Check required fields
            required_fields = ["id", "name", "date_of_birth"]
            missing_fields = [
                field for field in required_fields if field not in patient
            ]

            if missing_fields:
                return ProcessingResult(
                    success=False,
                    data=patient,
                    compliance_status="validation_failed",
                    security_flags=["missing_required_fields"],
                    processing_time=0.0,
                    error_message=f"Missing required fields: {missing_fields}",
                )

            # Validate data formats
            if not self._is_valid_date(patient.get("date_of_birth")):
                return ProcessingResult(
                    success=False,
                    data=patient,
                    compliance_status="validation_failed",
                    security_flags=["invalid_date_format"],
                    processing_time=0.0,
                    error_message="Invalid date of birth format",
                )

            return ProcessingResult(
                success=True,
                data=patient,
                compliance_status="validated",
                security_flags=["data_validated"],
                processing_time=0.0,
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                data=patient,
                compliance_status="validation_error",
                security_flags=["validation_error"],
                processing_time=0.0,
                error_message=str(e),
            )

    async def _apply_business_rules(
        self, patient: Dict[str, Any], rule_type: str
    ) -> ProcessingResult:
        """Apply business rules to patient data"""
        if not self.client:
            raise AbenaSecurityException("Client not initialized")
        try:
            rules_result = await self.client.apply_business_rules(patient, rule_type)

            if rules_result.get("errors"):
                return ProcessingResult(
                    success=False,
                    data=patient,
                    compliance_status="rules_violation",
                    security_flags=["business_rules_failed"],
                    processing_time=0.0,
                    error_message=(
                        f"Business rules violations: {rules_result['errors']}"
                    ),
                )

            return ProcessingResult(
                success=True,
                data=rules_result.get("processed_data", patient),
                compliance_status="rules_compliant",
                security_flags=["business_rules_applied"],
                processing_time=0.0,
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                data=patient,
                compliance_status="rules_error",
                security_flags=["rules_error"],
                processing_time=0.0,
                error_message=str(e),
            )

    async def _process_with_security(
        self, patient: Dict[str, Any], user_context: SecurityContext, operation: str
    ) -> ProcessingResult:
        """Process patient data with security measures"""
        if not self.client:
            raise AbenaSecurityException("Client not initialized")
        try:
            result = await self.client.process_data_with_security(
                patient, user_context, operation
            )

            return ProcessingResult(
                success=True,
                data=result.get("processed_data", patient),
                compliance_status=result.get("compliance_status", "unknown"),
                security_flags=result.get("security_flags", []),
                processing_time=result.get("processing_time", 0.0),
                audit_event_id=result.get("audit_event_id"),
            )

        except ComplianceException as e:
            self.processing_stats["compliance_violations"] += 1
            return ProcessingResult(
                success=False,
                data=patient,
                compliance_status="non_compliant",
                security_flags=["compliance_violation"],
                processing_time=0.0,
                error_message=str(e),
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                data=patient,
                compliance_status="security_error",
                security_flags=["security_error"],
                processing_time=0.0,
                error_message=str(e),
            )

    async def _apply_role_based_masking(
        self, patient: Dict[str, Any], user_role: str
    ) -> ProcessingResult:
        """Apply role-based data masking"""
        if not self.client:
            raise AbenaSecurityException("Client not initialized")
        try:
            # Define masking contexts based on user role
            masking_contexts = {
                "nurse": "nurse",
                "doctor": "physician",
                "technician": "technician",
                "admin": "administrator",
                "default": "default",
            }

            context = masking_contexts.get(user_role, "default")
            masked_data = await self.client.mask_data(patient, context)

            return ProcessingResult(
                success=True,
                data=masked_data,
                compliance_status="masked",
                security_flags=["data_masked"],
                processing_time=0.0,
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                data=patient,
                compliance_status="masking_error",
                security_flags=["masking_error"],
                processing_time=0.0,
                error_message=str(e),
            )

    async def _log_comprehensive_audit(
        self,
        patient: Dict[str, Any],
        user_context: SecurityContext,
        operation: str,
        processing_result: ProcessingResult,
    ) -> ProcessingResult:
        """Log comprehensive audit event"""
        if not self.client:
            raise AbenaSecurityException("Client not initialized")
        try:
            audit_event = AuditEvent(
                event_id=(f"audit_{int(time.time())}_{patient.get('id', 'unknown')}"),
                timestamp=datetime.now(timezone.utc),
                user_id=user_context.user_id,
                user_role=user_context.user_role,
                action=getattr(AuditAction, operation.upper(), AuditAction.READ),
                resource_type=AuditResourceType.PATIENT,
                resource_id=patient.get("id"),
                source_ip=user_context.source_ip,
                user_agent=user_context.user_agent,
                request_data={
                    "patient_id": patient.get("id"),
                    "operation": operation,
                },
                response_data={
                    "status": ("success" if processing_result.success else "failure"),
                    "compliance_status": processing_result.compliance_status,
                    "security_flags": processing_result.security_flags,
                },
                status="success" if processing_result.success else "failure",
                processing_time=processing_result.processing_time,
                compliance_flags=processing_result.security_flags,
                error_message=processing_result.error_message,
            )

            event_id = await self.client.log_audit_event(audit_event)

            return ProcessingResult(
                success=True,
                data=processing_result.data,
                compliance_status=processing_result.compliance_status,
                security_flags=processing_result.security_flags,
                processing_time=processing_result.processing_time,
                audit_event_id=event_id,
            )

        except Exception as e:
            logger.error(f"Audit logging failed: {e}")
            return processing_result

    async def _validate_compliance(
        self, user_context: SecurityContext
    ) -> ProcessingResult:
        """Validate compliance for the operation"""
        if not self.client:
            raise AbenaSecurityException("Client not initialized")
        try:
            compliance_result = await self.client.validate_compliance(user_context)

            return ProcessingResult(
                success=True,
                data={},
                compliance_status=(
                    "compliant" if compliance_result.compliant else "non_compliant"
                ),
                security_flags=["compliance_validated"],
                processing_time=0.0,
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                data={},
                compliance_status="compliance_error",
                security_flags=["compliance_error"],
                processing_time=0.0,
                error_message=str(e),
            )

    def _is_valid_date(self, date_str: Optional[str]) -> bool:
        """Validate date string format"""
        if not date_str:
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except (ValueError, TypeError):
            return False

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = self.processing_stats.copy()
        if stats["total_operations"] > 0:
            stats["success_rate"] = (
                stats["successful_operations"] / stats["total_operations"]
            ) * 100
            stats["average_processing_time"] = (
                stats["total_processing_time"] / stats["total_operations"]
            )
        else:
            stats["success_rate"] = 0.0
            stats["average_processing_time"] = 0.0

        return stats


async def main():
    """Main advanced workflow example"""
    logger.info("Starting Advanced Security Workflow Example")

    # Initialize configuration
    config = AbenaSecurityConfig(
        database_url="sqlite:///advanced_example.db",
        redis_url="redis://localhost:6379",
        master_key_path="/tmp/advanced_master.key",
        debug_mode=True,
        test_mode=True,
    )

    # Create workflow manager
    workflow = AdvancedSecurityWorkflow(config)

    try:
        # Initialize workflow
        await workflow.initialize()

        # Create test patient data
        patients = [
            {
                "id": "patient_001",
                "name": "John Doe",
                "ssn": "123-45-6789",
                "date_of_birth": "1985-03-15",
                "phone": "555-123-4567",
                "email": "john.doe@example.com",
                "medications": ["Aspirin", "Lisinopril"],
                "allergies": ["Penicillin"],
            },
            {
                "id": "patient_002",
                "name": "Jane Smith",
                "ssn": "987-65-4321",
                "date_of_birth": "1990-07-22",
                "phone": "555-987-6543",
                "email": "jane.smith@example.com",
                "medications": ["Metformin"],
                "allergies": ["Latex"],
            },
            {
                "id": "patient_003",
                "name": "Bob Johnson",
                "ssn": "456-78-9012",
                "date_of_birth": "1975-11-08",
                "phone": "555-456-7890",
                "email": "bob.johnson@example.com",
                "medications": ["Atorvastatin", "Amlodipine"],
                "allergies": ["Sulfa"],
            },
        ]

        # Create different user contexts for testing
        user_contexts = [
            SecurityContext(
                user_id="nurse_001",
                user_role="nurse",
                action="read",
                resource_type="patient",
                source_ip="192.168.1.100",
                permissions=["read_patient"],
            ),
            SecurityContext(
                user_id="doctor_001",
                user_role="doctor",
                action="read",
                resource_type="patient",
                source_ip="192.168.1.101",
                permissions=["read_patient", "write_patient"],
            ),
            SecurityContext(
                user_id="admin_001",
                user_role="admin",
                action="read",
                resource_type="patient",
                source_ip="192.168.1.102",
                permissions=[
                    "read_patient",
                    "write_patient",
                    "delete_patient",
                ],
            ),
        ]

        # Process patients with different user contexts
        for i, user_context in enumerate(user_contexts):
            logger.info(f"\n--- Processing with {user_context.user_role} context ---")

            results = await workflow.process_patient_batch(
                patients, user_context, "read"
            )

            # Analyze results
            successful = [r for r in results if r.success]
            failed = [r for r in results if not r.success]

            logger.info(f"Results for {user_context.user_role}:")
            logger.info(f"  - Successful: {len(successful)}")
            logger.info(f"  - Failed: {len(failed)}")

            for j, result in enumerate(results):
                status = "✓" if result.success else "✗"
                logger.info(f"  {status} Patient {j+1}: {result.compliance_status}")
                if result.error_message:
                    logger.info(f"    Error: {result.error_message}")

        # Get final statistics
        stats = workflow.get_processing_stats()
        logger.info("--- Final Statistics ---")
        logger.info(f"Total operations: {stats['total_operations']}")
        logger.info(f"Successful operations: {stats['successful_operations']}")
        logger.info(f"Failed operations: {stats['failed_operations']}")
        logger.info(f"Success rate: {stats['success_rate']:.2f}%")
        logger.info(f"Average processing time: {stats['average_processing_time']:.3f}s")
        logger.info(f"Compliance violations: {stats['compliance_violations']}")

        logger.info("✓ Advanced workflow completed successfully!")

    except Exception as e:
        logger.error(f"✗ Advanced workflow failed: {e}")
        raise

    finally:
        await workflow.close()


def print_separator():
    """Print a separator line"""
    print("=" * 80)


if __name__ == "__main__":
    print_separator()
    print("ABENA IHR SECURITY MODULE - ADVANCED WORKFLOW EXAMPLE")
    print_separator()

    try:
        asyncio.run(main())
        print_separator()
        print("✓ Advanced workflow completed successfully!")
        print_separator()
    except Exception as e:
        print_separator()
        print(f"✗ Advanced workflow failed: {e}")
        print_separator()
        exit(1)
