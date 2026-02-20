from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class FeedbackType(str, Enum):
    PROVIDER = "provider"
    PATIENT = "patient"
    SYSTEM = "system"

class OutcomeCategory(str, Enum):
    IMPROVED = "improved"
    STABLE = "stable"
    WORSENED = "worsened"

class SessionType(str, Enum):
    ANALYSIS = "analysis"
    RECOMMENDATION = "recommendation"
    FEEDBACK = "feedback"

# Learning Session Schemas
class LearningSessionCreate(BaseModel):
    module_name: str = Field(..., description="Name of the module (eCdome, Clinical Context, etc.)")
    session_type: SessionType = Field(..., description="Type of session")
    user_id: Optional[str] = None
    patient_id: Optional[str] = None

class LearningSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    module_name: str
    session_type: str
    user_id: Optional[str]
    patient_id: Optional[str]
    created_at: datetime

# Feedback Schemas
class FeedbackCreate(BaseModel):
    session_id: int
    feedback_type: FeedbackType
    rating: Optional[float] = Field(None, ge=1, le=5, description="Rating from 1-5")
    comments: Optional[str] = None
    feedback_data: Optional[Dict[str, Any]] = None

class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: int
    feedback_type: str
    rating: Optional[float]
    comments: Optional[str]
    feedback_data: Optional[Dict[str, Any]]
    is_processed: bool
    created_at: datetime

# Outcome Schemas
class OutcomeCreate(BaseModel):
    session_id: int
    patient_id: str
    outcome_type: str = Field(..., description="Type of outcome (therapy_response, side_effects, etc.)")
    outcome_value: Optional[float] = None
    outcome_category: Optional[OutcomeCategory] = None
    measurement_date: Optional[datetime] = None
    notes: Optional[str] = None
    confidence_score: Optional[float] = Field(0.5, ge=0, le=1)

class OutcomeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: int
    patient_id: str
    outcome_type: str
    outcome_value: Optional[float]
    outcome_category: Optional[str]
    measurement_date: Optional[datetime]
    notes: Optional[str]
    confidence_score: float
    created_at: datetime

# Adaptive Analytics Schemas
class AdaptiveAnalyticCreate(BaseModel):
    session_id: int
    analytic_type: str = Field(..., description="Type of analytic (pattern_recognition, prediction, etc.)")
    model_version: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    accuracy_score: Optional[float] = Field(None, ge=0, le=1)
    improvement_metrics: Optional[Dict[str, Any]] = None

class AdaptiveAnalyticResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: int
    analytic_type: str
    model_version: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    accuracy_score: Optional[float]
    improvement_metrics: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

# Learning Pattern Schemas
class LearningPatternCreate(BaseModel):
    pattern_name: str
    pattern_type: str = Field(..., description="Type of pattern (comorbidity, medication, genetic)")
    modules_involved: List[str] = Field(..., description="List of modules that contributed")
    pattern_data: Dict[str, Any]
    confidence_level: Optional[float] = Field(0.5, ge=0, le=1)

class LearningPatternResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    pattern_name: str
    pattern_type: str
    modules_involved: List[str]
    pattern_data: Dict[str, Any]
    confidence_level: float
    usage_count: int
    success_rate: float
    is_validated: bool
    created_at: datetime
    updated_at: Optional[datetime]

class LearningPatternUpdate(BaseModel):
    pattern_name: Optional[str] = None
    confidence_level: Optional[float] = None
    is_validated: Optional[bool] = None

# Dashboard Analytics Schemas
class LearningDashboard(BaseModel):
    total_sessions: int
    total_feedback: int
    total_outcomes: int
    avg_rating: float
    active_patterns: int
    module_performance: Dict[str, Dict[str, Any]]
    recent_improvements: List[Dict[str, Any]]

class ModulePerformance(BaseModel):
    module_name: str
    session_count: int
    avg_rating: float
    outcome_success_rate: float
    improvement_trend: float

# New schemas for enhanced features

# Alert schemas
class AlertCreate(BaseModel):
    alert_type: str  # critical, warning, info, success
    severity: str  # high, medium, low
    title: str
    message: str
    patient_id: Optional[str] = None
    user_id: Optional[str] = None
    module_source: str  # eCdome, Clinical Context, Learning Engine
    alert_data: Optional[Dict[str, Any]] = None
    requires_action: bool = False
    expires_at: Optional[datetime] = None

class AlertUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_dismissed: Optional[bool] = None
    action_taken: Optional[str] = None

class AlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    title: str
    message: str
    patient_id: Optional[str]
    user_id: Optional[str]
    module_source: str
    alert_data: Optional[Dict[str, Any]]
    is_read: bool
    is_dismissed: bool
    requires_action: bool
    action_taken: Optional[str]
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Manual Feedback schemas
class ManualFeedbackCreate(BaseModel):
    session_id: Optional[int] = None
    feedback_category: str  # recommendation_quality, prediction_accuracy, usability
    subcategory: Optional[str] = None
    user_role: str  # physician, nurse, pharmacist, patient
    user_id: str
    rating_scale: str = "1-5"
    rating_value: float
    feedback_text: Optional[str] = None
    suggestions: Optional[str] = None
    tags: Optional[List[str]] = None
    context_data: Optional[Dict[str, Any]] = None

class ManualFeedbackUpdate(BaseModel):
    is_verified: Optional[bool] = None
    verification_notes: Optional[str] = None
    learning_impact: Optional[str] = None

class ManualFeedbackResponse(BaseModel):
    id: int
    session_id: Optional[int]
    feedback_category: str
    subcategory: Optional[str]
    user_role: str
    user_id: str
    rating_scale: str
    rating_value: float
    feedback_text: Optional[str]
    suggestions: Optional[str]
    tags: Optional[List[str]]
    context_data: Optional[Dict[str, Any]]
    is_verified: bool
    verification_notes: Optional[str]
    learning_impact: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Bookmark schemas
class BookmarkCreate(BaseModel):
    user_id: str
    bookmark_type: str  # pattern, alert, insight, case, recommendation
    title: str
    description: Optional[str] = None
    content_data: Dict[str, Any]
    source_module: str  # eCdome, Clinical Context, Learning Engine
    source_id: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    is_shared: bool = False

class BookmarkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    is_shared: Optional[bool] = None

class BookmarkResponse(BaseModel):
    id: int
    user_id: str
    bookmark_type: str
    title: str
    description: Optional[str]
    content_data: Dict[str, Any]
    source_module: str
    source_id: Optional[str]
    tags: Optional[List[str]]
    category: Optional[str]
    is_shared: bool
    access_count: int
    last_accessed: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Search schemas
class SearchQuery(BaseModel):
    query: str
    modules: Optional[List[str]] = None  # Filter by modules
    content_types: Optional[List[str]] = None  # Filter by content types
    min_confidence: Optional[float] = 0.0
    limit: int = 10
    include_related: bool = True

class SearchResult(BaseModel):
    id: int
    content_type: str
    content_id: str
    source_module: str
    title: str
    content_text: str
    keywords: Optional[List[str]]
    content_metadata: Optional[Dict[str, Any]]
    confidence_score: Optional[float]
    relevance_score: float  # Calculated based on query
    clinical_context: Optional[Dict[str, Any]]
    genomic_markers: Optional[Dict[str, Any]]

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResult]
    related_insights: Optional[List["RelatedInsightResponse"]] = None
    search_time_ms: float

# Related Insights schemas
class RelatedInsightCreate(BaseModel):
    primary_content_type: str
    primary_content_id: str
    related_content_type: str
    related_content_id: str
    relationship_type: str  # similar_case, related_pattern, contraindication
    similarity_score: float  # 0.0 to 1.0
    relationship_data: Optional[Dict[str, Any]] = None
    clinical_relevance: Optional[str] = None  # high, medium, low

class RelatedInsightResponse(BaseModel):
    id: int
    primary_content_type: str
    primary_content_id: str
    related_content_type: str
    related_content_id: str
    relationship_type: str
    similarity_score: float
    relationship_data: Optional[Dict[str, Any]]
    clinical_relevance: Optional[str]
    is_verified: bool
    verification_source: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Dashboard enhancement schemas
class DashboardAlert(BaseModel):
    id: int
    title: str
    message: str
    severity: str
    alert_type: str
    created_at: datetime
    requires_action: bool

class DashboardMetrics(BaseModel):
    total_alerts: int
    unread_alerts: int
    critical_alerts: int
    total_bookmarks: int
    recent_feedback_count: int
    avg_feedback_rating: float
    search_queries_today: int
    top_search_terms: List[str] 