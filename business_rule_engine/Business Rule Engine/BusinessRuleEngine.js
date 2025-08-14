// Business Rule Engine
// Handles application-specific conflict policies and business logic
// Uses Abena SDK for authentication, data management, privacy, and blockchain

import AbenaSDK from './abena_sdk.js';

class BusinessRuleEngine {
    constructor(config = {}) {
        // Initialize Abena SDK
        this.abena = new AbenaSDK({
            authServiceUrl: config.authServiceUrl || 'http://localhost:3001',
            dataServiceUrl: config.dataServiceUrl || 'http://localhost:8001',
            privacyServiceUrl: config.privacyServiceUrl || 'http://localhost:8002',
            blockchainServiceUrl: config.blockchainServiceUrl || 'http://localhost:8003'
        });

        this.rules = new Map();
        this.ruleCategories = {
            CLINICAL: 'clinical',
            ADMINISTRATIVE: 'administrative',
            REGULATORY: 'regulatory',
            PRIVACY: 'privacy'
        };
        this.initializeDefaultRules();
    }

    // Add a new rule
    async addRule(ruleConfig, userId) {
        const rule = {
            id: ruleConfig.id || this.generateRuleId(),
            name: ruleConfig.name,
            category: ruleConfig.category,
            description: ruleConfig.description,
            condition: ruleConfig.condition, // Function that returns boolean
            action: ruleConfig.action, // Function to execute when rule fires
            priority: ruleConfig.priority || 5,
            enabled: ruleConfig.enabled !== false,
            metadata: ruleConfig.metadata || {},
            createdAt: new Date().toISOString(),
            lastModified: new Date().toISOString(),
            createdBy: userId
        };

        // Store rule using Abena data service with privacy controls
        await this.abena.storeData('business_rules', rule.id, rule, 'rule_management');
        
        this.rules.set(rule.id, rule);
        return rule.id;
    }

    // Update existing rule
    async updateRule(ruleId, updates, userId) {
        const rule = this.rules.get(ruleId);
        if (rule) {
            const updatedRule = { ...rule, ...updates, lastModified: new Date().toISOString() };
            
            // Update rule using Abena data service
            await this.abena.updateData('business_rules', ruleId, updatedRule, 'rule_management');
            
            Object.assign(rule, updatedRule);
            return true;
        }
        return false;
    }

    // Enable/disable rule
    async toggleRule(ruleId, enabled, userId) {
        const rule = this.rules.get(ruleId);
        if (rule) {
            rule.enabled = enabled;
            rule.lastModified = new Date().toISOString();
            
            // Update rule status using Abena data service
            await this.abena.updateData('business_rules', ruleId, { enabled, lastModified: rule.lastModified }, 'rule_management');
            
            return true;
        }
        return false;
    }

    // Execute rules against conflict data
    async processConflict(conflictData, userId) {
        // Get applicable rules with privacy controls
        const applicableRules = await this.getApplicableRules(conflictData, userId);
        const results = [];

        // Sort by priority (lower number = higher priority)
        applicableRules.sort((a, b) => a.priority - b.priority);

        for (const rule of applicableRules) {
            try {
                if (rule.condition(conflictData)) {
                    const actionResult = await rule.action(conflictData, this.abena);
                    results.push({
                        ruleId: rule.id,
                        ruleName: rule.name,
                        result: actionResult,
                        timestamp: new Date().toISOString()
                    });

                    // If rule indicates to stop processing, break
                    if (actionResult && actionResult.stopProcessing) {
                        break;
                    }
                }
            } catch (error) {
                console.error(`Error executing rule ${rule.id}:`, error);
                results.push({
                    ruleId: rule.id,
                    ruleName: rule.name,
                    error: error.message,
                    timestamp: new Date().toISOString()
                });
            }
        }

        const processingResult = {
            conflictId: conflictData.id,
            processedRules: results,
            recommendedAction: this.determineRecommendedAction(results),
            requiresManualReview: this.requiresManualReview(results)
        };

        // Log processing result to blockchain for audit trail
        await this.abena.logToBlockchain('conflict_processing', {
            conflictId: conflictData.id,
            userId,
            result: processingResult,
            timestamp: new Date().toISOString()
        });

        return processingResult;
    }

