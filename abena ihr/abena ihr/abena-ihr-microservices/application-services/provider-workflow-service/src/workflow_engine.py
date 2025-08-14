from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid

app = FastAPI(title="Provider Workflow Service")

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(BaseModel):
    id: str
    title: str
    description: str
    assigned_to: str
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime
    created_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

class Workflow(BaseModel):
    id: str
    name: str
    description: str
    tasks: List[Task]
    status: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}

class WorkflowEngine:
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.tasks: Dict[str, Task] = {}

    def create_workflow(self, name: str, description: str, tasks: List[Dict]) -> Workflow:
        workflow_id = str(uuid.uuid4())
        workflow_tasks = []
        
        for task_data in tasks:
            task = Task(
                id=str(uuid.uuid4()),
                title=task_data["title"],
                description=task_data["description"],
                assigned_to=task_data["assigned_to"],
                status=TaskStatus.PENDING,
                priority=TaskPriority(task_data.get("priority", "medium")),
                due_date=datetime.fromisoformat(task_data["due_date"]),
                created_at=datetime.now(),
                metadata=task_data.get("metadata", {})
            )
            workflow_tasks.append(task)
            self.tasks[task.id] = task

        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            tasks=workflow_tasks,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        
        self.workflows[workflow_id] = workflow
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self.workflows.get(workflow_id)

    def update_task_status(self, task_id: str, status: TaskStatus) -> Task:
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.status = status
        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now()
        
        return task

    def assign_task(self, task_id: str, assigned_to: str) -> Task:
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.assigned_to = assigned_to
        return task

    def get_tasks_by_provider(self, provider_id: str) -> List[Task]:
        return [task for task in self.tasks.values() if task.assigned_to == provider_id]

    def get_overdue_tasks(self) -> List[Task]:
        now = datetime.now()
        return [task for task in self.tasks.values() 
                if task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED] 
                and task.due_date < now]

workflow_engine = WorkflowEngine()

@app.post("/workflows")
async def create_workflow(workflow_data: Dict[str, Any]):
    try:
        workflow = workflow_engine.create_workflow(
            name=workflow_data["name"],
            description=workflow_data["description"],
            tasks=workflow_data["tasks"]
        )
        return {"workflow": workflow}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    workflow = workflow_engine.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"workflow": workflow}

@app.put("/tasks/{task_id}/status")
async def update_task_status(task_id: str, status: TaskStatus):
    try:
        task = workflow_engine.update_task_status(task_id, status)
        return {"task": task}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/tasks/{task_id}/assign")
async def assign_task(task_id: str, assigned_to: str):
    try:
        task = workflow_engine.assign_task(task_id, assigned_to)
        return {"task": task}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/providers/{provider_id}/tasks")
async def get_provider_tasks(provider_id: str):
    tasks = workflow_engine.get_tasks_by_provider(provider_id)
    return {"tasks": tasks}

@app.get("/tasks/overdue")
async def get_overdue_tasks():
    tasks = workflow_engine.get_overdue_tasks()
    return {"tasks": tasks} 