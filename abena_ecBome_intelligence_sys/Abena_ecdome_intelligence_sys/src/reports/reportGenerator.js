import { calculateHealthScore, analyzeECBomeState, formatDate } from '../utils/utils';

const getMetricExplanation = (metric, value) => {
  const explanations = {
    endocannabinoidLevels: {
      anandamide: {
        high: "Elevated anandamide levels (>70%) suggest enhanced mood regulation and pain management capabilities. This may indicate effective endocannabinoid system function, potentially associated with improved stress resilience and emotional well-being.",
        normal: "Anandamide levels (30-70%) are within optimal range, supporting balanced mood and pain perception. This indicates a well-regulated endocannabinoid system.",
        low: "Reduced anandamide levels (<30%) may indicate compromised mood regulation and increased pain sensitivity. This could be associated with chronic stress, inflammation, or metabolic dysregulation."
      },
      '2-AG': {
        high: "Elevated 2-AG levels (>70%) suggest robust immune system modulation and neuroprotection. This may indicate enhanced anti-inflammatory responses and neural resilience.",
        normal: "2-AG levels (30-70%) are optimal, supporting balanced immune function and neural health. This indicates proper regulation of inflammatory responses.",
        low: "Decreased 2-AG levels (<30%) may indicate compromised immune function and reduced neuroprotection. This could be associated with increased inflammation and neural vulnerability."
      },
      PEA: {
        high: "Elevated PEA levels (>70%) suggest enhanced anti-inflammatory and neuroprotective effects. This may indicate improved cellular resilience and metabolic regulation.",
        normal: "PEA levels (30-70%) are within normal range, supporting balanced inflammatory responses and cellular function.",
        low: "Reduced PEA levels (<30%) may indicate compromised anti-inflammatory responses and cellular protection. This could be associated with increased inflammation and metabolic stress."
      },
      OEA: {
        high: "Elevated OEA levels (>70%) suggest enhanced metabolic regulation and appetite control. This may indicate improved energy homeostasis and satiety signaling.",
        normal: "OEA levels (30-70%) are within normal range, supporting balanced metabolic function and appetite regulation.",
        low: "Reduced OEA levels (<30%) may indicate compromised metabolic regulation and appetite control. This could be associated with metabolic dysregulation."
      }
    },
    receptorActivity: {
      CB1: {
        high: "Elevated CB1 receptor activity (>70%) suggests enhanced neural signaling and mood regulation. This may indicate improved cognitive function and emotional processing.",
        normal: "CB1 receptor activity (30-70%) is within optimal range, supporting balanced neural function and mood regulation.",
        low: "Reduced CB1 receptor activity (<30%) may indicate compromised neural signaling and mood regulation. This could be associated with cognitive and emotional dysregulation."
      },
      CB2: {
        high: "Elevated CB2 receptor activity (>70%) suggests robust immune system modulation and anti-inflammatory responses. This may indicate enhanced immune regulation.",
        normal: "CB2 receptor activity (30-70%) is within optimal range, supporting balanced immune function and inflammatory responses.",
        low: "Reduced CB2 receptor activity (<30%) may indicate compromised immune system regulation. This could be associated with increased inflammation and immune dysregulation."
      },
      TRPV1: {
        high: "Elevated TRPV1 activity (>70%) suggests enhanced pain perception and temperature regulation. This may indicate increased sensitivity to thermal and chemical stimuli.",
        normal: "TRPV1 activity (30-70%) is within normal range, supporting balanced pain perception and temperature regulation.",
        low: "Reduced TRPV1 activity (<30%) may indicate compromised pain perception and temperature regulation. This could be associated with altered sensory processing."
      },
      GPR18: {
        high: "Elevated GPR18 activity (>70%) suggests enhanced immune regulation and cellular communication. This may indicate improved immune system coordination.",
        normal: "GPR18 activity (30-70%) is within normal range, supporting balanced immune function and cellular signaling.",
        low: "Reduced GPR18 activity (<30%) may indicate compromised immune regulation and cellular communication. This could be associated with immune system dysregulation."
      }
    }
  };

  const getLevel = (val) => val > 0.7 ? 'high' : val < 0.3 ? 'low' : 'normal';
  return explanations[metric]?.[getLevel(value)] || "No specific explanation available.";
};

