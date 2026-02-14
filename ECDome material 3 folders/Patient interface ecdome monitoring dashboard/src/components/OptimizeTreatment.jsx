import React, { useMemo, useState } from 'react';
import { Loader2, Zap, CheckCircle2, Copy, ExternalLink } from 'lucide-react';

const DEFAULT_QUANTUM_BASE =
  import.meta.env.VITE_QUANTUM_API_URL ||
  'https://abena-quantum-healthcare-platform.onrender.com';

function normalizeList(input) {
  return String(input || '')
    .split(',')
    .map(s => s.trim())
    .filter(Boolean);
}

export default function OptimizeTreatment({ onBack }) {
  const [medicationsText, setMedicationsText] = useState('Warfarin 5mg');
  const [supplementsText, setSupplementsText] = useState('Fish Oil 1000mg');
  const [conditionsText, setConditionsText] = useState('Type 2 Diabetes');

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const payload = useMemo(() => {
    return {
      patient_id: 'JANE_001',
      medications: normalizeList(medicationsText),
      supplements: normalizeList(supplementsText),
      conditions: normalizeList(conditionsText),
      run_ibm_job: true
    };
  }, [medicationsText, supplementsText, conditionsText]);

  const runOptimize = async () => {
    setSubmitting(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${DEFAULT_QUANTUM_BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data?.error || data?.detail || 'Request failed');
      }

      if (!data?.success) {
        throw new Error(data?.error || 'Optimization failed');
      }

      setResult(data.results || data);
    } catch (e) {
      setError(e?.message || 'Network error');
    } finally {
      setSubmitting(false);
    }
  };

  const ibmJobId = result?.ibm_job?.job_id || null;
  const ibmBackend = result?.ibm_job?.backend || null;
  const interaction = Array.isArray(result?.drug_interactions) ? result.drug_interactions[0] : null;

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 md:p-8">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Optimize My Treatment</h2>
          <p className="text-sm text-gray-600">
            Live demo workflow: submit your inputs, run quantum-backed analysis, and show the IBM Job ID.
          </p>
        </div>
        {onBack && (
          <button
            onClick={onBack}
            className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
          >
            Back
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-sm font-semibold text-gray-800 mb-2">Medications (comma-separated)</label>
          <input
            value={medicationsText}
            onChange={(e) => setMedicationsText(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Warfarin 5mg, Metformin 500mg"
          />
        </div>
        <div>
          <label className="block text-sm font-semibold text-gray-800 mb-2">Supplements (comma-separated)</label>
          <input
            value={supplementsText}
            onChange={(e) => setSupplementsText(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Fish Oil 1000mg, Vitamin K"
          />
        </div>
        <div>
          <label className="block text-sm font-semibold text-gray-800 mb-2">Conditions (comma-separated)</label>
          <input
            value={conditionsText}
            onChange={(e) => setConditionsText(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Type 2 Diabetes"
          />
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center mb-6">
        <button
          onClick={runOptimize}
          disabled={submitting}
          className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold hover:shadow-lg disabled:opacity-60"
        >
          {submitting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
          {submitting ? 'Running Quantum Optimization…' : 'Optimize My Treatment'}
        </button>

        <div className="text-xs text-gray-600">
          Quantum API: <span className="font-mono">{DEFAULT_QUANTUM_BASE}</span>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 mb-6">
          <div className="font-semibold mb-1">Error</div>
          <div className="text-sm">{error}</div>
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-green-50 border border-green-200">
            <div className="flex items-center gap-2 text-green-800 font-semibold">
              <CheckCircle2 className="w-5 h-5" />
              Analysis completed (Job submitted)
            </div>
            <div className="text-sm text-green-800 mt-2">
              Patient: <span className="font-mono">{result.patient_id}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl border border-gray-200 bg-white">
              <h3 className="font-bold text-gray-900 mb-2">IBM Quantum Proof</h3>
              {ibmJobId ? (
                <>
                  <div className="text-sm text-gray-700 mb-2">
                    <div><span className="font-semibold">Job ID:</span> <span className="font-mono">{ibmJobId}</span></div>
                    {ibmBackend && <div><span className="font-semibold">Backend:</span> <span className="font-mono">{ibmBackend}</span></div>}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => navigator.clipboard.writeText(ibmJobId)}
                      className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
                    >
                      <Copy className="w-4 h-4" />
                      Copy Job ID
                    </button>
                    <button
                      onClick={() => window.open('https://quantum.ibm.com/', '_blank', 'noopener,noreferrer')}
                      className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
                    >
                      <ExternalLink className="w-4 h-4" />
                      Open IBM Quantum Dashboard
                    </button>
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    Tip: open IBM Quantum, paste the Job ID in your Jobs view to show it live on-screen.
                  </div>
                </>
              ) : (
                <div className="text-sm text-gray-600">
                  IBM Job ID not available. (If this is Render: set <span className="font-mono">QISKIT_IBM_TOKEN</span> on the Quantum service and redeploy.)
                </div>
              )}
            </div>

            <div className="p-4 rounded-xl border border-gray-200 bg-white">
              <h3 className="font-bold text-gray-900 mb-2">Clinical Recommendation</h3>
              {interaction ? (
                <div className="text-sm text-gray-700">
                  <div className="mb-2">
                    <span className="font-semibold">Detected:</span>{' '}
                    {interaction.medication1} + {interaction.medication2} ({interaction.severity} risk)
                  </div>
                  <div className="p-3 rounded-lg bg-gray-50 border border-gray-200">
                    {interaction.recommendation}
                  </div>
                </div>
              ) : (
                <div className="text-sm text-gray-600">
                  No high-risk interaction detected for the provided inputs.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


