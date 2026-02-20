#!/usr/bin/env python3
"""
Example usage of the Outcome Tracking Module

This script demonstrates how to use the outcome tracking module
to record patient outcomes and manage treatment episodes.
"""

import uuid
from datetime import date, datetime
from app.database import SessionLocal
from app.services.outcome_service import OutcomeService
from app.services.episode_service import EpisodeService
from app.schemas.outcome import OutcomeCreate
from app.schemas.episode import EpisodeCreate


def main():
    """Main example function"""
    print("=== Outcome Tracking Module Example ===\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Initialize services
        outcome_service = OutcomeService(db)
        episode_service = EpisodeService(db)
        
        # Generate sample UUIDs
        patient_id = str(uuid.uuid4())
        provider_id = str(uuid.uuid4())
        
        print(f"Patient ID: {patient_id}")
        print(f"Provider ID: {provider_id}\n")
        
        # Example 1: Create a treatment episode
        print("1. Creating a treatment episode...")
        episode_data = EpisodeCreate(
            patient_id=patient_id,
            start_date=date(2024, 1, 15),
            treatment_plan={
                "recommendations": [
                    "Physical therapy 3x per week",
                    "Pain management with prescribed medication",
                    "Home exercise program"
                ],
                "goals": [
                    "Reduce pain score from 8 to 4",
                    "Improve functional mobility",
                    "Return to work within 6 weeks"
                ],
                "duration": "6 weeks",
                "provider_notes": "Patient presents with lower back pain"
            },
            provider_id=provider_id,
            status="active"
        )
        
        episode = episode_service.create_episode(episode_data)
        print(f"   Episode created: {episode.episode_id}")
        print(f"   Status: {episode.status}")
        print(f"   Treatment plan: {len(episode.treatment_plan['recommendations'])} recommendations\n")
        
        # Example 2: Record multiple outcomes over time
        print("2. Recording patient outcomes over time...")
        
        outcomes_data = [
            {
                "date": "2024-01-15",
                "pain_score": 8.0,
                "functional_assessment": 45.0
            },
            {
                "date": "2024-01-22",
                "pain_score": 7.0,
                "functional_assessment": 52.0
            },
            {
                "date": "2024-01-29",
                "pain_score": 6.5,
                "functional_assessment": 58.0
            },
            {
                "date": "2024-02-05",
                "pain_score": 5.5,
                "functional_assessment": 65.0
            },
            {
                "date": "2024-02-12",
                "pain_score": 4.5,
                "functional_assessment": 72.0
            }
        ]
        
        for outcome_data in outcomes_data:
            # Record pain score
            pain_outcome = OutcomeCreate(
                patient_id=patient_id,
                measurement_date=date.fromisoformat(outcome_data["date"]),
                outcome_type="pain_score",
                outcome_value=outcome_data["pain_score"],
                measurement_method="visual_analog_scale"
            )
            outcome_service.create_outcome(pain_outcome)
            
            # Record functional assessment
            functional_outcome = OutcomeCreate(
                patient_id=patient_id,
                measurement_date=date.fromisoformat(outcome_data["date"]),
                outcome_type="functional_assessment",
                outcome_value=outcome_data["functional_assessment"],
                measurement_method="standardized_test"
            )
            outcome_service.create_outcome(functional_outcome)
            
            print(f"   {outcome_data['date']}: Pain={outcome_data['pain_score']}, Function={outcome_data['functional_assessment']}")
        
        print()
        
        # Example 3: Get patient outcomes
        print("3. Retrieving patient outcomes...")
        patient_outcomes = outcome_service.get_patient_outcomes(patient_id)
        print(f"   Total outcomes recorded: {len(patient_outcomes)}")
        
        # Group by type
        pain_outcomes = [o for o in patient_outcomes if o.outcome_type == "pain_score"]
        functional_outcomes = [o for o in patient_outcomes if o.outcome_type == "functional_assessment"]
        
        print(f"   Pain scores: {len(pain_outcomes)}")
        print(f"   Functional assessments: {len(functional_outcomes)}\n")
        
        # Example 4: Get outcome statistics
        print("4. Analyzing outcome statistics...")
        
        pain_stats = outcome_service.get_outcome_statistics(patient_id, "pain_score")
        functional_stats = outcome_service.get_outcome_statistics(patient_id, "functional_assessment")
        
        print("   Pain Score Statistics:")
        print(f"     Count: {pain_stats['count']}")
        print(f"     Average: {pain_stats['average']:.1f}")
        print(f"     Range: {pain_stats['min']:.1f} - {pain_stats['max']:.1f}")
        print(f"     Trend: {pain_stats['trend']}")
        print(f"     Latest: {pain_stats['latest_value']:.1f}")
        
        print("\n   Functional Assessment Statistics:")
        print(f"     Count: {functional_stats['count']}")
        print(f"     Average: {functional_stats['average']:.1f}")
        print(f"     Range: {functional_stats['min']:.1f} - {functional_stats['max']:.1f}")
        print(f"     Trend: {functional_stats['trend']}")
        print(f"     Latest: {functional_stats['latest_value']:.1f}\n")
        
        # Example 5: Update treatment plan
        print("5. Updating treatment plan...")
        updated_plan = {
            "recommendations": [
                "Physical therapy 2x per week (reduced frequency)",
                "Pain management with prescribed medication",
                "Home exercise program",
                "Gradual return to work program"
            ],
            "goals": [
                "Maintain pain score below 5",
                "Achieve functional score above 70",
                "Full return to work within 2 weeks"
            ],
            "duration": "2 weeks remaining",
            "provider_notes": "Patient showing excellent progress. Ready for work return.",
            "progress_notes": "Pain reduced by 44%, function improved by 60%"
        }
        
        episode_service.update_treatment_plan(episode.episode_id, updated_plan)
        print("   Treatment plan updated with progress notes\n")
        
        # Example 6: Complete the episode
        print("6. Completing the treatment episode...")
        completed_episode = episode_service.complete_episode(episode.episode_id)
        print(f"   Episode status: {completed_episode.status}")
        print(f"   Episode completed successfully!\n")
        
        # Example 7: Get episode history
        print("7. Episode history...")
        all_episodes = episode_service.get_patient_episodes(patient_id)
        print(f"   Total episodes: {len(all_episodes)}")
        for ep in all_episodes:
            print(f"   Episode {ep.episode_id[:8]}...: {ep.status} (started {ep.start_date})")
        
        print("\n=== Example completed successfully! ===")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main() 