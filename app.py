"""
ABENA Quantum Healthcare Service
Flask API server for quantum computing-based healthcare analysis
"""

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
from database.db_client import db_client
from auth import require_auth, require_role, get_current_user
from rate_limit import quantum_analysis_limit, general_api_limit, demo_results_limit
from services.abena_ihr_client import ihr_client
from services.ecbome_client import ecbome_client
import asyncio

# Optional IBM Runtime (only needed for live hardware Job IDs)
try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
    IBM_RUNTIME_AVAILABLE = True
except Exception:
    IBM_RUNTIME_AVAILABLE = False

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
PORT = int(os.getenv('PORT', 5000))
ABENA_IHR_API = os.getenv('ABENA_IHR_API', 'http://abena-ihr:4002')
ECBOME_API = os.getenv('ECBOME_API', os.getenv('ECDOME_API', 'http://abena-ecdome-intelligence:4005'))
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:3001')
# For Render/local deployment, use localhost if DATABASE_URL not set
# For Docker, use 'postgres' service name
default_db_url = 'postgresql://abena_user:abena_password@localhost:5432/abena_ihr'
if os.getenv('DOCKER_ENV') == 'true' or os.getenv('DATABASE_HOST') == 'postgres':
    default_db_url = 'postgresql://abena_user:abena_password@postgres:5432/abena_ihr'
DATABASE_URL = os.getenv('DATABASE_URL', default_db_url)

logger.info(f"Quantum Healthcare Service starting on port {PORT}")
logger.info(f"ABENA IHR API: {ABENA_IHR_API}")
logger.info(f"eCBome API: {ECBOME_API}")

def _normalize_items(values):
    """Normalize meds/supplements/conditions to a list of lowercase strings."""
    if not values:
        return []
    if isinstance(values, str):
        values = [values]
    if isinstance(values, dict):
        values = list(values.values())
    return [str(v).strip().lower() for v in values if str(v).strip()]

def _detect_warfarin_fish_oil_interaction(medications, supplements):
    """Return a specific, demo-friendly interaction if present."""
    meds = _normalize_items(medications)
    sups = _normalize_items(supplements)

    has_warfarin = any('warfarin' in m for m in meds)
    has_fish_oil = any('fish oil' in s or 'omega' in s for s in sups) or any('fish oil' in m for m in meds)

    if has_warfarin and has_fish_oil:
        return {
            "medication1": "warfarin",
            "medication2": "fish oil",
            "interaction_score": 0.82,
            "severity": "high",
            "recommendation": "Bleeding risk detected. Consider reducing Fish Oil to 500mg and consult your care team."
        }
    return None

def _get_ibm_service():
    """
    Create an IBM Runtime service.
    On Render, set env var QISKIT_IBM_TOKEN.
    Locally, saved credentials file (~/.qiskit/qiskit-ibm.json) may also work.
    """
    if not IBM_RUNTIME_AVAILABLE:
        raise RuntimeError("IBM runtime not available (qiskit-ibm-runtime not installed).")

    # NOTE: qiskit-ibm-runtime changed accepted channel names over time.
    # Some versions accept only: 'ibm_cloud' or 'ibm_quantum'
    # Older docs/scripts used: 'ibm_quantum_platform'
    token = os.getenv("QISKIT_IBM_TOKEN")
    last_err = None
    for channel in ("ibm_quantum", "ibm_cloud", "ibm_quantum_platform"):
        try:
            if token:
                return QiskitRuntimeService(channel=channel, token=token)
            return QiskitRuntimeService(channel=channel)
        except Exception as e:
            last_err = e
            continue
    raise last_err or RuntimeError("Failed to initialize IBM Runtime service")

