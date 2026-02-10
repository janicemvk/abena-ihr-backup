import { 
  BackgroundModuleOrchestrator, 
  startAllModules, 
  getComprehensiveAnalysis,
  getOrchestratorStatus,
  stopAllModules 
} from '../src/index.js';

/**
 * BASIC USAGE EXAMPLE
 * Demonstrates how to use the 12 Core Background Modules System
 */

async function basicUsageExample() {
  console.log('🚀 Starting 12 Core Background Modules Example...\n');

  // Example patient and user IDs
  const patientId = 'patient-12345';
  const userId = 'user-67890';

  try {
    // Method 1: Using the quick start function
    console.log('📋 Method 1: Quick Start');
    console.log('========================');
    
    const startResult = await startAllModules(patientId, userId);
    console.log('✅ Modules started:', startResult.success);
    console.log('📊 Modules count:', startResult.modules.length);
    console.log('🕐 Started at:', startResult.timestamp);
    console.log('');

    // Wait a bit to let modules initialize
    console.log('⏳ Waiting 5 seconds for modules to initialize...');
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Get orchestrator status
    console.log('📊 Orchestrator Status');
    console.log('=====================');
    const status = getOrchestratorStatus();
    console.log('🔄 Is orchestrating:', status.isOrchestrating);
    console.log('👤 Patient ID:', status.patientId);
    console.log('📈 Active modules:', status.moduleCount);
    console.log('');

    // Get comprehensive analysis
    console.log('🔍 Comprehensive Analysis');
    console.log('========================');
    const analysis = await getComprehensiveAnalysis();
    console.log('📊 Overall health score:', analysis.overallHealthScore.toFixed(2));
    console.log('🧬 Modules analyzed:', Object.keys(analysis.moduleAnalyses).length);
    console.log('🔗 Cross-module insights generated:', Object.keys(analysis.crossModuleInsights).length);
    
    // Display module-specific health scores
    console.log('\n📈 Module Health Scores:');
    Object.entries(analysis.moduleAnalyses).forEach(([moduleName, moduleData]) => {
      if (moduleData.healthScore !== undefined) {
        console.log(`  ${moduleName}: ${moduleData.healthScore.toFixed(2)}`);
      }
    });

    // Display systemic patterns if any
    if (analysis.crossModuleInsights.systemicPatterns.length > 0) {
      console.log('\n⚠️  Systemic Patterns Detected:');
      analysis.crossModuleInsights.systemicPatterns.forEach(pattern => {
        console.log(`  - ${pattern.type}: ${pattern.description} (${pattern.severity})`);
      });
    }

    // Display predictive indicators
    if (analysis.crossModuleInsights.predictiveIndicators.length > 0) {
      console.log('\n🔮 Predictive Indicators:');
      analysis.crossModuleInsights.predictiveIndicators.forEach(indicator => {
        console.log(`  - ${indicator.type}: ${indicator.description} (${indicator.probability * 100}% probability)`);
      });
    }

    console.log('\n🎉 Analysis completed successfully!');

  } catch (error) {
    console.error('❌ Error in basic usage example:', error);
  } finally {
    // Clean up - stop all modules
    console.log('\n🛑 Stopping all modules...');
    await stopAllModules();
    console.log('✅ All modules stopped');
  }
}

/**
 * ADVANCED USAGE EXAMPLE
 * Shows how to use individual modules and custom configurations
 */
