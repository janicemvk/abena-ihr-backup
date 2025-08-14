import AbenaSDK from '@abena/sdk';

class ClinicalDecisionSupport {
  constructor(options = {}) {
    // Initialize Abena SDK for clinical decision support
    this.abena = new AbenaSDK({
      authServiceUrl: options.authServiceUrl || 'http://localhost:3001',
      dataServiceUrl: options.dataServiceUrl || 'http://localhost:8001',
      privacyServiceUrl: options.privacyServiceUrl || 'http://localhost:8002',
      blockchainServiceUrl: options.blockchainServiceUrl || 'http://localhost:8003'
    });
    
    this.rules = new Map();
    this.initializeRules();
  }

  /**
   * Initialize clinical decision support rules
   */
  initializeRules() {
    // Lab Result Rules
    this.rules.set('lab-results', {
      criticalValues: {
        'glucose': { low: 70, high: 200 },
        'sodium': { low: 135, high: 145 },
        'potassium': { low: 3.5, high: 5.0 },
        'creatinine': { low: 0.6, high: 1.2 }
      },
      trends: {
        'hemoglobin': { significant: 2.0 },
        'white-blood-cells': { significant: 3.0 }
      }
    });

    // Medication Rules
    this.rules.set('medications', {
      interactions: [
        {
          medications: ['warfarin', 'aspirin'],
          severity: 'high',
          action: 'require-review'
        },
        {
          medications: ['metformin', 'contrast-dye'],
          severity: 'high',
          action: 'hold-medication'
        }
      ],
      dosing: {
        'warfarin': {
          inrRange: { low: 2.0, high: 3.0 },
          adjustmentRules: [
            { inr: '< 1.5', action: 'increase-dose' },
            { inr: '> 4.0', action: 'hold-dose' }
          ]
        }
      }
    });

    // Vital Signs Rules
    this.rules.set('vital-signs', {
      ranges: {
        'blood-pressure': {
          systolic: { low: 90, high: 140 },
          diastolic: { low: 60, high: 90 }
        },
        'heart-rate': { low: 60, high: 100 },
        'temperature': { low: 97.0, high: 99.0 },
        'oxygen-saturation': { low: 95, high: 100 }
      },
      trends: {
        'blood-pressure': { significant: 20 },
        'heart-rate': { significant: 20 }
      }
    });
  }

  /**
   * Analyze clinical results and provide decision support
   * @param {Object} params - Analysis parameters
   * @returns {Promise<Object>} - Analysis results with recommendations
   */
  async analyzeResults({ patientId, dataType, results, context }) {
    try {
      const analysis = {
        timestamp: new Date(),
        patientId,
        dataType,
        findings: [],
        recommendations: [],
        alerts: []
      };

      // Apply appropriate rules based on data type
      switch (dataType) {
        case 'lab-results':
          await this.analyzeLabResults(results, analysis);
          break;
        case 'medications':
          await this.analyzeMedications(results, analysis);
          break;
        case 'vital-signs':
          await this.analyzeVitalSigns(results, analysis);
          break;
        default:
          console.warn(`No specific rules for data type: ${dataType}`);
      }

      // Add clinical context
      await this.addClinicalContext(analysis, context);

      // Generate recommendations
      await this.generateRecommendations(analysis);

      return analysis;
    } catch (error) {
      console.error('Error in clinical decision support:', error);
      throw error;
    }
  }

  /**
   * Analyze lab results
   * @param {Array} results - Lab results to analyze
   * @param {Object} analysis - Analysis object to update
   */
  async analyzeLabResults(results, analysis) {
    const labRules = this.rules.get('lab-results');

    for (const result of results) {
      if (!result.code || !result.value) continue;

      const testCode = result.code.coding[0].code;
      const value = result.valueQuantity.value;
      const unit = result.valueQuantity.unit;

      // Check critical values
      if (labRules.criticalValues[testCode]) {
        const { low, high } = labRules.criticalValues[testCode];
        if (value < low || value > high) {
          analysis.alerts.push({
            type: 'critical-value',
            test: testCode,
            value,
            unit,
            threshold: { low, high }
          });
        }
      }

      // Check trends if historical data available
      if (result.trend && labRules.trends[testCode]) {
        const { significant } = labRules.trends[testCode];
        if (Math.abs(result.trend) > significant) {
          analysis.findings.push({
            type: 'significant-trend',
            test: testCode,
            trend: result.trend,
            threshold: significant
          });
        }
      }
    }
  }

