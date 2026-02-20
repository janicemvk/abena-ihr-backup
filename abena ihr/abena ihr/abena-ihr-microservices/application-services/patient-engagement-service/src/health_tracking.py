from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json

app = FastAPI(title="Patient Health Tracking Service")

class VitalSignType(str, Enum):
    BLOOD_PRESSURE = "blood_pressure"
    HEART_RATE = "heart_rate"
    TEMPERATURE = "temperature"
    WEIGHT = "weight"
    HEIGHT = "height"
    BMI = "bmi"
    OXYGEN_SATURATION = "oxygen_saturation"
    RESPIRATORY_RATE = "respiratory_rate"
    BLOOD_GLUCOSE = "blood_glucose"
    PAIN_LEVEL = "pain_level"

class SymptomSeverity(str, Enum):
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"

class MedicationStatus(str, Enum):
    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"

class GoalStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class VitalSign(BaseModel):
    id: str
    patient_id: str
    vital_type: VitalSignType
    value: float
    unit: str
    systolic: Optional[float] = None  # For blood pressure
    diastolic: Optional[float] = None  # For blood pressure
    measured_at: datetime
    measured_by: str  # "patient", "provider", "device"
    device_id: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    is_abnormal: bool = False
    created_at: datetime
    metadata: Dict[str, Any] = {}

class Symptom(BaseModel):
    id: str
    patient_id: str
    symptom_name: str
    severity: SymptomSeverity
    description: str
    body_location: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    is_ongoing: bool = True
    triggers: List[str] = []
    alleviating_factors: List[str] = []
    impact_on_daily_life: str = "none"
    reported_at: datetime
    created_at: datetime
    metadata: Dict[str, Any] = {}

class Medication(BaseModel):
    id: str
    patient_id: str
    medication_name: str
    dosage: str
    frequency: str
    route: str  # oral, topical, injection, etc.
    status: MedicationStatus
    prescribed_by: str
    prescribed_at: datetime
    started_at: datetime
    end_date: Optional[datetime] = None
    instructions: str
    side_effects: List[str] = []
    allergies: List[str] = []
    refill_reminder: bool = False
    refill_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}

class MedicationDose(BaseModel):
    id: str
    medication_id: str
    patient_id: str
    dose_taken: bool
    scheduled_time: datetime
    taken_time: Optional[datetime] = None
    dose_amount: str
    notes: Optional[str] = None
    side_effects: List[str] = []
    created_at: datetime
    metadata: Dict[str, Any] = {}

class HealthGoal(BaseModel):
    id: str
    patient_id: str
    goal_type: str  # weight_loss, exercise, medication_adherence, etc.
    title: str
    description: str
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit: Optional[str] = None
    start_date: datetime
    target_date: datetime
    status: GoalStatus
    progress_percentage: float = 0.0
    milestones: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}

class HealthActivity(BaseModel):
    id: str
    patient_id: str
    activity_type: str  # exercise, sleep, nutrition, etc.
    title: str
    description: str
    duration_minutes: Optional[int] = None
    calories_burned: Optional[int] = None
    steps: Optional[int] = None
    distance: Optional[float] = None
    activity_date: datetime
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime
    metadata: Dict[str, Any] = {}

