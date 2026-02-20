"""
Business Rules Engine

Provides business rules processing capabilities
for data validation and transformation.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class BusinessRulesEngine:
    """Service for processing business rules"""

    def __init__(self):
        """Initialize business rules engine"""
        logger.info("BusinessRulesEngine initialized")

        # Mock business rules
        self.rules = {
            "validation": [
                {
                    "rule_id": "patient_validation_001",
                    "rule_name": "Patient Data Validation",
                    "description": "Validates required patient fields",
                    "conditions": [
                        {"field": "id", "operator": "not_empty"},
                        {"field": "name", "operator": "not_empty"},
                        {"field": "date_of_birth", "operator": "valid_date"},
                    ],
                    "actions": [
                        {
                            "action": "log_violation",
                            "message": "Missing required patient fields",
                        }
                    ],
                },
                {
                    "rule_id": "data_validation_002",
                    "rule_name": "Data Format Validation",
                    "description": "Validates data format requirements",
                    "conditions": [
                        {"field": "ssn", "operator": "valid_ssn_format"},
                        {"field": "phone", "operator": "valid_phone_format"},
                    ],
                    "actions": [
                        {
                            "action": "log_violation",
                            "message": "Invalid data format",
                        }
                    ],
                },
            ],
            "transformation": [
                {
                    "rule_id": "data_masking_001",
                    "rule_name": "Data Masking Rule",
                    "description": "Applies masking to sensitive fields",
                    "conditions": [
                        {"field": "ssn", "operator": "contains_sensitive_data"}
                    ],
                    "actions": [
                        {
                            "action": "mask_field",
                            "field": "ssn",
                            "method": "redaction",
                        }
                    ],
                },
                {
                    "rule_id": "format_standardization_001",
                    "rule_name": "Format Standardization",
                    "description": "Standardizes data formats",
                    "conditions": [
                        {
                            "field": "phone",
                            "operator": "needs_formatting",
                        }
                    ],
                    "actions": [
                        {
                            "action": "standardize_format",
                            "field": "phone",
                            "format": "XXX-XXX-XXXX",
                        }
                    ],
                },
            ],
            "compliance": [
                {
                    "rule_id": "hipaa_compliance_001",
                    "rule_name": "HIPAA Compliance Check",
                    "description": "Validates HIPAA compliance requirements",
                    "conditions": [
                        {"field": "encryption", "operator": "is_enabled"},
                        {"field": "audit_logging", "operator": "is_enabled"},
                    ],
                    "actions": [
                        {
                            "action": "log_compliance_violation",
                            "message": "HIPAA compliance violation",
                        }
                    ],
                }
            ],
        }

    def apply_rules(
        self, data: Dict[str, Any], rule_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply business rules to data

        Args:
            data: Data to process
            rule_type: Type of rules to apply (validation,
            transformation, compliance)

        Returns:
            Processing result with applied rules and actions
        """
        try:
            result: Dict[str, Any] = {
                "processed_data": data.copy(),
                "rules_applied": [],
                "actions_executed": [],
                "errors": [],
            }

            # Apply rules based on type
            if rule_type and rule_type in self.rules:
                rules_to_apply = self.rules[rule_type]
            else:
                # Apply all rules if no specific type
                rules_to_apply = []
                for rule_list in self.rules.values():
                    rules_to_apply.extend(rule_list)

            for rule in rules_to_apply:
                try:
                    # Check conditions
                    conditions_met = self._check_conditions(
                        data, rule["conditions"]
                    )

                    if conditions_met:
                        # Execute actions
                        actions_result = self._execute_actions(
                            data, rule["actions"]
                        )

                        result["rules_applied"].append(rule["rule_id"])
                        result["actions_executed"].extend(
                            actions_result.get("executed_actions", [])
                        )

                        if actions_result.get("errors"):
                            result["errors"].extend(actions_result["errors"])

                except Exception as e:
                    result["errors"].append(
                        f"Rule {rule['rule_id']} failed: {str(e)}"
                    )

            logger.info(
                f"Business rules applied: "
                f"{len(result['rules_applied'])} rules"
            )
            return result

        except Exception as e:
            logger.error(f"Business rules processing failed: {str(e)}")
            raise

    def _check_conditions(
        self, data: Dict[str, Any], conditions: List[Dict[str, Any]]
    ) -> bool:
        """Check if conditions are met"""
        for condition in conditions:
            field = condition["field"]
            operator = condition["operator"]

            if field not in data:
                return False

            field_value = data[field]

            if operator == "not_empty":
                if not field_value or str(field_value).strip() == "":
                    return False
            elif operator == "valid_date":
                # Mock date validation
                if not self._is_valid_date(field_value):
                    return False
            elif operator == "valid_ssn_format":
                # Mock SSN validation
                if not self._is_valid_ssn(field_value):
                    return False
            elif operator == "valid_phone_format":
                # Mock phone validation
                if not self._is_valid_phone(field_value):
                    return False
            elif operator == "contains_sensitive_data":
                # Mock sensitive data check
                if self._contains_sensitive_data(field_value):
                    return True
                else:
                    return False
            elif operator == "needs_formatting":
                # Mock formatting check
                if self._needs_formatting(field_value):
                    return True
                else:
                    return False
            elif operator == "is_enabled":
                # Mock enabled check
                if not self._is_enabled(field_value):
                    return False

        return True

    def _execute_actions(
        self, data: Dict[str, Any], actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute actions based on rules"""
        result: Dict[str, Any] = {"executed_actions": [], "errors": []}

        for action in actions:
            try:
                action_type = action["action"]

                if action_type == "log_violation":
                    result["executed_actions"].append(
                        f"Logged violation: {action.get('message', '')}"
                    )

                elif action_type == "mask_field":
                    field = action["field"]
                    method = action.get("method", "redaction")
                    if field in data:
                        data[field] = self._apply_masking(data[field], method)
                        result["executed_actions"].append(
                            f"Masked field: {field}"
                        )

                elif action_type == "standardize_format":
                    field = action["field"]
                    format_spec = action.get("format", "")
                    if field in data:
                        data[field] = self._standardize_format(
                            data[field], format_spec
                        )
                        result["executed_actions"].append(
                            f"Standardized field: {field}"
                        )

                elif action_type == "log_compliance_violation":
                    result["executed_actions"].append(
                        f"Logged compliance violation: "
                        f"{action.get('message', '')}"
                    )

            except Exception as e:
                result["errors"].append(f"Action execution failed: {str(e)}")

        return result

    def _is_valid_date(self, date_str: str) -> bool:
        """Mock date validation"""
        try:
            from datetime import datetime

            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except (ValueError, TypeError):
            return False

    def _is_valid_ssn(self, ssn: str) -> bool:
        """Mock SSN validation"""
        if not ssn:
            return False
        # Simple format check: XXX-XX-XXXX
        import re

        return bool(re.match(r"^\d{3}-\d{2}-\d{4}$", ssn))

    def _is_valid_phone(self, phone: str) -> bool:
        """Mock phone validation"""
        if not phone:
            return False
        # Simple format check: XXX-XXX-XXXX
        import re

        return bool(re.match(r"^\d{3}-\d{3}-\d{4}$", phone))

    def _contains_sensitive_data(self, value: str) -> bool:
        """Mock sensitive data check"""
        if not value:
            return False
        # Check for SSN pattern
        import re

        return bool(re.search(r"\d{3}-\d{2}-\d{4}", value))

    def _needs_formatting(self, value: str) -> bool:
        """Mock formatting check"""
        if not value:
            return False
        # Check if phone number needs formatting
        import re

        return bool(re.match(r"^\d{10}$", value.replace("-", "")))

    def _is_enabled(self, value: Any) -> bool:
        """Mock enabled check"""
        return bool(value)

    def _apply_masking(self, value: str, method: str) -> str:
        """Apply masking to value"""
        if method == "redaction":
            if len(value) > 4:
                return "***-" + value[-4:]
            else:
                return "***"
        else:
            return "***"

    def _standardize_format(self, value: str, format_spec: str) -> str:
        """Standardize format of value"""
        if not value:
            return value

        # Remove non-digits
        digits = "".join(filter(str.isdigit, value))

        if len(digits) == 10:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        else:
            return value
