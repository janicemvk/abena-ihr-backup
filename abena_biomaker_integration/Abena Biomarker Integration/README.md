# Abena IHR - Real-Time Biomarker Integration System

A sophisticated system for continuous monitoring and integration of real-time biomarker data to support clinical decision-making, patient monitoring, and personalized interventions.

## Features

- **Real-time biomarker monitoring** from multiple device types:
  - Continuous Glucose Monitors (CGM)
  - Heart Rate Variability (HRV) monitors
  - Cortisol sensors
  - Support for additional biomarker devices

- **Advanced data analysis** capabilities:
  - Trend detection and pattern recognition
  - Cross-biomarker correlations
  - Automated alert generation
  - Quality assessment of incoming data

- **Modern dashboard interface** for:
  - Real-time biomarker visualization
  - Alert management
  - Historical data analysis
  - Patient status monitoring

- **Flexible device integration** through multiple connection types:
  - API-based connections
  - Bluetooth Classic
  - Bluetooth Low Energy (BLE)
  - Serial connections

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/abena-biomarker-integration.git
   cd abena-biomarker-integration
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running the System Backend

```python
from abena_biomarker_integration import RealTimeBiomarkerIntegration
import asyncio

async def main():
    # Initialize the system
    biomarker_system = RealTimeBiomarkerIntegration()
    
    # Configure patient monitoring
    patient_id = "PATIENT_001"
    device_configs = [
        {
            'device_id': 'CGM_001',
            'device_type': 'continuous_glucose_monitor',
            'connection_type': 'api',
            'connection_params': {
                'api_url': 'https://api.dexcom.com',
                'api_key': 'your_api_key'
            },
            'sampling_rate': 0.2  # Every 5 minutes
        },
        {
            'device_id': 'HRV_001',
            'device_type': 'heart_rate_variability',
            'connection_type': 'bluetooth',
            'connection_params': {
                'mac_address': '00:11:22:33:44:55'
            },
            'sampling_rate': 1.0  # Every 1 minute
        }
    ]
    
    await biomarker_system.configure_patient_monitoring(patient_id, device_configs)
    await biomarker_system.start_patient_monitoring(patient_id)
    
    # The system will run in the background, collecting and analyzing data

if __name__ == "__main__":
    asyncio.run(main())
```

### Running the Dashboard

```
python gui.py
```

Then open your browser to `http://localhost:8050` to access the dashboard.

## Integration Best Practices

When integrating with the Abena system, it's important to use the Abena SDK rather than implementing your own authentication and data handling. Here's the correct approach:

### ❌ Wrong - Has its own auth/data:

```javascript
class SomeModule {
  constructor() {
    this.database = new Database();
    this.authSystem = new CustomAuth();
  }
}
```

### ✅ Correct - Uses Abena SDK:

```javascript
import AbenaSDK from '@abena/sdk';

class SomeModule {
  constructor() {
    this.abena = new AbenaSDK({
      authServiceUrl: 'http://localhost:3001',
      dataServiceUrl: 'http://localhost:8001',
      privacyServiceUrl: 'http://localhost:8002',
      blockchainServiceUrl: 'http://localhost:8003'
    });
  }
  
  async someMethod(patientId, userId) {
    // 1. Auto-handled auth & permissions
    const patientData = await this.abena.getPatientData(patientId, 'module_purpose');
    
    // 2. Auto-handled privacy & encryption
    // 3. Auto-handled audit logging
    
    // 4. Focus on your business logic
    return this.processData(patientData);
  }
}
```

The Abena SDK automatically handles:
- Authentication and authorization
- Data privacy and encryption
- Audit logging and compliance
- Blockchain integration for data integrity

This allows you to focus on your core business logic while ensuring all security and compliance requirements are met.

## System Architecture

The system consists of several key components:

1. **Device Interfaces**: Abstract classes that handle communication with specific biomarker devices
2. **Data Processing Engine**: Analyzes incoming biomarker data for patterns and anomalies
3. **Alert System**: Triggers notifications based on critical biomarker thresholds
4. **Data Visualization Dashboard**: Provides real-time insight into patient status

## Dependencies

- Python 3.8+
- NumPy, Pandas, and SciPy for data analysis
- Dash and Plotly for interactive visualization
- asyncio and aiohttp for asynchronous communication
- Bluetooth libraries for device connectivity

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This system is designed for research and educational purposes
- Not intended for clinical use without proper medical validation and certification 