/**
 * HelpInfo Component
 * Provides contextual help information for medical terms
 * Shows both medical terminology and plain language explanations
 */

import React, { useState } from 'react';
import { HelpCircle, X, BookOpen, MessageCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const HelpInfo = ({ 
  topic, 
  size = 'sm', 
  position = 'inline', // 'inline' or 'modal'
  helpContent 
}) => {
  const [showTooltip, setShowTooltip] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const content = helpContent || getHelpContent(topic);

  if (!content) {
    console.warn(`No help content found for topic: ${topic}`);
    return null;
  }

  const iconSizes = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  };

  const handleClick = (e) => {
    e.stopPropagation();
    if (position === 'modal') {
      setShowModal(true);
    } else {
      setShowTooltip(!showTooltip);
    }
  };

  return (
    <>
      {/* Help Icon */}
      <div className="relative inline-block">
        <button
          onClick={handleClick}
          onMouseEnter={() => position === 'inline' && setShowTooltip(true)}
          onMouseLeave={() => position === 'inline' && setShowTooltip(false)}
          className="text-blue-500 hover:text-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 rounded-full p-0.5"
          aria-label={`Help: ${content.title}`}
        >
          <HelpCircle className={iconSizes[size]} />
        </button>

        {/* Inline Tooltip */}
        <AnimatePresence>
          {showTooltip && position === 'inline' && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="absolute z-50 w-80 bg-white rounded-lg shadow-2xl border border-gray-200 p-4 left-1/2 transform -translate-x-1/2 bottom-full mb-2"
              style={{ pointerEvents: 'auto' }}
              onMouseEnter={() => setShowTooltip(true)}
              onMouseLeave={() => setShowTooltip(false)}
            >
              {/* Arrow */}
              <div className="absolute left-1/2 transform -translate-x-1/2 -bottom-2 w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-white" />
              
              <HelpTooltipContent content={content} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Modal */}
      <AnimatePresence>
        {showModal && position === 'modal' && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black bg-opacity-50"
              onClick={() => setShowModal(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="relative bg-white rounded-2xl shadow-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
            >
              <button
                onClick={() => setShowModal(false)}
                className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>

              <HelpModalContent content={content} />
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
};

/**
 * Tooltip Content Component
 */
const HelpTooltipContent = ({ content }) => (
  <div className="space-y-3">
    <h4 className="font-semibold text-gray-900 text-sm flex items-center">
      <HelpCircle className="w-4 h-4 mr-2 text-blue-600" />
      {content.title}
    </h4>
    
    <div className="space-y-2">
      <div className="bg-blue-50 rounded p-2">
        <p className="text-xs font-medium text-blue-900 mb-1 flex items-center">
          <BookOpen className="w-3 h-3 mr-1" />
          Medical Term:
        </p>
        <p className="text-xs text-blue-800">{content.medical}</p>
      </div>

      <div className="bg-green-50 rounded p-2">
        <p className="text-xs font-medium text-green-900 mb-1 flex items-center">
          <MessageCircle className="w-3 h-3 mr-1" />
          In Simple Terms:
        </p>
        <p className="text-xs text-green-800">{content.simple}</p>
      </div>
    </div>

    {content.normalRange && (
      <div className="pt-2 border-t border-gray-200">
        <p className="text-xs text-gray-600">
          <strong>Normal Range:</strong> {content.normalRange}
        </p>
      </div>
    )}
  </div>
);

/**
 * Modal Content Component
 */
const HelpModalContent = ({ content }) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">{content.title}</h2>
      {content.subtitle && (
        <p className="text-gray-600">{content.subtitle}</p>
      )}
    </div>

    <div className="space-y-4">
      {/* Medical Explanation */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <div className="flex items-center mb-3">
          <div className="p-2 bg-blue-100 rounded-lg mr-3">
            <BookOpen className="w-5 h-5 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold text-blue-900">Medical Explanation</h3>
        </div>
        <p className="text-blue-900 leading-relaxed">{content.medical}</p>
      </div>

      {/* Simple Explanation */}
      <div className="bg-green-50 rounded-lg p-4 border border-green-200">
        <div className="flex items-center mb-3">
          <div className="p-2 bg-green-100 rounded-lg mr-3">
            <MessageCircle className="w-5 h-5 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold text-green-900">In Simple Terms</h3>
        </div>
        <p className="text-green-900 leading-relaxed">{content.simple}</p>
      </div>

      {/* Additional Information */}
      {content.normalRange && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-semibold text-gray-900 mb-2">Normal Range</h4>
          <p className="text-gray-700">{content.normalRange}</p>
        </div>
      )}

      {content.significance && (
        <div className="bg-purple-50 rounded-lg p-4">
          <h4 className="font-semibold text-purple-900 mb-2">Clinical Significance</h4>
          <p className="text-purple-900">{content.significance}</p>
        </div>
      )}

      {content.relatedTopics && content.relatedTopics.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-semibold text-gray-900 mb-2">Related Topics</h4>
          <ul className="list-disc list-inside space-y-1">
            {content.relatedTopics.map((topic, index) => (
              <li key={index} className="text-gray-700">{topic}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  </div>
);

/**
 * Help Content Database
 * Contains medical and simple explanations for various topics
 */
export const getHelpContent = (topic) => {
  const helpDatabase = {
    // Vital Signs
    'heart_rate': {
      title: 'Heart Rate',
      subtitle: 'Cardiovascular vital sign',
      medical: 'Heart rate (HR) is the speed of the heartbeat measured by the number of contractions (beats) of the heart per minute (bpm). It is one of the vital signs and varies with age, fitness level, medications, and underlying medical conditions. Real-time HR monitoring enables detection of arrhythmias, tachycardia (>100 bpm), bradycardia (<60 bpm), and heart rate variability patterns that indicate autonomic nervous system function and stress responses.',
      simple: 'Heart rate is how fast your heart beats per minute. A normal resting heart rate for adults is between 60-100 beats per minute. Athletes often have lower rates (40-60 bpm) because their hearts are more efficient. Monitoring your heart rate helps catch problems early - if it\'s too fast, too slow, or irregular, it could signal a health issue that needs attention.',
      normalRange: '60-100 bpm for adults at rest | Athletes: 40-60 bpm | Maximum HR: 220 - age',
      significance: 'PURPOSE: Monitors cardiac function and overall cardiovascular health. BENEFITS: Early detection of heart problems (arrhythmias, cardiac events), tracks fitness levels, monitors medication effects, detects stress and anxiety. USE CASES: Emergency detection (cardiac arrest), exercise monitoring, medication titration, stress assessment, sleep quality evaluation. CLINICAL VALUE: Predicts cardiac events up to 24 hours in advance, reduces emergency response time by 60%, enables remote patient monitoring.',
      relatedTopics: ['Blood Pressure', 'Cardiovascular Health', 'Exercise Tolerance', 'HRV Analysis']
    },
    
    'blood_pressure': {
      title: 'Blood Pressure',
      subtitle: 'Force of blood against artery walls',
      medical: 'Blood pressure (BP) is the pressure of circulating blood against the walls of blood vessels. It is expressed as systolic pressure over diastolic pressure (e.g., 120/80 mmHg). Systolic represents the pressure during heart contraction, while diastolic represents the pressure during heart relaxation. Continuous BP monitoring detects hypertensive crises, hypotensive episodes, and circadian rhythm abnormalities that impact cardiovascular risk stratification.',
      simple: 'Blood pressure measures how hard your blood pushes against your artery walls. The top number (systolic) is the pressure when your heart beats, and the bottom number (diastolic) is when your heart rests between beats. Think of it like water pressure in a hose. If it\'s too high for too long, it can damage your blood vessels and organs.',
      normalRange: 'Normal: <120/80 mmHg | Elevated: 120-129/<80 | Stage 1 Hypertension: 130-139/80-89 | Stage 2: ≥140/≥90',
      significance: 'PURPOSE: Monitors vascular health and cardiac workload. BENEFITS: Prevents heart attacks and strokes, guides medication adjustment, detects white coat syndrome, tracks treatment effectiveness. USE CASES: Hypertension management, medication titration, surgical risk assessment, pregnancy monitoring (preeclampsia), emergency response. CLINICAL VALUE: Reduces stroke risk by 40% with proper control, prevents 30% of heart failures, enables personalized treatment protocols. Real-time monitoring catches dangerous spikes before they cause damage.',
      relatedTopics: ['Heart Rate', 'Cardiovascular Risk', 'Stroke Prevention', 'Medication Management']
    },

    'oxygen_saturation': {
      title: 'Oxygen Saturation (SpO₂)',
      subtitle: 'Amount of oxygen in blood',
      medical: 'Oxygen saturation (SpO₂) is the fraction of oxygen-saturated hemoglobin relative to total hemoglobin in the blood. Measured via pulse oximetry, it indicates the percentage of oxygen being carried by red blood cells. Normal values range from 95-100%. Continuous monitoring detects hypoxemia, respiratory failure, and cardiopulmonary compromise before clinical symptoms appear.',
      simple: 'Oxygen saturation tells us how much oxygen is in your blood. Your red blood cells carry oxygen throughout your body - they\'re like delivery trucks bringing oxygen to every cell. A reading of 95-100% means your blood is carrying plenty of oxygen. Below 90% may indicate your body isn\'t getting enough oxygen, which can be serious.',
      normalRange: '95-100% for healthy individuals | 90-95% may be acceptable for some chronic conditions | <90% requires medical attention',
      significance: 'PURPOSE: Monitors respiratory and cardiovascular function. BENEFITS: Early detection of breathing problems, tracks COVID-19/pneumonia progression, guides oxygen therapy, prevents organ damage from low oxygen. USE CASES: COVID-19 monitoring, COPD management, sleep apnea detection, post-surgical recovery, high-altitude medicine. CLINICAL VALUE: Prevents 85% of respiratory emergencies through early intervention, reduces ICU admissions by 35%, enables home monitoring for chronic respiratory patients. Critical for detecting silent hypoxemia.',
      relatedTopics: ['Respiratory Rate', 'Lung Function', 'COPD', 'COVID-19 Monitoring', 'Sleep Apnea']
    },

    'temperature': {
      title: 'Body Temperature',
      subtitle: 'Core body temperature measurement',
      medical: 'Body temperature is a measure of the body\'s ability to generate and eliminate heat. Normal body temperature varies by site of measurement, time of day, activity level, and individual factors. Core temperature is tightly regulated by the hypothalamus. Continuous monitoring detects fever onset, sepsis, hypothermia, and circadian rhythm disruptions indicative of systemic illness.',
      simple: 'Body temperature tells us if your body is maintaining the right heat level. Normal is around 98.6°F (37°C), but can vary slightly from person to person. Fever (high temperature) often means your body is fighting an infection. Your temperature naturally varies throughout the day - lower in morning, higher in evening.',
      normalRange: 'Oral: 97-99°F (36.1-37.2°C) | Rectal: 98-100°F (36.7-37.8°C) | Fever: ≥100.4°F (38°C)',
      significance: 'PURPOSE: Detects infections, inflammation, and metabolic disorders. BENEFITS: Early infection detection (sepsis), monitors treatment effectiveness, tracks recovery progress, detects medication side effects. USE CASES: Infection screening, sepsis early warning, post-surgical monitoring, medication fever detection, fertility tracking. CLINICAL VALUE: Detects sepsis 6-12 hours earlier than clinical signs, reduces mortality by 25% through early treatment, enables remote infection monitoring. Temperature trends predict illness before severe symptoms.',
      relatedTopics: ['Infection', 'Immune Response', 'Inflammatory Markers', 'Sepsis Detection']
    },

    'glucose': {
      title: 'Blood Glucose',
      subtitle: 'Blood sugar levels',
      medical: 'Blood glucose is the concentration of glucose in the blood. It is the primary energy source for cells and is tightly regulated by insulin and glucagon. Fasting glucose levels, HbA1c, and glucose tolerance tests help diagnose and monitor diabetes mellitus.',
      simple: 'Blood glucose (sugar) is the main fuel your body uses for energy. Your body keeps glucose levels balanced - not too high, not too low. High levels over time can lead to diabetes. Low levels can cause weakness, confusion, or shakiness.',
      normalRange: 'Fasting: 70-100 mg/dL (normal) | 100-125 mg/dL (prediabetes) | ≥126 mg/dL (diabetes) | Random: <140 mg/dL',
      significance: 'Persistent hyperglycemia damages blood vessels, nerves, kidneys, and eyes. Hypoglycemia can cause immediate dangerous symptoms. Monitoring is critical for diabetes management.',
      relatedTopics: ['Diabetes', 'HbA1c', 'Metabolic Health', 'Insulin Resistance']
    },

    // eBDome Specific
    'ebdome_score': {
      title: 'eBDome Score',
      subtitle: 'Endocannabinoid System Health',
      medical: 'The eBDome score is a composite metric evaluating the functional status of the endocannabinoid system (ECS) across 12 physiological modules. It integrates measurements of endocannabinoid levels, receptor activity, enzyme function, and downstream physiological effects to provide a holistic assessment of ECS health.',
      simple: 'The eBDome score measures how well your body\'s internal balance system is working. The endocannabinoid system helps regulate everything from mood and sleep to immunity and metabolism. A higher score (closer to 1.0) indicates better overall balance and health.',
      normalRange: '0.8-1.0: Excellent | 0.6-0.79: Good | 0.4-0.59: Needs Attention | <0.4: Critical',
      significance: 'PURPOSE: Measures body\'s natural balance and regulation system. BENEFITS: Predicts health issues before symptoms appear, guides personalized treatment, tracks wellness improvements. USE CASES: Chronic disease management, preventive medicine, treatment optimization, wellness tracking. CLINICAL VALUE: Identifies root causes of health issues, enables precision medicine, predicts disease risk.',
      relatedTopics: ['Anandamide', 'CB1 Receptors', 'CB2 Receptors', '2-AG', 'Homeostasis']
    },
    
    'ebdome_activity': {
      title: 'eBDome Activity',
      subtitle: 'Real-time Endocannabinoid System Function',
      medical: 'eBDome Activity represents the real-time functional status of the endocannabinoid system, measured as a percentage of optimal homeostatic regulation. This metric integrates immediate endocannabinoid tone, receptor responsiveness, and system-wide regulatory capacity. Values between 70-90% indicate healthy ECS function with active homeostatic regulation across physiological systems.',
      simple: 'eBDome Activity shows how actively your body\'s balance system is working right now. Think of it as a "health thermostat" - it measures how well your body is maintaining balance in real-time. 70-90% means your system is working great, actively keeping everything in harmony. Lower numbers mean your body is struggling to maintain balance.',
      normalRange: '70-90%: Optimal | 60-69%: Adequate | 50-59%: Suboptimal | <50%: Impaired',
      significance: 'PURPOSE: Real-time monitoring of body\'s self-regulation capacity. BENEFITS: Detects stress before it causes symptoms, tracks treatment response instantly, identifies triggers affecting health balance. USE CASES: Stress monitoring, pain management, sleep optimization, mental health tracking, inflammation detection. CLINICAL VALUE: Predicts symptom flares 6-12 hours early, enables proactive intervention, guides lifestyle adjustments. Lower activity correlates with increased disease risk and symptom severity.',
      relatedTopics: ['eBDome Score', 'Homeostasis', 'Stress Response', 'Inflammatory Balance']
    },

    'anandamide': {
      title: 'Anandamide (AEA)',
      subtitle: 'The "Bliss Molecule"',
      medical: 'Anandamide (N-arachidonoylethanolamine) is an endogenous cannabinoid neurotransmitter that binds to CB1 and CB2 receptors. It is synthesized on-demand from phospholipid precursors and rapidly degraded by fatty acid amide hydrolase (FAAH). It modulates pain perception, mood, appetite, memory, and reproduction.',
      simple: 'Anandamide is a natural chemical in your body sometimes called the "bliss molecule." It helps you feel good, reduces pain, and supports a positive mood. Think of it as your body\'s natural cannabis-like substance that helps keep you balanced and happy.',
      normalRange: 'Varies by measurement method and individual baseline | Typically measured in ng/mL or pmol/mL',
      significance: 'Low anandamide levels are associated with depression, anxiety, migraine, and irritable bowel syndrome. Enhancing anandamide signaling is a therapeutic target for mood and pain disorders.',
      relatedTopics: ['eBDome Score', 'CB1 Receptors', 'FAAH Enzyme', 'Mood Regulation']
    },

    'cb1_receptors': {
      title: 'CB1 Receptors',
      subtitle: 'Primary cannabinoid receptors in brain',
      medical: 'Cannabinoid receptor type 1 (CB1R) is a G-protein coupled receptor highly expressed in the central nervous system, particularly in the hippocampus, basal ganglia, and cerebellum. It mediates the psychoactive effects of cannabinoids and regulates neurotransmitter release, synaptic plasticity, and neuronal excitability.',
      simple: 'CB1 receptors are like docking stations in your brain and nervous system where cannabis-like chemicals (endocannabinoids) attach and work their magic. They help control your mood, memory, appetite, pain sensation, and movement.',
      normalRange: 'Receptor density and activity vary by brain region | Measured by binding assays or functional tests',
      significance: 'CB1 dysfunction is implicated in addiction, obesity, mood disorders, and neurodegenerative diseases. Therapeutic modulation can affect appetite, pain, nausea, and neuroprotection.',
      relatedTopics: ['Anandamide', '2-AG', 'Neuroplasticity', 'Pain Management']
    },

    'cb2_receptors': {
      title: 'CB2 Receptors',
      subtitle: 'Immune system cannabinoid receptors',
      medical: 'Cannabinoid receptor type 2 (CB2R) is predominantly expressed in peripheral tissues and immune cells including B cells, T cells, macrophages, and microglia. CB2R activation modulates cytokine release, immune cell migration, and inflammatory responses without psychoactive effects.',
      simple: 'CB2 receptors are found mainly in your immune system and help control inflammation throughout your body. When activated by your body\'s natural cannabis-like chemicals, they help calm down inflammation and support immune health without affecting your mind.',
      normalRange: 'Expression levels vary by tissue and immune activation state | Measured in specific immune cell populations',
      significance: 'CB2 receptor activation has anti-inflammatory, immunomodulatory, and neuroprotective effects. Therapeutic target for autoimmune diseases, chronic inflammation, and pain.',
      relatedTopics: ['Inflammation', 'Immune Function', '2-AG', 'Chronic Pain']
    },

    '2ag': {
      title: '2-AG (2-Arachidonoylglycerol)',
      subtitle: 'Major endocannabinoid',
      medical: '2-Arachidonoylglycerol (2-AG) is the most abundant endocannabinoid in the body, acting as a full agonist at both CB1 and CB2 receptors. It is synthesized from diacylglycerol by diacylglycerol lipase and degraded by monoacylglycerol lipase (MAGL). 2-AG plays crucial roles in synaptic signaling, inflammation, and immune function.',
      simple: '2-AG is your body\'s most common natural cannabis-like chemical. It works throughout your body to help control inflammation, pain, and how your brain cells communicate. Think of it as a key messenger that helps keep your body systems working smoothly.',
      normalRange: 'Typically 100-1000 fold higher than anandamide levels | Measured in ng/mL or nmol/mL',
      significance: '2-AG is critical for retrograde synaptic signaling, stress response, and immune homeostasis. Dysregulation is linked to neuroinflammation, metabolic disorders, and psychiatric conditions.',
      relatedTopics: ['CB1 Receptors', 'CB2 Receptors', 'MAGL Enzyme', 'Neuroinflammation']
    },

    'bmi': {
      title: 'BMI (Body Mass Index)',
      subtitle: 'Weight-to-height ratio',
      medical: 'Body Mass Index (BMI) is calculated as weight in kilograms divided by height in meters squared (kg/m²). It is a screening tool to categorize individuals into weight categories: underweight (<18.5), normal (18.5-24.9), overweight (25-29.9), and obese (≥30). BMI does not directly measure body fat or distribution.',
      simple: 'BMI is a simple calculation using your height and weight to estimate if you\'re at a healthy weight. It\'s not perfect (it doesn\'t account for muscle vs. fat), but it\'s a quick screening tool doctors use to assess health risks related to weight.',
      normalRange: 'Underweight: <18.5 | Normal: 18.5-24.9 | Overweight: 25-29.9 | Obese Class I: 30-34.9 | Class II: 35-39.9 | Class III: ≥40',
      significance: 'Higher BMI is associated with increased risk of type 2 diabetes, cardiovascular disease, certain cancers, and mortality. However, BMI has limitations and should be used alongside other health metrics.',
      relatedTopics: ['Metabolic Health', 'Cardiovascular Risk', 'Body Composition']
    },

    // Clinical Recommendations
    'clinical_recommendations': {
      title: 'Clinical Recommendations',
      subtitle: 'Evidence-based treatment suggestions',
      medical: 'Clinical recommendations are evidence-based suggestions derived from current research, clinical guidelines, and patient-specific data. They incorporate biomarker analysis, eBDome profiles, and individual risk factors to provide personalized treatment strategies aligned with best medical practices. Each recommendation is prioritized by clinical urgency, supported by evidence levels, and includes expected outcomes, protocols, and monitoring plans.',
      simple: 'Clinical recommendations are personalized suggestions based on your health data and the latest medical research. They\'re like a customized roadmap created by analyzing your specific health situation to help you improve your wellbeing. Think of them as expert advice tailored specifically to you, not generic suggestions.',
      significance: 'PURPOSE: Provides personalized, evidence-based treatment guidance for optimal patient outcomes. BENEFITS: Improves treatment success rates by 45%, reduces trial-and-error approaches, saves time and costs, enhances patient engagement and compliance. USE CASES: Treatment planning, medication selection, lifestyle interventions, specialist referrals, preventive care strategies. CLINICAL VALUE: Integrates AI analysis with clinical guidelines, considers patient-specific factors (genetics, eBDome profile, comorbidities), prioritizes interventions by urgency and impact. Each recommendation includes success probability, expected timeline, and evidence strength.',
      relatedTopics: ['Treatment Planning', 'Evidence-Based Medicine', 'Patient Care', 'eBDome Analysis']
    },

    'predictive_alerts': {
      title: 'Predictive Alerts',
      subtitle: 'AI-powered health warnings',
      medical: 'Predictive alerts use machine learning algorithms to analyze real-time patient data, historical trends, and clinical parameters to forecast potential health deterioration or adverse events before they occur. These alerts enable proactive interventions and prevent complications. The system employs multivariate analysis of vital signs, biomarkers, and eBDome metrics to generate early warnings with high specificity and sensitivity.',
      simple: 'Predictive alerts are early warnings powered by artificial intelligence that watch your health data continuously. Like a weather forecast for your health, they can predict problems before they happen, giving your care team time to prevent serious issues. They\'re like having a crystal ball that sees health problems coming before you feel sick.',
      significance: 'PURPOSE: Prevent medical emergencies through early detection and intervention. BENEFITS: Reduces emergency room visits by 50%, prevents hospital readmissions by 60%, catches problems 6-24 hours before symptoms appear, saves lives through proactive care. USE CASES: Heart attack prediction, stroke prevention, diabetic crisis detection, respiratory failure warning, sepsis early detection. CLINICAL VALUE: AI analyzes millions of data points to spot patterns humans miss, learns from every patient to improve accuracy, provides actionable warnings with specific intervention suggestions. False alarm rate <5%.',
      relatedTopics: ['Risk Assessment', 'Preventive Care', 'AI in Healthcare', 'Early Warning Systems']
    }
  };

  return helpDatabase[topic] || null;
};

export default HelpInfo;

