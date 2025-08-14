from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID

from app.models.episode import TreatmentEpisode
from app.schemas.episode import EpisodeCreate, EpisodeUpdate, EpisodeResponse


class EpisodeService:
    """Service for managing treatment episodes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_episode(self, episode_data: EpisodeCreate) -> EpisodeResponse:
        """Create a new treatment episode"""
        db_episode = TreatmentEpisode(**episode_data.dict())
        self.db.add(db_episode)
        self.db.commit()
        self.db.refresh(db_episode)
        return EpisodeResponse.from_orm(db_episode)
    
    def get_episode(self, episode_id: UUID) -> Optional[EpisodeResponse]:
        """Get a specific episode by ID"""
        episode = self.db.query(TreatmentEpisode).filter(
            TreatmentEpisode.episode_id == episode_id
        ).first()
        return EpisodeResponse.from_orm(episode) if episode else None
    
    def get_patient_episodes(
        self, 
        patient_id: UUID, 
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[EpisodeResponse]:
        """Get all episodes for a specific patient"""
        query = self.db.query(TreatmentEpisode).filter(
            TreatmentEpisode.patient_id == patient_id
        )
        
        if status:
            query = query.filter(TreatmentEpisode.status == status)
        
        episodes = query.order_by(desc(TreatmentEpisode.start_date)).offset(offset).limit(limit).all()
        return [EpisodeResponse.from_orm(episode) for episode in episodes]
    
    def update_episode(self, episode_id: UUID, episode_data: EpisodeUpdate) -> Optional[EpisodeResponse]:
        """Update an existing episode"""
        episode = self.db.query(TreatmentEpisode).filter(
            TreatmentEpisode.episode_id == episode_id
        ).first()
        
        if not episode:
            return None
        
        update_data = episode_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(episode, field, value)
        
        self.db.commit()
        self.db.refresh(episode)
        return EpisodeResponse.from_orm(episode)
    
    def delete_episode(self, episode_id: UUID) -> bool:
        """Delete an episode"""
        episode = self.db.query(TreatmentEpisode).filter(
            TreatmentEpisode.episode_id == episode_id
        ).first()
        
        if not episode:
            return False
        
        self.db.delete(episode)
        self.db.commit()
        return True
    
    def get_active_episode(self, patient_id: UUID) -> Optional[EpisodeResponse]:
        """Get the currently active episode for a patient"""
        episode = self.db.query(TreatmentEpisode).filter(
            TreatmentEpisode.patient_id == patient_id,
            TreatmentEpisode.status == "active"
        ).first()
        return EpisodeResponse.from_orm(episode) if episode else None
    
    def complete_episode(self, episode_id: UUID) -> Optional[EpisodeResponse]:
        """Mark an episode as completed"""
        episode = self.db.query(TreatmentEpisode).filter(
            TreatmentEpisode.episode_id == episode_id
        ).first()
        
        if not episode:
            return None
        
        episode.status = "completed"
        self.db.commit()
        self.db.refresh(episode)
        return EpisodeResponse.from_orm(episode)
    
    def discontinue_episode(self, episode_id: UUID, reason: str = None) -> Optional[EpisodeResponse]:
        """Discontinue an episode"""
        episode = self.db.query(TreatmentEpisode).filter(
            TreatmentEpisode.episode_id == episode_id
        ).first()
        
        if not episode:
            return None
        
        episode.status = "discontinued"
        if reason and episode.treatment_plan:
            if not isinstance(episode.treatment_plan, dict):
                episode.treatment_plan = {}
            episode.treatment_plan["discontinuation_reason"] = reason
        
        self.db.commit()
        self.db.refresh(episode)
        return EpisodeResponse.from_orm(episode)
    
    def update_treatment_plan(self, episode_id: UUID, treatment_plan: dict) -> Optional[EpisodeResponse]:
        """Update the treatment plan for an episode"""
        episode = self.db.query(TreatmentEpisode).filter(
            TreatmentEpisode.episode_id == episode_id
        ).first()
        
        if not episode:
            return None
        
        episode.treatment_plan = treatment_plan
        self.db.commit()
        self.db.refresh(episode)
        return EpisodeResponse.from_orm(episode) 