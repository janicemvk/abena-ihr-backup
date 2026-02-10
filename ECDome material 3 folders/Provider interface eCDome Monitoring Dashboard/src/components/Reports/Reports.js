/**
 * Reports Component
 * Displays all patient lab reports in table format
 * Allows viewing and downloading individual reports
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  FileText, 
  Download, 
  Eye, 
  Search,
  Filter,
  Calendar,
  User,
  Activity,
  ChevronRight,
  Beaker
} from 'lucide-react';
import { mockPatientDetails, mockPatients } from '../../services/mockPatientData';
import { generateReport, downloadReport, ReportTypes } from '../../utils/reportGenerator';
import HelpInfo from '../Common/HelpInfo';
import toast from 'react-hot-toast';

const Reports = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPatient, setFilterPatient] = useState('all');
  const [allReports, setAllReports] = useState([]);
  const [filteredReports, setFilteredReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Generate list of all lab reports
  useEffect(() => {
    const reports = [];
    
    Object.keys(mockPatientDetails).forEach(patientId => {
      const patientDetails = mockPatientDetails[patientId];
      const patientInfo = patientDetails.patientInfo;
      const labResults = patientInfo.labResults;
      
      if (labResults && labResults.results && Object.keys(labResults.results).length > 0) {
        const patient = mockPatients.find(p => p.id === patientId);
        
        reports.push({
          id: `LAB-${patientId}-${Date.now()}`,
          reportId: `ABENA-LAB-${patientId.replace('PAT-', '')}`,
          patientId: patientId,
          patientName: patientInfo.name || patient?.name,
          patientMRN: patient?.mrn,
          type: 'Lab Results Summary',
          reportType: 'lab_results',
          date: labResults.testDate || new Date(labResults.lastUpdated).toLocaleDateString(),
          timestamp: labResults.lastUpdated,
          testCount: Object.keys(labResults.results).length,
          status: getReportStatus(labResults),
          abnormalCount: countAbnormalResults(labResults.results),
          patientData: { data: patientDetails },
          labResults: labResults
        });
      }
    });

    // Sort by date (most recent first)
    reports.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    setAllReports(reports);
    setFilteredReports(reports);
  }, []);

  // Filter reports
  useEffect(() => {
    let filtered = [...allReports];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(report => 
        report.patientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.reportId.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.patientMRN?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Patient filter
    if (filterPatient !== 'all') {
      filtered = filtered.filter(report => report.patientId === filterPatient);
    }

    setFilteredReports(filtered);
  }, [searchTerm, filterPatient, allReports]);

  const handleViewReport = async (report) => {
    setIsGenerating(true);
    try {
      const reportData = await generateReport(ReportTypes.LAB_RESULTS, report.patientData);
      
      // Open in new window
      const newWindow = window.open('', '_blank');
      newWindow.document.write(reportData.content);
      newWindow.document.close();
      
      toast.success('Report opened in new window');
      setIsGenerating(false);
    } catch (error) {
      toast.error('Failed to generate report');
      setIsGenerating(false);
    }
  };

  const handleDownloadReport = async (report) => {
    setIsGenerating(true);
    try {
      const reportData = await generateReport(ReportTypes.LAB_RESULTS, report.patientData);
      downloadReport(reportData, `${report.patientName.replace(/\s+/g, '_')}_Lab_Results_${report.reportId}.html`);
      toast.success(`Downloaded: ${report.patientName} - Lab Results`);
      setIsGenerating(false);
    } catch (error) {
      toast.error('Failed to download report');
      setIsGenerating(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'normal': 'bg-green-100 text-green-800',
      'review': 'bg-yellow-100 text-yellow-800',
      'critical': 'bg-red-100 text-red-800'
    };
    return statusMap[status] || statusMap['normal'];
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <FileText className="w-7 h-7 text-green-600" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-3xl font-bold text-gray-900">Patient Lab Reports</h1>
                <HelpInfo 
                  helpContent={{
                    title: 'Patient Lab Reports Repository',
                    subtitle: 'Centralized Laboratory Test Results',
                    medical: 'The Lab Reports Repository provides centralized access to all patient laboratory test results across the patient panel. Each report contains comprehensive lab panels including lipid profiles, metabolic panels, complete blood counts, kidney/liver function tests, and specialized biomarkers relevant to patient conditions. Reports can be viewed instantly or downloaded for external sharing, specialist consultations, or patient records.',
                    simple: 'This is where all patient lab test results are stored in one place. You can see everyone\'s test results, search for specific patients or tests, view detailed results on screen, or download them as files. It\'s like a filing cabinet for all lab work, making it easy to find any patient\'s test results quickly.',
                    significance: 'PURPOSE: Centralized lab result access and management. BENEFITS: Quick report lookup, trend analysis across patients, easy sharing with specialists, downloadable for patient records, reduces duplicate testing. USE CASES: Pre-appointment review, trend monitoring, specialist referrals, patient education, quality assurance. CLINICAL VALUE: Reduces result lookup time by 70%, enables population health analysis, improves care coordination, prevents unnecessary repeat testing.',
                    relatedTopics: ['Lab Result Interpretation', 'Trend Analysis', 'Clinical Decision Support']
                  }}
                  size="sm"
                  position="modal"
                />
              </div>
              <p className="text-gray-600">View and download all patient laboratory test results</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-600">{filteredReports.length} reports</span>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
            {/* Search */}
            <div className="md:col-span-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by patient name, Report ID, or MRN..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Patient Filter */}
            <div className="md:col-span-4">
              <select
                value={filterPatient}
                onChange={(e) => setFilterPatient(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="all">All Patients</option>
                {mockPatients.map(patient => (
                  <option key={patient.id} value={patient.id}>{patient.name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Active Filters */}
          {(searchTerm || filterPatient !== 'all') && (
            <div className="mt-3 flex items-center space-x-2">
              <span className="text-sm text-gray-600">Active filters:</span>
              {searchTerm && (
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                  Search: "{searchTerm}"
                </span>
              )}
              {filterPatient !== 'all' && (
                <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                  Patient: {mockPatients.find(p => p.id === filterPatient)?.name}
                </span>
              )}
              <button
                onClick={() => {
                  setSearchTerm('');
                  setFilterPatient('all');
                }}
                className="text-xs text-blue-600 hover:text-blue-800"
              >
                Clear all
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Reports List Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Report ID</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Patient</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Report Type</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Test Date</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Tests</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Status</th>
              <th className="px-6 py-4 text-right text-xs font-medium text-gray-700 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredReports.map((report, index) => (
              <motion.tr
                key={report.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.03 }}
                className="hover:bg-green-50 transition-colors cursor-pointer"
                onClick={() => handleViewReport(report)}
              >
                {/* Report ID */}
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-2">
                    <Beaker className="w-5 h-5 text-green-600" />
                    <div>
                      <div className="font-medium text-gray-900">{report.reportId}</div>
                      <div className="text-xs text-gray-500">{report.id}</div>
                    </div>
                  </div>
                </td>

                {/* Patient */}
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <User className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">{report.patientName}</div>
                      <div className="text-sm text-gray-600">{report.patientId}</div>
                      <div className="text-xs text-gray-500">MRN: {report.patientMRN}</div>
                    </div>
                  </div>
                </td>

                {/* Report Type */}
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-gray-500" />
                    <span className="text-sm text-gray-900">{report.type}</span>
                  </div>
                </td>

                {/* Test Date */}
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-1 text-sm text-gray-600">
                    <Calendar className="w-4 h-4" />
                    <span>{report.date}</span>
                  </div>
                </td>

                {/* Test Count */}
                <td className="px-6 py-4">
                  <div className="text-center">
                    <div className="text-lg font-bold text-blue-600">{report.testCount}</div>
                    <div className="text-xs text-gray-500">tests</div>
                    {report.abnormalCount > 0 && (
                      <div className="text-xs text-red-600 font-medium mt-1">
                        {report.abnormalCount} abnormal
                      </div>
                    )}
                  </div>
                </td>

                {/* Status */}
                <td className="px-6 py-4">
                  <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${getStatusBadge(report.status)}`}>
                    {report.status.toUpperCase()}
                  </span>
                </td>

                {/* Actions */}
                <td className="px-6 py-4">
                  <div className="flex items-center justify-end space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleViewReport(report);
                      }}
                      disabled={isGenerating}
                      className="px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors flex items-center space-x-1 disabled:opacity-50"
                      title="View Report"
                    >
                      <Eye className="w-3 h-3" />
                      <span>View</span>
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDownloadReport(report);
                      }}
                      disabled={isGenerating}
                      className="px-3 py-1.5 text-sm border border-green-600 text-green-600 rounded hover:bg-green-50 transition-colors flex items-center space-x-1 disabled:opacity-50"
                      title="Download Report"
                    >
                      <Download className="w-3 h-3" />
                      <span>Download</span>
                    </button>
                  </div>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>

        {/* Empty State */}
        {filteredReports.length === 0 && (
          <div className="p-12 text-center">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No reports found</h3>
            <p className="text-gray-600">
              {searchTerm || filterPatient !== 'all' 
                ? 'No reports match your current filters.' 
                : 'No lab reports available.'}
            </p>
          </div>
        )}
      </div>

      {/* Summary Stats */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Reports</p>
              <p className="text-2xl font-bold text-gray-900">{allReports.length}</p>
            </div>
            <FileText className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Tests</p>
              <p className="text-2xl font-bold text-blue-600">
                {allReports.reduce((sum, r) => sum + r.testCount, 0)}
              </p>
            </div>
            <Beaker className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Abnormal Results</p>
              <p className="text-2xl font-bold text-red-600">
                {allReports.reduce((sum, r) => sum + r.abnormalCount, 0)}
              </p>
            </div>
            <Activity className="w-8 h-8 text-red-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Patients with Labs</p>
              <p className="text-2xl font-bold text-purple-600">{allReports.length}</p>
            </div>
            <User className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <FileText className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-900 mb-1">Report Access</h4>
            <p className="text-sm text-blue-700">
              Click any row to view the full report in a new window, or use the Download button to save reports as HTML files. 
              All reports can be printed to PDF from your browser for patient records or specialist referrals.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper functions
const getReportStatus = (labResults) => {
  if (!labResults.results) return 'normal';
  
  const results = Object.values(labResults.results);
  const hasAbnormal = results.some(r => {
    const status = (typeof r === 'object' ? r.status : 'normal')?.toLowerCase();
    return status === 'high' || status === 'low' || status === 'critical';
  });
  
  if (hasAbnormal) return 'review';
  return 'normal';
};

const countAbnormalResults = (results) => {
  if (!results) return 0;
  
  return Object.values(results).filter(r => {
    const status = (typeof r === 'object' ? r.status : 'normal')?.toLowerCase();
    return status === 'high' || status === 'low' || status === 'critical' || status === 'elevated';
  }).length;
};

export default Reports; 