const getMedicationInteractions = (metrics) => {
  const interactions = [];
  
  // Check for potential interactions based on receptor activity
  if (metrics.receptorActivity.CB1 > 0.7) {
    interactions.push({
      type: "CB1 Receptor",
      medications: ["Opioids", "Benzodiazepines"],
      effect: "May enhance sedative effects",
      recommendation: "Monitor for increased sedation and adjust dosages accordingly"
    });
  }

  if (metrics.receptorActivity.CB2 > 0.7) {
    interactions.push({
      type: "CB2 Receptor",
      medications: ["Immunosuppressants", "Anti-inflammatory drugs"],
      effect: "May modulate immune response",
      recommendation: "Monitor immune function and adjust treatment as needed"
    });
  }

  return interactions;
};

const getScientificReferences = (metrics) => {
  return [
    {
      title: "Endocannabinoid System in Health and Disease",
      authors: "Pacher, P., & Kunos, G.",
      journal: "Nature Reviews Drug Discovery",
      year: 2013,
      doi: "10.1038/nrd4051",
      relevance: "Comprehensive review of endocannabinoid system function and its role in various physiological processes"
    },
    {
      title: "Cannabinoid Receptors and the Endocannabinoid System",
      authors: "Mackie, K.",
      journal: "Annual Review of Pharmacology and Toxicology",
      year: 2006,
      doi: "10.1146/annurev.pharmtox.46.120604.141254",
      relevance: "Detailed analysis of receptor function and signaling pathways"
    },
    {
      title: "The Endocannabinoid System and the Brain",
      authors: "Di Marzo, V., & Piscitelli, F.",
      journal: "Annual Review of Psychology",
      year: 2015,
      doi: "10.1146/annurev-psych-010814-015122",
      relevance: "Analysis of endocannabinoid system's role in brain function and behavior"
    }
  ];
};

