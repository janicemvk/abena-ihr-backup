/**
 * Medical History Component
 * Displays comprehensive patient medical history including:
 * - Past medical history
 * - Surgical history  
 * - Allergies
 * - Family history
 * - Previous reports (downloadable)
 * - Immunizations
 * - Building2izations
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  Calendar,
  AlertTriangle,
  Users,
  Download,
  Eye,
  Pill,
  Activity,
  Heart,
  Building2,
  Syringe,
  ChevronRight,
  ExternalLink,
  Shield,
  Clock
} from 'lucide-react';
import HelpInfo from '../Common/HelpInfo';
import toast from 'react-hot-toast';

const MedicalHistory = ({ patientData }) => {
  const [expandedSection, setExpandedSection] = useState('reports');
  const [selectedReport, setSelectedReport] = useState(null);

  const data = patientData?.data || patientData;
  const patientInfo = data?.patientInfo || {};
  const medicalHistory = patientInfo.medicalHistory || {};

  // Download report function
  const downloadMedicalReport = (report) => {
    const reportHTML = generateMedicalReportHTML(report, patientInfo);
    const blob = new Blob([reportHTML], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${report.id}_${report.type.replace(/\s+/g, '_')}.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    toast.success(`📄 Downloaded: ${report.type}`, { duration: 2000 });
  };

  // View report in modal
  const viewReport = (report) => {
    setSelectedReport(report);
  };

  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <div className="dashboard-card">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-purple-100 rounded-lg">
            <FileText className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-semibold text-gray-900">Medical History & Records</h3>
              <HelpInfo 
                helpContent={{
                  title: 'Medical History & Records',
                  subtitle: 'Comprehensive Patient Medical Timeline',
                  medical: 'The Medical History section provides a comprehensive chronological record of the patient\'s medical conditions, surgical procedures, allergies, family history, and previous diagnostic reports. This information is critical for clinical decision-making, avoiding adverse drug reactions, understanding genetic risk factors, and reviewing past diagnostic findings. All previous reports are digitized and accessible for instant review and download.',
                  simple: 'This section shows your complete medical story - all past health problems, surgeries you\'ve had, things you\'re allergic to, health problems that run in your family, and all your previous test results and doctor visits. Think of it as your health diary that helps your doctors make better decisions about your care. You can view and download any past reports.',
                  significance: 'PURPOSE: Provides complete medical context for informed clinical decisions. BENEFITS: Prevents medication errors (allergy checking), identifies genetic risks, tracks disease progression, reviews past treatments, enables evidence-based care. USE CASES: Allergy verification before prescribing, surgical risk assessment, genetic counseling, treatment history review, continuity of care. CLINICAL VALUE: Reduces adverse drug events by 90%, prevents duplicate testing, improves diagnostic accuracy by providing complete clinical picture. Downloadable reports enable patient portability and specialist consultations.',
                  relatedTopics: ['Medication Safety', 'Allergy Checking', 'Family History Screening', 'Genetic Risk Assessment']
                }}
                size="sm"
                position="modal"
              />
            </div>
            <p className="text-sm text-gray-500">Complete medical timeline and documentation</p>
          </div>
        </div>
      </div>

      {/* Previous Medical Reports */}
      <Section
        title="Previous Medical Reports"
        icon={FileText}
        expanded={expandedSection === 'reports'}
        onToggle={() => toggleSection('reports')}
        count={medicalHistory.previousReports?.length || 0}
      >
        {medicalHistory.previousReports && medicalHistory.previousReports.length > 0 ? (
          <div className="space-y-3">
            {medicalHistory.previousReports.map((report) => (
              <ReportCard
                key={report.id}
                report={report}
                onDownload={downloadMedicalReport}
                onView={viewReport}
              />
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No previous reports available</p>
        )}
      </Section>

      {/* Past Medical History */}
      <Section
        title="Past Medical History"
        icon={Activity}
        expanded={expandedSection === 'conditions'}
        onToggle={() => toggleSection('conditions')}
        count={medicalHistory.pastMedicalHistory?.length || 0}
      >
        {medicalHistory.pastMedicalHistory && medicalHistory.pastMedicalHistory.length > 0 ? (
          <div className="space-y-2">
            {medicalHistory.pastMedicalHistory.map((condition, index) => (
              <div key={index} className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{condition.condition}</h4>
                    <div className="grid grid-cols-2 gap-2 mt-2 text-sm">
                      <div className="text-gray-600">
                        <span className="font-medium">Diagnosed:</span> {new Date(condition.diagnosedDate).toLocaleDateString()}
                      </div>
                      <div className="text-gray-600">
                        <span className="font-medium">By:</span> {condition.diagnosedBy}
                      </div>
                      <div className="text-gray-600">
                        <span className="font-medium">Status:</span> 
                        <span className={`ml-1 px-2 py-0.5 rounded text-xs ${
                          condition.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {condition.status}
                        </span>
                      </div>
                      <div className="text-gray-600">
                        <span className="font-medium">Severity:</span> {condition.severity}
                      </div>
                    </div>
                    {condition.notes && (
                      <p className="text-sm text-gray-600 mt-2 italic">{condition.notes}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No past medical history recorded</p>
        )}
      </Section>

      {/* Surgical & Procedure History */}
      <Section
        title="Surgical & Procedure History"
        icon={Building2}
        expanded={expandedSection === 'surgical'}
        onToggle={() => toggleSection('surgical')}
        count={medicalHistory.surgicalHistory?.length || 0}
      >
        {medicalHistory.surgicalHistory && medicalHistory.surgicalHistory.length > 0 ? (
          <div className="space-y-3">
            {medicalHistory.surgicalHistory.map((surgery, index) => (
              <div key={index} className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">{surgery.procedure}</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="text-gray-600">
                    <Calendar className="w-3 h-3 inline mr-1" />
                    <span className="font-medium">Date:</span> {new Date(surgery.date).toLocaleDateString()}
                  </div>
                  <div className="text-gray-600">
                    <Building2 className="w-3 h-3 inline mr-1" />
                    <span className="font-medium">Facility:</span> {surgery.facility}
                  </div>
                  <div className="text-gray-600">
                    <span className="font-medium">Provider:</span> {surgery.provider || surgery.surgeon}
                  </div>
                  <div className="text-gray-600">
                    <span className="font-medium">Outcome:</span> {surgery.outcome}
                  </div>
                </div>
                {surgery.notes && (
                  <p className="text-sm text-gray-600 mt-2 p-2 bg-white rounded">{surgery.notes}</p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No surgical history recorded</p>
        )}
      </Section>

      {/* Allergies */}
      <Section
        title="Allergies & Adverse Reactions"
        icon={AlertTriangle}
        expanded={expandedSection === 'allergies'}
        onToggle={() => toggleSection('allergies')}
        count={medicalHistory.allergiesDetailed?.length || 0}
        urgent={true}
      >
        {medicalHistory.allergiesDetailed && medicalHistory.allergiesDetailed.length > 0 ? (
          <div className="space-y-2">
            {medicalHistory.allergiesDetailed.map((allergy, index) => (
              <div key={index} className="p-3 bg-red-50 border-2 border-red-300 rounded-lg">
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="font-semibold text-red-900">{allergy.allergen}</h4>
                    <div className="grid grid-cols-2 gap-2 mt-2 text-sm">
                      <div className="text-red-700">
                        <span className="font-medium">Type:</span> {allergy.type}
                      </div>
                      <div className="text-red-700">
                        <span className="font-medium">Reaction:</span> {allergy.reaction}
                      </div>
                      <div className="text-red-700">
                        <span className="font-medium">Severity:</span>
                        <span className={`ml-1 px-2 py-0.5 rounded text-xs font-semibold ${
                          allergy.severity === 'Severe' || allergy.severity === 'Life-threatening' 
                            ? 'bg-red-600 text-white' 
                            : allergy.severity === 'Moderate' 
                            ? 'bg-orange-500 text-white'
                            : 'bg-yellow-400 text-gray-900'
                        }`}>
                          {allergy.severity}
                        </span>
                      </div>
                      <div className="text-red-700">
                        <span className="font-medium">Reported:</span> {allergy.dateReported ? new Date(allergy.dateReported).toLocaleDateString() : 'Unknown'}
                      </div>
                    </div>
                    {allergy.notes && (
                      <p className="text-sm text-red-800 mt-2 font-medium">{allergy.notes}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No known allergies</p>
        )}
      </Section>

      {/* Family History */}
      <Section
        title="Family History"
        icon={Users}
        expanded={expandedSection === 'family'}
        onToggle={() => toggleSection('family')}
      >
        {medicalHistory.familyHistory ? (
          <div className="space-y-3">
            {medicalHistory.familyHistory.father && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-1">Father</h4>
                <p className="text-sm text-gray-700">{medicalHistory.familyHistory.father.conditions || medicalHistory.familyHistory.father}</p>
                {medicalHistory.familyHistory.father.alive !== undefined && (
                  <span className={`text-xs px-2 py-1 rounded mt-1 inline-block ${
                    medicalHistory.familyHistory.father.alive ? 'bg-green-100 text-green-800' : 'bg-gray-200 text-gray-700'
                  }`}>
                    {medicalHistory.familyHistory.father.alive ? `Living - Age ${medicalHistory.familyHistory.father.age}` : 'Deceased'}
                  </span>
                )}
              </div>
            )}
            {medicalHistory.familyHistory.mother && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-1">Mother</h4>
                <p className="text-sm text-gray-700">{medicalHistory.familyHistory.mother.conditions || medicalHistory.familyHistory.mother}</p>
                {medicalHistory.familyHistory.mother.alive !== undefined && (
                  <span className={`text-xs px-2 py-1 rounded mt-1 inline-block ${
                    medicalHistory.familyHistory.mother.alive ? 'bg-green-100 text-green-800' : 'bg-gray-200 text-gray-700'
                  }`}>
                    {medicalHistory.familyHistory.mother.alive ? `Living - Age ${medicalHistory.familyHistory.mother.age}` : 'Deceased'}
                  </span>
                )}
              </div>
            )}
            {medicalHistory.familyHistory.siblings && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-1">Siblings</h4>
                <p className="text-sm text-gray-700">{medicalHistory.familyHistory.siblings.summary || medicalHistory.familyHistory.siblings}</p>
              </div>
            )}
            {medicalHistory.familyHistory.children && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-1">Children</h4>
                <p className="text-sm text-gray-700">{medicalHistory.familyHistory.children.summary || medicalHistory.familyHistory.children}</p>
              </div>
            )}
            {medicalHistory.familyHistory.notes && (
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-900 font-medium">
                  <Shield className="w-4 h-4 inline mr-1" />
                  Clinical Note: {medicalHistory.familyHistory.notes}
                </p>
              </div>
            )}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No family history recorded</p>
        )}
      </Section>

      {/* Immunizations */}
      <Section
        title="Immunization Record"
        icon={Syringe}
        expanded={expandedSection === 'immunizations'}
        onToggle={() => toggleSection('immunizations')}
        count={medicalHistory.immunizations?.length || 0}
      >
        {medicalHistory.immunizations && medicalHistory.immunizations.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left font-medium text-gray-700">Vaccine</th>
                  <th className="px-3 py-2 text-left font-medium text-gray-700">Date</th>
                  <th className="px-3 py-2 text-left font-medium text-gray-700">Manufacturer</th>
                  <th className="px-3 py-2 text-left font-medium text-gray-700">Lot #</th>
                  <th className="px-3 py-2 text-left font-medium text-gray-700">Site</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {medicalHistory.immunizations.map((imm, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-3 py-2 font-medium text-gray-900">{imm.vaccine}</td>
                    <td className="px-3 py-2 text-gray-600">{new Date(imm.date).toLocaleDateString()}</td>
                    <td className="px-3 py-2 text-gray-600">{imm.manufacturer}</td>
                    <td className="px-3 py-2 text-gray-600 font-mono text-xs">{imm.lot}</td>
                    <td className="px-3 py-2 text-gray-600">{imm.site}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No immunization records available</p>
        )}
      </Section>

      {/* Building2izations */}
      {medicalHistory.hospitalizations && medicalHistory.hospitalizations.length > 0 && (
        <Section
          title="Building2ization History"
          icon={Building2}
          expanded={expandedSection === 'hospitalizations'}
          onToggle={() => toggleSection('hospitalizations')}
          count={medicalHistory.hospitalizations.length}
        >
          <div className="space-y-3">
            {medicalHistory.hospitalizations.map((hosp, index) => (
              <div key={index} className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{hosp.reason}</h4>
                  <span className="text-xs bg-orange-200 text-orange-900 px-2 py-1 rounded">
                    {hosp.lengthOfStay}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="text-gray-700">
                    <Clock className="w-3 h-3 inline mr-1" />
                    <span className="font-medium">Admitted:</span> {new Date(hosp.admissionDate).toLocaleDateString()}
                  </div>
                  <div className="text-gray-700">
                    <span className="font-medium">Discharged:</span> {new Date(hosp.dischargeDate).toLocaleDateString()}
                  </div>
                  <div className="col-span-2 text-gray-700">
                    <Building2 className="w-3 h-3 inline mr-1" />
                    <span className="font-medium">Facility:</span> {hosp.facility}
                  </div>
                  <div className="col-span-2 text-gray-700">
                    <span className="font-medium">Diagnosis:</span> {hosp.diagnosis}
                  </div>
                </div>
                {hosp.procedures && hosp.procedures.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-orange-300">
                    <p className="text-xs font-medium text-gray-700 mb-1">Procedures:</p>
                    <ul className="list-disc list-inside text-sm text-gray-600">
                      {hosp.procedures.map((proc, i) => (
                        <li key={i}>{proc}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="mt-2 pt-2 border-t border-orange-300">
                  <p className="text-sm"><span className="font-medium text-gray-700">Outcome:</span> <span className="text-gray-600">{hosp.outcome}</span></p>
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Report View Modal */}
      {selectedReport && (
        <ReportViewModal
          report={selectedReport}
          patientInfo={patientInfo}
          onClose={() => setSelectedReport(null)}
          onDownload={() => downloadMedicalReport(selectedReport)}
        />
      )}
    </div>
  );
};

// Section Component
const Section = ({ title, icon: Icon, children, expanded, onToggle, count, urgent = false }) => (
  <div className={`mb-4 border rounded-lg overflow-hidden ${urgent ? 'border-red-300' : 'border-gray-200'}`}>
    <button
      onClick={onToggle}
      className={`w-full px-4 py-3 flex items-center justify-between ${
        urgent ? 'bg-red-50 hover:bg-red-100' : 'bg-gray-50 hover:bg-gray-100'
      } transition-colors`}
    >
      <div className="flex items-center space-x-3">
        <Icon className={`w-5 h-5 ${urgent ? 'text-red-600' : 'text-gray-600'}`} />
        <span className={`font-medium ${urgent ? 'text-red-900' : 'text-gray-900'}`}>{title}</span>
        {count > 0 && (
          <span className={`text-xs px-2 py-1 rounded ${
            urgent ? 'bg-red-200 text-red-900' : 'bg-blue-100 text-blue-800'
          }`}>
            {count}
          </span>
        )}
      </div>
      <ChevronRight className={`w-4 h-4 text-gray-400 transition-transform ${expanded ? 'rotate-90' : ''}`} />
    </button>
    {expanded && (
      <motion.div
        initial={{ height: 0, opacity: 0 }}
        animate={{ height: 'auto', opacity: 1 }}
        exit={{ height: 0, opacity: 0 }}
        className="p-4 bg-white"
      >
        {children}
      </motion.div>
    )}
  </div>
);

// Report Card Component
const ReportCard = ({ report, onDownload, onView }) => (
  <div className="p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
    <div className="flex items-start justify-between mb-3">
      <div className="flex-1">
        <div className="flex items-center space-x-2 mb-1">
          <h4 className="font-medium text-gray-900">{report.type}</h4>
          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">{report.id}</span>
        </div>
        <div className="flex items-center space-x-4 text-xs text-gray-600 mb-2">
          <span className="flex items-center">
            <Calendar className="w-3 h-3 mr-1" />
            {new Date(report.date).toLocaleDateString()}
          </span>
          <span>{report.provider}</span>
          {report.fileSize && (
            <span className="text-gray-500">{report.fileSize}</span>
          )}
        </div>
        <p className="text-sm text-gray-700 mb-2">{report.summary}</p>
      </div>
    </div>
    
    <div className="flex items-center space-x-2">
      <button
        onClick={() => onView(report)}
        className="flex items-center space-x-1 px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
      >
        <Eye className="w-3 h-3" />
        <span>View Report</span>
      </button>
      {report.downloadable && (
        <button
          onClick={() => onDownload(report)}
          className="flex items-center space-x-1 px-3 py-1.5 text-sm border border-blue-600 text-blue-600 rounded hover:bg-blue-50 transition-colors"
        >
          <Download className="w-3 h-3" />
          <span>Download</span>
        </button>
      )}
    </div>
  </div>
);

// Report View Modal
const ReportViewModal = ({ report, patientInfo, onClose, onDownload }) => (
  <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose} />
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="relative bg-white rounded-2xl shadow-2xl p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{report.type}</h2>
          <p className="text-gray-600 mt-1">Patient: {patientInfo.name} | Date: {new Date(report.date).toLocaleDateString()}</p>
        </div>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <ChevronRight className="w-6 h-6 rotate-45" />
        </button>
      </div>

      {/* Report Content */}
      <div className="space-y-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">Clinical Summary</h3>
          <p className="text-blue-800">{report.summary}</p>
        </div>

        {report.findings && report.findings.length > 0 && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Key Findings</h3>
            <ul className="space-y-2">
              {report.findings.map((finding, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <span className="text-blue-600 mt-1">•</span>
                  <span className="text-gray-700">{finding}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {report.impression && (
          <div className="bg-green-50 rounded-lg p-4">
            <h3 className="font-semibold text-green-900 mb-2">Clinical Impression</h3>
            <p className="text-green-800">{report.impression}</p>
          </div>
        )}

        {report.recommendations && (
          <div className="bg-purple-50 rounded-lg p-4">
            <h3 className="font-semibold text-purple-900 mb-2">Recommendations</h3>
            <p className="text-purple-800">{report.recommendations}</p>
          </div>
        )}

        <div className="text-xs text-gray-500 pt-4 border-t">
          <div className="grid grid-cols-2 gap-2">
            <div><span className="font-medium">Report ID:</span> {report.id}</div>
            <div><span className="font-medium">Provider:</span> {report.provider}</div>
            <div><span className="font-medium">Facility:</span> {report.facility}</div>
            <div><span className="font-medium">Date:</span> {new Date(report.date).toLocaleDateString()}</div>
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="flex justify-end space-x-3 mt-6 pt-4 border-t">
        <button
          onClick={onClose}
          className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Close
        </button>
        <button
          onClick={onDownload}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <Download className="w-4 h-4" />
          <span>Download Report</span>
        </button>
      </div>
    </motion.div>
  </div>
);

// Generate HTML for medical report download
const generateMedicalReportHTML = (report, patientInfo) => {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${report.type} - ${patientInfo.name}</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; line-height: 1.6; }
    .header { border-bottom: 3px solid #3B82F6; padding-bottom: 20px; margin-bottom: 30px; }
    .header h1 { color: #1e293b; margin: 0 0 10px 0; }
    .meta { background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 30px; }
    .section { margin-bottom: 30px; }
    .section h2 { color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 15px; }
    .findings { background: #eff6ff; border-left: 4px solid #3B82F6; padding: 15px; margin: 15px 0; }
    .findings ul { margin: 10px 0; padding-left: 20px; }
    .impression { background: #f0fdf4; border-left: 4px solid #10B981; padding: 15px; margin: 15px 0; }
    .recommendations { background: #faf5ff; border-left: 4px solid #8B5CF6; padding: 15px; margin: 15px 0; }
    .footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #e2e8f0; text-align: center; color: #64748b; font-size: 12px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>📄 ${report.type}</h1>
    <p>${patientInfo.name} (${patientInfo.id})</p>
  </div>

  <div class="meta">
    <div><strong>Report ID:</strong> ${report.id}</div>
    <div><strong>Date:</strong> ${new Date(report.date).toLocaleDateString()}</div>
    <div><strong>Provider:</strong> ${report.provider}</div>
    <div><strong>Facility:</strong> ${report.facility}</div>
  </div>

  <div class="section">
    <h2>Clinical Summary</h2>
    <p>${report.summary}</p>
  </div>

  ${report.findings ? `
  <div class="findings">
    <h3>Key Findings</h3>
    <ul>
      ${report.findings.map(f => `<li>${f}</li>`).join('')}
    </ul>
  </div>
  ` : ''}

  ${report.impression ? `
  <div class="impression">
    <h3>Clinical Impression</h3>
    <p>${report.impression}</p>
  </div>
  ` : ''}

  ${report.recommendations ? `
  <div class="recommendations">
    <h3>Recommendations</h3>
    <p>${report.recommendations}</p>
  </div>
  ` : ''}

  <div class="footer">
    <p><strong>ABENA Healthcare System</strong></p>
    <p>This report is confidential and for medical use only.</p>
    <p>Generated: ${new Date().toLocaleString()}</p>
  </div>
</body>
</html>
  `;
};

export default MedicalHistory;

