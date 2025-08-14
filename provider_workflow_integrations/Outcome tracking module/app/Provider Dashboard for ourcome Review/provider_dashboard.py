import json
import requests
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import uuid
import logging
from dataclasses import dataclass, asdict

# Import Abena SDK for authentication, authorization, and data handling
from abena_sdk import AbenaClient, AbenaAuth, AbenaDataHandler
from abena_sdk.models import AbenaInsight, AbenaPatient, AbenaOutcome, AbenaEpisode
from abena_sdk.exceptions import AbenaAuthError, AbenaDataError


@dataclass
class ClinicalSummary:
    """Represents a structured clinical summary for provider review"""
    summary_id: str
    patient_id: str
    provider_id: str
    summary_date: date
    outcome_summary: Dict[str, Any]
    treatment_episodes: List[Dict[str, Any]]
    abena_insights: List[Dict[str, Any]]
    recommendations: List[str]
    risk_factors: List[str]
    next_steps: List[str]
    created_at: datetime


class EMRIntegration:
    """Integration service for EMR systems and clinical summaries using Abena SDK"""
    
    def __init__(self, abena_client: AbenaClient = None, fhir_base_url: str = None):
        # Initialize Abena SDK components
        self.abena_auth = AbenaAuth()
        self.abena_data = AbenaDataHandler()
        self.abena_client = abena_client or AbenaClient()
        self.fhir_base_url = fhir_base_url or "https://fhir.example.com"
        self.logger = logging.getLogger(__name__)
        
        # EMR system configuration
        self.emr_config = {
            "fhir_version": "R4",
            "timeout": 30,
            "retry_attempts": 3
        }
    
    def push_abena_insights_to_emr(self, patient_id: str, insights: List[AbenaInsight]) -> Dict[str, Any]:
        """
        Format insights for EMR consumption and send via FHIR API using Abena SDK
        
        Args:
            patient_id: Patient identifier
            insights: List of Abena insights to push
            
        Returns:
            Dictionary with push results and status
        """
        try:
            # Use Abena SDK for authentication
            auth_token = self.abena_auth.get_access_token()
            
            # Format insights for FHIR Observation resources using Abena SDK
            fhir_observations = []
            for insight in insights:
                fhir_observation = self._format_insight_as_fhir(insight)
                fhir_observations.append(fhir_observation)
            
            # Send to EMR via FHIR API with Abena authentication
            push_results = []
            for observation in fhir_observations:
                result = self._send_fhir_observation(observation, auth_token)
                push_results.append(result)
            
            # Log the push operation
            self.logger.info(f"Pushed {len(insights)} insights to EMR for patient {patient_id}")
            
            return {
                "success": True,
                "patient_id": patient_id,
                "insights_pushed": len(insights),
                "push_results": push_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except AbenaAuthError as e:
            self.logger.error(f"Abena authentication failed: {str(e)}")
            return {
                "success": False,
                "error": f"Authentication failed: {str(e)}",
                "patient_id": patient_id,
                "insights_pushed": 0
            }
        except Exception as e:
            self.logger.error(f"Failed to push insights to EMR: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "patient_id": patient_id,
                "insights_pushed": 0
            }
    
    def create_clinical_summary(self, patient_id: str, provider_id: str = None) -> ClinicalSummary:
        """
        Generate structured clinical notes with Abena recommendations using Abena SDK
        
        Args:
            patient_id: Patient identifier
            provider_id: Provider identifier (optional)
            
        Returns:
            ClinicalSummary object with comprehensive patient information
        """
        try:
            # Use Abena SDK for data retrieval
            patient_data = self.abena_data.get_patient_data(patient_id)
            outcomes = self.abena_data.get_patient_outcomes(patient_id)
            episodes = self.abena_data.get_patient_episodes(patient_id)
            
            # Generate outcome summary using Abena SDK
            outcome_summary = self._generate_outcome_summary(outcomes)
            
            # Format episode summaries
            episode_summaries = self._format_episode_summaries(episodes)
            
            # Generate Abena insights using SDK
            abena_insights = self.abena_data.generate_insights(patient_id, outcomes, episodes)
            
            # Create recommendations based on insights
            recommendations = self._generate_recommendations(abena_insights, outcome_summary)
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(outcomes, abena_insights)
            
            # Determine next steps
            next_steps = self._determine_next_steps(abena_insights, outcome_summary)
            
            # Create clinical summary
            summary = ClinicalSummary(
                summary_id=str(uuid.uuid4()),
                patient_id=patient_id,
                provider_id=provider_id or "system",
                summary_date=date.today(),
                outcome_summary=outcome_summary,
                treatment_episodes=episode_summaries,
                abena_insights=[asdict(insight) for insight in abena_insights],
                recommendations=recommendations,
                risk_factors=risk_factors,
                next_steps=next_steps,
                created_at=datetime.utcnow()
            )
            
            self.logger.info(f"Created clinical summary for patient {patient_id}")
            return summary
            
        except AbenaDataError as e:
            self.logger.error(f"Abena data retrieval failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create clinical summary: {str(e)}")
            raise
    
    def get_provider_dashboard_data(self, provider_id: str, date_range: str = "30d") -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for provider review using Abena SDK
        
        Args:
            provider_id: Provider identifier
            date_range: Time range for data (7d, 30d, 90d)
            
        Returns:
            Dictionary with dashboard data
        """
        try:
            # Use Abena SDK for data retrieval
            auth_token = self.abena_auth.get_access_token()
            
            # Calculate date range
            end_date = date.today()
            if date_range == "7d":
                start_date = end_date - timedelta(days=7)
            elif date_range == "30d":
                start_date = end_date - timedelta(days=30)
            elif date_range == "90d":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get provider's patients using Abena SDK
            provider_patients = self.abena_data.get_provider_patients(provider_id, auth_token)
            
            # Get recent outcomes using Abena SDK
            recent_outcomes = self.abena_data.get_recent_outcomes(start_date, end_date, auth_token)
            
            # Group by patient
            patients_data = {}
            for outcome in recent_outcomes:
                if outcome.patient_id not in patients_data:
                    patients_data[outcome.patient_id] = {
                        "patient_id": str(outcome.patient_id),
                        "recent_outcomes": [],
                        "insights": [],
                        "risk_level": "low"
                    }
                patients_data[outcome.patient_id]["recent_outcomes"].append({
                    "outcome_type": outcome.outcome_type,
                    "value": float(outcome.outcome_value),
                    "date": outcome.measurement_date.isoformat()
                })
            
            # Generate insights for each patient using Abena SDK
            for patient_id, patient_data in patients_data.items():
                patient_outcomes = self.abena_data.get_patient_outcomes(patient_id, auth_token)
                patient_episodes = self.abena_data.get_patient_episodes(patient_id, auth_token)
                patient_insights = self.abena_data.generate_insights(patient_id, patient_outcomes, patient_episodes, auth_token)
                
                patient_data["insights"] = [asdict(insight) for insight in patient_insights]
                
                # Determine risk level using Abena SDK
                risk_level = self.abena_data.calculate_risk_level(patient_insights)
                patient_data["risk_level"] = risk_level
            
            # Calculate dashboard metrics using Abena SDK
            dashboard_metrics = self.abena_data.calculate_dashboard_metrics(patients_data, auth_token)
            
            return {
                "provider_id": provider_id,
                "date_range": date_range,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "dashboard_metrics": dashboard_metrics,
                "patients": list(patients_data.values()),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except AbenaAuthError as e:
            self.logger.error(f"Abena authentication failed: {str(e)}")
            return {"error": f"Authentication failed: {str(e)}"}
        except AbenaDataError as e:
            self.logger.error(f"Abena data retrieval failed: {str(e)}")
            return {"error": f"Data retrieval failed: {str(e)}"}
        except Exception as e:
            self.logger.error(f"Failed to get dashboard data: {str(e)}")
            return {"error": str(e)}
    
    # Private helper methods
    
    def _format_insight_as_fhir(self, insight: AbenaInsight) -> Dict[str, Any]:
        """Format Abena insight as FHIR Observation resource using Abena SDK"""
        return {
            "resourceType": "Observation",
            "id": insight.insight_id,
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "survey",
                    "display": "Survey"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://abena.com/fhir/insight-types",
                    "code": insight.insight_type,
                    "display": insight.title
                }]
            },
            "subject": {
                "reference": f"Patient/{insight.patient_id}"
            },
            "effectiveDateTime": insight.created_at.isoformat(),
            "valueString": insight.description,
            "component": [
                {
                    "code": {
                        "coding": [{
                            "system": "http://abena.com/fhir/severity",
                            "code": insight.severity,
                            "display": insight.severity.title()
                        }]
                    },
                    "valueString": insight.severity
                },
                {
                    "code": {
                        "coding": [{
                            "system": "http://abena.com/fhir/recommendations",
                            "code": "recommendations",
                            "display": "Recommendations"
                        }]
                    },
                    "valueString": "; ".join(insight.recommendations)
                }
            ],
            "note": [{
                "text": json.dumps(insight.evidence)
            }]
        }
    
    def _send_fhir_observation(self, observation: Dict[str, Any], auth_token: str) -> Dict[str, Any]:
        """Send FHIR Observation to EMR system using Abena authentication"""
        try:
            url = f"{self.fhir_base_url}/Observation"
            
            # Use Abena SDK headers
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/fhir+json",
                "Accept": "application/fhir+json"
            }
            
            for attempt in range(self.emr_config["retry_attempts"]):
                try:
                    response = requests.post(
                        url,
                        json=observation,
                        headers=headers,
                        timeout=self.emr_config["timeout"]
                    )
                    
                    if response.status_code in [200, 201]:
                        return {
                            "success": True,
                            "observation_id": observation["id"],
                            "fhir_id": response.json().get("id"),
                            "status_code": response.status_code
                        }
                    else:
                        self.logger.warning(f"FHIR API returned {response.status_code}: {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    if attempt == self.emr_config["retry_attempts"] - 1:
                        raise e
                    continue
            
            return {
                "success": False,
                "observation_id": observation["id"],
                "error": f"Failed after {self.emr_config['retry_attempts']} attempts"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to send FHIR observation: {str(e)}")
            return {
                "success": False,
                "observation_id": observation["id"],
                "error": str(e)
            }
    
    def _generate_outcome_summary(self, outcomes: List[AbenaOutcome]) -> Dict[str, Any]:
        """Generate summary of patient outcomes using Abena SDK data"""
        if not outcomes:
            return {"total_outcomes": 0, "outcome_types": [], "trends": {}}
        
        # Group by outcome type
        outcomes_by_type = {}
        for outcome in outcomes:
            if outcome.outcome_type not in outcomes_by_type:
                outcomes_by_type[outcome.outcome_type] = []
            outcomes_by_type[outcome.outcome_type].append(outcome)
        
        # Calculate statistics for each type
        trends = {}
        for outcome_type, type_outcomes in outcomes_by_type.items():
            values = [float(o.outcome_value) for o in type_outcomes]
            sorted_outcomes = sorted(type_outcomes, key=lambda x: x.measurement_date)
            
            # Calculate trend
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
            
            trends[outcome_type] = {
                "count": len(values),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "latest": values[-1] if values else None,
                "trend": trend,
                "latest_date": sorted_outcomes[-1].measurement_date.isoformat() if sorted_outcomes else None
            }
        
        return {
            "total_outcomes": len(outcomes),
            "outcome_types": list(outcomes_by_type.keys()),
            "trends": trends,
            "last_updated": max(o.measurement_date for o in outcomes).isoformat() if outcomes else None
        }
    
    def _format_episode_summaries(self, episodes: List[AbenaEpisode]) -> List[Dict[str, Any]]:
        """Format treatment episodes for clinical summary using Abena SDK data"""
        episode_summaries = []
        for episode in episodes:
            summary = {
                "episode_id": str(episode.episode_id),
                "start_date": episode.start_date.isoformat(),
                "status": episode.status,
                "provider_id": str(episode.provider_id),
                "treatment_plan": episode.treatment_plan or {},
                "duration_days": (date.today() - episode.start_date).days if episode.status == "active" else None
            }
            episode_summaries.append(summary)
        
        return episode_summaries
    
    def _generate_recommendations(self, insights: List[AbenaInsight], 
                                outcome_summary: Dict[str, Any]) -> List[str]:
        """Generate clinical recommendations based on insights and outcomes"""
        recommendations = []
        
        # Add recommendations from insights
        for insight in insights:
            recommendations.extend(insight.recommendations)
        
        # Add outcome-based recommendations
        for outcome_type, trend_data in outcome_summary.get("trends", {}).items():
            if trend_data["latest"] is not None:
                if outcome_type == "pain_score" and trend_data["latest"] > 7:
                    recommendations.append("Consider pain management intervention")
                elif outcome_type == "functional_assessment" and trend_data["latest"] < 50:
                    recommendations.append("Recommend physical therapy assessment")
                elif outcome_type == "adherence_rate" and trend_data["latest"] < 80:
                    recommendations.append("Review medication adherence strategies")
        
        # Remove duplicates and return
        return list(set(recommendations))
    
    def _identify_risk_factors(self, outcomes: List[AbenaOutcome], 
                             insights: List[AbenaInsight]) -> List[str]:
        """Identify risk factors based on outcomes and insights"""
        risk_factors = []
        
        # Check for high-severity insights
        high_severity_insights = [i for i in insights if i.severity in ["high", "critical"]]
        if high_severity_insights:
            risk_factors.append("Multiple high-severity clinical alerts")
        
        # Check outcome patterns
        outcome_summary = self._generate_outcome_summary(outcomes)
        for outcome_type, trend_data in outcome_summary.get("trends", {}).items():
            if trend_data["latest"] is not None:
                if outcome_type == "pain_score" and trend_data["latest"] > 8:
                    risk_factors.append("High pain levels")
                elif outcome_type == "functional_assessment" and trend_data["latest"] < 30:
                    risk_factors.append("Severe functional limitations")
                elif outcome_type == "adherence_rate" and trend_data["latest"] < 60:
                    risk_factors.append("Poor medication adherence")
        
        return risk_factors
    
    def _determine_next_steps(self, insights: List[AbenaInsight], 
                            outcome_summary: Dict[str, Any]) -> List[str]:
        """Determine next clinical steps"""
        next_steps = []
        
        # Add steps based on insights
        for insight in insights:
            if insight.severity in ["high", "critical"]:
                next_steps.append("Schedule urgent follow-up appointment")
                break
        
        # Add general next steps
        if outcome_summary.get("total_outcomes", 0) == 0:
            next_steps.append("Initiate baseline outcome assessment")
        else:
            next_steps.append("Continue monitoring patient outcomes")
            next_steps.append("Review treatment plan effectiveness")
        
        return list(set(next_steps))