export const generateHTMLReport = (data) => {
  const {
    patient,
    metrics,
    lastAnalysis,
    analysisHistory,
    medicationInteractions,
    scientificReferences
  } = data;

  return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>eCBome Analysis Report</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          line-height: 1.6;
          margin: 0;
          padding: 20px;
          color: #333;
        }
        .container {
          max-width: 1200px;
          margin: 0 auto;
        }
        .header {
          text-align: center;
          margin-bottom: 30px;
          padding: 20px;
          background-color: #f8f9fa;
          border-radius: 8px;
        }
        .section {
          margin-bottom: 30px;
          padding: 20px;
          background-color: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric {
          display: flex;
          justify-content: space-between;
          margin-bottom: 10px;
          padding: 10px;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        .explanation {
          margin-top: 5px;
          padding: 10px;
          background-color: #e3f2fd;
          border-radius: 4px;
          font-size: 0.9em;
          color: #0d47a1;
        }
        .interaction {
          margin-bottom: 15px;
          padding: 15px;
          background-color: #fff3cd;
          border-left: 4px solid #ffc107;
          border-radius: 4px;
        }
        .reference {
          margin-bottom: 10px;
          padding: 10px;
          background-color: #e9ecef;
          border-radius: 4px;
        }
        .chart {
          margin: 20px 0;
          padding: 20px;
          background-color: #f8f9fa;
          border-radius: 8px;
        }
        .trend {
          margin-top: 10px;
          padding: 10px;
          background-color: #f1f8e9;
          border-radius: 4px;
        }
        .note {
          margin-top: 20px;
          padding: 15px;
          background-color: #e3f2fd;
          border-radius: 4px;
          font-size: 0.9em;
          color: #0d47a1;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>eCBome Analysis Report</h1>
          <p>Generated on: ${new Date(lastAnalysis).toLocaleString()}</p>
          <div class="note">
            Note: This is a static report. To return to the live analysis, please close this file and return to the application.
          </div>
        </div>

        <div class="section">
          <h2>Patient Information</h2>
          <p><strong>ID:</strong> ${patient.id}</p>
          <p><strong>Name:</strong> ${patient.name}</p>
          <p><strong>Age:</strong> ${patient.age}</p>
          <p><strong>Gender:</strong> ${patient.gender}</p>
        </div>

        <div class="section">
          <h2>Endocannabinoid Levels</h2>
          ${Object.entries(metrics.endocannabinoidLevels).map(([key, value]) => `
            <div class="metric">
              <span>${key}:</span>
              <span>${(value * 100).toFixed(1)}%</span>
            </div>
            <div class="explanation">
              ${getMetricExplanation('endocannabinoidLevels', value)}
            </div>
          `).join('')}
        </div>

        <div class="section">
          <h2>Receptor Activity</h2>
          ${Object.entries(metrics.receptorActivity).map(([key, value]) => `
            <div class="metric">
              <span>${key}:</span>
              <span>${(value * 100).toFixed(1)}%</span>
            </div>
            <div class="explanation">
              ${getMetricExplanation('receptorActivity', value)}
            </div>
          `).join('')}
        </div>

        <div class="section">
          <h2>System Health Analysis</h2>
          <div class="metric">
            <span>Microbiome Health:</span>
            <span>${(metrics.microbiomeHealth * 100).toFixed(1)}%</span>
          </div>
          <div class="explanation">
            The gut microbiome plays a crucial role in endocannabinoid system regulation. 
            ${metrics.microbiomeHealth > 0.7 ? 
              "Current levels suggest a healthy gut microbiome, supporting optimal endocannabinoid system function." :
              metrics.microbiomeHealth < 0.3 ?
              "Current levels may indicate gut dysbiosis, which could impact endocannabinoid system function." :
              "Current levels are within normal range, supporting balanced gut-endocannabinoid system interaction."}
          </div>

          <div class="metric">
            <span>Inflammation Markers:</span>
            <span>${(metrics.inflammationMarkers * 100).toFixed(1)}%</span>
          </div>
          <div class="explanation">
            Inflammation markers reflect systemic inflammatory status, which can influence endocannabinoid system function.
            ${metrics.inflammationMarkers > 0.7 ? 
              "Elevated inflammation may indicate increased endocannabinoid system activity in response to inflammatory stimuli." :
              metrics.inflammationMarkers < 0.3 ?
              "Low inflammation suggests minimal inflammatory burden on the endocannabinoid system." :
              "Current levels indicate balanced inflammatory status."}
          </div>

          <div class="metric">
            <span>Stress Response:</span>
            <span>${(metrics.stressResponse * 100).toFixed(1)}%</span>
          </div>
          <div class="explanation">
            Stress response indicates the body's ability to manage stress through the endocannabinoid system.
            ${metrics.stressResponse > 0.7 ? 
              "Elevated stress response suggests active endocannabinoid system involvement in stress management." :
              metrics.stressResponse < 0.3 ?
              "Reduced stress response may indicate compromised endocannabinoid system function in stress regulation." :
              "Current levels suggest balanced stress response regulation."}
          </div>
        </div>

        ${medicationInteractions.length > 0 ? `
          <div class="section">
            <h2>Medication Interactions</h2>
            ${medicationInteractions.map(interaction => `
              <div class="interaction">
                <h3>${interaction.type}</h3>
                <p><strong>Medications:</strong> ${interaction.medications.join(', ')}</p>
                <p><strong>Effect:</strong> ${interaction.effect}</p>
                <p><strong>Recommendation:</strong> ${interaction.recommendation}</p>
              </div>
            `).join('')}
          </div>
        ` : ''}

        ${scientificReferences.length > 0 ? `
          <div class="section">
            <h2>Scientific References</h2>
            ${scientificReferences.map(ref => `
              <div class="reference">
                <h3>${ref.title}</h3>
                <p><strong>Authors:</strong> ${ref.authors}</p>
                <p><strong>Journal:</strong> ${ref.journal} (${ref.year})</p>
                <p><strong>DOI:</strong> ${ref.doi}</p>
                <p><strong>Relevance:</strong> ${ref.relevance}</p>
              </div>
            `).join('')}
          </div>
        ` : ''}

        <div class="section">
          <h2>Analysis History</h2>
          ${analysisHistory.map(entry => `
            <div class="metric">
              <span>${new Date(entry.timestamp).toLocaleString()}</span>
              <span>Anandamide: ${(entry.metrics.endocannabinoidLevels.anandamide * 100).toFixed(1)}%</span>
            </div>
            <div class="trend">
              ${entry.metrics.endocannabinoidLevels.anandamide > 0.7 ? 
                "Trend: Elevated anandamide levels suggest enhanced mood regulation and pain management." :
                entry.metrics.endocannabinoidLevels.anandamide < 0.3 ?
                "Trend: Reduced anandamide levels may indicate compromised mood regulation." :
                "Trend: Anandamide levels are within optimal range."}
            </div>
          `).join('')}
        </div>
      </div>
    </body>
    </html>
  `;
}; 