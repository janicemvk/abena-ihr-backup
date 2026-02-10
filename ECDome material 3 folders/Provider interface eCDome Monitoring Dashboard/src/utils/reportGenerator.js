/**
 * ABENA Clinical Report Generator
 * Generates comprehensive patient health reports with eCBome analysis
 */

export const ReportTypes = {
  COMPREHENSIVE: 'comprehensive',
  ECBOME_ANALYSIS: 'ecbome_analysis',
  MODULE_ASSESSMENT: 'module_assessment',
  TREATMENT_PROGRESS: 'treatment_progress',
  LAB_RESULTS: 'lab_results'
};

/**
 * Generate a comprehensive clinical report
 */
export const generateReport = async (reportType, patientData, realtimeData = null) => {
  const timestamp = new Date().toISOString();
  const reportId = `ABENA-RPT-${Date.now()}`;

  let reportContent = '';

  switch (reportType) {
    case ReportTypes.COMPREHENSIVE:
      reportContent = generateComprehensiveReport(patientData, realtimeData, reportId, timestamp);
      break;
    case ReportTypes.ECBOME_ANALYSIS:
      reportContent = generateECBomeReport(patientData, reportId, timestamp);
      break;
    case ReportTypes.MODULE_ASSESSMENT:
      reportContent = generateModuleAssessmentReport(patientData, reportId, timestamp);
      break;
    case ReportTypes.TREATMENT_PROGRESS:
      reportContent = generateTreatmentProgressReport(patientData, reportId, timestamp);
      break;
    case ReportTypes.LAB_RESULTS:
      reportContent = generateLabResultsReport(patientData, reportId, timestamp);
      break;
    default:
      reportContent = generateComprehensiveReport(patientData, realtimeData, reportId, timestamp);
  }

  return {
    content: reportContent,
    reportId,
    timestamp,
    reportType
  };
};

/**
 * Download report as HTML file (can be printed to PDF)
 */
