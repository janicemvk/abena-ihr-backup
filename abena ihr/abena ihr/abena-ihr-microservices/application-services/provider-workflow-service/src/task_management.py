from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json

app = FastAPI(title="Provider Task Management Service")

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    OVERDUE = "overdue"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class TaskType(str, Enum):
    PATIENT_CARE = "patient_care"
    ADMINISTRATIVE = "administrative"
    CLINICAL_REVIEW = "clinical_review"
    DOCUMENTATION = "documentation"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    CONSULTATION = "consultation"
    LAB_REVIEW = "lab_review"
    IMAGING_REVIEW = "imaging_review"

class TaskCategory(str, Enum):
    CLINICAL = "clinical"
    ADMINISTRATIVE = "administrative"
    QUALITY_IMPROVEMENT = "quality_improvement"
    RESEARCH = "research"
    EDUCATION = "education"
    EMERGENCY = "emergency"

class Task(BaseModel):
    id: str
    title: str
    description: str
    task_type: TaskType
    category: TaskCategory
    priority: TaskPriority
    status: TaskStatus
    assigned_to: str
    created_by: str
    patient_id: Optional[str] = None
    due_date: datetime
    estimated_duration_minutes: int
    actual_duration_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tags: List[str] = []
    dependencies: List[str] = []  # Task IDs this task depends on
    subtasks: List[str] = []      # Sub-task IDs
    parent_task_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

class TaskComment(BaseModel):
    id: str
    task_id: str
    user_id: str
    comment: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}

class TaskAttachment(BaseModel):
    id: str
    task_id: str
    filename: str
    file_type: str
    file_size: int
    uploaded_by: str
    uploaded_at: datetime
    file_url: str
    metadata: Dict[str, Any] = {}

