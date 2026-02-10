import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class TreatmentEpisode(Base):
    """Treatment episode model"""
    
    __tablename__ = "treatment_episodes"
    
    episode_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    treatment_plan = Column(JSONB, nullable=True)  # Store Abena recommendations
    provider_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String(20), nullable=False, default="active", index=True)
    
    def __repr__(self):
        return f"<TreatmentEpisode(episode_id={self.episode_id}, patient_id={self.patient_id}, status={self.status})>" 