export const downloadReport = (reportData, filename = null) => {
  const { content, reportId, reportType } = reportData;
  const fname = filename || `ABENA_Report_${reportType}_${reportId}.html`;

  const blob = new Blob([content], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fname;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Print report (opens browser print dialog for PDF export)
 */
export const printReport = (reportContent) => {
  const printWindow = window.open('', '_blank');
  printWindow.document.write(reportContent);
  printWindow.document.close();
  
  // Wait for content to load before printing
  printWindow.onload = () => {
    printWindow.print();
  };
};

/**
 * Generate comprehensive health report
 */
const generateComprehensiveReport = (patientData, realtimeData, reportId, timestamp) => {
  const data = patientData?.data || patientData;
  const patientInfo = data?.patientInfo || {};
  const ecbomeProfile = data?.ecbomeProfile || {};
  const vitals = realtimeData?.data?.vitalSigns || patientInfo?.vitalSigns || {};
  const recommendations = data?.recommendations || [];
  const alerts = data?.alerts || [];

  const reportDate = new Date(timestamp).toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ABENA Comprehensive Health Report - ${patientInfo.name || 'Patient'}</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 1200px;
      margin: 0 auto;
      padding: 40px 20px;
      background: #fff;
    }
    
    .header {
      border-bottom: 4px solid #6366f1;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }
    
    .header h1 {
      color: #1e293b;
      font-size: 28px;
      margin-bottom: 10px;
    }
    
    .header .subtitle {
      color: #64748b;
      font-size: 14px;
    }
    
    .report-meta {
      background: #f8fafc;
      padding: 15px;
      border-radius: 8px;
      margin-bottom: 30px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
    }
    
    .report-meta .meta-item {
      display: flex;
      flex-direction: column;
    }
    
    .report-meta .label {
      font-size: 12px;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }
    
    .report-meta .value {
      font-size: 16px;
      color: #1e293b;
      font-weight: 600;
    }
    
    .section {
      margin-bottom: 40px;
      page-break-inside: avoid;
    }
    
    .section-title {
      font-size: 20px;
      color: #1e293b;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 10px;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
    }
    
    .section-title .icon {
      margin-right: 10px;
      color: #6366f1;
    }
    
    .card {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 15px;
    }
    
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
    }
    
    .data-row {
      display: flex;
      justify-content: space-between;
      padding: 12px 0;
      border-bottom: 1px solid #e2e8f0;
    }
    
    .data-row:last-child {
      border-bottom: none;
    }
    
    .data-label {
      font-weight: 500;
      color: #64748b;
    }
    
    .data-value {
      font-weight: 600;
      color: #1e293b;
    }
    
    .alert-box {
      padding: 15px;
      border-radius: 8px;
      margin-bottom: 10px;
      border-left: 4px solid;
    }
    
    .alert-critical {
      background: #fef2f2;
      border-color: #dc2626;
      color: #7f1d1d;
    }
    
    .alert-warning {
      background: #fffbeb;
      border-color: #f59e0b;
      color: #78350f;
    }
    
    .alert-info {
      background: #eff6ff;
      border-color: #3b82f6;
      color: #1e3a8a;
    }
    
    .recommendation {
      background: #f0fdf4;
      border: 1px solid #86efac;
      border-radius: 8px;
      padding: 15px;
      margin-bottom: 10px;
    }
    
    .recommendation-title {
      font-weight: 600;
      color: #166534;
      margin-bottom: 5px;
    }
    
    .recommendation-text {
      color: #15803d;
      font-size: 14px;
    }
    
    .badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
    }
    
    .badge-success {
      background: #dcfce7;
      color: #166534;
    }
    
    .badge-warning {
      background: #fef3c7;
      color: #92400e;
    }
    
    .badge-danger {
      background: #fee2e2;
      color: #991b1b;
    }
    
    .badge-info {
      background: #dbeafe;
      color: #1e40af;
    }
    
    .ecbome-component {
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 15px;
      margin-bottom: 10px;
    }
    
    .component-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    
    .component-name {
      font-weight: 600;
      color: #1e293b;
      font-size: 16px;
    }
    
    .component-score {
      font-size: 20px;
      font-weight: 700;
      color: #6366f1;
    }
    
    .progress-bar {
      width: 100%;
      height: 8px;
      background: #e2e8f0;
      border-radius: 4px;
      overflow: hidden;
      margin-bottom: 8px;
    }
    
    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
      border-radius: 4px;
      transition: width 0.3s ease;
    }
    
    .vital-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
      margin-top: 15px;
    }
    
    .vital-card {
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 15px;
      text-align: center;
    }
    
    .vital-label {
      font-size: 12px;
      color: #64748b;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    
    .vital-value {
      font-size: 24px;
      font-weight: 700;
      color: #1e293b;
    }
    
    .vital-unit {
      font-size: 14px;
      color: #64748b;
      font-weight: 400;
    }
    
    .footer {
      margin-top: 60px;
      padding-top: 20px;
      border-top: 2px solid #e2e8f0;
      text-align: center;
      color: #64748b;
      font-size: 12px;
    }
    
    .medication-list, .allergy-list {
      list-style: none;
    }
    
    .medication-item, .allergy-item {
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 12px;
      margin-bottom: 8px;
    }
    
    .medication-name {
      font-weight: 600;
      color: #1e293b;
      margin-bottom: 4px;
    }
    
    .medication-details {
      font-size: 14px;
      color: #64748b;
    }
    
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 15px;
    }
    
    th {
      background: #f1f5f9;
      padding: 12px;
      text-align: left;
      font-weight: 600;
      color: #475569;
      border-bottom: 2px solid #e2e8f0;
    }
    
    td {
      padding: 12px;
      border-bottom: 1px solid #e2e8f0;
      color: #1e293b;
    }
    
    tr:last-child td {
      border-bottom: none;
    }
    
    @media print {
      body {
        padding: 20px;
      }
      
      .section {
        page-break-inside: avoid;
      }
      
      .no-print {
        display: none;
      }
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>🧠 ABENA Comprehensive Health Report</h1>
    <p class="subtitle">Advanced Biomarker & Endocannabinoid Network Analysis</p>
  </div>

  <div class="report-meta">
    <div class="meta-item">
      <span class="label">Report ID</span>
      <span class="value">${reportId}</span>
    </div>
    <div class="meta-item">
      <span class="label">Generated</span>
      <span class="value">${reportDate}</span>
    </div>
    <div class="meta-item">
      <span class="label">Patient ID</span>
      <span class="value">${patientInfo.id || 'N/A'}</span>
    </div>
    <div class="meta-item">
      <span class="label">Provider</span>
      <span class="value">${patientInfo.provider || 'N/A'}</span>
    </div>
  </div>

  <!-- Patient Demographics -->
  <div class="section">
    <h2 class="section-title">
      <span class="icon">👤</span>
      Patient Demographics
    </h2>
    <div class="card">
      <div class="grid">
        <div class="data-row">
          <span class="data-label">Name</span>
          <span class="data-value">${patientInfo.name || 'N/A'}</span>
        </div>
        <div class="data-row">
          <span class="data-label">Age</span>
          <span class="data-value">${patientInfo.age || 'N/A'} years</span>
        </div>
        <div class="data-row">
          <span class="data-label">Gender</span>
          <span class="data-value">${patientInfo.gender || 'N/A'}</span>
        </div>
        <div class="data-row">
          <span class="data-label">Status</span>
          <span class="data-value">
            <span class="badge badge-${getBadgeClass(patientInfo.status)}">
              ${(patientInfo.status || 'unknown').toUpperCase()}
            </span>
          </span>
        </div>
        <div class="data-row">
          <span class="data-label">Risk Level</span>
          <span class="data-value">
            <span class="badge badge-${getRiskBadgeClass(patientInfo.riskLevel)}">
              ${(patientInfo.riskLevel || 'unknown').toUpperCase()}
            </span>
          </span>
        </div>
        <div class="data-row">
          <span class="data-label">Last Visit</span>
          <span class="data-value">${patientInfo.lastVisit ? new Date(patientInfo.lastVisit).toLocaleDateString() : 'N/A'}</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Current Vital Signs -->
  <div class="section">
    <h2 class="section-title">
      <span class="icon">❤️</span>
      Current Vital Signs
    </h2>
    <div class="card">
      <div class="vital-grid">
        ${generateVitalCard('Heart Rate', vitals.heartRate, 'bpm')}
        ${generateVitalCard('Blood Pressure', vitals.bloodPressure, '')}
        ${generateVitalCard('Temperature', vitals.temperature, '°F')}
        ${generateVitalCard('O₂ Saturation', vitals.oxygenSaturation, '%')}
        ${generateVitalCard('Respiratory Rate', vitals.respiratoryRate, '/min')}
        ${generateVitalCard('Glucose', vitals.glucose, 'mg/dL')}
      </div>
    </div>
  </div>

  <!-- Active Alerts -->
  ${alerts && alerts.length > 0 ? `
  <div class="section">
    <h2 class="section-title">
      <span class="icon">⚠️</span>
      Active Alerts
    </h2>
    ${alerts.map(alert => `
      <div class="alert-box alert-${alert.severity || 'info'}">
        <strong>${alert.title || 'Alert'}</strong>
        <p>${alert.message || alert.description || ''}</p>
        ${alert.timestamp ? `<small>Triggered: ${new Date(alert.timestamp).toLocaleString()}</small>` : ''}
      </div>
    `).join('')}
  </div>
  ` : ''}

  <!-- eCBome Profile Analysis -->
  <div class="section">
    <h2 class="section-title">
      <span class="icon">🧬</span>
      eCBome Profile Analysis
    </h2>
    <div class="card">
      <div class="data-row">
        <span class="data-label">Overall eCBome Score</span>
        <span class="data-value" style="font-size: 24px; color: #6366f1;">
          ${ecbomeProfile.overallScore || ecbomeProfile.score || 'N/A'}
        </span>
      </div>
      <div class="data-row">
        <span class="data-label">Status</span>
        <span class="data-value">
          <span class="badge badge-${getScoreBadgeClass(ecbomeProfile.overallScore || ecbomeProfile.score)}">
            ${ecbomeProfile.status || getScoreStatus(ecbomeProfile.overallScore || ecbomeProfile.score)}
          </span>
        </span>
      </div>
    </div>

    ${ecbomeProfile.components ? `
    <h3 style="margin-top: 25px; margin-bottom: 15px; color: #1e293b;">12-Module Component Analysis</h3>
    ${Object.entries(ecbomeProfile.components).map(([key, component]) => `
      <div class="ecbome-component">
        <div class="component-header">
          <span class="component-name">${formatComponentName(key)}</span>
          <span class="component-score">${(component.reading * 100).toFixed(0)}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${(component.reading * 100).toFixed(0)}%"></div>
        </div>
        <div style="font-size: 13px; color: #64748b;">
          Status: <strong style="color: ${getStatusColor(component.status)}">${(component.status || 'unknown').toUpperCase()}</strong>
          ${component.trend ? ` | Trend: ${component.trend}` : ''}
        </div>
        ${component.notes ? `<div style="margin-top: 8px; font-size: 13px; color: #475569;">${component.notes}</div>` : ''}
      </div>
    `).join('')}
    ` : ''}
  </div>

  <!-- Medications -->
  ${patientInfo.medications && patientInfo.medications.length > 0 ? `
  <div class="section">
    <h2 class="section-title">
      <span class="icon">💊</span>
      Current Medications
    </h2>
    <ul class="medication-list">
      ${patientInfo.medications.map(med => `
        <li class="medication-item">
          <div class="medication-name">${med.name}</div>
          <div class="medication-details">${med.dosage} - ${med.frequency}</div>
          ${med.prescriber ? `<div class="medication-details">Prescribed by: ${med.prescriber}</div>` : ''}
        </li>
      `).join('')}
    </ul>
  </div>
  ` : ''}

  <!-- Allergies -->
  ${patientInfo.allergies && patientInfo.allergies.length > 0 ? `
  <div class="section">
    <h2 class="section-title">
      <span class="icon">⚠️</span>
      Known Allergies
    </h2>
    <ul class="allergy-list">
      ${patientInfo.allergies.map(allergy => `
        <li class="allergy-item">
          <strong style="color: #dc2626;">${typeof allergy === 'string' ? allergy : allergy.allergen || 'Unknown'}</strong>
          ${typeof allergy === 'object' && allergy.reaction ? `<div style="font-size: 14px; color: #64748b;">Reaction: ${allergy.reaction}</div>` : ''}
        </li>
      `).join('')}
    </ul>
  </div>
  ` : ''}

  <!-- Clinical Recommendations -->
  ${recommendations && recommendations.length > 0 ? `
  <div class="section">
    <h2 class="section-title">
      <span class="icon">📋</span>
      Evidence-Based Recommendations
    </h2>
    ${recommendations.map((rec, index) => `
      <div class="recommendation">
        <div class="recommendation-title">
          ${index + 1}. ${rec.title || rec.category || 'Recommendation'}
          ${rec.priority ? `<span class="badge badge-${rec.priority === 'high' ? 'danger' : 'info'}" style="margin-left: 10px; font-size: 10px;">${rec.priority.toUpperCase()}</span>` : ''}
        </div>
        <div class="recommendation-text">${rec.description || rec.recommendation || rec.text || ''}</div>
        ${rec.evidence ? `<div style="margin-top: 5px; font-size: 12px; color: #15803d;"><em>Evidence: ${rec.evidence}</em></div>` : ''}
      </div>
    `).join('')}
  </div>
  ` : ''}

  <!-- Medical Conditions -->
  ${patientInfo.conditions && patientInfo.conditions.length > 0 ? `
  <div class="section">
    <h2 class="section-title">
      <span class="icon">📝</span>
      Active Medical Conditions
    </h2>
    <table>
      <thead>
        <tr>
          <th>Condition</th>
          <th>Status</th>
          ${patientInfo.conditions.some(c => typeof c === 'object' && c.diagnosedDate) ? '<th>Diagnosed</th>' : ''}
        </tr>
      </thead>
      <tbody>
        ${patientInfo.conditions.map(condition => `
          <tr>
            <td>${typeof condition === 'string' ? condition : condition.name || 'N/A'}</td>
            <td>
              <span class="badge badge-info">
                ${typeof condition === 'object' && condition.status ? condition.status.toUpperCase() : 'ACTIVE'}
              </span>
            </td>
            ${typeof condition === 'object' && condition.diagnosedDate ? `<td>${new Date(condition.diagnosedDate).toLocaleDateString()}</td>` : ''}
          </tr>
        `).join('')}
      </tbody>
    </table>
  </div>
  ` : ''}

  <div class="footer">
    <p><strong>ABENA Healthcare System</strong></p>
    <p>Advanced Biomarker & Endocannabinoid Network Analysis</p>
    <p>This report is confidential and intended for healthcare professionals only.</p>
    <p style="margin-top: 10px;">Generated: ${reportDate} | Report ID: ${reportId}</p>
  </div>
</body>
</html>
  `;
};

/**
 * Generate eCBome-focused analysis report
 */
const generateECBomeReport = (patientData, reportId, timestamp) => {
  const data = patientData?.data || patientData;
  const patientInfo = data?.patientInfo || {};
  const ecbomeProfile = data?.ecbomeProfile || {};

  const reportDate = new Date(timestamp).toLocaleString();

  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ABENA eCBome Analysis Report - ${patientInfo.name || 'Patient'}</title>
  <style>
    ${getCommonStyles()}
  </style>
</head>
<body>
  <div class="header">
    <h1>🧬 ABENA eCBome Analysis Report</h1>
    <p class="subtitle">Endocannabinoid System Comprehensive Assessment</p>
  </div>

  <div class="report-meta">
    <div class="meta-item">
      <span class="label">Report ID</span>
      <span class="value">${reportId}</span>
    </div>
    <div class="meta-item">
      <span class="label">Patient</span>
      <span class="value">${patientInfo.name || 'N/A'}</span>
    </div>
    <div class="meta-item">
      <span class="label">Generated</span>
      <span class="value">${reportDate}</span>
    </div>
  </div>

  <div class="section">
    <h2 class="section-title">Overall eCBome Score</h2>
    <div class="card" style="text-align: center; padding: 40px;">
      <div style="font-size: 72px; font-weight: 700; color: #6366f1; margin-bottom: 10px;">
        ${ecbomeProfile.overallScore || ecbomeProfile.score || 'N/A'}
      </div>
      <div style="font-size: 24px; color: #64748b;">
        ${ecbomeProfile.status || getScoreStatus(ecbomeProfile.overallScore || ecbomeProfile.score)}
      </div>
    </div>
  </div>

  ${ecbomeProfile.components ? `
  <div class="section">
    <h2 class="section-title">12-Module Detailed Analysis</h2>
    ${Object.entries(ecbomeProfile.components).map(([key, component]) => `
      <div class="ecbome-component" style="margin-bottom: 20px;">
        <div class="component-header">
          <span class="component-name" style="font-size: 18px;">${formatComponentName(key)}</span>
          <span class="component-score" style="font-size: 28px;">${(component.reading * 100).toFixed(0)}%</span>
        </div>
        <div class="progress-bar" style="height: 12px; margin: 15px 0;">
          <div class="progress-fill" style="width: ${(component.reading * 100).toFixed(0)}%"></div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px;">
          <div>
            <span style="font-size: 12px; color: #64748b;">Status:</span>
            <strong style="color: ${getStatusColor(component.status)}; margin-left: 5px;">${(component.status || 'unknown').toUpperCase()}</strong>
          </div>
          ${component.trend ? `
          <div>
            <span style="font-size: 12px; color: #64748b;">Trend:</span>
            <strong style="margin-left: 5px;">${component.trend}</strong>
          </div>
          ` : ''}
        </div>
        ${component.interpretation ? `<div style="margin-top: 15px; padding: 15px; background: #f8fafc; border-radius: 6px; font-size: 14px;">${component.interpretation}</div>` : ''}
      </div>
    `).join('')}
  </div>
  ` : ''}

  <div class="footer">
    <p><strong>ABENA Healthcare System - eCBome Analysis</strong></p>
    <p>Generated: ${reportDate} | Report ID: ${reportId}</p>
  </div>
</body>
</html>
  `;
};