class TaskManagementService:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.comments: Dict[str, List[TaskComment]] = {}
        self.attachments: Dict[str, List[TaskAttachment]] = {}
        self.task_templates: Dict[str, Dict] = {}

    def create_task(self, title: str, description: str, task_type: TaskType,
                   category: TaskCategory, priority: TaskPriority, assigned_to: str,
                   created_by: str, due_date: datetime, estimated_duration_minutes: int,
                   patient_id: str = None, tags: List[str] = None,
                   dependencies: List[str] = None, parent_task_id: str = None) -> Task:
        task_id = str(uuid.uuid4())
        
        # Validate dependencies exist
        if dependencies:
            for dep_id in dependencies:
                if dep_id not in self.tasks:
                    raise ValueError(f"Dependency task {dep_id} not found")
        
        # Validate parent task exists
        if parent_task_id and parent_task_id not in self.tasks:
            raise ValueError(f"Parent task {parent_task_id} not found")
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            task_type=task_type,
            category=category,
            priority=priority,
            status=TaskStatus.PENDING,
            assigned_to=assigned_to,
            created_by=created_by,
            patient_id=patient_id,
            due_date=due_date,
            estimated_duration_minutes=estimated_duration_minutes,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=tags or [],
            dependencies=dependencies or [],
            parent_task_id=parent_task_id,
            metadata={}
        )
        
        self.tasks[task_id] = task
        self.comments[task_id] = []
        self.attachments[task_id] = []
        
        # Add to parent task's subtasks if applicable
        if parent_task_id:
            self.tasks[parent_task_id].subtasks.append(task_id)
        
        return task

    def update_task_status(self, task_id: str, status: TaskStatus, 
                          user_id: str, notes: str = None) -> Task:
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        old_status = task.status
        task.status = status
        task.updated_at = datetime.now()
        
        # Update timestamps based on status
        if status == TaskStatus.IN_PROGRESS and old_status == TaskStatus.PENDING:
            task.started_at = datetime.now()
        elif status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now()
        
        # Add comment if notes provided
        if notes:
            self.add_task_comment(task_id, user_id, notes)
        
        # Check dependencies before allowing completion
        if status == TaskStatus.COMPLETED:
            self._check_dependencies_completed(task_id)
        
        return task

    def _check_dependencies_completed(self, task_id: str):
        task = self.tasks[task_id]
        for dep_id in task.dependencies:
            dep_task = self.tasks[dep_id]
            if dep_task.status != TaskStatus.COMPLETED:
                raise ValueError(f"Cannot complete task: dependency {dep_id} is not completed")

    def assign_task(self, task_id: str, assigned_to: str, assigned_by: str) -> Task:
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.assigned_to = assigned_to
        task.updated_at = datetime.now()
        
        # Add assignment comment
        comment = f"Task reassigned to {assigned_to} by {assigned_by}"
        self.add_task_comment(task_id, assigned_by, comment)
        
        return task

    def add_task_comment(self, task_id: str, user_id: str, comment: str) -> TaskComment:
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task_comment = TaskComment(
            id=str(uuid.uuid4()),
            task_id=task_id,
            user_id=user_id,
            comment=comment,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        
        self.comments[task_id].append(task_comment)
        return task_comment

    def add_task_attachment(self, task_id: str, filename: str, file_type: str,
                           file_size: int, uploaded_by: str, file_url: str) -> TaskAttachment:
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        attachment = TaskAttachment(
            id=str(uuid.uuid4()),
            task_id=task_id,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            uploaded_by=uploaded_by,
            uploaded_at=datetime.now(),
            file_url=file_url,
            metadata={}
        )
        
        self.attachments[task_id].append(attachment)
        return attachment

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def get_tasks_by_provider(self, provider_id: str, status: TaskStatus = None) -> List[Task]:
        tasks = [task for task in self.tasks.values() if task.assigned_to == provider_id]
        
        if status:
            tasks = [task for task in tasks if task.status == status]
        
        return sorted(tasks, key=lambda x: (x.priority, x.due_date))

    def get_overdue_tasks(self, provider_id: str = None) -> List[Task]:
        now = datetime.now()
        overdue_tasks = []
        
        for task in self.tasks.values():
            if (task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED] and
                task.due_date < now):
                if provider_id is None or task.assigned_to == provider_id:
                    overdue_tasks.append(task)
        
        return sorted(overdue_tasks, key=lambda x: x.due_date)

    def get_high_priority_tasks(self, provider_id: str = None) -> List[Task]:
        high_priority_tasks = []
        
        for task in self.tasks.values():
            if (task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED] and
                task.priority in [TaskPriority.HIGH, TaskPriority.URGENT, TaskPriority.CRITICAL]):
                if provider_id is None or task.assigned_to == provider_id:
                    high_priority_tasks.append(task)
        
        return sorted(high_priority_tasks, key=lambda x: (x.priority, x.due_date))

    def get_tasks_by_patient(self, patient_id: str) -> List[Task]:
        tasks = [task for task in self.tasks.values() if task.patient_id == patient_id]
        return sorted(tasks, key=lambda x: x.created_at, reverse=True)

    def get_task_comments(self, task_id: str) -> List[TaskComment]:
        return self.comments.get(task_id, [])

    def get_task_attachments(self, task_id: str) -> List[TaskAttachment]:
        return self.attachments.get(task_id, [])

    def update_task_progress(self, task_id: str, actual_duration_minutes: int = None,
                           notes: str = None, user_id: str = None) -> Task:
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.updated_at = datetime.now()
        
        if actual_duration_minutes is not None:
            task.actual_duration_minutes = actual_duration_minutes
        
        if notes and user_id:
            self.add_task_comment(task_id, user_id, notes)
        
        return task

    def create_task_template(self, name: str, template_data: Dict[str, Any]) -> str:
        template_id = str(uuid.uuid4())
        self.task_templates[template_id] = {
            "id": template_id,
            "name": name,
            "template": template_data,
            "created_at": datetime.now().isoformat()
        }
        return template_id

    def create_task_from_template(self, template_id: str, **kwargs) -> Task:
        if template_id not in self.task_templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.task_templates[template_id]["template"]
        template.update(kwargs)
        
        return self.create_task(**template)

    def get_task_statistics(self, provider_id: str = None) -> Dict[str, Any]:
        tasks = self.tasks.values()
        if provider_id:
            tasks = [task for task in tasks if task.assigned_to == provider_id]
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        pending_tasks = len([t for t in tasks if t.status == TaskStatus.PENDING])
        overdue_tasks = len([t for t in tasks if t.due_date < datetime.now() and 
                           t.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]])
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "overdue_tasks": overdue_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }

task_management_service = TaskManagementService()