    // Get rules applicable to specific conflict type
    async getApplicableRules(conflictData, userId) {
        // Get rules from Abena data service with privacy controls
        const allRules = await this.abena.getData('business_rules', null, 'rule_execution');
        
        return allRules.filter(rule => {
            if (!rule.enabled) return false;
            
            // Check if rule applies to this conflict type
            if (rule.metadata.conflictTypes && 
                !rule.metadata.conflictTypes.includes(conflictData.type)) {
                return false;
            }
            
            // Check if rule applies to this data source
            if (rule.metadata.dataSources && 
                !rule.metadata.dataSources.some(source => 
                    conflictData.sources?.includes(source))) {
                return false;
            }
            
            return true;
        });
    }

    // Initialize default clinical rules
    async initializeDefaultRules() {
        // Medication conflict rules
        await this.addRule({
            id: 'medication_dosage_conflict',
            name: 'Medication Dosage Conflict Resolution',
            category: this.ruleCategories.CLINICAL,
            description: 'Handle conflicts in medication dosages between systems',
            condition: (data) => data.type === 'medication_dosage',
            action: async (data, abena) => {
                // Get patient medication history with privacy controls
                const patientMedHistory = await abena.getPatientData(data.patientId, 'medication_conflict_resolution');
                
                // Prefer most recent prescription
                const mostRecent = data.conflictingValues.reduce((latest, current) => 
                    new Date(current.timestamp) > new Date(latest.timestamp) ? current : latest
                );
                
                return {
                    resolution: 'use_most_recent',
                    selectedValue: mostRecent,
                    requiresPhysicianReview: mostRecent.dosage > data.previousDosage * 2
                };
            },
            priority: 1,
            metadata: {
                conflictTypes: ['medication_dosage', 'prescription_conflict'],
                dataSources: ['ehr', 'pharmacy', 'provider_input']
            }
        }, 'system');

        // Lab result conflict rules
        await this.addRule({
            id: 'lab_result_conflict',
            name: 'Lab Result Value Conflict',
            category: this.ruleCategories.CLINICAL,
            description: 'Handle conflicts in lab result values',
            condition: (data) => data.type === 'lab_result',
            action: async (data, abena) => {
                // Get patient lab history with privacy controls
                const patientLabHistory = await abena.getPatientData(data.patientId, 'lab_conflict_resolution');
                
                // Use average if values are within 10% of each other, otherwise flag for review
                const values = data.conflictingValues.map(v => parseFloat(v.value));
                const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
                const variance = Math.max(...values) - Math.min(...values);
                const percentVariance = (variance / avg) * 100;
                
                if (percentVariance <= 10) {
                    return {
                        resolution: 'use_average',
                        selectedValue: avg.toFixed(2),
                        requiresManualReview: false
                    };
                } else {
                    return {
                        resolution: 'requires_review',
                        requiresManualReview: true,
                        reason: 'High variance in lab values'
                    };
                }
            },
            priority: 2,
            metadata: {
                conflictTypes: ['lab_result'],
                dataSources: ['lab_system', 'ehr', 'manual_entry']
            }
        }, 'system');

        // Patient demographic conflicts
        await this.addRule({
            id: 'patient_demo_conflict',
            name: 'Patient Demographics Conflict',
            category: this.ruleCategories.ADMINISTRATIVE,
            description: 'Handle conflicts in patient demographic information',
            condition: (data) => data.type === 'patient_demographics',
            action: async (data, abena) => {
                // Get patient demographic history with privacy controls
                const patientDemoHistory = await abena.getPatientData(data.patientId, 'demographic_conflict_resolution');
                
                // For critical fields, require manual review
                const criticalFields = ['dateOfBirth', 'socialSecurityNumber', 'medicalRecordNumber'];
                const isCritical = criticalFields.includes(data.field);
                
                if (isCritical) {
                    return {
                        resolution: 'requires_manual_review',
                        requiresManualReview: true,
                        priority: 'high',
                        reason: 'Critical demographic field conflict'
                    };
                } else {
                    // For non-critical fields, use most recently updated value
                    const mostRecent = data.conflictingValues.reduce((latest, current) => 
                        new Date(current.lastUpdated) > new Date(latest.lastUpdated) ? current : latest
                    );
                    return {
                        resolution: 'use_most_recent',
                        selectedValue: mostRecent,
                        requiresManualReview: false
                    };
                }
            },
            priority: 1,
            metadata: {
                conflictTypes: ['patient_demographics'],
                dataSources: ['registration', 'ehr', 'insurance']
            }
        }, 'system');

        // Privacy and consent rules
        await this.addRule({
            id: 'privacy_consent_conflict',
            name: 'Privacy Consent Conflict Resolution',
            category: this.ruleCategories.PRIVACY,
            description: 'Handle conflicts in patient privacy and consent settings',
            condition: (data) => data.type === 'privacy_consent',
            action: async (data, abena) => {
                // Get patient privacy settings with privacy controls
                const patientPrivacySettings = await abena.getPatientData(data.patientId, 'privacy_conflict_resolution');
                
                // Always err on the side of more restrictive privacy settings
                const mostRestrictive = data.conflictingValues.reduce((restrictive, current) => 
                    current.restrictionLevel > restrictive.restrictionLevel ? current : restrictive
                );
                
                return {
                    resolution: 'use_most_restrictive',
                    selectedValue: mostRestrictive,
                    requiresManualReview: false,
                    auditRequired: true
                };
            },
            priority: 1,
            metadata: {
                conflictTypes: ['privacy_consent', 'data_sharing'],
                dataSources: ['patient_portal', 'registration', 'legal']
            }
        }, 'system');
    }

