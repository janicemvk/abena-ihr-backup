# ABENA Clinical Dashboard - Quick Reference

## Dashboard Type: **PROVIDER DASHBOARD** 👨‍⚕️

This is the **Provider interface** for healthcare professionals to monitor their patients. There is a separate patient interface for patients to view their own data.

## Current User
**Dr. Martinez** - Provider viewing and managing 5 patients

---

## 5 Active Patients

### 1. **James Wilson (PAT-001)** - 46M
- **Risk**: 🔴 HIGH | **Status**: Active | **eCBome**: 58%
- **Conditions**: Severe Hypertension (188/90), Sleep Apnea, CAD, Obesity
- **Critical Alert**: Stage 2 Hypertension requires immediate attention
- **Key Issue**: Active smoker (1 PPD) with cardiovascular disease

### 2. **Sarah Chen (PAT-002)** - 32F
- **Risk**: 🟢 LOW | **Status**: Active | **eCBome**: 85%
- **Conditions**: Chronic low back pain with radiculopathy
- **Healthy Profile**: Active lifestyle, excellent vitals, vegetarian diet
- **Key Issue**: Progressive radiculopathy needs imaging/specialist

### 3. **Margaret Davis (PAT-003)** - 56F
- **Risk**: 🔴 HIGH | **Status**: Active | **eCBome**: 62%
- **Conditions**: Type 2 Diabetes, Neuropathy, HTN, GERD, Obesity
- **Labs**: HbA1C 7.0%, Glucose 150, on insulin therapy
- **Key Issue**: Suboptimal diabetes control with complications

### 4. **Robert Thompson (PAT-004)** - 78M
- **Risk**: 🔴 HIGH | **Status**: 🚨 CRITICAL | **eCBome**: 45%
- **Conditions**: CHF (EF 35%), AFib, CKD Stage 3, MI history
- **Critical Alerts**: 
  - CHF exacerbation (BNP 850)
  - Low O2 sat (93%)
  - Complex polypharmacy (8 meds including Warfarin)
- **Key Issue**: May require hospitalization for decompensated CHF

### 5. **Emily Rodriguez (PAT-005)** - 28F
- **Risk**: 🟡 MEDIUM | **Status**: Active | **eCBome**: 71%
- **Conditions**: GAD, Prediabetes, PCOS, Metabolic Syndrome, Obesity
- **Risk Factors**: Strong family hx of DM & CVD, sedentary job, high stress
- **Key Issue**: Prediabetes with multiple metabolic syndrome components

---

## System Statistics

- **Total Patients**: 5
- **Active**: 4
- **Critical**: 1 (PAT-004)
- **Average eCBome Score**: 64%
- **System Uptime**: 98.5%
- **Data Points**: 1.2M

---

## Dashboard Capabilities

### ✅ Fully Functional Features

1. **Patient Selection** - Switch between all 5 patients
2. **Patient Overview** - Demographics, vitals, medications, allergies
3. **Real-time Monitoring** - Live vital signs and eCBome readings
4. **eCBome Analysis** - 12-module system analysis
5. **Timeline View** - 24-hour eCBome trends
6. **Clinical Alerts** - Patient-specific warnings and notifications
7. **Recommendations** - Evidence-based clinical suggestions
8. **Dashboard Controls** - Time range, view mode, module filters
9. **Quick Actions** - Patient management tools
10. **System Statistics** - Practice-wide metrics

### 📊 12 eCBome Modules Tracked

1. Endocannabinoid system
2. Metabolome
3. Inflammatome
4. Immunome
5. Chronobiome (Circadian rhythm)
6. Cardiovascular system
7. Stress Response
8. Microbiome (Gut health)
9. Nutriome (Nutrition)
10. Toxicome (Toxin exposure)
11. Pharmacome (Drug metabolism)
12. Hormonal system

---

## How to Test

### Switch Between Patients
1. Click **"Change Patient"** in Patient Selection card
2. Search or select from dropdown
3. View updated patient-specific data across all components

### Explore Time Ranges
- Click **Time Range** controls: 24 Hours | 7 Days | 30 Days
- Observe how historical data adjusts

### View Different Modules
- Use **Module Filter** dropdown to focus on specific systems
- Toggle between Overview | Detailed | Comparison views

### Check Alerts & Recommendations
- Scroll to **Predictive Alerts** section
- View **Clinical Recommendations** with priority levels
- Each patient has unique, condition-specific alerts

---

## Data Source

All mock data is based on 5 realistic medical cases from:
- `/var/www/html/abena/sample_patient_cases.json` (Original case scenarios)
- `src/services/mockPatientData.js` (Implemented dashboard data)

---

## Technical Notes

### Mock Data Implementation
- **Network delay simulation**: 150-400ms for realistic behavior
- **Dynamic vital signs**: Slight variations on each refresh
- **Patient-specific data**: Medically accurate for each condition
- **No database required**: All data is self-contained

### Design Preservation
- ✅ **Zero CSS changes**
- ✅ **No layout modifications**
- ✅ **Existing components preserved**
- ✅ **Only data layer updated**

### Console Logging
Check browser console for detailed logging:
- ✅ Patient data loaded
- ✅ Mock real-time data
- ✅ Alerts and recommendations loaded
- ✅ Timeline data generated

---

## Next Steps (Optional)

To connect to real database:
1. Update API endpoints in `patientService.js`
2. Replace mock data imports with API calls
3. Update response data structure mapping if needed
4. Test with real patient data

The current implementation provides a complete, working dashboard for:
- 🎯 **Demonstrations**
- 🎯 **Testing**
- 🎯 **Development**
- 🎯 **Training**
- 🎯 **User feedback sessions**

---

## Quick Access

- **Dashboard URL**: `http://138.68.24.154:4009`
- **User**: Dr. Martinez
- **Patients**: PAT-001 through PAT-005
- **Documentation**: See `MOCK_DATA_GUIDE.md` for detailed information

---

**Status**: ✅ **FULLY FUNCTIONAL - ALL 5 PATIENTS READY**

Last Updated: October 29, 2025

