from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class LearningSession(Base):
    """Tracks learning sessions across all modules"""
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    module_name = Column(String(100), nullable=False)  # eCdome, Clinical Context, etc.
    session_type = Column(String(50), nullable=False)  # analysis, recommendation, feedback
    user_id = Column(String(100), nullable=True)
    patient_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    feedbacks = relationship("Feedback", back_populates="session")
    outcomes = relationship("Outcome", back_populates="session")
    analytics = relationship("AdaptiveAnalytic", back_populates="session")

class Feedback(Base):
    """Stores feedback from providers and patients"""
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("learning_sessions.id"))
    feedback_type = Column(String(50), nullable=False)  # provider, patient, system
    rating = Column(Float, nullable=True)  # 1-5 scale
    comments = Column(Text, nullable=True)
    feedback_data = Column(JSON, nullable=True)  # Structured feedback
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("LearningSession", back_populates="feedbacks")

class Outcome(Base):
    """Tracks patient outcomes for adaptive learning"""
    __tablename__ = "outcomes"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("learning_sessions.id"))
    patient_id = Column(String(100), nullable=False)
    outcome_type = Column(String(100), nullable=False)  # therapy_response, side_effects, etc.
    outcome_value = Column(Float, nullable=True)
    outcome_category = Column(String(50), nullable=True)  # improved, stable, worsened
    measurement_date = Column(DateTime(timezone=True))
    notes = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("LearningSession", back_populates="outcomes")

class AdaptiveAnalytic(Base):
    """Stores adaptive analytics and model improvements"""
    __tablename__ = "adaptive_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("learning_sessions.id"))
    analytic_type = Column(String(100), nullable=False)  # pattern_recognition, prediction, etc.
    model_version = Column(String(50), nullable=False)
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=False)
    accuracy_score = Column(Float, nullable=True)
    improvement_metrics = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    session = relationship("LearningSession", back_populates="analytics")

class LearningPattern(Base):
    """Stores discovered patterns from cross-module learning"""
    __tablename__ = "learning_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    pattern_name = Column(String(200), nullable=False)
    pattern_type = Column(String(100), nullable=False)  # comorbidity, medication, genetic
    modules_involved = Column(JSON, nullable=False)  # List of modules that contributed
    pattern_data = Column(JSON, nullable=False)
    confidence_level = Column(Float, default=0.5)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    is_validated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Alert(Base):
    """Real-time clinical alerts system"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(100), nullable=False)  # critical, warning, info, success
    severity = Column(String(50), nullable=False)  # high, medium, low
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    patient_id = Column(String(100), nullable=True)
    user_id = Column(String(100), nullable=True)
    module_source = Column(String(100), nullable=False)  # eCdome, Clinical Context, Learning Engine
    alert_data = Column(JSON, nullable=True)  # Additional structured data
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    requires_action = Column(Boolean, default=False)
    action_taken = Column(String(200), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ManualFeedback(Base):
    """Enhanced manual feedback system for learning improvement"""
    __tablename__ = "manual_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("learning_sessions.id"), nullable=True)
    feedback_category = Column(String(100), nullable=False)  # recommendation_quality, prediction_accuracy, usability
    subcategory = Column(String(100), nullable=True)
    user_role = Column(String(50), nullable=False)  # physician, nurse, pharmacist, patient
    user_id = Column(String(100), nullable=False)
    rating_scale = Column(String(20), default="1-5")  # 1-5, 1-10, boolean
    rating_value = Column(Float, nullable=False)
    feedback_text = Column(Text, nullable=True)
    suggestions = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # Searchable tags
    context_data = Column(JSON, nullable=True)  # Clinical context when feedback was given
    is_verified = Column(Boolean, default=False)
    verification_notes = Column(Text, nullable=True)
    learning_impact = Column(Text, nullable=True)  # How this feedback improved the system
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Bookmark(Base):
    """Bookmark system for saving important discoveries and insights"""
    __tablename__ = "bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    bookmark_type = Column(String(100), nullable=False)  # pattern, alert, insight, case, recommendation
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    content_data = Column(JSON, nullable=False)  # The actual bookmarked content
    source_module = Column(String(100), nullable=False)  # eCdome, Clinical Context, Learning Engine
    source_id = Column(String(100), nullable=True)  # ID of the original content
    tags = Column(JSON, nullable=True)  # User-defined tags
    category = Column(String(100), nullable=True)  # User-defined category
    is_shared = Column(Boolean, default=False)  # Can other users see this bookmark
    access_count = Column(Integer, default=0)  # How often this bookmark is accessed
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SearchIndex(Base):
    """Search index for cross-module semantic search"""
    __tablename__ = "search_index"
    
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(100), nullable=False)  # pattern, alert, outcome, feedback, case
    content_id = Column(String(100), nullable=False)  # ID of the original content
    source_module = Column(String(100), nullable=False)  # eCdome, Clinical Context, Learning Engine
    title = Column(String(200), nullable=False)
    content_text = Column(Text, nullable=False)  # Searchable text content
    keywords = Column(JSON, nullable=True)  # Extracted keywords
    content_metadata = Column(JSON, nullable=True)  # Additional searchable metadata (renamed from metadata)
    confidence_score = Column(Float, nullable=True)
    patient_demographics = Column(JSON, nullable=True)  # For case-based searches
    clinical_context = Column(JSON, nullable=True)  # Comorbidities, medications, etc.
    genomic_markers = Column(JSON, nullable=True)  # For genomic pattern searches
    is_validated = Column(Boolean, default=False)
    validation_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class RelatedInsight(Base):
    """Related insights and similar cases system"""
    __tablename__ = "related_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    primary_content_type = Column(String(100), nullable=False)
    primary_content_id = Column(String(100), nullable=False)
    related_content_type = Column(String(100), nullable=False)
    related_content_id = Column(String(100), nullable=False)
    relationship_type = Column(String(100), nullable=False)  # similar_case, related_pattern, contraindication
    similarity_score = Column(Float, nullable=False)  # 0.0 to 1.0
    relationship_data = Column(JSON, nullable=True)  # Details about the relationship
    clinical_relevance = Column(String(100), nullable=True)  # high, medium, low
    is_verified = Column(Boolean, default=False)
    verification_source = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 