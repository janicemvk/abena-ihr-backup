import uuid
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import json
import hashlib
import secrets

from app.database import SessionLocal
from app.models.outcome import PatientOutcome
from app.models.episode import TreatmentEpisode
from app.schemas.outcome import OutcomeCreate


class SurveyLink:
    """Represents a survey link with tracking information"""
    
    def __init__(self, survey_id: str, patient_id: str, survey_type: str, 
                 link_hash: str, expires_at: datetime, is_completed: bool = False):
        self.survey_id = survey_id
        self.patient_id = patient_id
        self.survey_type = survey_type
        self.link_hash = link_hash
        self.expires_at = expires_at
        self.is_completed = is_completed
        self.created_at = datetime.utcnow()


class MedicationLog:
    """Represents a medication adherence log entry"""
    
    def __init__(self, patient_id: str, medication_name: str, 
                 scheduled_time: datetime, taken_time: Optional[datetime] = None,
                 dosage: str = "1", notes: str = ""):
        self.log_id = str(uuid.uuid4())
        self.patient_id = patient_id
        self.medication_name = medication_name
        self.scheduled_time = scheduled_time
        self.taken_time = taken_time
        self.dosage = dosage
        self.notes = notes
        self.created_at = datetime.utcnow()


class OutcomeCollectionService:
    """Service for patient-facing outcome collection and tracking"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self._survey_links: Dict[str, SurveyLink] = {}  # In production, use database
        self._medication_logs: Dict[str, List[MedicationLog]] = {}  # In production, use database
    
    def create_patient_survey(self, patient_id: str, survey_type: str, 
                             expires_in_days: int = 7) -> Dict[str, Any]:
        """
        Generate time-stamped survey links and handle survey reminders
        
        Args:
            patient_id: Patient identifier
            survey_type: Type of survey (pain_assessment, functional_survey, etc.)
            expires_in_days: Number of days until survey expires
            
        Returns:
            Dictionary containing survey information and link
        """
        # Generate unique survey ID and link hash
        survey_id = str(uuid.uuid4())
        link_hash = self._generate_survey_hash(patient_id, survey_type)
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create survey link object
        survey_link = SurveyLink(
            survey_id=survey_id,
            patient_id=patient_id,
            survey_type=survey_type,
            link_hash=link_hash,
            expires_at=expires_at
        )
        
        # Store survey link (in production, save to database)
        self._survey_links[survey_id] = survey_link
        
        # Generate survey URL
        survey_url = f"/survey/{link_hash}"
        
        # Create survey template based on type
        survey_template = self._get_survey_template(survey_type)
        
        return {
            "survey_id": survey_id,
            "patient_id": patient_id,
            "survey_type": survey_type,
            "survey_url": survey_url,
            "expires_at": expires_at.isoformat(),
            "template": survey_template,
            "status": "active"
        }
    
    def validate_and_store_survey_response(self, link_hash: str, 
                                         responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and store survey responses
        
        Args:
            link_hash: Hash from survey link
            responses: Patient survey responses
            
        Returns:
            Dictionary with validation results and stored data
        """
        # Find survey by link hash
        survey_link = self._find_survey_by_hash(link_hash)
        if not survey_link:
            return {"success": False, "error": "Invalid or expired survey link"}
        
        if survey_link.is_completed:
            return {"success": False, "error": "Survey already completed"}
        
        if datetime.utcnow() > survey_link.expires_at:
            return {"success": False, "error": "Survey link has expired"}
        
        # Validate responses based on survey type
        validation_result = self._validate_survey_responses(survey_link.survey_type, responses)
        if not validation_result["valid"]:
            return {"success": False, "error": validation_result["error"]}
        
        # Convert responses to outcome measurements
        outcomes_created = []
        for outcome_data in self._convert_responses_to_outcomes(survey_link.patient_id, responses):
            try:
                outcome = OutcomeCreate(**outcome_data)
                # Store in database using existing outcome service
                from app.services.outcome_service import OutcomeService
                outcome_service = OutcomeService(self.db)
                created_outcome = outcome_service.create_outcome(outcome)
                outcomes_created.append(created_outcome)
            except Exception as e:
                return {"success": False, "error": f"Failed to store outcome: {str(e)}"}
        
        # Mark survey as completed
        survey_link.is_completed = True
        
        return {
            "success": True,
            "survey_id": survey_link.survey_id,
            "patient_id": survey_link.patient_id,
            "outcomes_created": len(outcomes_created),
            "completion_time": datetime.utcnow().isoformat()
        }
    
    def track_medication_adherence(self, patient_id: str, medication_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log medication usage and flag adherence issues
        
        Args:
            patient_id: Patient identifier
            medication_data: Dictionary containing medication information
            
        Returns:
            Dictionary with adherence tracking results
        """
        # Extract medication information
        medication_name = medication_data.get("medication_name")
        scheduled_time = datetime.fromisoformat(medication_data.get("scheduled_time"))
        taken_time = datetime.fromisoformat(medication_data.get("taken_time")) if medication_data.get("taken_time") else None
        dosage = medication_data.get("dosage", "1")
        notes = medication_data.get("notes", "")
        
        # Create medication log entry
        medication_log = MedicationLog(
            patient_id=patient_id,
            medication_name=medication_name,
            scheduled_time=scheduled_time,
            taken_time=taken_time,
            dosage=dosage,
            notes=notes
        )
        
        # Store medication log (in production, save to database)
        if patient_id not in self._medication_logs:
            self._medication_logs[patient_id] = []
        self._medication_logs[patient_id].append(medication_log)
        
        # Calculate adherence metrics
        adherence_metrics = self._calculate_adherence_metrics(patient_id, medication_name)
        
        # Flag adherence issues
        adherence_issues = self._flag_adherence_issues(adherence_metrics)
        
        return {
            "success": True,
            "log_id": medication_log.log_id,
            "adherence_rate": adherence_metrics["adherence_rate"],
            "missed_doses": adherence_metrics["missed_doses"],
            "on_time_doses": adherence_metrics["on_time_doses"],
            "issues": adherence_issues
        }
    
    def calculate_outcome_trends(self, patient_id: str, timeframe: str = "30d") -> Dict[str, Any]:
        """
        Analyze outcome trajectories and generate trend visualizations
        
        Args:
            patient_id: Patient identifier
            timeframe: Time period for analysis (7d, 30d, 90d, all)
            
        Returns:
            Dictionary with trend analysis and visualization data
        """
        # Calculate date range
        end_date = date.today()
        if timeframe == "7d":
            start_date = end_date - timedelta(days=7)
        elif timeframe == "30d":
            start_date = end_date - timedelta(days=30)
        elif timeframe == "90d":
            start_date = end_date - timedelta(days=90)
        else:  # all
            start_date = date(2020, 1, 1)  # Reasonable default
        
        # Get patient outcomes from database
        from app.services.outcome_service import OutcomeService
        outcome_service = OutcomeService(self.db)
        
        # Get all outcomes for the patient
        all_outcomes = outcome_service.get_patient_outcomes(patient_id)
        
        # Filter by date range
        filtered_outcomes = [
            outcome for outcome in all_outcomes 
            if start_date <= outcome.measurement_date <= end_date
        ]
        
        # Group outcomes by type
        outcomes_by_type = {}
        for outcome in filtered_outcomes:
            if outcome.outcome_type not in outcomes_by_type:
                outcomes_by_type[outcome.outcome_type] = []
            outcomes_by_type[outcome.outcome_type].append(outcome)
        
        # Calculate trends for each outcome type
        trends = {}
        for outcome_type, outcomes in outcomes_by_type.items():
            if len(outcomes) < 2:
                trends[outcome_type] = {
                    "trend": "insufficient_data",
                    "data_points": len(outcomes),
                    "visualization_data": []
                }
                continue
            
            # Sort by date
            sorted_outcomes = sorted(outcomes, key=lambda x: x.measurement_date)
            
            # Calculate trend metrics
            values = [float(outcome.outcome_value) for outcome in sorted_outcomes]
            dates = [outcome.measurement_date.isoformat() for outcome in sorted_outcomes]
            
            # Simple trend calculation
            if len(values) >= 2:
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)
                
                if second_avg > first_avg + 0.5:
                    trend = "improving"
                elif second_avg < first_avg - 0.5:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
            
            # Prepare visualization data
            visualization_data = {
                "labels": dates,
                "values": values,
                "trend": trend,
                "statistics": {
                    "count": len(values),
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "latest": values[-1] if values else None
                }
            }
            
            trends[outcome_type] = {
                "trend": trend,
                "data_points": len(outcomes),
                "visualization_data": visualization_data
            }
        
        return {
            "patient_id": patient_id,
            "timeframe": timeframe,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_outcomes": len(filtered_outcomes),
            "outcome_types": list(outcomes_by_type.keys()),
            "trends": trends
        }
    
    def send_survey_reminders(self, patient_id: str, survey_type: str = None) -> Dict[str, Any]:
        """
        Send reminders for pending surveys
        
        Args:
            patient_id: Patient identifier
            survey_type: Optional specific survey type to remind about
            
        Returns:
            Dictionary with reminder status
        """
        # Find pending surveys for patient
        pending_surveys = []
        for survey_id, survey_link in self._survey_links.items():
            if (survey_link.patient_id == patient_id and 
                not survey_link.is_completed and 
                datetime.utcnow() <= survey_link.expires_at):
                
                if survey_type is None or survey_link.survey_type == survey_type:
                    pending_surveys.append(survey_link)
        
        # In production, integrate with email/SMS service
        reminders_sent = []
        for survey in pending_surveys:
            reminder_data = {
                "survey_id": survey.survey_id,
                "survey_type": survey.survey_type,
                "expires_at": survey.expires_at.isoformat(),
                "reminder_sent_at": datetime.utcnow().isoformat()
            }
            reminders_sent.append(reminder_data)
        
        return {
            "patient_id": patient_id,
            "reminders_sent": len(reminders_sent),
            "pending_surveys": len(pending_surveys),
            "reminder_details": reminders_sent
        }
    
    # Private helper methods
    
    def _generate_survey_hash(self, patient_id: str, survey_type: str) -> str:
        """Generate a unique hash for survey links"""
        unique_string = f"{patient_id}_{survey_type}_{datetime.utcnow().isoformat()}_{secrets.token_hex(8)}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    def _get_survey_template(self, survey_type: str) -> Dict[str, Any]:
        """Get survey template based on type"""
        templates = {
            "pain_assessment": {
                "title": "Pain Assessment Survey",
                "questions": [
                    {
                        "id": "pain_level",
                        "type": "scale",
                        "question": "On a scale of 0-10, how would you rate your current pain level?",
                        "min": 0,
                        "max": 10,
                        "outcome_type": "pain_score"
                    },
                    {
                        "id": "pain_location",
                        "type": "text",
                        "question": "Where is your pain located?",
                        "outcome_type": "pain_location"
                    }
                ]
            },
            "functional_survey": {
                "title": "Functional Assessment Survey",
                "questions": [
                    {
                        "id": "mobility_score",
                        "type": "scale",
                        "question": "How would you rate your current mobility? (0-100)",
                        "min": 0,
                        "max": 100,
                        "outcome_type": "mobility_score"
                    },
                    {
                        "id": "daily_activities",
                        "type": "scale",
                        "question": "How well can you perform daily activities? (0-100)",
                        "min": 0,
                        "max": 100,
                        "outcome_type": "functional_assessment"
                    }
                ]
            },
            "quality_of_life": {
                "title": "Quality of Life Assessment",
                "questions": [
                    {
                        "id": "overall_wellbeing",
                        "type": "scale",
                        "question": "How would you rate your overall wellbeing? (0-100)",
                        "min": 0,
                        "max": 100,
                        "outcome_type": "quality_of_life"
                    },
                    {
                        "id": "satisfaction",
                        "type": "scale",
                        "question": "How satisfied are you with your current treatment? (0-100)",
                        "min": 0,
                        "max": 100,
                        "outcome_type": "satisfaction_score"
                    }
                ]
            }
        }
        return templates.get(survey_type, {"title": "General Survey", "questions": []})
    
    def _find_survey_by_hash(self, link_hash: str) -> Optional[SurveyLink]:
        """Find survey link by hash"""
        for survey_link in self._survey_links.values():
            if survey_link.link_hash == link_hash:
                return survey_link
        return None
    
    def _validate_survey_responses(self, survey_type: str, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Validate survey responses"""
        template = self._get_survey_template(survey_type)
        
        for question in template.get("questions", []):
            question_id = question["id"]
            if question_id not in responses:
                return {"valid": False, "error": f"Missing response for question: {question_id}"}
            
            response_value = responses[question_id]
            
            if question["type"] == "scale":
                try:
                    value = float(response_value)
                    if value < question["min"] or value > question["max"]:
                        return {
                            "valid": False, 
                            "error": f"Response for {question_id} must be between {question['min']} and {question['max']}"
                        }
                except (ValueError, TypeError):
                    return {"valid": False, "error": f"Invalid numeric response for {question_id}"}
        
        return {"valid": True}
    
    def _convert_responses_to_outcomes(self, patient_id: str, responses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert survey responses to outcome measurements"""
        outcomes = []
        measurement_date = date.today()
        
        # Map response IDs to outcome types (in production, use database mapping)
        outcome_mapping = {
            "pain_level": "pain_score",
            "mobility_score": "mobility_score",
            "daily_activities": "functional_assessment",
            "overall_wellbeing": "quality_of_life",
            "satisfaction": "satisfaction_score"
        }
        
        for response_id, value in responses.items():
            if response_id in outcome_mapping:
                outcome_data = {
                    "patient_id": patient_id,
                    "measurement_date": measurement_date,
                    "outcome_type": outcome_mapping[response_id],
                    "outcome_value": float(value),
                    "measurement_method": "patient_survey"
                }
                outcomes.append(outcome_data)
        
        return outcomes
    
    def _calculate_adherence_metrics(self, patient_id: str, medication_name: str) -> Dict[str, Any]:
        """Calculate medication adherence metrics"""
        if patient_id not in self._medication_logs:
            return {
                "adherence_rate": 0.0,
                "missed_doses": 0,
                "on_time_doses": 0,
                "total_doses": 0
            }
        
        medication_logs = [
            log for log in self._medication_logs[patient_id] 
            if log.medication_name == medication_name
        ]
        
        if not medication_logs:
            return {
                "adherence_rate": 0.0,
                "missed_doses": 0,
                "on_time_doses": 0,
                "total_doses": 0
            }
        
        total_doses = len(medication_logs)
        taken_doses = len([log for log in medication_logs if log.taken_time is not None])
        missed_doses = total_doses - taken_doses
        
        # Calculate on-time doses (within 2 hours of scheduled time)
        on_time_doses = 0
        for log in medication_logs:
            if log.taken_time:
                time_diff = abs((log.taken_time - log.scheduled_time).total_seconds() / 3600)
                if time_diff <= 2:  # Within 2 hours
                    on_time_doses += 1
        
        adherence_rate = (taken_doses / total_doses) * 100 if total_doses > 0 else 0
        
        return {
            "adherence_rate": round(adherence_rate, 2),
            "missed_doses": missed_doses,
            "on_time_doses": on_time_doses,
            "total_doses": total_doses
        }
    
    def _flag_adherence_issues(self, adherence_metrics: Dict[str, Any]) -> List[str]:
        """Flag potential adherence issues"""
        issues = []
        
        if adherence_metrics["adherence_rate"] < 80:
            issues.append("Low adherence rate - consider intervention")
        
        if adherence_metrics["missed_doses"] > 3:
            issues.append("Multiple missed doses detected")
        
        if adherence_metrics["adherence_rate"] < 60:
            issues.append("Critical adherence issue - immediate attention required")
        
        return issues
    
    def __del__(self):
        """Cleanup database session"""
        if hasattr(self, 'db') and self.db:
            self.db.close()