@app.post("/tasks")
async def create_task(task_data: Dict[str, Any]):
    try:
        task = task_management_service.create_task(
            title=task_data["title"],
            description=task_data["description"],
            task_type=TaskType(task_data["task_type"]),
            category=TaskCategory(task_data["category"]),
            priority=TaskPriority(task_data["priority"]),
            assigned_to=task_data["assigned_to"],
            created_by=task_data["created_by"],
            due_date=datetime.fromisoformat(task_data["due_date"]),
            estimated_duration_minutes=task_data["estimated_duration_minutes"],
            patient_id=task_data.get("patient_id"),
            tags=task_data.get("tags", []),
            dependencies=task_data.get("dependencies", []),
            parent_task_id=task_data.get("parent_task_id")
        )
        return {"task": task}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/tasks/{task_id}/status")
async def update_task_status(task_id: str, status: TaskStatus, user_id: str, notes: str = None):
    try:
        task = task_management_service.update_task_status(task_id, status, user_id, notes)
        return {"task": task}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/tasks/{task_id}/assign")
async def assign_task(task_id: str, assigned_to: str, assigned_by: str):
    try:
        task = task_management_service.assign_task(task_id, assigned_to, assigned_by)
        return {"task": task}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/tasks/{task_id}/comments")
async def add_task_comment(task_id: str, comment_data: Dict[str, Any]):
    try:
        comment = task_management_service.add_task_comment(
            task_id=task_id,
            user_id=comment_data["user_id"],
            comment=comment_data["comment"]
        )
        return {"comment": comment}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/tasks/{task_id}/attachments")
async def add_task_attachment(task_id: str, attachment_data: Dict[str, Any]):
    try:
        attachment = task_management_service.add_task_attachment(
            task_id=task_id,
            filename=attachment_data["filename"],
            file_type=attachment_data["file_type"],
            file_size=attachment_data["file_size"],
            uploaded_by=attachment_data["uploaded_by"],
            file_url=attachment_data["file_url"]
        )
        return {"attachment": attachment}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = task_management_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task": task}

@app.get("/providers/{provider_id}/tasks")
async def get_provider_tasks(provider_id: str, status: TaskStatus = None):
    tasks = task_management_service.get_tasks_by_provider(provider_id, status)
    return {"tasks": tasks}

@app.get("/tasks/overdue")
async def get_overdue_tasks(provider_id: str = None):
    tasks = task_management_service.get_overdue_tasks(provider_id)
    return {"tasks": tasks}

@app.get("/tasks/high-priority")
async def get_high_priority_tasks(provider_id: str = None):
    tasks = task_management_service.get_high_priority_tasks(provider_id)
    return {"tasks": tasks}

@app.get("/patients/{patient_id}/tasks")
async def get_patient_tasks(patient_id: str):
    tasks = task_management_service.get_tasks_by_patient(patient_id)
    return {"tasks": tasks}

@app.get("/tasks/{task_id}/comments")
async def get_task_comments(task_id: str):
    comments = task_management_service.get_task_comments(task_id)
    return {"comments": comments}

@app.get("/tasks/{task_id}/attachments")
async def get_task_attachments(task_id: str):
    attachments = task_management_service.get_task_attachments(task_id)
    return {"attachments": attachments}

@app.put("/tasks/{task_id}/progress")
async def update_task_progress(task_id: str, progress_data: Dict[str, Any]):
    try:
        task = task_management_service.update_task_progress(
            task_id=task_id,
            actual_duration_minutes=progress_data.get("actual_duration_minutes"),
            notes=progress_data.get("notes"),
            user_id=progress_data.get("user_id")
        )
        return {"task": task}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/task-templates")
async def create_task_template(template_data: Dict[str, Any]):
    try:
        template_id = task_management_service.create_task_template(
            name=template_data["name"],
            template_data=template_data["template"]
        )
        return {"template_id": template_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/tasks/from-template/{template_id}")
async def create_task_from_template(template_id: str, task_data: Dict[str, Any]):
    try:
        task = task_management_service.create_task_from_template(template_id, **task_data)
        return {"task": task}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/providers/{provider_id}/task-statistics")
async def get_task_statistics(provider_id: str):
    stats = task_management_service.get_task_statistics(provider_id)
    return {"statistics": stats} 