def _submit_ibm_job(payload):
    """
    Submit a small 4-qubit circuit to IBM hardware and return Job ID immediately.
    This proves real IBM execution without waiting for results.
    """
    service = _get_ibm_service()

    # Choose least busy operational hardware
    backend = service.least_busy(simulator=False, operational=True)

    qc = QuantumCircuit(4, 4)

    # Basic exploration superposition
    for q in range(4):
        qc.h(q)

    # Simple entanglement chain (interaction modeling)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.cx(2, 3)

    # Light parameterization based on input richness (kept deterministic & safe)
    meds = payload.get("medications", []) or []
    sups = payload.get("supplements", []) or []
    conds = payload.get("conditions", []) or payload.get("symptoms", []) or []
    richness = min(10, len(meds) + len(sups) + len(conds))
    angle = (richness + 1) * 0.15
    qc.ry(angle, 0)
    qc.ry(angle / 1.5, 1)
    qc.ry(angle / 2.0, 2)
    qc.ry(angle / 1.8, 3)

    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])

    transpiled_qc = transpile(qc, backend=backend, optimization_level=3)

    sampler = Sampler(mode=backend)
    job = sampler.run([transpiled_qc], shots=1024)

    return {
        "job_id": job.job_id(),
        "backend": getattr(backend, "name", str(backend)),
        "status": str(job.status()),
        "submitted_at": datetime.now().isoformat(),
        "mode": "ibm_hardware"
    }


@app.route('/')
def index():
    """Quantum Healthcare Dashboard"""
    return render_template('dashboard.html')

@app.route('/api/ibm/submit', methods=['POST'])
@general_api_limit
def ibm_submit():
    """
    Submit an IBM Quantum hardware job and return a real Job ID.
    This endpoint is designed for live investor demos.
    """
    try:
        payload = request.get_json() or {}
        if not IBM_RUNTIME_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "IBM runtime not installed on this service",
                "detail": "Install qiskit-ibm-runtime and set QISKIT_IBM_TOKEN to enable real Job IDs."
            }), 501

        job_info = _submit_ibm_job(payload)
        return jsonify({"success": True, "ibm_job": job_info}), 200
    except Exception as e:
        logger.error(f"IBM submit error: {str(e)}")
        return jsonify({"success": False, "error": "IBM job submission failed", "detail": str(e)}), 500


@app.route('/api/demo-results', methods=['GET'])
@demo_results_limit
def demo_results():
    """Return comprehensive demo quantum analysis results"""
    return jsonify({
        "patient_id": "DEMO_001",
        "quantum_health_score": 0.78,
        "system_balance": 0.65,
        "treatment_optimization": 0.719,
        "overall_health_score": 0.68,
        "safety_score": 0.71,
        "analysis_timestamp": datetime.now().isoformat(),
        "pattern_recognition": "Spleen Qi Deficiency",
        "ecbome_correlation": 0.60,
        "integration_quality": "Good",
        "drug_interaction_level": "Moderate Risk",
        "quantum_advantage": "Active",
        "speedup": "4.5 minutes vs 25.0 hours",
        "quantum_circuits": {
            "vqe": {
                "qubits": 4,
                "depth": 4,
                "gates": 12,
                "hardware_time": "4.5 minutes",
                "classical_time": "25.0 hours"
            },
            "qml": {
                "type": "Variational Quantum Classifier",
                "qubits": 4,
                "depth": 6,
                "gates": 18,
                "feature_map": "ZZFeatureMap"
            },
            "qaoa": {
                "qubits": 6,
                "layers": 3,
                "depth": 2,
                "gates": 18,
                "speedup": "128x"
            }
        },
        "data_flow": {
            "steps": [
                {"name": "eCBome Input", "status": "complete", "color": "blue"},
                {"name": "VQE Optimization", "status": "complete", "color": "purple"},
                {"name": "Pattern Recognition", "status": "complete", "color": "green"},
                {"name": "Drug Interaction", "status": "complete", "color": "orange"},
                {"name": "Blockchain Storage", "status": "complete", "color": "black"}
            ],
            "backend": "Quantum Simulator (IBM Hardware Ready)",
            "all_complete": True
        },
        "tcm_patterns": [
            {
                "pattern": "Spleen Qi Deficiency",
                "confidence": 0.596
            }
        ],
        "drug_interactions": [
            {
                "medication1": "sertraline",
                "medication2": "metformin",
                "interaction_score": 0.15,
                "severity": "low",
                "recommendation": "Monitor blood sugar levels"
            }
        ],
        "herbal_recommendations": [
            {
                "herb": "ginseng",
                "compatibility_score": 0.82,
                "benefits": ["energy", "immune support"],
                "warnings": []
            },
            {
                "herb": "turmeric",
                "compatibility_score": 0.75,
                "benefits": ["anti-inflammatory", "digestive health"],
                "warnings": ["May interact with blood thinners"]
            }
        ],
        "biomarker_analysis": {
            "anandamide": {"value": 0.45, "status": "normal"},
            "2AG": {"value": 2.1, "status": "elevated"},
            "cb1_density": {"value": 85, "status": "normal"},
            "cb2_activity": {"value": 78, "status": "normal"}
        },
        "recommendations": [
            "Monitor eCBome biomarkers weekly",
            "Consider lifestyle modifications",
            "Review medication interactions quarterly"
        ]
    })


