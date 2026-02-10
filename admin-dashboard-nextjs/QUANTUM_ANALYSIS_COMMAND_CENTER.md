# Quantum Analysis Command Center

## Overview

The Quantum Analysis Command Center is a comprehensive dashboard for monitoring and managing the Abena IHR Quantum Healthcare Analysis System. It provides real-time visibility into the entire quantum analysis workflow, from data input through blockchain storage.

## Features

### 🔍 Real-Time Monitoring
- **System Status**: Monitor API, blockchain, and analysis engine status
- **Data Flow Visualization**: See the complete pipeline from input to blockchain
- **Live Metrics**: Track total analyses, processing times, and system performance

### 📊 Analysis Components

1. **Data Input**
   - Patient data ingestion
   - Biomarker collection
   - Symptom tracking
   - Medication records

2. **VQE Optimization** (Variational Quantum Eigensolver)
   - Treatment optimization
   - Energy calculations
   - Protocol recommendations
   - Quantum advantage tracking

3. **Pattern Recognition** (Quantum Machine Learning)
   - Pattern detection
   - TCM correlation
   - Ayurveda analysis
   - Confidence scoring

4. **Drug Interaction Analysis** (QAOA)
   - Safety scoring
   - Molecular interaction energy
   - Clinical recommendations
   - Risk assessment

5. **Blockchain Storage**
   - Quantum-secured records
   - Integrity verification
   - Access control
   - Immutable audit trail

### 📈 Dashboard Sections

#### System Status Cards
- API Status (Online/Offline)
- Blockchain Connection Status
- Analysis Engine Status
- Total Analyses Counter

#### Data Flow Pipeline
Visual representation of the complete workflow:
- Input → VQE → Pattern Recognition → Drug Interaction → Blockchain
- Real-time status indicators for each step
- Data metrics at each stage

#### Analysis Results
- **Overall Scores**: Quantum score, treatment score, safety score, confidence level
- **VQE Progress**: Step-by-step optimization visualization
- **Pattern Recognition**: Detected patterns and confidence levels
- **Drug Interactions**: Safety scores and clinical recommendations
- **Recommendations**: Priority-based action items

#### Summary Panel
- Final recommendation
- Integration quality assessment
- Quantum advantage status
- Deployment readiness

## Setup

### Prerequisites

1. **Quantum Analysis API** must be running:
   ```bash
   cd "C:\Users\Jan Marie\Documents\Python Development Files\abena-quantum-healthcare"
   python app.py
   ```
   The API runs on `http://localhost:5000` by default.

2. **Environment Configuration**

   Create or update `.env.local` in the Admin Portal project:
   ```env
   NEXT_PUBLIC_QUANTUM_API_URL=http://localhost:5000
   ```

   If not set, it defaults to `http://localhost:5000`.

### Access

1. Navigate to the Admin Portal: `http://localhost:3010`
2. Log in with admin credentials
3. Click **"Quantum Analysis"** in the sidebar or dashboard

## Usage

### Viewing Real-Time Data

1. The dashboard automatically loads the latest analysis results
2. Enable **Auto-refresh** to update every 30 seconds
3. Click **Refresh** to manually update data

### Understanding the Data Flow

The pipeline shows:
- **Green**: Completed steps
- **Blue**: Active processing
- **Gray**: Pending steps

Each step displays relevant metrics:
- **Input**: Patient ID, biomarker count, medication count
- **VQE**: Treatment score, final energy
- **Pattern**: Confidence level, patterns detected
- **Interaction**: Safety score, interaction level
- **Blockchain**: Connection status

### Interpreting Scores

- **Overall Quantum Score**: Combined score from all analyses (0-100%)
- **Treatment Score**: VQE optimization result (0-100%)
- **Safety Score**: Drug interaction safety (0-100%)
- **Confidence Level**: Pattern recognition confidence (0-100%)

### Recommendations

The system provides priority-based recommendations:
1. **Priority 1**: Critical actions (e.g., proceed with protocol)
2. **Priority 2**: Important considerations (e.g., consult practitioners)
3. **Priority 3**: Monitoring requirements (e.g., drug interactions)

## Integration with Blockchain

The Quantum Analysis Command Center connects to the `AbenaQuantumHealthRecord` smart contract to:
- Verify record integrity
- Track blockchain connection status
- Monitor quantum-secured storage
- Display access control information

### Smart Contract Features

- **Quantum-secured records**: Post-quantum cryptography
- **Patient registration**: Quantum public key management
- **Provider access**: Controlled record access
- **Integrity verification**: Hash-based validation

## Troubleshooting

### API Not Responding

1. Check if the Quantum API is running:
   ```bash
   curl http://localhost:5000/api/demo-results
   ```

2. Verify the API URL in `.env.local`

3. Check browser console for CORS errors

### Blockchain Status Shows Disconnected

- This is currently a mock status
- In production, this will connect to the deployed smart contract
- Verify blockchain network configuration

### No Data Displayed

1. Ensure the Quantum API is running
2. Check browser console for errors
3. Verify network connectivity
4. Try refreshing the page

## Technical Details

### API Endpoints

- `GET /api/demo-results`: Get demo analysis results
- `POST /api/analyze`: Run analysis on patient data

### Data Structure

See `src/lib/services/quantumAnalysisService.ts` for TypeScript interfaces:
- `QuantumAnalysisResult`
- `VQEAnalysis`
- `PatternAnalysis`
- `InteractionAnalysis`
- `QuantumSystemStatus`

### Components

- **Page**: `src/app/admin/quantum-analysis/page.tsx`
- **Service**: `src/lib/services/quantumAnalysisService.ts`

## Future Enhancements

- Real-time blockchain transaction monitoring
- Historical analysis trends
- Export analysis reports
- Custom analysis parameters
- Multi-patient batch processing
- Integration with patient dashboard
- Provider-specific views

## Related Documentation

- Quantum Healthcare Analyzer: `abena-quantum-healthcare/quantum_healthcare_analyzer.py`
- Smart Contract: `abena-quantum-healthcare/contracts/AbenaQuantumHealthRecord.sol`
- Flask API: `abena-quantum-healthcare/app.py`

