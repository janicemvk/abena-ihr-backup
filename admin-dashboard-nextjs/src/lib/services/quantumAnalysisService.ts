/**
 * Quantum Analysis Service
 * Connects to the Abena Quantum Healthcare Analysis API via Integration Bridge
 * The bridge proxies requests to the Flask API (port 5000)
 */

const INTEGRATION_BRIDGE_URL = process.env.NEXT_PUBLIC_INTEGRATION_BRIDGE_URL || 'http://localhost:8081';
const QUANTUM_API_BASE_URL = process.env.NEXT_PUBLIC_QUANTUM_API_URL || 'http://localhost:5000';

export interface QuantumAnalysisRequest {
  patient_id: string;
  symptoms: number[];
  biomarkers: {
    anandamide: number;
    '2AG': number;
    cb1_density: number;
    cb2_activity: number;
  };
  medications: string[];
  recommended_herbs?: string[];
}

export interface QuantumCircuitDiagram {
  type: string;
  qubits: number;
  gates?: Array<{
    type: string;
    qubit?: number;
    qubits?: number[];
    layer: number;
    parameter?: string;
    control?: number;
    target?: number;
  }>;
  measurements?: number[];
  depth: number;
  total_gates: number;
  layers?: number;
  feature_map?: any;
  variational_form?: any;
}

export interface QuantumMetrics {
  circuit_depth?: number;
  gate_count?: number;
  qubit_count?: number;
  estimated_hardware_time?: string;
  classical_equivalent_time?: string;
  feature_dimension?: number;
  quantum_feature_map_dimension?: number;
  classical_advantage?: string;
  problem_size?: number;
  qaoa_layers?: number;
  classical_complexity?: string;
  quantum_complexity?: string;
  speedup_estimate?: string;
}

export interface VQEAnalysis {
  optimization_progress: Array<{ step: number; energy: number; gradient?: number; convergence_rate?: number }>;
  final_energy: number;
  treatment_score: number;
  confidence_level: number;
  protocol: string;
  quantum_advantage: boolean;
  function_evaluations: number;
  circuit_diagram?: QuantumCircuitDiagram;
  quantum_metrics?: QuantumMetrics;
}

export interface PatternMatch {
  pattern_name: string;
  ecbome_correlation: number;
  quantum_measurement_probability: number;
  combined_confidence: number;
  herbal_formulas: string[];
  key_herbs: string[];
  symptoms_match: string[];
}

export interface PatternAnalysis {
  detected_pattern: string;
  pattern_confidence: number;
  ecbome_correlation?: number;
  quantum_measurement_probability?: number;
  patterns_detected: number;
  all_pattern_matches?: PatternMatch[];
  tcm_recommendation: string;
  ayurveda_correlation: string;
  circuit_diagram?: QuantumCircuitDiagram;
  quantum_metrics?: QuantumMetrics;
}

export interface DrugInteraction {
  medication: string;
  herb: string;
  severity: string;
  type: string;
  recommendation: string;
}

export interface InteractionAnalysis {
  safety_score: number;
  interaction_level: string;
  molecular_interaction_energy: number;
  clinical_recommendation: string;
  medications: string[];
  recommended_herbs: string[];
  interactions_detected?: DrugInteraction[];
  optimal_combination?: {
    medications: string[];
    herbs: string[];
  };
  circuit_diagram?: QuantumCircuitDiagram;
  quantum_metrics?: QuantumMetrics;
}

export interface BiomarkerAnalysis {
  name: string;
  value: number;
  normal: number;
  status: 'normal' | 'above_normal' | 'below_normal';
  unit: string;
}

