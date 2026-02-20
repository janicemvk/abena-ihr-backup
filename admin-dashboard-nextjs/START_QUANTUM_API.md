# Start Quantum Analysis API

## Issue
Getting "NetworkError when attempting to fetch resource" when clicking on Quantum Analysis.

## Root Cause
The Quantum Analysis API (Flask server) is not running on port 5000.

## Solution

### Start the Quantum API Server

1. **Open a new terminal/PowerShell window**

2. **Navigate to the Quantum Healthcare directory**:
   ```powershell
   cd "C:\Users\Jan Marie\Documents\Python Development Files\abena-quantum-healthcare"
   ```

3. **Activate Python virtual environment** (if you have one):
   ```powershell
   # If you have a venv
   .\venv\Scripts\Activate.ps1
   ```

4. **Install dependencies** (if not already installed):
   ```powershell
   pip install flask flask-cors numpy
   ```

5. **Start the Flask API server**:
   ```powershell
   python app.py
   ```

   You should see:
   ```
   🧬 IBENA IHR Quantum Healthcare Dashboard
   Dashboard: http://localhost:5000
   API: /api/demo-results | /api/analyze
    * Running on http://127.0.0.1:5000
   ```

6. **Keep this terminal open** - the server needs to keep running

7. **Go back to the Admin Portal** and refresh the Quantum Analysis page

### Verify API is Running

Test the API endpoint:
```powershell
curl http://localhost:5000/api/demo-results
```

Or open in browser:
```
http://localhost:5000/api/demo-results
```

You should see JSON data with quantum analysis results.

### Quick Start Script

You can also create a PowerShell script to start it quickly:

**`start-quantum-api.ps1`**:
```powershell
cd "C:\Users\Jan Marie\Documents\Python Development Files\abena-quantum-healthcare"
python app.py
```

Then just run:
```powershell
.\start-quantum-api.ps1
```

## Troubleshooting

### Port 5000 Already in Use

If you get "Address already in use", find and kill the process:
```powershell
# Find the process
netstat -ano | findstr :5000

# Kill it (replace PID with the actual process ID)
taskkill /PID <PID> /F
```

### Module Not Found Error

If you get import errors, install the required packages:
```powershell
pip install flask flask-cors numpy
```

### Python Not Found

Make sure Python is installed and in your PATH:
```powershell
python --version
```

If not found, use `py` instead:
```powershell
py app.py
```

## Environment Variables

The Admin Portal is configured to connect to:
- **Default**: `http://localhost:5000`
- **Configurable**: Set `NEXT_PUBLIC_QUANTUM_API_URL` in `.env.local`

## Next Steps

Once the API is running:
1. Refresh the Quantum Analysis page in the Admin Portal
2. The dashboard should load with real-time data
3. Enable auto-refresh to see live updates

