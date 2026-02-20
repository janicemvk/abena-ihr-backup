const express = require('express');
const cors = require('cors');
// const { Pool } = require('pg');

const app = express();
const PORT = process.env.PORT || 4001;

// PostgreSQL Database Connection - temporarily disabled
// const pool = new Pool({
//     connectionString: process.env.DATABASE_URL || 'postgresql://abena_user:abena_password@postgres:5432/abena_ihr',
//     ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
// });

// Test database connection
// pool.query('SELECT NOW()', (err, res) => {
//     if (err) {
//         console.error('❌ Database connection failed:', err.message);
//     } else {
//         console.log('✅ Database connected successfully');
//     }
// });

// Configure CORS with specific origins
app.use(cors({
    origin: [
        'http://localhost:3000',
        'http://localhost:4005',  // eCDome Intelligence
        'http://localhost:4006',  // Gamification
        'http://localhost:4007',  // Unified Integration
        'http://localhost:4008',  // Provider Dashboard
        'http://localhost:4009',  // Patient Dashboard
        'http://localhost:4011',  // Data Ingestion
        'http://localhost:4012',  // Biomarker GUI
        'http://localhost:8000',  // Telemedicine Platform
        'http://localhost:8080',  // API Gateway
    ],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));

app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'Background Modules',
        timestamp: new Date().toISOString(),
        database: 'connecting...'
    });
});

// Core biological modules endpoints
app.get('/api/v1/modules/metabolome', (req, res) => {
    res.json({
        success: true,
        data: {
            module: 'metabolome',
            status: 'active',
            lastUpdate: new Date().toISOString(),
            metrics: {
                glucose: 95,
                insulin: 8.5,
                hba1c: 5.7
            }
        }
    });
});

app.get('/api/v1/modules/microbiome', (req, res) => {
    res.json({
        success: true,
        data: {
            module: 'microbiome',
            status: 'active',
            lastUpdate: new Date().toISOString(),
            metrics: {
                diversity: 0.85,
                firmicutes: 0.45,
                bacteroidetes: 0.35
            }
        }
    });
});

app.get('/api/v1/modules/inflammatome', (req, res) => {
    res.json({
        success: true,
        data: {
            module: 'inflammatome',
            status: 'active',
            lastUpdate: new Date().toISOString(),
            metrics: {
                crp: 2.1,
                il6: 3.2,
                tnf_alpha: 1.8
            }
        }
    });
});

app.get('/api/v1/modules/immunome', (req, res) => {
    res.json({
        success: true,
        data: {
            module: 'immunome',
            status: 'active',
            lastUpdate: new Date().toISOString(),
            metrics: {
                cd4: 850,
                cd8: 450,
                nk_cells: 120
            }
        }
    });
});

app.get('/api/v1/modules/chronobiome', (req, res) => {
    res.json({
        success: true,
        data: {
            module: 'chronobiome',
            status: 'active',
            lastUpdate: new Date().toISOString(),
            metrics: {
                sleep_quality: 0.78,
                circadian_rhythm: 0.82,
                melatonin: 12.5
            }
        }
    });
});

app.get('/api/v1/modules/nutriome', (req, res) => {
    res.json({
        success: true,
        data: {
            module: 'nutriome',
            status: 'active',
            lastUpdate: new Date().toISOString(),
            metrics: {
                vitamin_d: 32,
                omega_3: 2.8,
                antioxidants: 0.75
            }
        }
    });
});

app.get('/api/v1/modules/toxicome', (req, res) => {
    res.json({
        success: true,
        data: {
            module: 'toxicome',
            status: 'active',
            lastUpdate: new Date().toISOString(),
            metrics: {
                heavy_metals: 0.12,
                pesticides: 0.08,
                air_pollution: 0.15
            }
        }
    });
});

app.get('/api/v1/modules/pharmacome', (req, res) => {
    res.json({
        success: true,
        data: {
            module: 'pharmacome',
            status: 'active',
            lastUpdate: new Date().toISOString(),
            metrics: {
                drug_metabolism: 0.88,
                interactions: 0.05,
                efficacy: 0.92
            }
        }
    });
});

app.get('/api/v1/modules/stress-response', (req, res) => {
    res.json({
        success: true,
        data: {
            module: 'stress-response',
            status: 'active',
            lastUpdate: new Date().toISOString(),
            metrics: {
                cortisol: 15.2,
                heart_rate_variability: 45,
                stress_index: 0.35
            }
        }
    });
});

app.get('/api/v1/modules/cardiovascular', (req, res) => {
    res.json({
        success: true,
        data: {
            module: 'cardiovascular',
            status: 'active',
            lastUpdate: new Date().toISOString(),
            metrics: {
                blood_pressure: '120/80',
                heart_rate: 72,
                cardiac_output: 5.2
            }
        }
    });
});

app.get('/api/v1/modules/neurological', (req, res) => {
    res.json({
        success: true,
        data: {
            module: 'neurological',
            status: 'active',
            lastUpdate: new Date().toISOString(),
            metrics: {
                brain_activity: 0.78,
                cognitive_function: 0.85,
                memory_score: 0.82
            }
        }
    });
});

