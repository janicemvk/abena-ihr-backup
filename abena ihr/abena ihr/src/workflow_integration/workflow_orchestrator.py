"""
Workflow Orchestrator

This module provides workflow orchestration and task management
capabilities for the Abena IHR Clinical Outcomes Management System.
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import asyncio
import json
from dataclasses import dataclass, field
from enum import Enum

from ..core.data_models import WorkflowTask, WorkflowStatus, SystemEvent
from ..core.utils import generate_uuid, safe_json_dumps

# Configure logging
logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Enumeration of task priorities."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class WorkflowType(Enum):
    """Enumeration of workflow types."""
    PATIENT_ADMISSION = "patient_admission"
    CLINICAL_ASSESSMENT = "clinical_assessment"
    TREATMENT_PLANNING = "treatment_planning"
    OUTCOME_EVALUATION = "outcome_evaluation"
    DISCHARGE_PLANNING = "discharge_planning"
    PREDICTIVE_ANALYSIS = "predictive_analysis"
    DATA_COLLECTION = "data_collection"


@dataclass
class WorkflowDefinition:
    """Definition of a workflow."""
    id: str = field(default_factory=generate_uuid)
    name: str = ""
    description: str = ""
    workflow_type: WorkflowType = WorkflowType.CLINICAL_ASSESSMENT
    steps: List[Dict[str, Any]] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class WorkflowInstance:
    """Instance of a workflow execution."""
    id: str = field(default_factory=generate_uuid)
    workflow_definition_id: str = ""
    patient_id: Optional[str] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: int = 0
    context: Dict[str, Any] = field(default_factory=dict)
    tasks: List[WorkflowTask] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = datetime.now()


class WorkflowOrchestrator:
    """Main workflow orchestrator for managing healthcare workflows."""
    
    def __init__(self):
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.workflow_instances: Dict[str, WorkflowInstance] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self._load_workflow_definitions()
    
    def _load_workflow_definitions(self):
        """Load predefined workflow definitions."""
        # Patient Admission Workflow
        admission_workflow = WorkflowDefinition(
            name="Patient Admission",
            description="Standard workflow for admitting new patients",
            workflow_type=WorkflowType.PATIENT_ADMISSION,
            steps=[
                {
                    "id": "registration",
                    "name": "Patient Registration",
                    "description": "Register patient in the system",
                    "handler": "register_patient",
                    "required": True,
                    "estimated_duration": 15
                },
                {
                    "id": "initial_assessment",
                    "name": "Initial Assessment",
                    "description": "Perform initial clinical assessment",
                    "handler": "perform_initial_assessment",
                    "required": True,
                    "estimated_duration": 30
                },
                {
                    "id": "data_collection",
                    "name": "Data Collection",
                    "description": "Collect baseline clinical data",
                    "handler": "collect_baseline_data",
                    "required": True,
                    "estimated_duration": 20
                },
                {
                    "id": "prediction_analysis",
                    "name": "Prediction Analysis",
                    "description": "Run predictive models for outcomes",
                    "handler": "run_prediction_analysis",
                    "required": False,
                    "estimated_duration": 10
                }
            ],
            triggers=["patient_admitted"]
        )
        
        # Clinical Assessment Workflow
        assessment_workflow = WorkflowDefinition(
            name="Clinical Assessment",
            description="Comprehensive clinical assessment workflow",
            workflow_type=WorkflowType.CLINICAL_ASSESSMENT,
            steps=[
                {
                    "id": "vital_signs",
                    "name": "Vital Signs Assessment",
                    "description": "Record and assess vital signs",
                    "handler": "assess_vital_signs",
                    "required": True,
                    "estimated_duration": 10
                },
                {
                    "id": "physical_exam",
                    "name": "Physical Examination",
                    "description": "Perform physical examination",
                    "handler": "perform_physical_exam",
                    "required": True,
                    "estimated_duration": 45
                },
                {
                    "id": "lab_orders",
                    "name": "Laboratory Orders",
                    "description": "Order necessary laboratory tests",
                    "handler": "order_laboratory_tests",
                    "required": False,
                    "estimated_duration": 15
                },
                {
                    "id": "outcome_evaluation",
                    "name": "Outcome Evaluation",
                    "description": "Evaluate clinical outcomes",
                    "handler": "evaluate_outcomes",
                    "required": True,
                    "estimated_duration": 20
                }
            ],
            triggers=["assessment_required", "vital_signs_updated"]
        )
        
        self.workflow_definitions[admission_workflow.id] = admission_workflow
        self.workflow_definitions[assessment_workflow.id] = assessment_workflow
        
        logger.info(f"Loaded {len(self.workflow_definitions)} workflow definitions")
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """Register a task handler function."""
        self.task_handlers[task_type] = handler
        logger.info(f"Registered task handler: {task_type}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler function."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered event handler for: {event_type}")
    
    def start_workflow(
        self,
        workflow_definition_id: str,
        patient_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[WorkflowInstance]:
        """
        Start a new workflow instance.
        
        Args:
            workflow_definition_id: ID of the workflow definition
            patient_id: Optional patient ID
            context: Optional context data
            
        Returns:
            Workflow instance or None if failed
        """
        try:
            if workflow_definition_id not in self.workflow_definitions:
                logger.error(f"Workflow definition not found: {workflow_definition_id}")
                return None
            
            workflow_def = self.workflow_definitions[workflow_definition_id]
            
            # Create workflow instance
            instance = WorkflowInstance(
                workflow_definition_id=workflow_definition_id,
                patient_id=patient_id,
                context=context or {},
                status=WorkflowStatus.IN_PROGRESS
            )
            
            # Create initial tasks
            if workflow_def.steps:
                first_step = workflow_def.steps[0]
                task = WorkflowTask(
                    task_name=first_step["name"],
                    description=first_step["description"],
                    status=WorkflowStatus.PENDING,
                    patient_id=patient_id,
                    priority=TaskPriority.MEDIUM.value
                )
                instance.tasks.append(task)
            
            # Store instance
            self.workflow_instances[instance.id] = instance
            
            # Trigger event
            self._trigger_event("workflow_started", {
                "workflow_instance_id": instance.id,
                "workflow_definition_id": workflow_definition_id,
                "patient_id": patient_id
            })
            
            logger.info(f"Started workflow instance: {instance.id}")
            return instance
            
        except Exception as e:
            logger.error(f"Error starting workflow: {e}")
            return None
    
    def execute_task(self, task_id: str, user_id: Optional[str] = None) -> bool:
        """
        Execute a specific task.
        
        Args:
            task_id: ID of the task to execute
            user_id: Optional user ID executing the task
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find task in workflow instances
            task = None
            workflow_instance = None
            
            for instance in self.workflow_instances.values():
                for t in instance.tasks:
                    if t.id == task_id:
                        task = t
                        workflow_instance = instance
                        break
                if task:
                    break
            
            if not task or not workflow_instance:
                logger.error(f"Task not found: {task_id}")
                return False
            
            # Update task status
            task.status = WorkflowStatus.IN_PROGRESS
            task.assigned_to = user_id
            task.updated_at = datetime.now()
            
            # Execute task handler if available
            workflow_def = self.workflow_definitions[workflow_instance.workflow_definition_id]
            current_step = workflow_def.steps[workflow_instance.current_step]
            
            handler_name = current_step.get("handler")
            if handler_name and handler_name in self.task_handlers:
                try:
                    result = self.task_handlers[handler_name](
                        task_id=task_id,
                        patient_id=workflow_instance.patient_id,
                        context=workflow_instance.context
                    )
                    
                    # Update task based on result
                    if result:
                        task.status = WorkflowStatus.COMPLETED
                        task.completed_at = datetime.now()
                        
                        # Move to next step
                        self._advance_workflow(workflow_instance)
                    else:
                        task.status = WorkflowStatus.FAILED
                        
                except Exception as e:
                    logger.error(f"Error executing task handler {handler_name}: {e}")
                    task.status = WorkflowStatus.FAILED
            else:
                # No handler, mark as completed
                task.status = WorkflowStatus.COMPLETED
                task.completed_at = datetime.now()
                self._advance_workflow(workflow_instance)
            
            task.updated_at = datetime.now()
            workflow_instance.updated_at = datetime.now()
            
            # Trigger event
            self._trigger_event("task_completed", {
                "task_id": task_id,
                "workflow_instance_id": workflow_instance.id,
                "status": task.status.value
            })
            
            logger.info(f"Executed task: {task_id}, status: {task.status}")
            return True
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            return False
    
    def _advance_workflow(self, workflow_instance: WorkflowInstance):
        """Advance workflow to next step."""
        try:
            workflow_def = self.workflow_definitions[workflow_instance.workflow_definition_id]
            
            # Check if workflow is complete
            if workflow_instance.current_step >= len(workflow_def.steps) - 1:
                workflow_instance.status = WorkflowStatus.COMPLETED
                workflow_instance.completed_at = datetime.now()
                
                # Trigger workflow completion event
                self._trigger_event("workflow_completed", {
                    "workflow_instance_id": workflow_instance.id,
                    "patient_id": workflow_instance.patient_id
                })
                
                logger.info(f"Workflow completed: {workflow_instance.id}")
                return
            
            # Move to next step
            workflow_instance.current_step += 1
            next_step = workflow_def.steps[workflow_instance.current_step]
            
            # Create task for next step
            task = WorkflowTask(
                task_name=next_step["name"],
                description=next_step["description"],
                status=WorkflowStatus.PENDING,
                patient_id=workflow_instance.patient_id,
                priority=TaskPriority.MEDIUM.value
            )
            workflow_instance.tasks.append(task)
            
            logger.info(f"Advanced workflow {workflow_instance.id} to step {workflow_instance.current_step}")
            
        except Exception as e:
            logger.error(f"Error advancing workflow: {e}")
    
    def _trigger_event(self, event_type: str, event_data: Dict[str, Any]):
        """Trigger an event and call registered handlers."""
        try:
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        handler(event_data)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event_type}: {e}")
        except Exception as e:
            logger.error(f"Error triggering event {event_type}: {e}")
    
    def get_workflow_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Get workflow instance by ID."""
        return self.workflow_instances.get(instance_id)
    
    def get_patient_workflows(self, patient_id: str) -> List[WorkflowInstance]:
        """Get all workflows for a patient."""
        return [
            instance for instance in self.workflow_instances.values()
            if instance.patient_id == patient_id
        ]
    
    def get_pending_tasks(self, user_id: Optional[str] = None) -> List[WorkflowTask]:
        """Get pending tasks, optionally filtered by user."""
        tasks = []
        for instance in self.workflow_instances.values():
            for task in instance.tasks:
                if task.status == WorkflowStatus.PENDING:
                    if user_id is None or task.assigned_to == user_id:
                        tasks.append(task)
        return tasks
    
    def cancel_workflow(self, instance_id: str) -> bool:
        """
        Cancel a workflow instance.
        
        Args:
            instance_id: ID of the workflow instance to cancel
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if instance_id in self.workflow_instances:
                instance = self.workflow_instances[instance_id]
                instance.status = WorkflowStatus.CANCELLED
                instance.completed_at = datetime.now()
                
                # Cancel all pending tasks
                for task in instance.tasks:
                    if task.status == WorkflowStatus.PENDING:
                        task.status = WorkflowStatus.CANCELLED
                        task.completed_at = datetime.now()
                
                # Trigger event
                self._trigger_event("workflow_cancelled", {
                    "workflow_instance_id": instance_id,
                    "patient_id": instance.patient_id
                })
                
                logger.info(f"Cancelled workflow instance: {instance_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cancelling workflow: {e}")
            return False

    # Application Layer - Business logic for clinical workflows
    def process_clinical_data(self, patient_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process clinical data for a patient.
        
        Args:
            patient_id: ID of the patient
            data: Clinical data to process
            
        Returns:
            Processed clinical data with workflow status
        """
        try:
            # Validate patient data
            if not patient_id or not data:
                raise ValueError("Invalid patient_id or data")
            
            # Create workflow context
            context = {
                "patient_id": patient_id,
                "clinical_data": data,
                "processing_timestamp": datetime.now().isoformat()
            }
            
            # Determine workflow type based on data
            workflow_type = self._determine_workflow_type(data)
            
            # Start appropriate workflow
            workflow_instance = self.start_workflow(
                workflow_definition_id=workflow_type,
                patient_id=patient_id,
                context=context
            )
            
            if workflow_instance:
                # Process the data through workflow steps
                result = self._execute_clinical_workflow(workflow_instance, data)
                
                return {
                    "status": "success",
                    "patient_id": patient_id,
                    "workflow_instance_id": workflow_instance.id,
                    "processed_data": result,
                    "workflow_status": workflow_instance.status.value
                }
            else:
                return {
                    "status": "error",
                    "patient_id": patient_id,
                    "error": "Failed to start workflow"
                }
                
        except Exception as e:
            logger.error(f"Error processing clinical data for patient {patient_id}: {e}")
            return {
                "status": "error",
                "patient_id": patient_id,
                "error": str(e)
            }
    
    def _determine_workflow_type(self, data: Dict[str, Any]) -> str:
        """Determine the appropriate workflow type based on clinical data."""
        if "vital_signs" in data:
            return "Clinical Assessment"
        elif "admission_date" in data:
            return "Patient Admission"
        elif "treatment_plan" in data:
            return "Treatment Planning"
        else:
            return "Clinical Assessment"  # Default
    
    def _execute_clinical_workflow(self, workflow_instance: WorkflowInstance, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute clinical workflow steps."""
        processed_data = data.copy()
        
        # Add workflow metadata
        processed_data["workflow_metadata"] = {
            "workflow_id": workflow_instance.id,
            "started_at": workflow_instance.started_at.isoformat(),
            "steps_completed": len([t for t in workflow_instance.tasks if t.status == WorkflowStatus.COMPLETED])
        }
        
        return processed_data


# Global workflow orchestrator instance
workflow_orchestrator = WorkflowOrchestrator()


def get_workflow_orchestrator() -> WorkflowOrchestrator:
    """Get the global workflow orchestrator instance."""
    return workflow_orchestrator 