    // Determine recommended action based on rule results
    determineRecommendedAction(results) {
        const resolutions = results.map(r => r.result?.resolution).filter(Boolean);
        
        if (resolutions.includes('requires_manual_review') || resolutions.includes('requires_review')) {
            return 'manual_review_required';
        }
        
        if (resolutions.includes('use_most_recent')) {
            return 'auto_resolve_most_recent';
        }
        
        if (resolutions.includes('use_average')) {
            return 'auto_resolve_average';
        }
        
        return 'default_handling';
    }

    // Check if manual review is required
    requiresManualReview(results) {
        return results.some(r => 
            r.result?.requiresManualReview || 
            r.result?.requiresPhysicianReview ||
            r.error
        );
    }

    // Get all rules by category
    async getRulesByCategory(category, userId) {
        const allRules = await this.abena.getData('business_rules', null, 'rule_management');
        return allRules.filter(rule => rule.category === category);
    }

    // Generate unique rule ID
    generateRuleId() {
        return `RULE_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Export rules for backup/transfer
    async exportRules(userId) {
        return await this.abena.getData('business_rules', null, 'rule_export');
    }

    // Import rules from backup
    async importRules(rulesArray, userId) {
        for (const rule of rulesArray) {
            await this.abena.storeData('business_rules', rule.id, rule, 'rule_import');
            this.rules.set(rule.id, rule);
        }
    }

    // Get rule execution statistics
    async getRuleStats(userId) {
        const allRules = await this.abena.getData('business_rules', null, 'rule_statistics');
        
        const stats = {
            totalRules: allRules.length,
            enabledRules: allRules.filter(r => r.enabled).length,
            byCategory: {}
        };

        Object.values(this.ruleCategories).forEach(category => {
            stats.byCategory[category] = allRules.filter(r => r.category === category).length;
        });

        return stats;
    }

    // Get conflict processing history
    async getConflictHistory(patientId, userId) {
        return await this.abena.getPatientData(patientId, 'conflict_history');
    }

    // Get audit trail for rule changes
    async getRuleAuditTrail(ruleId, userId) {
        return await this.abena.getAuditTrail('business_rules', ruleId);
    }
}

export default BusinessRuleEngine; 