app.get('/api/v1/modules/hormonal', (req, res) => {
    res.json({
        success: true,
        data: {
            module: 'hormonal',
            status: 'active',
            lastUpdate: new Date().toISOString(),
            metrics: {
                testosterone: 450,
                estrogen: 85,
                thyroid_tsh: 2.1
            }
        }
    });
});

// Analysis endpoint
app.get('/api/v1/analysis/:analysisId', (req, res) => {
    res.json({
        success: true,
        data: {
            analysisId: req.params.analysisId,
            status: 'completed',
            results: {
                overallHealthScore: 85,
                recommendations: ['Increase physical activity', 'Monitor stress levels'],
                alerts: [],
                timestamp: new Date().toISOString()
            }
        }
    });
});

// Provider Dashboard endpoints - TEMPORARILY USING MOCK DATA
app.get('/patients', (req, res) => {
    // Mock data for now - will be replaced with database queries
    const mockPatients = [
        {
            id: '444ed30b-defc-47c9-93ca-5b522828d7ec',
            name: 'John Doe',
            age: 40,
            gender: 'Male',
            lastVisit: '2025-06-07T23:34:05.951832+00:00',
            provider: 'Dr. Martinez',
            status: 'active',
            riskLevel: 'medium',
            ecdomeScore: 0.75
        },
        {
            id: '357af4b8-8032-4dbd-b50b-d2650f2b70e2',
            name: 'Alice Johnson',
            age: 35,
            gender: 'Female',
            lastVisit: '2025-06-07T23:40:27.842165+00:00',
            provider: 'Dr. Smith',
            status: 'active',
            riskLevel: 'low',
            ecdomeScore: 0.82
        },
        {
            id: '151733f9-6109-4053-bfc8-af0237c3eded',
            name: 'Emily Davis',
            age: 40,
            gender: 'Female',
            lastVisit: '2025-06-07T23:48:08.731074+00:00',
            provider: 'Dr. Williams',
            status: 'active',
            riskLevel: 'medium',
            ecdomeScore: 0.78
        }
    ];
    
    console.log('✅ Mock patient data loaded:', mockPatients.length, 'patients');
    res.json(mockPatients);
});

app.get('/ecdome', (req, res) => {
    const scope = req.query.scope || 'clinical-dashboard';
    
    res.json({
        success: true,
        data: {
            patientId: '444ed30b-defc-47c9-93ca-5b522828d7ec',
            ecdomeScore: 86,
            status: 'Excellent',
            components: {
                anandamide: { level: 0.75, status: 'normal' },
                twoAG: { level: 0.68, status: 'normal' },
                cb1Receptor: { activity: 0.82, status: 'optimal' },
                cb2Receptor: { activity: 0.79, status: 'optimal' },
                faahEnzyme: { activity: 0.71, status: 'normal' },
                maglEnzyme: { activity: 0.73, status: 'normal' }
            },
            systemBalance: 0.86,
            recommendations: ['Continue current treatment plan', 'Monitor stress levels'],
            timestamp: new Date().toISOString(),
            scope: scope
        }
    });
});

app.get('/realtime', (req, res) => {
    res.json({
        success: true,
        data: {
            patientId: '444ed30b-defc-47c9-93ca-5b522828d7ec',
            vitals: {
                heartRate: 71,
                bloodPressure: { systolic: 124, diastolic: 72 },
                temperature: 98.6,
                oxygenSaturation: 98
            },
            ecdomeMetrics: {
                currentScore: 86,
                trend: 'stable',
                alerts: []
            },
            modules: {
                metabolome: { status: 'active', reading: 0.82 },
                microbiome: { status: 'active', reading: 0.79 },
                inflammatome: { status: 'active', reading: 0.75 },
                immunome: { status: 'active', reading: 0.88 },
                chronobiome: { status: 'active', reading: 0.81 },
                nutriome: { status: 'active', reading: 0.84 },
                toxicome: { status: 'active', reading: 0.77 },
                pharmacome: { status: 'active', reading: 0.83 },
                stressResponse: { status: 'active', reading: 0.76 },
                cardiovascular: { status: 'active', reading: 0.85 },
                neurological: { status: 'active', reading: 0.87 },
                hormonal: { status: 'active', reading: 0.80 }
            },
            timestamp: new Date().toISOString()
        }
    });
});

// Patient-specific endpoints for Provider Dashboard - TEMPORARILY USING MOCK DATA
app.get('/patients/:patientId/data', (req, res) => {
    const { patientId } = req.params;
    
    res.json({
        success: true,
        data: {
            patientInfo: {
                id: patientId,
                name: 'John Doe',
                age: 40,
                gender: 'Male',
                lastVisit: new Date().toISOString(),
                provider: 'Dr. Martinez',
                status: 'active',
                riskLevel: 'medium',
                ecdomeScore: 0.75,
                vitalSigns: {
                    heartRate: 72,
                    bloodPressure: '120/80',
                    temperature: 98.6,
                    oxygenSaturation: 98
                },
                medications: [
                    { name: 'Metformin', dosage: '500mg', frequency: 'Twice daily' },
                    { name: 'Lisinopril', dosage: '10mg', frequency: 'Once daily' }
                ],
                allergies: ['Penicillin', 'Shellfish'],
                conditions: ['Type 2 Diabetes', 'Hypertension'],
                lastLabResults: {
                    glucose: 95,
                    hba1c: 6.2,
                    cholesterol: 180
                }
            },
            ecdomeProfile: {
                score: 0.75,
                status: 'Good',
                components: {
                    endocannabinoid: { status: 'active', reading: 0.80 },
                    metabolic: { status: 'active', reading: 0.75 },
                    immune: { status: 'active', reading: 0.70 },
                    hormonal: { status: 'active', reading: 0.80 }
                }
            },
            timestamp: new Date().toISOString()
        }
    });
});