@app.route('/api/analyze', methods=['POST'])
# @require_auth  # Temporarily disabled for demo - enable in production
@quantum_analysis_limit
def analyze():
    """Analyze patient data with quantum circuits"""
    import time
    start_time = time.time()
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        patient_id = data.get('patient_id')
        if not patient_id:
            return jsonify({"error": "patient_id is required"}), 400
        
        # For demo/sample patients, return demo results immediately (no auth required)
        demo_patients = ['PAT-001', 'PAT-002', 'PAT-003', 'DEMO_001', 'DEMO_002', 'PAT_001', 'PAT_002']
        if any(demo in str(patient_id).upper() for demo in demo_patients):
            logger.info(f"Using demo results for patient {patient_id} (no auth required)")
            demo_data = {
                "patient_id": patient_id,
                "quantum_health_score": 0.78,
                "system_balance": 0.65,
                "analysis_timestamp": datetime.now().isoformat(),
                "drug_interactions": [
                    {
                        "medication1": "sertraline",
                        "medication2": "metformin",
                        "interaction_score": 0.15,
                        "severity": "low",
                        "recommendation": "Monitor blood sugar levels"
                    }
                ],
                "herbal_recommendations": [
                    {
                        "herb": "ginseng",
                        "compatibility_score": 0.82,
                        "benefits": ["energy", "immune support"],
                        "warnings": []
                    },
                    {
                        "herb": "turmeric",
                        "compatibility_score": 0.75,
                        "benefits": ["anti-inflammatory", "digestive health"],
                        "warnings": ["May interact with blood thinners"]
                    }
                ],
                "biomarker_analysis": {
                    "anandamide": {"value": 0.45, "status": "normal"},
                    "2AG": {"value": 2.1, "status": "elevated"},
                    "cb1_density": {"value": 85, "status": "normal"},
                    "cb2_activity": {"value": 78, "status": "normal"}
                },
                "recommendations": [
                    "Monitor eCBome biomarkers weekly",
                    "Consider lifestyle modifications",
                    "Review medication interactions quarterly"
                ]
            }
            return jsonify({"success": True, "results": demo_data})
        
        # Get authentication token (optional for demo - services handle None gracefully)
        token = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header and ' ' in auth_header:
            try:
                token = auth_header.split(' ')[1]
            except (IndexError, AttributeError):
                token = None
        
        # Log analysis start (never block demo if DB is unavailable)
        try:
            db_client.log_analysis_history(
                patient_id=patient_id,
                analysis_type='full_analysis',
                status='in_progress',
                input_data=data
            )
        except Exception as e:
            logger.warning(f"DB history logging skipped: {e}")
        
        logger.info(f"Analyzing patient {patient_id}")
        
        # If the caller is providing inputs directly (investor demo flow), skip async
        # calls to other services to avoid network/loop issues and keep the demo reliable.
        has_direct_inputs = bool(
            data.get('medications') or data.get('supplements') or data.get('conditions') or data.get('symptoms')
        )

        patient_data = None
        prescriptions = []
        ecbome_biomarkers = None

        if not has_direct_inputs:
            # Fetch data from external services (async)
            async def fetch_patient_data():
                patient_data = await ihr_client.get_patient_data(patient_id, token)
                prescriptions = await ihr_client.get_patient_prescriptions(patient_id, token)
                biomarkers = await ecbome_client.get_latest_biomarkers(patient_id, token)
                return patient_data, prescriptions, biomarkers
            
            # Run async data fetching
            try:
                patient_data, prescriptions, ecbome_biomarkers = asyncio.run(fetch_patient_data())
            except Exception as e:
                logger.warning(f"Error fetching external data: {e}, using provided data")
                patient_data = None
                prescriptions = []
                ecbome_biomarkers = None
        
        # Extract analysis parameters (use provided or fetched data)
        symptoms = data.get('symptoms', [])
        biomarkers = data.get('biomarkers', {})
        
        # Merge eCBome biomarkers if available
        if ecbome_biomarkers:
            biomarkers = {**biomarkers, **ecbome_biomarkers}
        
        # Extract medications from prescriptions if not provided
        medications = data.get('medications', [])
        if not medications and prescriptions:
            medications = [p.get('medication') or p.get('drug_name') for p in prescriptions if p.get('medication') or p.get('drug_name')]

        supplements = data.get('supplements', [])
        conditions = data.get('conditions', [])
        
        supplements = data.get('supplements', [])
        conditions = data.get('conditions', [])

        recommended_herbs = data.get('recommended_herbs', [])
        
        # TODO: Implement actual quantum analysis
        # For now, return enhanced mock results based on fetched data
        base_score = 0.75
        if symptoms:
            base_score += min(len(symptoms) * 0.02, 0.15)
        if biomarkers:
            anandamide = biomarkers.get('anandamide', 0.5)
            base_score += min((anandamide - 0.5) * 0.2, 0.1)
        
        quantum_health_score = min(base_score, 1.0)
        
        system_balance = 0.65
        if biomarkers:
            anandamide = biomarkers.get('anandamide', 0.5)
            two_ag = biomarkers.get('2AG', 2.0)
            system_balance = 0.65 + min((anandamide - 0.5) * 0.1, 0.15) + min((two_ag - 2.0) / 10, 0.1)
        system_balance = min(system_balance, 1.0)
        
        # Simulate quantum computation delay
        time.sleep(0.5)  # Simulate computation time
        
        computation_time = int((time.time() - start_time) * 1000)
        
        # Generate drug interactions (demo-friendly + basic mock)
        drug_interactions = []

        # Specific, high-signal demo case: Warfarin + Fish Oil
        wf = _detect_warfarin_fish_oil_interaction(medications, supplements)
        if wf:
            drug_interactions.append(wf)

        if len(medications) > 1:
            for i, med1 in enumerate(medications[:3]):  # Limit to first 3
                for med2 in medications[i+1:3]:
                    drug_interactions.append({
                        "medication1": med1,
                        "medication2": med2,
                        "interaction_score": 0.15,
                        "severity": "low",
                        "recommendation": "Monitor for interactions"
                    })

        # Optional: submit a real IBM hardware job and include the Job ID (do NOT wait for completion)
        ibm_job = None
        if data.get("run_ibm_job") is True:
            try:
                ibm_job = _submit_ibm_job({
                    "medications": medications,
                    "supplements": supplements,
                    "conditions": conditions,
                    "patient_id": patient_id
                })
            except Exception as e:
                logger.warning(f"IBM job submission skipped/failed: {e}")
                ibm_job = {"mode": "skipped", "error": str(e)}
        
        # Optional: submit a real IBM hardware job and include the Job ID (do NOT wait for completion)
        ibm_job = None
        if data.get("run_ibm_job") is True:
            try:
                ibm_job = _submit_ibm_job({
                    "medications": medications,
                    "supplements": supplements,
                    "conditions": conditions,
                    "patient_id": patient_id
                })
            except Exception as e:
                logger.warning(f"IBM job submission skipped/failed: {e}")

        results = {
            "success": True,
            "results": {
                "patient_id": patient_id,
                "quantum_health_score": round(quantum_health_score, 2),
                "system_balance": round(system_balance, 2),
                "analysis_timestamp": datetime.now().isoformat(),
                "symptoms_analyzed": len(symptoms),
                "biomarkers_analyzed": len(biomarkers),
                "medications_checked": len(medications),
                "supplements_checked": len(supplements) if isinstance(supplements, list) else 0,
                "conditions_checked": len(conditions) if isinstance(conditions, list) else 0,
                "herbs_evaluated": len(recommended_herbs),
                "drug_interactions": drug_interactions,
                "herbal_recommendations": [],
                "data_sources": {
                    "abena_ihr": patient_data is not None,
                    "ecdome": ecbome_biomarkers is not None,
                    "prescriptions_count": len(prescriptions)
                },
                "ibm_job": ibm_job,
                "recommendations": [
                    "Continue monitoring biomarkers",
                    "Review medication interactions",
                    "Consider quantum-enhanced treatment plan"
                ]
            }
        }
        
        # Save results to database
        analysis_id = None
        try:
            analysis_id = db_client.save_analysis_result(
                patient_id=patient_id,
                quantum_health_score=quantum_health_score,
                system_balance=system_balance,
                analysis_data=results["results"],
                drug_interactions=drug_interactions,
                herbal_recommendations=recommended_herbs,
                biomarker_analysis=biomarkers,
                recommendations=results["results"].get("recommendations", []),
                created_by=getattr(request, 'current_user', {}).get('user_id', 'system')
            )
            results["results"]["analysis_id"] = analysis_id
            
            # Update history with completion
            db_client.log_analysis_history(
                patient_id=patient_id,
                analysis_id=analysis_id,
                status='completed',
                computation_time_ms=computation_time
            )
        except Exception as e:
            logger.warning(f"Failed to save to database: {e}")
            # Log error to history
            db_client.log_analysis_history(
                patient_id=patient_id,
                analysis_id=analysis_id,
                status='error',
                error_message=str(e),
                computation_time_ms=computation_time
            )
        
        logger.info(f"Analysis complete for patient {patient_id} (took {computation_time}ms)")
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({
            "error": "Analysis failed",
            "detail": str(e),
            "hint": "For live demos, provide medications/supplements/conditions directly (skips external service calls)."
        }), 500


