import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.models.learning import (
    LearningSession, Feedback, Outcome, AdaptiveAnalytic, LearningPattern
)
from app.schemas.learning import (
    LearningDashboard, ModulePerformance
)
from app.core.config import settings
import json

class LearningEngineService:
    """Core Learning Engine for Abena IHR platform"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_learning_session(self, module_name: str, session_type: str, 
                                    user_id: Optional[str] = None, 
                                    patient_id: Optional[str] = None) -> LearningSession:
        """Create a new learning session"""
        session = LearningSession(
            module_name=module_name,
            session_type=session_type,
            user_id=user_id,
            patient_id=patient_id
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    async def process_feedback(self, session_id: int, feedback_data: Dict[str, Any]) -> bool:
        """Process feedback and trigger adaptive learning"""
        try:
            # Mark feedback as processed
            feedback = self.db.query(Feedback).filter(
                Feedback.session_id == session_id,
                Feedback.is_processed == False
            ).first()
            
            if feedback:
                feedback.is_processed = True
                self.db.commit()
                
                # Trigger adaptive analytics
                await self._update_adaptive_analytics(session_id, feedback_data)
                
                # Update learning patterns
                await self._update_learning_patterns(session_id, feedback_data)
                
            return True
        except Exception as e:
            print(f"Error processing feedback: {e}")
            return False
    
    async def track_outcome(self, session_id: int, patient_id: str, 
                          outcome_type: str, outcome_data: Dict[str, Any]) -> Outcome:
        """Track patient outcome and update learning models"""
        outcome = Outcome(
            session_id=session_id,
            patient_id=patient_id,
            outcome_type=outcome_type,
            outcome_value=outcome_data.get('value'),
            outcome_category=outcome_data.get('category'),
            measurement_date=outcome_data.get('measurement_date', datetime.utcnow()),
            notes=outcome_data.get('notes'),
            confidence_score=outcome_data.get('confidence_score', 0.5)
        )
        
        self.db.add(outcome)
        self.db.commit()
        
        # Update learning based on outcome
        await self._adaptive_learning_from_outcome(outcome)
        
        return outcome
    
    async def get_adaptive_recommendations(self, module_name: str, 
                                         context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate adaptive recommendations based on learning patterns"""
        
        # Get relevant learning patterns
        patterns = self.db.query(LearningPattern).filter(
            LearningPattern.modules_involved.contains([module_name]),
            LearningPattern.is_validated == True,
            LearningPattern.confidence_level >= 0.7
        ).order_by(desc(LearningPattern.success_rate)).limit(10).all()
        
        recommendations = {
            'primary_recommendations': [],
            'alternative_options': [],
            'risk_factors': [],
            'confidence_score': 0.0,
            'learning_insights': []
        }
        
        total_confidence = 0.0
        applicable_patterns = 0
        
        for pattern in patterns:
            # Check if pattern applies to current context
            if self._pattern_matches_context(pattern, context_data):
                applicable_patterns += 1
                pattern_weight = pattern.confidence_level * pattern.success_rate
                total_confidence += pattern_weight
                
                # Generate recommendations from pattern
                pattern_recs = self._generate_pattern_recommendations(pattern, context_data)
                
                if pattern.confidence_level >= 0.8:
                    recommendations['primary_recommendations'].extend(pattern_recs)
                else:
                    recommendations['alternative_options'].extend(pattern_recs)
                
                recommendations['learning_insights'].append({
                    'pattern_name': pattern.pattern_name,
                    'confidence': pattern.confidence_level,
                    'success_rate': pattern.success_rate,
                    'usage_count': pattern.usage_count
                })
        
        if applicable_patterns > 0:
            recommendations['confidence_score'] = total_confidence / applicable_patterns
        
        return recommendations
    
    async def get_learning_dashboard(self) -> LearningDashboard:
        """Get comprehensive learning dashboard data"""
        
        # Basic statistics
        total_sessions = self.db.query(LearningSession).count()
        total_feedback = self.db.query(Feedback).count()
        total_outcomes = self.db.query(Outcome).count()
        
        # Average rating
        avg_rating_result = self.db.query(func.avg(Feedback.rating)).filter(
            Feedback.rating.isnot(None)
        ).scalar()
        avg_rating = float(avg_rating_result) if avg_rating_result else 0.0
        
        # Active patterns
        active_patterns = self.db.query(LearningPattern).filter(
            LearningPattern.is_validated == True
        ).count()
        
        # Module performance
        module_performance = await self._calculate_module_performance()
        
        # Recent improvements
        recent_improvements = await self._get_recent_improvements()
        
        return LearningDashboard(
            total_sessions=total_sessions,
            total_feedback=total_feedback,
            total_outcomes=total_outcomes,
            avg_rating=avg_rating,
            active_patterns=active_patterns,
            module_performance=module_performance,
            recent_improvements=recent_improvements
        )
    
    async def _update_adaptive_analytics(self, session_id: int, feedback_data: Dict[str, Any]):
        """Update adaptive analytics based on feedback"""
        session = self.db.query(LearningSession).filter(LearningSession.id == session_id).first()
        if not session:
            return
        
        # Create adaptive analytic record
        analytic = AdaptiveAnalytic(
            session_id=session_id,
            analytic_type="feedback_analysis",
            model_version="1.0",
            input_data=feedback_data,
            output_data={
                "adaptation_type": "feedback_integration",
                "improvement_areas": self._identify_improvement_areas(feedback_data)
            },
            accuracy_score=feedback_data.get('rating', 0) / 5.0 if feedback_data.get('rating') else None
        )
        
        self.db.add(analytic)
        self.db.commit()
    
    async def _update_learning_patterns(self, session_id: int, feedback_data: Dict[str, Any]):
        """Update or create learning patterns based on feedback"""
        session = self.db.query(LearningSession).filter(LearningSession.id == session_id).first()
        if not session:
            return
        
        # Extract pattern from feedback
        if feedback_data.get('rating', 0) >= 4.0:  # Good feedback
            pattern_name = f"{session.module_name}_success_pattern_{datetime.utcnow().strftime('%Y%m%d')}"
            
            # Check if similar pattern exists
            existing_pattern = self.db.query(LearningPattern).filter(
                LearningPattern.pattern_name.like(f"{session.module_name}_success_pattern%"),
                LearningPattern.pattern_type == session.session_type
            ).first()
            
            if existing_pattern:
                # Update existing pattern
                existing_pattern.usage_count += 1
                existing_pattern.success_rate = (existing_pattern.success_rate + 1.0) / 2.0
                existing_pattern.confidence_level = min(1.0, existing_pattern.confidence_level + 0.1)
            else:
                # Create new pattern
                pattern = LearningPattern(
                    pattern_name=pattern_name,
                    pattern_type=session.session_type,
                    modules_involved=[session.module_name],
                    pattern_data=feedback_data,
                    confidence_level=0.6,
                    usage_count=1,
                    success_rate=1.0
                )
                self.db.add(pattern)
        
        self.db.commit()
    
    async def _adaptive_learning_from_outcome(self, outcome: Outcome):
        """Adapt learning models based on patient outcomes"""
        session = self.db.query(LearningSession).filter(
            LearningSession.id == outcome.session_id
        ).first()
        
        if not session:
            return
        
        # Calculate outcome success
        success_score = self._calculate_outcome_success(outcome)
        
        # Update related patterns
        patterns = self.db.query(LearningPattern).filter(
            LearningPattern.modules_involved.contains([session.module_name])
        ).all()
        
        for pattern in patterns:
            # Update success rate based on outcome
            new_success_rate = (pattern.success_rate + success_score) / 2.0
            pattern.success_rate = new_success_rate
            
            # Validate pattern if success rate is high
            if new_success_rate >= 0.8 and pattern.usage_count >= 5:
                pattern.is_validated = True
        
        self.db.commit()
    
    def _pattern_matches_context(self, pattern: LearningPattern, context_data: Dict[str, Any]) -> bool:
        """Check if a pattern matches the current context"""
        pattern_data = pattern.pattern_data
        
        # Simple matching logic - can be enhanced with ML
        match_score = 0.0
        total_factors = 0
        
        for key, value in pattern_data.items():
            if key in context_data:
                total_factors += 1
                if context_data[key] == value:
                    match_score += 1.0
                elif isinstance(value, (int, float)) and isinstance(context_data[key], (int, float)):
                    similarity = 1.0 - abs(value - context_data[key]) / max(abs(value), abs(context_data[key]), 1)
                    match_score += similarity
        
        return (match_score / total_factors) >= 0.7 if total_factors > 0 else False
    
    def _generate_pattern_recommendations(self, pattern: LearningPattern, 
                                        context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations from a learning pattern"""
        recommendations = []
        
        # Extract actionable insights from pattern data
        pattern_data = pattern.pattern_data
        
        if 'successful_actions' in pattern_data:
            for action in pattern_data['successful_actions']:
                recommendations.append({
                    'action': action,
                    'confidence': pattern.confidence_level,
                    'success_rate': pattern.success_rate,
                    'evidence': f"Based on {pattern.usage_count} similar cases"
                })
        
        return recommendations
    
    async def _calculate_module_performance(self) -> Dict[str, Dict[str, Any]]:
        """Calculate performance metrics for each module"""
        modules = self.db.query(LearningSession.module_name).distinct().all()
        performance = {}
        
        for (module_name,) in modules:
            # Session count
            session_count = self.db.query(LearningSession).filter(
                LearningSession.module_name == module_name
            ).count()
            
            # Average rating
            avg_rating_result = self.db.query(func.avg(Feedback.rating)).join(
                LearningSession
            ).filter(
                LearningSession.module_name == module_name,
                Feedback.rating.isnot(None)
            ).scalar()
            avg_rating = float(avg_rating_result) if avg_rating_result else 0.0
            
            # Outcome success rate
            successful_outcomes = self.db.query(Outcome).join(LearningSession).filter(
                LearningSession.module_name == module_name,
                Outcome.outcome_category == 'improved'
            ).count()
            
            total_outcomes = self.db.query(Outcome).join(LearningSession).filter(
                LearningSession.module_name == module_name
            ).count()
            
            success_rate = (successful_outcomes / total_outcomes) if total_outcomes > 0 else 0.0
            
            performance[module_name] = {
                'session_count': session_count,
                'avg_rating': avg_rating,
                'outcome_success_rate': success_rate,
                'improvement_trend': 0.0  # Placeholder for trend calculation
            }
        
        return performance
    
    async def _get_recent_improvements(self) -> List[Dict[str, Any]]:
        """Get recent improvements and learning insights"""
        recent_analytics = self.db.query(AdaptiveAnalytic).filter(
            AdaptiveAnalytic.created_at >= datetime.utcnow() - timedelta(days=30)
        ).order_by(desc(AdaptiveAnalytic.created_at)).limit(10).all()
        
        improvements = []
        for analytic in recent_analytics:
            improvements.append({
                'date': analytic.created_at.isoformat(),
                'type': analytic.analytic_type,
                'improvement': analytic.output_data.get('improvement_areas', []),
                'accuracy_score': analytic.accuracy_score
            })
        
        return improvements
    
    def _identify_improvement_areas(self, feedback_data: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement from feedback"""
        areas = []
        
        if feedback_data.get('rating', 5) < 3:
            areas.append('recommendation_accuracy')
        
        if 'comments' in feedback_data and feedback_data['comments']:
            # Simple keyword analysis
            comments = feedback_data['comments'].lower()
            if 'slow' in comments:
                areas.append('response_time')
            if 'unclear' in comments or 'confusing' in comments:
                areas.append('clarity')
            if 'missing' in comments:
                areas.append('completeness')
        
        return areas
    
    def _calculate_outcome_success(self, outcome: Outcome) -> float:
        """Calculate success score from outcome"""
        if outcome.outcome_category == 'improved':
            return 1.0
        elif outcome.outcome_category == 'stable':
            return 0.6
        elif outcome.outcome_category == 'worsened':
            return 0.0
        else:
            # Use outcome value if available
            if outcome.outcome_value is not None:
                return min(1.0, max(0.0, outcome.outcome_value))
            return 0.5 