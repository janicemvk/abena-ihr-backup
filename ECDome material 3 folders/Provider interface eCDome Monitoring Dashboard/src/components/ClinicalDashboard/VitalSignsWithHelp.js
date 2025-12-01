/**
 * VitalSignsWithHelp Component
 * Example component showing how to integrate HelpInfo into vital signs display
 * This demonstrates the pattern for adding help to any dashboard section
 */

import React from 'react';
import { Heart, Activity, Thermometer, Wind } from 'lucide-react';
import SectionHeader from '../Common/SectionHeader';
import DataCard from '../Common/DataCard';

const VitalSignsWithHelp = ({ vitalSigns, realtimeData }) => {
  // Use realtime data if available, otherwise use static vital signs
  const vitals = realtimeData?.vitalSigns || vitalSigns || {};

  // Helper function to determine status based on value
  const getHeartRateStatus = (hr) => {
    if (!hr) return 'info';
    if (hr < 60 || hr > 100) return 'warning';
    if (hr < 50 || hr > 120) return 'critical';
    return 'normal';
  };

  const getOxygenStatus = (spo2) => {
    if (!spo2) return 'info';
    if (spo2 < 90) return 'critical';
    if (spo2 < 95) return 'warning';
    return 'normal';
  };

  const getTempStatus = (temp) => {
    if (!temp) return 'info';
    if (temp >= 100.4 || temp < 95) return 'critical';
    if (temp >= 99.5 || temp < 96) return 'warning';
    return 'normal';
  };

  const getBPStatus = (bp) => {
    if (!bp) return 'info';
    // Simple parsing of "120/80" format
    const parts = bp.split('/');
    if (parts.length === 2) {
      const systolic = parseInt(parts[0]);
      const diastolic = parseInt(parts[1]);
      if (systolic >= 140 || diastolic >= 90) return 'warning';
      if (systolic >= 180 || diastolic >= 120) return 'critical';
    }
    return 'normal';
  };

  return (
    <div className="dashboard-card">
      {/* Section Header with Help */}
      <SectionHeader
        icon={Heart}
        title="Vital Signs"
        subtitle="Current patient vital measurements"
        helpTopic="vital_signs"
        helpContent={{
          title: 'Vital Signs Overview',
          medical: 'Vital signs are clinical measurements that indicate the status of the body\'s life-sustaining (vital) functions. These measurements include heart rate, blood pressure, respiratory rate, body temperature, and oxygen saturation. They are essential for assessing general physical health, detecting or monitoring medical conditions, and establishing baseline functions.',
          simple: 'Vital signs are basic body measurements that tell us how well your body is working. They\'re like the dashboard lights in a car - they give quick information about your body\'s main systems. Doctors check these first to get a quick picture of your health.',
          significance: 'Abnormal vital signs can indicate acute or chronic medical conditions requiring intervention. Regular monitoring helps detect changes early and guide treatment decisions.',
          relatedTopics: ['Heart Rate', 'Blood Pressure', 'Oxygen Saturation', 'Body Temperature']
        }}
        helpPosition="modal"
      />

      {/* Vital Signs Grid with Individual Help Icons */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
        <DataCard
          label="Heart Rate"
          value={vitals.heartRate || '--'}
          unit="bpm"
          icon={Heart}
          helpTopic="heart_rate"
          status={getHeartRateStatus(vitals.heartRate)}
        />

        <DataCard
          label="Blood Pressure"
          value={vitals.bloodPressure || '--'}
          unit="mmHg"
          icon={Activity}
          helpTopic="blood_pressure"
          status={getBPStatus(vitals.bloodPressure)}
        />

        <DataCard
          label="O₂ Saturation"
          value={vitals.oxygenSaturation || '--'}
          unit="%"
          icon={Wind}
          helpTopic="oxygen_saturation"
          status={getOxygenStatus(vitals.oxygenSaturation)}
        />

        <DataCard
          label="Temperature"
          value={vitals.temperature || '--'}
          unit="°F"
          icon={Thermometer}
          helpTopic="temperature"
          status={getTempStatus(vitals.temperature)}
        />
      </div>

      {/* Additional Vitals if Available */}
      {(vitals.respiratoryRate || vitals.glucose) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          {vitals.respiratoryRate && (
            <DataCard
              label="Respiratory Rate"
              value={vitals.respiratoryRate}
              unit="/min"
              icon={Wind}
              helpContent={{
                title: 'Respiratory Rate',
                medical: 'Respiratory rate (RR) is the number of breaths per minute. Normal adult range is 12-20 breaths/minute at rest. It reflects pulmonary function and metabolic state.',
                simple: 'Respiratory rate is how many breaths you take per minute. Normal is about 12-20 breaths per minute when resting. Faster breathing might mean your body needs more oxygen.',
                normalRange: 'Adults: 12-20 breaths/minute at rest'
              }}
              status={vitals.respiratoryRate >= 12 && vitals.respiratoryRate <= 20 ? 'normal' : 'warning'}
            />
          )}

          {vitals.glucose && (
            <DataCard
              label="Blood Glucose"
              value={vitals.glucose}
              unit="mg/dL"
              helpTopic="glucose"
              status={vitals.glucose >= 70 && vitals.glucose <= 140 ? 'normal' : 'warning'}
            />
          )}
        </div>
      )}

      {/* Timestamp if using realtime data */}
      {realtimeData && realtimeData.timestamp && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 flex items-center">
            <Activity className="w-3 h-3 mr-1" />
            Last updated: {new Date(realtimeData.timestamp).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
};

export default VitalSignsWithHelp;