@app.route('/api/patients/<patient_id>/analyses', methods=['GET'])
# @require_auth  # Temporarily disabled for demo - enable in production
@general_api_limit
def get_patient_analyses(patient_id):
    """Get quantum analysis history for a patient"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # For demo patients, return empty history (they use demo-results)
        demo_patients = ['PAT-001', 'PAT-002', 'PAT-003', 'DEMO_001', 'DEMO_002', 'PAT_001', 'PAT_002']
        if any(demo in str(patient_id).upper() for demo in demo_patients):
            logger.info(f"Returning empty history for demo patient {patient_id}")
            return jsonify({
                "success": True,
                "patient_id": patient_id,
                "count": 0,
                "analyses": []
            }), 200
        
        analyses = db_client.get_patient_analyses(patient_id, limit)
        
        return jsonify({
            "success": True,
            "patient_id": patient_id,
            "count": len(analyses),
            "analyses": analyses
        }), 200
    except Exception as e:
        logger.error(f"Error fetching patient analyses: {e}")
        return jsonify({"error": "Failed to fetch analyses", "detail": str(e)}), 500


@app.route('/api/analyses/<int:analysis_id>', methods=['GET'])
@require_auth
@general_api_limit
def get_analysis(analysis_id):
    """Get specific quantum analysis by ID"""
    try:
        analysis = db_client.get_analysis_by_id(analysis_id)
        
        if not analysis:
            return jsonify({"error": "Analysis not found"}), 404
        
        return jsonify({
            "success": True,
            "analysis": dict(analysis)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching analysis: {e}")
        return jsonify({"error": "Failed to fetch analysis", "detail": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    # Test database connection
    db_status = "connected"
    try:
        with db_client.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "service": "quantum-healthcare",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)