async function advancedUsageExample() {
  console.log('\n🔬 Advanced Usage Example...\n');

  // Method 2: Using the orchestrator directly with custom configuration
  console.log('📋 Method 2: Advanced Orchestrator Usage');
  console.log('========================================');

  const orchestrator = new BackgroundModuleOrchestrator();
  
  try {
    // Start with custom patient/user
    const patientId = 'advanced-patient-123';
    const userId = 'advanced-user-456';

    await orchestrator.startAllBackgroundModules(patientId, userId);
    console.log('✅ Advanced orchestrator started');

    // Get status
    const status = orchestrator.getOrchestratorStatus();
    console.log('📊 Advanced status:', {
      isOrchestrating: status.isOrchestrating,
      moduleCount: status.moduleCount,
      patientId: status.patientId
    });

    // Perform immediate analysis
    console.log('\n🔍 Performing immediate comprehensive analysis...');
    const analysis = await orchestrator.getComprehensiveAnalysis();
    
    // Display eCBome integration analysis
    console.log('\n🧬 eCBome Integration Analysis:');
    console.log('  Overall integration score:', analysis.crossModuleInsights.ecbomeIntegration.overallIntegration.toFixed(2));
    console.log('  Systemic ECS health:', analysis.crossModuleInsights.ecbomeIntegration.systemicECSHealth.toFixed(2));
    console.log('  Correlation strength:', analysis.crossModuleInsights.ecbomeIntegration.correlationStrength.toFixed(2));

    // Display module interactions
    if (analysis.crossModuleInsights.moduleInteractions.length > 0) {
      console.log('\n🔄 Module Interactions:');
      analysis.crossModuleInsights.moduleInteractions.forEach(interaction => {
        console.log(`  - ${interaction.modules.join(' ↔ ')}: ${interaction.description}`);
      });
    }

    // Display intervention opportunities
    if (analysis.crossModuleInsights.interventionOpportunities.length > 0) {
      console.log('\n💡 Intervention Opportunities:');
      analysis.crossModuleInsights.interventionOpportunities.forEach(opportunity => {
        console.log(`  - ${opportunity.moduleName}: ${opportunity.interventionType} (${opportunity.expectedImpact} impact)`);
      });
    }

    console.log('\n🎉 Advanced analysis completed!');

  } catch (error) {
    console.error('❌ Error in advanced usage example:', error);
  } finally {
    // Stop the orchestrator
    await orchestrator.stopAllBackgroundModules();
    console.log('✅ Advanced orchestrator stopped');
  }
}

/**
 * MONITORING EXAMPLE
 * Shows how to set up continuous monitoring
 */
async function monitoringExample() {
  console.log('\n📊 Monitoring Example...\n');

  const patientId = 'monitoring-patient-789';
  const userId = 'monitoring-user-012';

  console.log('📋 Setting up continuous monitoring');
  console.log('==================================');

  try {
    // Start monitoring
    await startAllModules(patientId, userId);
    console.log('✅ Monitoring started');

    // Set up periodic analysis reporting
    let analysisCount = 0;
    const maxAnalyses = 3;

    const monitoringInterval = setInterval(async () => {
      analysisCount++;
      console.log(`\n📊 Analysis #${analysisCount} - ${new Date().toLocaleTimeString()}`);
      
      try {
        const analysis = await getComprehensiveAnalysis();
        console.log(`  Overall health score: ${analysis.overallHealthScore.toFixed(2)}`);
        console.log(`  Modules reporting: ${Object.keys(analysis.moduleAnalyses).length}`);
        
        // Check for critical patterns
        const criticalCount = analysis.crossModuleInsights.systemicPatterns.filter(
          p => p.severity === 'HIGH'
        ).length;
        
        if (criticalCount > 0) {
          console.log(`  🚨 Critical patterns detected: ${criticalCount}`);
        } else {
          console.log('  ✅ No critical patterns detected');
        }
        
      } catch (error) {
        console.error('  ❌ Analysis failed:', error.message);
      }

      // Stop after max analyses
      if (analysisCount >= maxAnalyses) {
        clearInterval(monitoringInterval);
        console.log('\n🏁 Monitoring example completed');
        
        // Clean up
        await stopAllModules();
        console.log('✅ Monitoring stopped');
      }
    }, 10000); // Every 10 seconds for demo

  } catch (error) {
    console.error('❌ Error in monitoring example:', error);
  }
}

// Run examples
async function runExamples() {
  console.log('🧬 12 Core Background Modules - Usage Examples');
  console.log('==============================================\n');

  try {
    // Run basic usage example
    await basicUsageExample();
    
    // Wait a bit between examples
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Run advanced usage example  
    await advancedUsageExample();
    
    // Wait a bit more
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Run monitoring example
    await monitoringExample();
    
  } catch (error) {
    console.error('❌ Error running examples:', error);
  }
}

// Export for use in other files
export { 
  basicUsageExample, 
  advancedUsageExample, 
  monitoringExample, 
  runExamples 
};

// Run examples if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runExamples();
} 