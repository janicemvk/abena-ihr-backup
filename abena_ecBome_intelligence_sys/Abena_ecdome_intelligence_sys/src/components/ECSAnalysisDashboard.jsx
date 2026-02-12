import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { receptorNetwork } from '../data/receptorNetwork';

const ECSAnalysisDashboard = () => {
  const [chartData, setChartData] = useState([]);
  const [systemMetrics, setSystemMetrics] = useState({
    overallBalance: 0.72,
    receptorActivity: {},
    ligandLevels: {},
    systemHealth: 'optimal'
  });

  useEffect(() => {
    // Generate time-series data for charts
    const generateChartData = () => {
      const data = [];
      const now = new Date();
      
      for (let i = 29; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        
        data.push({
          date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          // Endocannabinoid ligands
          anandamide: 45 + Math.random() * 20,
          '2-AG': 50 + Math.random() * 15,
          PEA: 55 + Math.random() * 10,
          OEA: 40 + Math.random() * 15,
          // Endocannabinoid receptors
          CB1: 70 + Math.random() * 15,
          CB2: 60 + Math.random() * 15,
          TRPV1: 50 + Math.random() * 15,
          GPR18: 40 + Math.random() * 10,
          // PPAR receptors
          PPARα: 60 + Math.random() * 15,
          PPARγ: 55 + Math.random() * 15,
          PPARδ: 50 + Math.random() * 10,
          // Serotonin receptors
          '5-HT1A': 65 + Math.random() * 10,
          '5-HT2A': 55 + Math.random() * 15,
          '5-HT3': 50 + Math.random() * 10,
          '5-HT4': 45 + Math.random() * 15,
          '5-HT6': 40 + Math.random() * 10,
          '5-HT7': 45 + Math.random() * 10,
          // Dopamine receptors
          D1: 60 + Math.random() * 15,
          D2: 55 + Math.random() * 15,
          D3: 50 + Math.random() * 10,
          D4: 45 + Math.random() * 10,
          D5: 50 + Math.random() * 10,
          // Adrenergic receptors
          α1A: 55 + Math.random() * 15,
          α2A: 50 + Math.random() * 10,
          β1: 60 + Math.random() * 15,
          β2: 65 + Math.random() * 10,
          β3: 45 + Math.random() * 10,
          // System health metrics
          microbiomeHealth: 70 + Math.random() * 15,
          inflammationMarkers: 30 + Math.random() * 15,
          stressResponse: 50 + Math.random() * 20
        });
      }
      
      return data;
    };

    setChartData(generateChartData());

    // Initialize system metrics
    setSystemMetrics({
      overallBalance: 0.72,
      receptorActivity: {
        CB1: 0.75,
        CB2: 0.65,
        TRPV1: 0.55,
        GPR18: 0.45,
        PPARα: 0.65,
        PPARγ: 0.60,
        PPARδ: 0.55
      },
      ligandLevels: {
        anandamide: 0.55,
        '2-AG': 0.58,
        PEA: 0.60,
        OEA: 0.48
      },
      systemHealth: 'optimal'
    });
  }, []);

  // Prepare receptor data for display
  const receptorData = Object.entries(receptorNetwork).slice(0, 8).map(([key, value]) => ({
    receptor: key,
    name: value.name,
    activity: systemMetrics.receptorActivity[key] || 0.5,
    functions: value.functions.length,
    interactions: value.interactions.length
  }));

  // Radar chart data for receptor activity
  const radarData = [
    {
      subject: 'CB1',
      activity: (systemMetrics.receptorActivity.CB1 || 0.5) * 100,
      fullMark: 100
    },
    {
      subject: 'CB2',
      activity: (systemMetrics.receptorActivity.CB2 || 0.5) * 100,
      fullMark: 100
    },
    {
      subject: 'TRPV1',
      activity: (systemMetrics.receptorActivity.TRPV1 || 0.5) * 100,
      fullMark: 100
    },
    {
      subject: 'GPR18',
      activity: (systemMetrics.receptorActivity.GPR18 || 0.5) * 100,
      fullMark: 100
    },
    {
      subject: 'PPARα',
      activity: (systemMetrics.receptorActivity.PPARα || 0.5) * 100,
      fullMark: 100
    },
    {
      subject: 'PPARγ',
      activity: (systemMetrics.receptorActivity.PPARγ || 0.5) * 100,
      fullMark: 100
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            eCS Intelligence System Analysis Dashboard
          </h1>
          <p className="text-lg text-gray-600">
            Real-time endocannabinoid system analysis with receptors, ligands, and system metrics
          </p>
        </div>

        {/* System Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Overall System Balance</h3>
            <div className="text-3xl font-bold text-indigo-600">
              {(systemMetrics.overallBalance * 100).toFixed(0)}%
            </div>
            <p className="text-xs text-gray-500 mt-2">Optimal Range: 65-85%</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Active Receptors</h3>
            <div className="text-3xl font-bold text-green-600">
              {Object.keys(receptorNetwork).length}
            </div>
            <p className="text-xs text-gray-500 mt-2">Total Receptors Monitored</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Ligand Levels</h3>
            <div className="text-3xl font-bold text-blue-600">4</div>
            <p className="text-xs text-gray-500 mt-2">Primary Endocannabinoids</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600 mb-2">System Health</h3>
            <div className="text-3xl font-bold text-green-600 capitalize">
              {systemMetrics.systemHealth}
            </div>
            <p className="text-xs text-gray-500 mt-2">All Systems Operational</p>
          </div>
        </div>

        {/* Receptor Activity Radar Chart */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Receptor Activity Overview</h2>
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="Activity"
                  dataKey="activity"
                  stroke="#4F46E5"
                  fill="#4F46E5"
                  fillOpacity={0.6}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Receptor Information Grid */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Receptor Network Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {receptorData.map((receptor) => (
              <div key={receptor.receptor} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">{receptor.receptor}</h3>
                  <div className="text-sm font-medium text-indigo-600">
                    {(receptor.activity * 100).toFixed(0)}%
                  </div>
                </div>
                <p className="text-xs text-gray-600 mb-3">{receptor.name}</p>
                <div className="space-y-1 text-xs text-gray-500">
                  <div>{receptor.functions} Functions</div>
                  <div>{receptor.interactions} Interactions</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Endocannabinoid Ligands */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Endocannabinoid Ligands</h3>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="anandamide" stroke="#4BC0C0" name="Anandamide" strokeWidth={2} />
                  <Line type="monotone" dataKey="2-AG" stroke="#FF6384" name="2-AG" strokeWidth={2} />
                  <Line type="monotone" dataKey="PEA" stroke="#36A2EB" name="PEA" strokeWidth={2} />
                  <Line type="monotone" dataKey="OEA" stroke="#9966FF" name="OEA" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Endocannabinoid Receptors */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Endocannabinoid Receptors</h3>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="CB1" stroke="#FF9F40" name="CB1" strokeWidth={2} />
                  <Line type="monotone" dataKey="CB2" stroke="#4BC0C0" name="CB2" strokeWidth={2} />
                  <Line type="monotone" dataKey="TRPV1" stroke="#36A2EB" name="TRPV1" strokeWidth={2} />
                  <Line type="monotone" dataKey="GPR18" stroke="#9966FF" name="GPR18" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* PPAR Receptors */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">PPAR Receptors</h3>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="PPARα" stroke="#FF6384" name="PPARα" strokeWidth={2} />
                  <Line type="monotone" dataKey="PPARγ" stroke="#36A2EB" name="PPARγ" strokeWidth={2} />
                  <Line type="monotone" dataKey="PPARδ" stroke="#9966FF" name="PPARδ" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Serotonin Receptors */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Serotonin (5-HT) Receptors</h3>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="5-HT1A" stroke="#FF9F40" name="5-HT1A" strokeWidth={2} />
                  <Line type="monotone" dataKey="5-HT2A" stroke="#4BC0C0" name="5-HT2A" strokeWidth={2} />
                  <Line type="monotone" dataKey="5-HT3" stroke="#36A2EB" name="5-HT3" strokeWidth={2} />
                  <Line type="monotone" dataKey="5-HT4" stroke="#9966FF" name="5-HT4" strokeWidth={2} />
                  <Line type="monotone" dataKey="5-HT6" stroke="#FF6384" name="5-HT6" strokeWidth={2} />
                  <Line type="monotone" dataKey="5-HT7" stroke="#C9CBCF" name="5-HT7" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Dopamine Receptors */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Dopamine Receptors</h3>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="D1" stroke="#FF9F40" name="D1" strokeWidth={2} />
                  <Line type="monotone" dataKey="D2" stroke="#4BC0C0" name="D2" strokeWidth={2} />
                  <Line type="monotone" dataKey="D3" stroke="#36A2EB" name="D3" strokeWidth={2} />
                  <Line type="monotone" dataKey="D4" stroke="#9966FF" name="D4" strokeWidth={2} />
                  <Line type="monotone" dataKey="D5" stroke="#FF6384" name="D5" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Adrenergic Receptors */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Adrenergic Receptors</h3>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="α1A" stroke="#FF9F40" name="α1A" strokeWidth={2} />
                  <Line type="monotone" dataKey="α2A" stroke="#4BC0C0" name="α2A" strokeWidth={2} />
                  <Line type="monotone" dataKey="β1" stroke="#36A2EB" name="β1" strokeWidth={2} />
                  <Line type="monotone" dataKey="β2" stroke="#9966FF" name="β2" strokeWidth={2} />
                  <Line type="monotone" dataKey="β3" stroke="#FF6384" name="β3" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* System Health Metrics */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">System Health Metrics</h3>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="microbiomeHealth" stroke="#4BC0C0" name="Microbiome" strokeWidth={2} />
                  <Line type="monotone" dataKey="inflammationMarkers" stroke="#FF6384" name="Inflammation" strokeWidth={2} />
                  <Line type="monotone" dataKey="stressResponse" stroke="#36A2EB" name="Stress" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Receptor Activity Bar Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Current Receptor Activity Levels</h3>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={receptorData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="receptor" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="activity" fill="#4F46E5" name="Activity %" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ECSAnalysisDashboard;




