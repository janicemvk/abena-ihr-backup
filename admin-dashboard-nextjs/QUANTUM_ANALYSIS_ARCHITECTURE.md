# Quantum Analysis Architecture

## Overview

The Quantum Analysis system is now an **independent component** accessible through the Integration Bridge, rather than being embedded solely in the Admin Portal. This allows it to be accessed from multiple portals (Admin, Clinical Dashboard, eCBome Intelligence Center).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Integration Bridge                       │
│                      (Port 8081)                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Quantum Analysis Routes (Proxy)                     │  │
│  │  - GET  /api/quantum/demo-results                    │  │
│  │  - POST /api/quantum/analyze-patient                 │  │
│  │  - GET  /api/quantum/status                          │  │
│  └─────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
└──────────────────────────┼──────────────────────────────────┘
                           │
                           │ Proxies to
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Quantum Flask API                              │
│              (Port 5000)                                    │
│  - GET  /api/demo-results                                   │
│  - POST /api/analyze                                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│         Quantum Analysis Command Center                      │
│         (Accessible from multiple portals)                    │
│                                                               │
│  - Admin Portal: /admin/quantum-analysis                     │
│  - Clinical Dashboard: Link to bridge                       │
│  - eCBome Intelligence: Link to bridge                      │
└─────────────────────────────────────────────────────────────┘
```

## Access Points

### 1. Admin Portal
- **Route**: `/admin/quantum-analysis`
- **Service**: Uses `quantumAnalysisService.ts` which connects via Integration Bridge
- **Link**: Available in sidebar navigation

### 2. Clinical Dashboard
- **Link**: Should be added to Clinical Dashboard navigation
- **URL**: `http://localhost:8081/quantum-analysis` (via bridge)
- **Access**: Through Integration Bridge proxy

### 3. eCBome Intelligence Center
- **Link**: Should be added to eCBome Intelligence navigation
- **URL**: `http://localhost:8081/quantum-analysis` (via bridge)
- **Access**: Through Integration Bridge proxy

## Integration Bridge Routes

The Integration Bridge now includes these quantum analysis routes:

### GET `/api/quantum/demo-results`
- Proxies to Flask API `/api/demo-results`
- Returns demo quantum analysis results
- Used for dashboard display

### POST `/api/quantum/analyze-patient`
- Proxies to Flask API `/api/analyze`
- Accepts patient data and runs quantum analysis
- Saves results to database (if patient_id provided)

### GET `/api/quantum/status`
- Checks Flask API status
- Returns system health information
- Used for status monitoring

## Service Configuration

### Admin Portal Service
The `quantumAnalysisService.ts` now:
1. **First tries Integration Bridge** (`http://localhost:8081`)
2. **Falls back to direct Flask API** (`http://localhost:5000`) if bridge unavailable
3. Provides seamless connection regardless of access point

### Environment Variables

**Integration Bridge** (`.env`):
```env
QUANTUM_FLASK_API_URL=http://localhost:5000
```

**Admin Portal** (`.env.local`):
```env
NEXT_PUBLIC_INTEGRATION_BRIDGE_URL=http://localhost:8081
NEXT_PUBLIC_QUANTUM_API_URL=http://localhost:5000  # Fallback
```

## Benefits of This Architecture

1. **Independence**: Quantum Analysis is not tied to any single portal
2. **Centralized Access**: All portals connect through Integration Bridge
3. **Consistency**: Same API endpoints regardless of access point
4. **Scalability**: Easy to add new access points
5. **Maintainability**: Single source of truth for quantum analysis
6. **Security**: Centralized authentication through bridge

## Next Steps

1. ✅ Integration Bridge routes added
2. ✅ Admin Portal service updated to use bridge
3. ⏳ Add link to Clinical Dashboard
4. ⏳ Add link to eCBome Intelligence Center
5. ⏳ Create standalone quantum analysis page (optional)

## Testing

1. **Start Integration Bridge**:
   ```powershell
   cd "C:\Users\Jan Marie\Documents\Python Development Files\abena ihr\integration-bridge"
   node server.js
   ```

2. **Start Flask API**:
   ```powershell
   cd "C:\Users\Jan Marie\Documents\Python Development Files\abena-quantum-healthcare"
   python app.py
   ```

3. **Test Bridge Endpoint**:
   ```powershell
   curl http://localhost:8081/api/quantum/demo-results
   ```

4. **Access from Admin Portal**:
   - Navigate to `http://localhost:3010/admin/quantum-analysis`
   - Should load data via Integration Bridge