/**
 * Generate 12-Module Assessment Report
 */
const generateModuleAssessmentReport = (patientData, reportId, timestamp) => {
  // Similar to eCBome report but with more detailed module breakdowns
  return generateECBomeReport(patientData, reportId, timestamp);
};

/**
 * Generate Treatment Progress Report
 */
const generateTreatmentProgressReport = (patientData, reportId, timestamp) => {
  const data = patientData?.data || patientData;
  const patientInfo = data?.patientInfo || {};
  const recommendations = data?.recommendations || [];

  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ABENA Treatment Progress Report - ${patientInfo.name || 'Patient'}</title>
  <style>${getCommonStyles()}</style>
</head>
<body>
  <div class="header">
    <h1>📊 ABENA Treatment Progress Report</h1>
  </div>
  
  <div class="report-meta">
    <div class="meta-item">
      <span class="label">Patient</span>
      <span class="value">${patientInfo.name || 'N/A'}</span>
    </div>
    <div class="meta-item">
      <span class="label">Report ID</span>
      <span class="value">${reportId}</span>
    </div>
  </div>

  <div class="section">
    <h2 class="section-title">Current Treatment Plan</h2>
    ${patientInfo.medications && patientInfo.medications.length > 0 ? `
      <ul class="medication-list">
        ${patientInfo.medications.map(med => `
          <li class="medication-item">
            <div class="medication-name">${med.name}</div>
            <div class="medication-details">${med.dosage} - ${med.frequency}</div>
          </li>
        `).join('')}
      </ul>
    ` : '<p>No active medications</p>'}
  </div>

  ${recommendations && recommendations.length > 0 ? `
  <div class="section">
    <h2 class="section-title">Ongoing Recommendations</h2>
    ${recommendations.map((rec, i) => `
      <div class="recommendation">
        <div class="recommendation-title">${i + 1}. ${rec.title || rec.category || 'Recommendation'}</div>
        <div class="recommendation-text">${rec.description || rec.recommendation || ''}</div>
      </div>
    `).join('')}
  </div>
  ` : ''}

  <div class="footer">
    <p><strong>ABENA Healthcare System</strong></p>
    <p>Generated: ${new Date(timestamp).toLocaleString()}</p>
  </div>
</body>
</html>
  `;
};

/**
 * Generate Lab Results Summary Report
 */
const generateLabResultsReport = (patientData, reportId, timestamp) => {
  const data = patientData?.data || patientData;
  const patientInfo = data?.patientInfo || {};
  const labResults = patientInfo.labResults || patientInfo.lastLabResults || {};
  const results = labResults.results || labResults;
  const testDate = labResults.testDate || 'N/A';
  
  const reportDate = new Date(timestamp).toLocaleString();

  // Helper to get status badge color
  const getStatusBadge = (status) => {
    const statusMap = {
      'normal': 'background: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;',
      'optimal': 'background: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;',
      'good': 'background: #dbeafe; color: #1e40af; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;',
      'borderline': 'background: #fef3c7; color: #92400e; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;',
      'elevated': 'background: #fed7aa; color: #9a3412; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;',
      'high': 'background: #fecaca; color: #991b1b; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;',
      'low': 'background: #fecaca; color: #991b1b; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;',
      'critical': 'background: #fee2e2; color: #7f1d1d; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;'
    };
    return statusMap[status?.toLowerCase()] || statusMap['normal'];
  };

  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ABENA Lab Results - ${patientInfo.name || 'Patient'}</title>
  <style>${getCommonStyles()}</style>
</head>
<body>
  <div class="header">
    <h1>🔬 ABENA Lab Results Summary</h1>
    <p class="subtitle">Comprehensive Laboratory Test Results</p>
  </div>
  
  <div class="report-meta">
    <div class="meta-item">
      <span class="label">Patient</span>
      <span class="value">${patientInfo.name || 'N/A'} (ID: ${patientInfo.id || 'N/A'})</span>
    </div>
    <div class="meta-item">
      <span class="label">Report ID</span>
      <span class="value">${reportId}</span>
    </div>
    <div class="meta-item">
      <span class="label">Test Date</span>
      <span class="value">${testDate}</span>
    </div>
    <div class="meta-item">
      <span class="label">Generated</span>
      <span class="value">${reportDate}</span>
    </div>
  </div>

  <div class="section">
    <h2 class="section-title">Latest Lab Results</h2>
    ${Object.keys(results).length === 0 ? '<p class="text-gray-600">No lab results available for this patient.</p>' : `
    <table>
      <thead>
        <tr>
          <th>Test Name</th>
          <th>Result</th>
          <th>Unit</th>
          <th>Status</th>
          <th>Reference Range</th>
        </tr>
      </thead>
      <tbody>
        ${Object.entries(results).map(([test, data]) => {
          // Handle both old format (simple values) and new format (objects)
          const isObject = typeof data === 'object' && data.value !== undefined;
          const value = isObject ? data.value : data;
          const unit = isObject ? data.unit : '';
          const status = isObject ? data.status : 'normal';
          const reference = isObject ? data.reference : getLabReferenceRange(test);
          
          return `
          <tr>
            <td><strong>${test}</strong></td>
            <td style="font-size: 16px; font-weight: 600;">${value}</td>
            <td style="color: #64748b;">${unit}</td>
            <td><span style="${getStatusBadge(status)}">${status?.toUpperCase() || 'N/A'}</span></td>
            <td style="color: #64748b;">${reference}</td>
          </tr>
        `}).join('')}
      </tbody>
    </table>
    `}
  </div>

  ${Object.keys(results).length > 0 ? `
  <div class="section">
    <h2 class="section-title">Clinical Interpretation</h2>
    <div class="card">
      <h4 style="font-weight: 600; color: #1e293b; margin-bottom: 12px;">Result Summary</h4>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
        <div style="background: #dcfce7; padding: 12px; border-radius: 8px;">
          <div style="font-size: 24px; font-weight: 700; color: #166534;">
            ${Object.values(results).filter(r => {
              const status = (typeof r === 'object' ? r.status : 'normal')?.toLowerCase();
              return status === 'normal' || status === 'optimal' || status === 'good';
            }).length}
          </div>
          <div style="font-size: 12px; color: #166534;">Normal Results</div>
        </div>
        <div style="background: #fef3c7; padding: 12px; border-radius: 8px;">
          <div style="font-size: 24px; font-weight: 700; color: #92400e;">
            ${Object.values(results).filter(r => {
              const status = (typeof r === 'object' ? r.status : 'normal')?.toLowerCase();
              return status === 'borderline' || status === 'elevated';
            }).length}
          </div>
          <div style="font-size: 12px; color: #92400e;">Borderline/Elevated</div>
        </div>
        <div style="background: #fecaca; padding: 12px; border-radius: 8px;">
          <div style="font-size: 24px; font-weight: 700; color: #991b1b;">
            ${Object.values(results).filter(r => {
              const status = (typeof r === 'object' ? r.status : 'normal')?.toLowerCase();
              return status === 'high' || status === 'low' || status === 'critical';
            }).length}
          </div>
          <div style="font-size: 12px; color: #991b1b;">Abnormal Results</div>
        </div>
      </div>
    </div>
  </div>
  ` : ''}

  <div class="footer">
    <p><strong>ABENA Healthcare System - Laboratory Services</strong></p>
    <p>These results should be interpreted by a qualified healthcare provider in the context of patient history and clinical presentation.</p>
    <p style="margin-top: 10px;">Generated: ${reportDate} | Report ID: ${reportId}</p>
  </div>
</body>
</html>
  `;
};