class HealthTrackingService:
    def __init__(self):
        self.vital_signs: Dict[str, List[VitalSign]] = {}
        self.symptoms: Dict[str, List[Symptom]] = {}
        self.medications: Dict[str, List[Medication]] = {}
        self.medication_doses: Dict[str, List[MedicationDose]] = {}
        self.health_goals: Dict[str, List[HealthGoal]] = {}
        self.health_activities: Dict[str, List[HealthActivity]] = {}
        self.normal_ranges: Dict[str, Dict[str, Any]] = {}

    def add_vital_sign(self, patient_id: str, vital_type: VitalSignType, value: float,
                      unit: str, measured_at: datetime, measured_by: str,
                      systolic: float = None, diastolic: float = None,
                      device_id: str = None, location: str = None, notes: str = None) -> VitalSign:
        vital_sign = VitalSign(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            vital_type=vital_type,
            value=value,
            unit=unit,
            systolic=systolic,
            diastolic=diastolic,
            measured_at=measured_at,
            measured_by=measured_by,
            device_id=device_id,
            location=location,
            notes=notes,
            is_abnormal=self._check_abnormal_vital(vital_type, value, systolic, diastolic),
            created_at=datetime.now(),
            metadata={}
        )
        
        if patient_id not in self.vital_signs:
            self.vital_signs[patient_id] = []
        
        self.vital_signs[patient_id].append(vital_sign)
        return vital_sign

    def _check_abnormal_vital(self, vital_type: VitalSignType, value: float, 
                            systolic: float = None, diastolic: float = None) -> bool:
        # Define normal ranges (simplified - in production, use age/gender-specific ranges)
        normal_ranges = {
            VitalSignType.BLOOD_PRESSURE: {"systolic": (90, 140), "diastolic": (60, 90)},
            VitalSignType.HEART_RATE: (60, 100),
            VitalSignType.TEMPERATURE: (36.1, 37.2),
            VitalSignType.WEIGHT: (30, 200),  # kg
            VitalSignType.HEIGHT: (100, 250),  # cm
            VitalSignType.BMI: (18.5, 25),
            VitalSignType.OXYGEN_SATURATION: (95, 100),
            VitalSignType.RESPIRATORY_RATE: (12, 20),
            VitalSignType.BLOOD_GLUCOSE: (70, 140),  # mg/dL
            VitalSignType.PAIN_LEVEL: (0, 10)
        }
        
        if vital_type == VitalSignType.BLOOD_PRESSURE:
            if systolic and diastolic:
                sys_range = normal_ranges[vital_type]["systolic"]
                dia_range = normal_ranges[vital_type]["diastolic"]
                return not (sys_range[0] <= systolic <= sys_range[1] and 
                           dia_range[0] <= diastolic <= dia_range[1])
            return False
        
        if vital_type in normal_ranges:
            range_min, range_max = normal_ranges[vital_type]
            return not (range_min <= value <= range_max)
        
        return False

    def get_vital_signs(self, patient_id: str, vital_type: VitalSignType = None,
                       start_date: datetime = None, end_date: datetime = None) -> List[VitalSign]:
        vital_signs = self.vital_signs.get(patient_id, [])
        
        if vital_type:
            vital_signs = [v for v in vital_signs if v.vital_type == vital_type]
        
        if start_date:
            vital_signs = [v for v in vital_signs if v.measured_at >= start_date]
        
        if end_date:
            vital_signs = [v for v in vital_signs if v.measured_at <= end_date]
        
        return sorted(vital_signs, key=lambda x: x.measured_at, reverse=True)

    def get_vital_trends(self, patient_id: str, vital_type: VitalSignType, days: int = 30) -> Dict[str, Any]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        vital_signs = self.get_vital_signs(patient_id, vital_type, start_date, end_date)
        
        if not vital_signs:
            return {"trend": "no_data", "values": [], "abnormal_count": 0}
        
        values = [v.value for v in vital_signs]
        abnormal_count = len([v for v in vital_signs if v.is_abnormal])
        
        # Simple trend calculation
        if len(values) >= 2:
            trend = "increasing" if values[0] > values[-1] else "decreasing" if values[0] < values[-1] else "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "trend": trend,
            "values": values,
            "abnormal_count": abnormal_count,
            "latest_value": vital_signs[0].value if vital_signs else None,
            "latest_date": vital_signs[0].measured_at if vital_signs else None
        }

    def add_symptom(self, patient_id: str, symptom_name: str, severity: SymptomSeverity,
                   description: str, body_location: str = None, started_at: datetime = None,
                   triggers: List[str] = None, alleviating_factors: List[str] = None,
                   impact_on_daily_life: str = "none") -> Symptom:
        symptom = Symptom(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            symptom_name=symptom_name,
            severity=severity,
            description=description,
            body_location=body_location,
            started_at=started_at or datetime.now(),
            triggers=triggers or [],
            alleviating_factors=alleviating_factors or [],
            impact_on_daily_life=impact_on_daily_life,
            reported_at=datetime.now(),
            created_at=datetime.now(),
            metadata={}
        )
        
        if patient_id not in self.symptoms:
            self.symptoms[patient_id] = []
        
        self.symptoms[patient_id].append(symptom)
        return symptom

    def update_symptom(self, symptom_id: str, updates: Dict[str, Any]) -> Symptom:
        # Find symptom across all patients
        for symptoms in self.symptoms.values():
            for symptom in symptoms:
                if symptom.id == symptom_id:
                    for key, value in updates.items():
                        if hasattr(symptom, key):
                            setattr(symptom, key, value)
                    return symptom
        
        raise ValueError(f"Symptom {symptom_id} not found")

    def get_active_symptoms(self, patient_id: str) -> List[Symptom]:
        symptoms = self.symptoms.get(patient_id, [])
        return [s for s in symptoms if s.is_ongoing]

    def add_medication(self, patient_id: str, medication_name: str, dosage: str,
                      frequency: str, route: str, prescribed_by: str, instructions: str,
                      started_at: datetime = None, end_date: datetime = None,
                      side_effects: List[str] = None, allergies: List[str] = None) -> Medication:
        medication = Medication(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            medication_name=medication_name,
            dosage=dosage,
            frequency=frequency,
            route=route,
            status=MedicationStatus.ACTIVE,
            prescribed_by=prescribed_by,
            prescribed_at=datetime.now(),
            started_at=started_at or datetime.now(),
            end_date=end_date,
            instructions=instructions,
            side_effects=side_effects or [],
            allergies=allergies or [],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        
        if patient_id not in self.medications:
            self.medications[patient_id] = []
        
        self.medications[patient_id].append(medication)
        return medication

    def record_medication_dose(self, medication_id: str, patient_id: str, dose_taken: bool,
                             scheduled_time: datetime, dose_amount: str,
                             taken_time: datetime = None, notes: str = None,
                             side_effects: List[str] = None) -> MedicationDose:
        dose = MedicationDose(
            id=str(uuid.uuid4()),
            medication_id=medication_id,
            patient_id=patient_id,
            dose_taken=dose_taken,
            scheduled_time=scheduled_time,
            taken_time=taken_time,
            dose_amount=dose_amount,
            notes=notes,
            side_effects=side_effects or [],
            created_at=datetime.now(),
            metadata={}
        )
        
        if patient_id not in self.medication_doses:
            self.medication_doses[patient_id] = []
        
        self.medication_doses[patient_id].append(dose)
        return dose

    def get_medication_adherence(self, patient_id: str, medication_id: str = None, days: int = 30) -> Dict[str, Any]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        doses = self.medication_doses.get(patient_id, [])
        if medication_id:
            doses = [d for d in doses if d.medication_id == medication_id]
        
        doses = [d for d in doses if d.scheduled_time >= start_date]
        
        if not doses:
            return {"adherence_rate": 0, "total_doses": 0, "taken_doses": 0}
        
        total_doses = len(doses)
        taken_doses = len([d for d in doses if d.dose_taken])
        adherence_rate = (taken_doses / total_doses * 100) if total_doses > 0 else 0
        
        return {
            "adherence_rate": adherence_rate,
            "total_doses": total_doses,
            "taken_doses": taken_doses,
            "missed_doses": total_doses - taken_doses
        }

    def create_health_goal(self, patient_id: str, goal_type: str, title: str, description: str,
                          target_value: float = None, current_value: float = None, unit: str = None,
                          start_date: datetime = None, target_date: datetime = None) -> HealthGoal:
        goal = HealthGoal(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            goal_type=goal_type,
            title=title,
            description=description,
            target_value=target_value,
            current_value=current_value,
            unit=unit,
            start_date=start_date or datetime.now(),
            target_date=target_date,
            status=GoalStatus.NOT_STARTED,
            progress_percentage=0.0,
            milestones=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        
        if patient_id not in self.health_goals:
            self.health_goals[patient_id] = []
        
        self.health_goals[patient_id].append(goal)
        return goal

    def update_goal_progress(self, goal_id: str, current_value: float = None, 
                           progress_percentage: float = None, status: GoalStatus = None) -> HealthGoal:
        # Find goal across all patients
        for goals in self.health_goals.values():
            for goal in goals:
                if goal.id == goal_id:
                    if current_value is not None:
                        goal.current_value = current_value
                    if progress_percentage is not None:
                        goal.progress_percentage = progress_percentage
                    if status is not None:
                        goal.status = status
                    
                    goal.updated_at = datetime.now()
                    return goal
        
        raise ValueError(f"Goal {goal_id} not found")

    def add_health_activity(self, patient_id: str, activity_type: str, title: str, description: str,
                          activity_date: datetime, duration_minutes: int = None,
                          calories_burned: int = None, steps: int = None, distance: float = None,
                          start_time: datetime = None, end_time: datetime = None) -> HealthActivity:
        activity = HealthActivity(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            activity_type=activity_type,
            title=title,
            description=description,
            duration_minutes=duration_minutes,
            calories_burned=calories_burned,
            steps=steps,
            distance=distance,
            activity_date=activity_date,
            start_time=start_time,
            end_time=end_time,
            created_at=datetime.now(),
            metadata={}
        )
        
        if patient_id not in self.health_activities:
            self.health_activities[patient_id] = []
        
        self.health_activities[patient_id].append(activity)
        return activity

    def get_health_summary(self, patient_id: str) -> Dict[str, Any]:
        # Get latest vital signs
        latest_vitals = {}
        for vital_type in VitalSignType:
            vitals = self.get_vital_signs(patient_id, vital_type, limit=1)
            if vitals:
                latest_vitals[vital_type.value] = {
                    "value": vitals[0].value,
                    "unit": vitals[0].unit,
                    "measured_at": vitals[0].measured_at,
                    "is_abnormal": vitals[0].is_abnormal
                }
        
        # Get active symptoms
        active_symptoms = self.get_active_symptoms(patient_id)
        
        # Get active medications
        active_medications = [m for m in self.medications.get(patient_id, []) 
                            if m.status == MedicationStatus.ACTIVE]
        
        # Get medication adherence
        adherence = self.get_medication_adherence(patient_id)
        
        # Get active goals
        active_goals = [g for g in self.health_goals.get(patient_id, []) 
                       if g.status in [GoalStatus.NOT_STARTED, GoalStatus.IN_PROGRESS]]
        
        # Get recent activities
        recent_activities = self.health_activities.get(patient_id, [])
        recent_activities = sorted(recent_activities, key=lambda x: x.activity_date, reverse=True)[:5]
        
        return {
            "latest_vitals": latest_vitals,
            "active_symptoms_count": len(active_symptoms),
            "active_medications_count": len(active_medications),
            "medication_adherence": adherence,
            "active_goals_count": len(active_goals),
            "recent_activities": recent_activities,
            "summary_date": datetime.now()
        }

health_tracking_service = HealthTrackingService()

@app.post("/patients/{patient_id}/vitals")
async def add_vital_sign(patient_id: str, vital_data: Dict[str, Any]):
    try:
        vital_sign = health_tracking_service.add_vital_sign(
            patient_id=patient_id,
            vital_type=VitalSignType(vital_data["vital_type"]),
            value=vital_data["value"],
            unit=vital_data["unit"],
            measured_at=datetime.fromisoformat(vital_data["measured_at"]),
            measured_by=vital_data["measured_by"],
            systolic=vital_data.get("systolic"),
            diastolic=vital_data.get("diastolic"),
            device_id=vital_data.get("device_id"),
            location=vital_data.get("location"),
            notes=vital_data.get("notes")
        )
        return {"vital_sign": vital_sign}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/{patient_id}/vitals")
async def get_vital_signs(patient_id: str, vital_type: VitalSignType = None, 
                         start_date: str = None, end_date: str = None):
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        vital_signs = health_tracking_service.get_vital_signs(patient_id, vital_type, start_dt, end_dt)
        return {"vital_signs": vital_signs}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/{patient_id}/vitals/{vital_type}/trends")
async def get_vital_trends(patient_id: str, vital_type: VitalSignType, days: int = 30):
    trends = health_tracking_service.get_vital_trends(patient_id, vital_type, days)
    return {"trends": trends}

@app.post("/patients/{patient_id}/symptoms")
async def add_symptom(patient_id: str, symptom_data: Dict[str, Any]):
    try:
        symptom = health_tracking_service.add_symptom(
            patient_id=patient_id,
            symptom_name=symptom_data["symptom_name"],
            severity=SymptomSeverity(symptom_data["severity"]),
            description=symptom_data["description"],
            body_location=symptom_data.get("body_location"),
            started_at=datetime.fromisoformat(symptom_data["started_at"]) if symptom_data.get("started_at") else None,
            triggers=symptom_data.get("triggers", []),
            alleviating_factors=symptom_data.get("alleviating_factors", []),
            impact_on_daily_life=symptom_data.get("impact_on_daily_life", "none")
        )
        return {"symptom": symptom}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/{patient_id}/symptoms/active")
async def get_active_symptoms(patient_id: str):
    symptoms = health_tracking_service.get_active_symptoms(patient_id)
    return {"symptoms": symptoms}

@app.put("/symptoms/{symptom_id}")
async def update_symptom(symptom_id: str, updates: Dict[str, Any]):
    try:
        symptom = health_tracking_service.update_symptom(symptom_id, updates)
        return {"symptom": symptom}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/patients/{patient_id}/medications")
async def add_medication(patient_id: str, medication_data: Dict[str, Any]):
    try:
        medication = health_tracking_service.add_medication(
            patient_id=patient_id,
            medication_name=medication_data["medication_name"],
            dosage=medication_data["dosage"],
            frequency=medication_data["frequency"],
            route=medication_data["route"],
            prescribed_by=medication_data["prescribed_by"],
            instructions=medication_data["instructions"],
            started_at=datetime.fromisoformat(medication_data["started_at"]) if medication_data.get("started_at") else None,
            end_date=datetime.fromisoformat(medication_data["end_date"]) if medication_data.get("end_date") else None,
            side_effects=medication_data.get("side_effects", []),
            allergies=medication_data.get("allergies", [])
        )
        return {"medication": medication}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/medications/{medication_id}/doses")
async def record_medication_dose(medication_id: str, dose_data: Dict[str, Any]):
    try:
        dose = health_tracking_service.record_medication_dose(
            medication_id=medication_id,
            patient_id=dose_data["patient_id"],
            dose_taken=dose_data["dose_taken"],
            scheduled_time=datetime.fromisoformat(dose_data["scheduled_time"]),
            dose_amount=dose_data["dose_amount"],
            taken_time=datetime.fromisoformat(dose_data["taken_time"]) if dose_data.get("taken_time") else None,
            notes=dose_data.get("notes"),
            side_effects=dose_data.get("side_effects", [])
        )
        return {"dose": dose}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/{patient_id}/medications/adherence")
async def get_medication_adherence(patient_id: str, medication_id: str = None, days: int = 30):
    adherence = health_tracking_service.get_medication_adherence(patient_id, medication_id, days)
    return {"adherence": adherence}

@app.post("/patients/{patient_id}/goals")
async def create_health_goal(patient_id: str, goal_data: Dict[str, Any]):
    try:
        goal = health_tracking_service.create_health_goal(
            patient_id=patient_id,
            goal_type=goal_data["goal_type"],
            title=goal_data["title"],
            description=goal_data["description"],
            target_value=goal_data.get("target_value"),
            current_value=goal_data.get("current_value"),
            unit=goal_data.get("unit"),
            start_date=datetime.fromisoformat(goal_data["start_date"]) if goal_data.get("start_date") else None,
            target_date=datetime.fromisoformat(goal_data["target_date"]) if goal_data.get("target_date") else None
        )
        return {"goal": goal}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/goals/{goal_id}/progress")
async def update_goal_progress(goal_id: str, progress_data: Dict[str, Any]):
    try:
        goal = health_tracking_service.update_goal_progress(
            goal_id=goal_id,
            current_value=progress_data.get("current_value"),
            progress_percentage=progress_data.get("progress_percentage"),
            status=GoalStatus(progress_data["status"]) if progress_data.get("status") else None
        )
        return {"goal": goal}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/patients/{patient_id}/activities")
async def add_health_activity(patient_id: str, activity_data: Dict[str, Any]):
    try:
        activity = health_tracking_service.add_health_activity(
            patient_id=patient_id,
            activity_type=activity_data["activity_type"],
            title=activity_data["title"],
            description=activity_data["description"],
            activity_date=datetime.fromisoformat(activity_data["activity_date"]),
            duration_minutes=activity_data.get("duration_minutes"),
            calories_burned=activity_data.get("calories_burned"),
            steps=activity_data.get("steps"),
            distance=activity_data.get("distance"),
            start_time=datetime.fromisoformat(activity_data["start_time"]) if activity_data.get("start_time") else None,
            end_time=datetime.fromisoformat(activity_data["end_time"]) if activity_data.get("end_time") else None
        )
        return {"activity": activity}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/{patient_id}/health-summary")
async def get_health_summary(patient_id: str):
    summary = health_tracking_service.get_health_summary(patient_id)
    return {"summary": summary} 