  /**
   * Analyze medications
   * @param {Array} results - Medication data to analyze
   * @param {Object} analysis - Analysis object to update
   */
  async analyzeMedications(results, analysis) {
    const medRules = this.rules.get('medications');

    // Check for drug interactions
    for (const interaction of medRules.interactions) {
      const hasInteraction = interaction.medications.every(med => 
        results.some(r => r.medicationCode === med)
      );

      if (hasInteraction) {
        analysis.alerts.push({
          type: 'drug-interaction',
          medications: interaction.medications,
          severity: interaction.severity,
          action: interaction.action
        });
      }
    }

    // Check dosing
    for (const result of results) {
      if (medRules.dosing[result.medicationCode]) {
        const dosingRules = medRules.dosing[result.medicationCode];
        
        if (result.inr) {
          if (result.inr < dosingRules.inrRange.low || result.inr > dosingRules.inrRange.high) {
            analysis.recommendations.push({
              type: 'dosing-adjustment',
              medication: result.medicationCode,
              currentInr: result.inr,
              targetRange: dosingRules.inrRange
            });
          }
        }
      }
    }
  }

  /**
   * Analyze vital signs
   * @param {Array} results - Vital signs data to analyze
   * @param {Object} analysis - Analysis object to update
   */
  async analyzeVitalSigns(results, analysis) {
    const vitalRules = this.rules.get('vital-signs');

    for (const result of results) {
      if (!result.code || !result.value) continue;

      const vitalCode = result.code.coding[0].code;
      const value = result.valueQuantity.value;

      // Check ranges
      if (vitalRules.ranges[vitalCode]) {
        const range = vitalRules.ranges[vitalCode];
        
        if (vitalCode === 'blood-pressure') {
          if (value.systolic < range.systolic.low || value.systolic > range.systolic.high ||
              value.diastolic < range.diastolic.low || value.diastolic > range.diastolic.high) {
            analysis.alerts.push({
              type: 'abnormal-vital',
              vital: vitalCode,
              value,
              range
            });
          }
        } else {
          if (value < range.low || value > range.high) {
            analysis.alerts.push({
              type: 'abnormal-vital',
              vital: vitalCode,
              value,
              range
            });
          }
        }
      }

      // Check trends
      if (result.trend && vitalRules.trends[vitalCode]) {
        const { significant } = vitalRules.trends[vitalCode];
        if (Math.abs(result.trend) > significant) {
          analysis.findings.push({
            type: 'significant-trend',
            vital: vitalCode,
            trend: result.trend,
            threshold: significant
          });
        }
      }
    }
  }

  /**
   * Add clinical context to analysis
   * @param {Object} analysis - Analysis object to update
   * @param {Object} context - Clinical context
   */
  async addClinicalContext(analysis, context) {
    try {
      // Use Abena SDK to get patient clinical context with auto-handled privacy
      const patientContext = await this.abena.getPatientClinicalContext(analysis.patientId, 'clinical_decision_support');
      
      analysis.context = {
        conditions: patientContext.conditions || [],
        riskFactors: patientContext.riskFactors || [],
        allergies: patientContext.allergies || [],
        medications: patientContext.medications || [],
        labHistory: patientContext.labHistory || [],
        vitalHistory: patientContext.vitalHistory || []
      };
    } catch (error) {
      console.warn('Could not retrieve patient clinical context:', error.message);
      // Fallback to context provided in parameters
      if (context.patientConditions) {
        analysis.context = {
          conditions: context.patientConditions,
          riskFactors: context.riskFactors || [],
          allergies: context.allergies || []
        };
      }
    }
  }

  /**
   * Generate clinical recommendations
   * @param {Object} analysis - Analysis object to update
   */
  async generateRecommendations(analysis) {
    // Add recommendations based on findings and alerts
    for (const alert of analysis.alerts) {
      switch (alert.type) {
        case 'critical-value':
          analysis.recommendations.push({
            type: 'immediate-action',
            priority: 'high',
            action: 'review-critical-value',
            details: {
              test: alert.test,
              value: alert.value,
              threshold: alert.threshold
            }
          });
          break;
        case 'drug-interaction':
          analysis.recommendations.push({
            type: 'medication-review',
            priority: alert.severity === 'high' ? 'high' : 'medium',
            action: alert.action,
            details: {
              medications: alert.medications
            }
          });
          break;
        case 'abnormal-vital':
          analysis.recommendations.push({
            type: 'vital-sign-review',
            priority: 'medium',
            action: 'assess-patient',
            details: {
              vital: alert.vital,
              value: alert.value
            }
          });
          break;
      }
    }

    // Add recommendations based on trends
    for (const finding of analysis.findings) {
      if (finding.type === 'significant-trend') {
        analysis.recommendations.push({
          type: 'trend-analysis',
          priority: 'medium',
          action: 'monitor-closely',
          details: {
            parameter: finding.test || finding.vital,
            trend: finding.trend
          }
        });
      }
    }
  }
}

export { ClinicalDecisionSupport }; 