// Helper functions
function generateVitalCard(label, value, unit) {
  if (!value && value !== 0) return '';
  
  return `
    <div class="vital-card">
      <div class="vital-label">${label}</div>
      <div class="vital-value">
        ${value}<span class="vital-unit">${unit ? ' ' + unit : ''}</span>
      </div>
    </div>
  `;
}

function formatComponentName(name) {
  return name
    .replace(/([A-Z])/g, ' $1')
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
    .trim();
}

function getBadgeClass(status) {
  const statusMap = {
    'active': 'success',
    'stable': 'success',
    'monitoring': 'warning',
    'critical': 'danger',
    'inactive': 'info'
  };
  return statusMap[status?.toLowerCase()] || 'info';
}

function getRiskBadgeClass(riskLevel) {
  const riskMap = {
    'low': 'success',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger'
  };
  return riskMap[riskLevel?.toLowerCase()] || 'info';
}

function getScoreBadgeClass(score) {
  if (!score) return 'info';
  const numScore = parseFloat(score);
  if (numScore >= 0.8) return 'success';
  if (numScore >= 0.6) return 'warning';
  return 'danger';
}

function getScoreStatus(score) {
  if (!score) return 'Unknown';
  const numScore = parseFloat(score);
  if (numScore >= 0.8) return 'Excellent';
  if (numScore >= 0.7) return 'Good';
  if (numScore >= 0.6) return 'Fair';
  if (numScore >= 0.5) return 'Needs Attention';
  return 'Critical';
}

