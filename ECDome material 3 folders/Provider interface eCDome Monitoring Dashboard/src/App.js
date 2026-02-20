import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { motion } from 'framer-motion';
import ClinicalDashboard from './components/ClinicalDashboard/ClinicalDashboard';
import PatientList from './components/PatientList/PatientList';
import PatientDetail from './components/PatientDetail/PatientDetail';
import Settings from './components/Settings/Settings';
import Reports from './components/Reports/Reports';
import Layout from './components/Layout/Layout';
import { PatientProvider } from './contexts/PatientContext';
import { DashboardProvider } from './contexts/DashboardContext';

const App = () => {
  return (
    <PatientProvider>
      <DashboardProvider>
        <Layout>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Routes>
              <Route path="/" element={<ClinicalDashboard />} />
              <Route path="/dashboard" element={<ClinicalDashboard />} />
              <Route path="/patients" element={<PatientList />} />
              <Route path="/patient/:id" element={<PatientDetail />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </motion.div>
        </Layout>
      </DashboardProvider>
    </PatientProvider>
  );
};

export default App; 