export interface QuantumAnalysisResult {
  analysis_timestamp: string;
  system_status: string;
  patient_id: string;
  scores: {
    treatment_score: number;
    overall_score: number;
    safety_score: number;
    confidence_level: number;
  };
  vqe_analysis: VQEAnalysis;
  pattern_analysis: PatternAnalysis;
  interaction_analysis: InteractionAnalysis;
  biomarker_analysis: BiomarkerAnalysis[];
  treatment_components: Array<{ name: string; score: number; color: string }>;
  recommendations: Array<{
    priority: number;
    title: string;
    description: string;
    status: string;
    confidence?: number;
    herbal_formulas?: string[];
    interactions?: DrugInteraction[];
    safety_score?: number;
  }>;
  blockchain?: {
    status: string;
    transaction: {
      transaction_hash: string;
      block_number: number;
      gas_used: number;
      timestamp: string;
      quantum_proof: string;
      post_quantum_signature: string;
      encrypted: boolean;
    };
    storage_method: string;
    access_control: string;
  };
  summary: {
    overall_quantum_score: number;
    quantum_advantage_status: boolean;
    integration_quality: string;
    final_recommendation: string;
    ready_for_deployment: boolean;
    hardware_ready?: boolean;
    simulation_mode?: boolean;
  };
  quantum_backend?: string;
}

export interface QuantumSystemStatus {
  api_status: 'online' | 'offline';
  blockchain_status: 'connected' | 'disconnected';
  analysis_engine: 'operational' | 'maintenance';
  last_analysis: string | null;
  total_analyses: number;
  average_processing_time: number;
}

class QuantumAnalysisService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = QUANTUM_API_BASE_URL;
  }

  /**
   * Check if the quantum API is available via integration bridge
   */
  async checkApiStatus(): Promise<boolean> {
    try {
      // Try integration bridge first
      const bridgeResponse = await fetch(`${INTEGRATION_BRIDGE_URL}/api/quantum/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (bridgeResponse.ok) {
        const status = await bridgeResponse.json();
        return status.quantum_flask_api?.status === 'online';
      }
      
      // Fallback to direct Flask API
      const response = await fetch(`${QUANTUM_API_BASE_URL}/api/demo-results`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      return response.ok;
    } catch (error) {
      console.error('Quantum API status check failed:', error);
      return false;
    }
  }

  /**
   * Get demo results from the quantum analysis system via integration bridge
   */
  async getDemoResults(): Promise<QuantumAnalysisResult> {
    try {
      // Try integration bridge first
      let response = await fetch(`${INTEGRATION_BRIDGE_URL}/api/quantum/demo-results`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const bridgeData = await response.json();
        return bridgeData.data || bridgeData;
      }

      // Fallback to direct Flask API
      response = await fetch(`${QUANTUM_API_BASE_URL}/api/demo-results`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching demo results:', error);
      throw error;
    }
  }

  /**
   * Run quantum analysis on patient data via integration bridge
   */
  async analyzePatient(data: QuantumAnalysisRequest): Promise<QuantumAnalysisResult> {
    try {
      // Try integration bridge first
      let response = await fetch(`${INTEGRATION_BRIDGE_URL}/api/quantum/analyze-patient`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        const bridgeData = await response.json();
        return bridgeData.data || bridgeData;
      }

      // Fallback to direct Flask API
      response = await fetch(`${QUANTUM_API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result.results || result;
    } catch (error) {
      console.error('Error running quantum analysis:', error);
      throw error;
    }
  }

  /**
   * Get system status via integration bridge
   */
  async getSystemStatus(): Promise<QuantumSystemStatus> {
    try {
      // Get status from integration bridge
      const response = await fetch(`${INTEGRATION_BRIDGE_URL}/api/quantum/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const status = await response.json();
        const flaskStatus = status.quantum_flask_api?.status === 'online';
        
        return {
          api_status: flaskStatus ? 'online' : 'offline',
          blockchain_status: 'connected', // Would check blockchain in production
          analysis_engine: flaskStatus ? 'operational' : 'maintenance',
          last_analysis: new Date().toISOString(),
          total_analyses: 0, // Would come from database
          average_processing_time: 2.5, // seconds
        };
      }
    } catch (error) {
      console.warn('Could not fetch status from bridge:', error);
    }

    // Fallback status check
    const apiStatus = await this.checkApiStatus();
    
    return {
      api_status: apiStatus ? 'online' : 'offline',
      blockchain_status: 'disconnected',
      analysis_engine: apiStatus ? 'operational' : 'maintenance',
      last_analysis: null,
      total_analyses: 0,
      average_processing_time: 0,
    };
  }
}

export const quantumAnalysisService = new QuantumAnalysisService();