function getStatusColor(status) {
  const colorMap = {
    'active': '#16a34a',
    'optimal': '#16a34a',
    'good': '#16a34a',
    'normal': '#0ea5e9',
    'warning': '#f59e0b',
    'elevated': '#f59e0b',
    'critical': '#dc2626',
    'low': '#dc2626'
  };
  return colorMap[status?.toLowerCase()] || '#64748b';
}

function getLabReferenceRange(test) {
  const ranges = {
    'glucose': '70-100 mg/dL',
    'hba1c': '4.0-5.6%',
    'cholesterol': '<200 mg/dL',
    'ldl': '<100 mg/dL',
    'hdl': '>40 mg/dL',
    'triglycerides': '<150 mg/dL'
  };
  return ranges[test?.toLowerCase()] || 'Varies';
}

function getCommonStyles() {
  return `
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 40px 20px; background: #fff; }
    .header { border-bottom: 4px solid #6366f1; padding-bottom: 20px; margin-bottom: 30px; }
    .header h1 { color: #1e293b; font-size: 28px; margin-bottom: 10px; }
    .header .subtitle { color: #64748b; font-size: 14px; }
    .report-meta { background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
    .report-meta .meta-item { display: flex; flex-direction: column; }
    .report-meta .label { font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
    .report-meta .value { font-size: 16px; color: #1e293b; font-weight: 600; }
    .section { margin-bottom: 40px; page-break-inside: avoid; }
    .section-title { font-size: 20px; color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px; }
    .card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 15px; }
    .ecbome-component { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
    .component-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .component-name { font-weight: 600; color: #1e293b; font-size: 16px; }
    .component-score { font-size: 20px; font-weight: 700; color: #6366f1; }
    .progress-bar { width: 100%; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; margin-bottom: 8px; }
    .progress-fill { height: 100%; background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%); border-radius: 4px; }
    .recommendation { background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
    .recommendation-title { font-weight: 600; color: #166534; margin-bottom: 5px; }
    .recommendation-text { color: #15803d; font-size: 14px; }
    .medication-list, .allergy-list { list-style: none; }
    .medication-item { background: white; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; margin-bottom: 8px; }
    .medication-name { font-weight: 600; color: #1e293b; margin-bottom: 4px; }
    .medication-details { font-size: 14px; color: #64748b; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th { background: #f1f5f9; padding: 12px; text-align: left; font-weight: 600; color: #475569; border-bottom: 2px solid #e2e8f0; }
    td { padding: 12px; border-bottom: 1px solid #e2e8f0; color: #1e293b; }
    .footer { margin-top: 60px; padding-top: 20px; border-top: 2px solid #e2e8f0; text-align: center; color: #64748b; font-size: 12px; }
    @media print { body { padding: 20px; } .section { page-break-inside: avoid; } }
  `;
}

export default {
  generateReport,
  downloadReport,
  printReport,
  ReportTypes
};