app.get('/patients/:patientId/ecdome', (req, res) => {
    const { patientId } = req.params;
    const { scope } = req.query;
    
    res.json({
        success: true,
        data: {
            patientId: patientId,
            patientName: 'John Doe',
            ecdomeScore: 86,
            status: 'Excellent',
            components: {
                anandamide: { level: 0.75, status: 'normal' },
                twoAG: { level: 0.68, status: 'normal' },
                cb1Receptor: { activity: 0.82, status: 'optimal' },
                cb2Receptor: { activity: 0.79, status: 'optimal' },
                faahEnzyme: { activity: 0.71, status: 'normal' },
                maglEnzyme: { activity: 0.73, status: 'normal' }
            },
            systemBalance: 0.86,
            recommendations: ['Continue current treatment plan', 'Monitor stress levels'],
            timestamp: new Date().toISOString(),
            scope: scope
        }
    });
});

app.get('/patients/:patientId/realtime', (req, res) => {
    const { patientId } = req.params;
    const { timeRange } = req.query;
    
    res.json({
        success: true,
        data: {
            patientId: patientId,
            vitals: {
                heartRate: 71,
                bloodPressure: { systolic: 124, diastolic: 72 },
                temperature: 98.6,
                oxygenSaturation: 98
            },
            ecdomeMetrics: {
                currentScore: 86,
                trend: 'stable',
                alerts: []
            },
            modules: {
                metabolome: { status: 'active', reading: 0.82 },
                microbiome: { status: 'active', reading: 0.79 },
                inflammatome: { status: 'active', reading: 0.75 },
                immunome: { status: 'active', reading: 0.88 },
                chronobiome: { status: 'active', reading: 0.81 },
                nutriome: { status: 'active', reading: 0.84 },
                toxicome: { status: 'active', reading: 0.77 },
                pharmacome: { status: 'active', reading: 0.83 },
                stressResponse: { status: 'active', reading: 0.76 },
                cardiovascular: { status: 'active', reading: 0.85 },
                neurological: { status: 'active', reading: 0.87 },
                hormonal: { status: 'active', reading: 0.80 }
            },
            timestamp: new Date().toISOString(),
            timeRange: timeRange
        }
    });
});

app.get('/patients/:patientId/ecdome/components', (req, res) => {
    const { patientId } = req.params;
    
    res.json({
        success: true,
        data: {
            patientId: patientId,
            components: {
                anandamide: { level: 0.75, status: 'normal', trend: 'stable' },
                twoAG: { level: 0.68, status: 'normal', trend: 'stable' },
                cb1Receptor: { activity: 0.82, status: 'optimal', trend: 'improving' },
                cb2Receptor: { activity: 0.79, status: 'optimal', trend: 'stable' },
                faahEnzyme: { activity: 0.71, status: 'normal', trend: 'stable' },
                maglEnzyme: { activity: 0.73, status: 'normal', trend: 'stable' }
            },
            timestamp: new Date().toISOString()
        }
    });
});

app.get('/patients/:patientId/alerts/predictive', (req, res) => {
    const { patientId } = req.params;
    
    res.json({
        success: true,
        data: {
            patientId: patientId,
            alerts: [
                {
                    id: 'alert_001',
                    type: 'predictive',
                    severity: 'medium',
                    message: 'Potential cardiovascular risk detected in next 30 days',
                    confidence: 0.78,
                    recommendations: ['Schedule follow-up appointment', 'Monitor blood pressure']
                }
            ],
            timestamp: new Date().toISOString()
        }
    });
});

app.get('/patients/:patientId/recommendations', (req, res) => {
    const { patientId } = req.params;
    
    res.json({
        success: true,
        data: {
            patientId: patientId,
            recommendations: [
                {
                    id: 'rec_001',
                    type: 'lifestyle',
                    priority: 'high',
                    title: 'Increase Physical Activity',
                    description: 'Aim for 150 minutes of moderate exercise per week',
                    rationale: 'Based on current cardiovascular metrics'
                },
                {
                    id: 'rec_002',
                    type: 'nutrition',
                    priority: 'medium',
                    title: 'Optimize Omega-3 Intake',
                    description: 'Increase consumption of fatty fish or supplements',
                    rationale: 'Current levels below optimal range'
                }
            ],
            timestamp: new Date().toISOString()
        }
    });
});

app.listen(PORT, () => {
    console.log(`Background Modules Health Server running on port ${PORT}`);
}); 