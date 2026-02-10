"""
Database client for Quantum Healthcare Service
Handles database connections and operations
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
import logging
from typing import Optional, Dict, Any, List
import json

logger = logging.getLogger(__name__)

class QuantumDBClient:
    """Database client for quantum healthcare operations"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'postgresql://abena_user:abena_password@postgres:5432/abena_ihr')
        self.pool = None
        # Don't initialize pool on import - wait until first use
        # This prevents build failures if database isn't available
    
    def _init_pool(self):
        """Initialize connection pool (lazy initialization)"""
        if self.pool is not None:
            return  # Already initialized
        
        try:
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=self.database_url
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize database pool: {e}. Database features will be disabled.")
            self.pool = None
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool"""
        # Lazy initialization
        if self.pool is None:
            self._init_pool()
        
        if not self.pool:
            raise Exception("Database pool not initialized. Check DATABASE_URL environment variable.")
        
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            self.pool.putconn(conn)
    
    def save_analysis_result(
        self,
        patient_id: str,
        quantum_health_score: float,
        system_balance: float,
        analysis_data: Dict[str, Any],
        drug_interactions: Optional[List[Dict]] = None,
        herbal_recommendations: Optional[List[Dict]] = None,
        biomarker_analysis: Optional[Dict] = None,
        recommendations: Optional[List[str]] = None,
        created_by: Optional[str] = None
    ) -> Optional[int]:
        """Save quantum analysis result to database"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        INSERT INTO quantum_analysis_results (
                            patient_id, quantum_health_score, system_balance,
                            analysis_data, drug_interactions, herbal_recommendations,
                            biomarker_analysis, recommendations, created_by
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        patient_id,
                        quantum_health_score,
                        system_balance,
                        json.dumps(analysis_data),
                        json.dumps(drug_interactions) if drug_interactions else None,
                        json.dumps(herbal_recommendations) if herbal_recommendations else None,
                        json.dumps(biomarker_analysis) if biomarker_analysis else None,
                        recommendations,
                        created_by
                    ))
                    result = cur.fetchone()
                    analysis_id = result['id'] if result else None
                    
                    # Log to history
                    if analysis_id:
                        cur.execute("""
                            INSERT INTO quantum_analysis_history (
                                patient_id, analysis_id, status, computation_time_ms
                            ) VALUES (%s, %s, %s, %s)
                        """, (patient_id, analysis_id, 'completed', None))
                    
                    logger.info(f"Saved analysis result for patient {patient_id}, ID: {analysis_id}")
                    return analysis_id
        except Exception as e:
            logger.error(f"Error saving analysis result: {e}")
            return None
    
    def get_patient_analyses(self, patient_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent quantum analyses for a patient"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, analysis_timestamp, quantum_health_score,
                               system_balance, analysis_data, recommendations,
                               created_at
                        FROM quantum_analysis_results
                        WHERE patient_id = %s
                        ORDER BY analysis_timestamp DESC
                        LIMIT %s
                    """, (patient_id, limit))
                    results = cur.fetchall()
                    return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error fetching patient analyses: {e}")
            return []
    
    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """Get specific analysis by ID"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT * FROM quantum_analysis_results
                        WHERE id = %s
                    """, (analysis_id,))
                    result = cur.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching analysis by ID: {e}")
            return None
    
    def log_analysis_history(
        self,
        patient_id: str,
        analysis_id: Optional[int] = None,
        analysis_type: str = 'full_analysis',
        status: str = 'completed',
        error_message: Optional[str] = None,
        computation_time_ms: Optional[int] = None,
        input_data: Optional[Dict] = None
    ):
        """Log analysis operation to history table"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO quantum_analysis_history (
                            patient_id, analysis_id, analysis_type, status,
                            error_message, computation_time_ms, input_data
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        patient_id,
                        analysis_id,
                        analysis_type,
                        status,
                        error_message,
                        computation_time_ms,
                        json.dumps(input_data) if input_data else None
                    ))
                    logger.info(f"Logged analysis history for patient {patient_id}")
        except Exception as e:
            logger.error(f"Error logging analysis history: {e}")
    
    def get_drug_interaction(
        self,
        medication1: str,
        medication2: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached drug interaction result"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT * FROM quantum_drug_interactions
                        WHERE (medication1 = %s AND medication2 = %s)
                           OR (medication1 = %s AND medication2 = %s)
                    """, (medication1, medication2, medication2, medication1))
                    result = cur.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching drug interaction: {e}")
            return None
    
    def cache_drug_interaction(
        self,
        medication1: str,
        medication2: str,
        interaction_score: float,
        severity: str,
        recommendation: str,
        quantum_model_version: str = '1.0'
    ):
        """Cache drug interaction result"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO quantum_drug_interactions (
                            medication1, medication2, interaction_score,
                            severity, recommendation, quantum_model_version
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (medication1, medication2)
                        DO UPDATE SET
                            interaction_score = EXCLUDED.interaction_score,
                            severity = EXCLUDED.severity,
                            recommendation = EXCLUDED.recommendation,
                            quantum_model_version = EXCLUDED.quantum_model_version,
                            last_updated = CURRENT_TIMESTAMP
                    """, (
                        medication1, medication2, interaction_score,
                        severity, recommendation, quantum_model_version
                    ))
                    logger.info(f"Cached drug interaction: {medication1} + {medication2}")
        except Exception as e:
            logger.error(f"Error caching drug interaction: {e}")
    
    def get_herbal_compatibility(
        self,
        herb_name: str,
        medication: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get cached herbal compatibility result"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    if medication:
                        cur.execute("""
                            SELECT * FROM quantum_herbal_compatibility
                            WHERE herb_name = %s AND medication = %s
                        """, (herb_name, medication))
                    else:
                        cur.execute("""
                            SELECT * FROM quantum_herbal_compatibility
                            WHERE herb_name = %s AND medication IS NULL
                        """, (herb_name,))
                    result = cur.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching herbal compatibility: {e}")
            return None
    
    def cache_herbal_compatibility(
        self,
        herb_name: str,
        medication: Optional[str],
        compatibility_score: float,
        benefits: List[str],
        warnings: List[str],
        contraindications: List[str],
        quantum_model_version: str = '1.0'
    ):
        """Cache herbal compatibility result"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO quantum_herbal_compatibility (
                            herb_name, medication, compatibility_score,
                            benefits, warnings, contraindications, quantum_model_version
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (herb_name, medication)
                        DO UPDATE SET
                            compatibility_score = EXCLUDED.compatibility_score,
                            benefits = EXCLUDED.benefits,
                            warnings = EXCLUDED.warnings,
                            contraindications = EXCLUDED.contraindications,
                            quantum_model_version = EXCLUDED.quantum_model_version,
                            last_updated = CURRENT_TIMESTAMP
                    """, (
                        herb_name, medication, compatibility_score,
                        benefits, warnings, contraindications, quantum_model_version
                    ))
                    logger.info(f"Cached herbal compatibility: {herb_name}")
        except Exception as e:
            logger.error(f"Error caching herbal compatibility: {e}")

# Global instance
db_client = QuantumDBClient()



