import React, { useMemo, useState } from 'react';
import { Loader2, Zap, CheckCircle2, Copy, ExternalLink } from 'lucide-react';

const DEFAULT_QUANTUM_BASE =
  import.meta.env.VITE_QUANTUM_API_URL ||
  'https://abena-quantum-healthcare-platform.onrender.com';

const PRECOMPUTED_IBM_PROOFS = [
  {
    label: '4-qubit validation',
    jobId: 'd5skpr8husoc73epvu20',
    backend: 'ibm_fez',
    date: 'Jan 27, 2026',
    notes: 'Baseline proof (16 combinations)',
  },
  {
    label: '6-qubit validation',
    jobId: 'd6957k5bujdc73d1pod0',
    backend: 'ibm_fez',
    date: 'Feb 15, 2026',
    notes: 'Scaled proof (64 combinations)',
  },
];

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
  const [manualIbmJobId, setManualIbmJobId] = useState('');
  const [selectedPrecomputedProof, setSelectedPrecomputedProof] = useState(PRECOMPUTED_IBM_PROOFS[1].jobId);

  const [submitting, setSubmitting] = useState(false);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [requestInfo, setRequestInfo] = useState(null);
  const [requestStatus, setRequestStatus] = useState(null); // pending | ordered | released

  const payload = useMemo(() => {
    return {
      patient_id: 'JANE_001',
      medications: normalizeList(medicationsText),
      supplements: normalizeList(supplementsText),
      conditions: normalizeList(conditionsText),
    };
  }, [medicationsText, supplementsText, conditionsText]);

  const submitToProvider = async () => {
    setSubmitting(true);
    setError(null);
    setResult(null);
    setRequestInfo(null);
    setRequestStatus(null);

    try {
      const res = await fetch(`${DEFAULT_QUANTUM_BASE}/api/quantum-requests`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data?.error || data?.detail || 'Request failed');
      }

      if (!data?.success || !data?.request) {
        throw new Error(data?.error || 'Failed to submit request');
      }

      setRequestInfo(data.request);
      setRequestStatus(data.request.status || 'pending');
    } catch (e) {
      setError(e?.message || 'Network error');
    } finally {
      setSubmitting(false);
    }
  };

  const checkStatus = async () => {
    if (!requestInfo?.request_id) return;
    setChecking(true);
    setError(null);
    try {
      // Check request status (patient can see status but not results until released)
      const reqRes = await fetch(
        `${DEFAULT_QUANTUM_BASE}/api/quantum-requests?patient_id=${encodeURIComponent(payload.patient_id)}`,
        { method: 'GET' }
      );
      const reqData = await reqRes.json();
      if (!reqRes.ok) throw new Error(reqData?.error || 'Failed to check request status');

      const latest = Array.isArray(reqData?.requests)
        ? reqData.requests.find(r => r?.request_id === requestInfo.request_id)
        : null;

      if (latest?.status) setRequestStatus(latest.status);

      // Only fetch released results via the patient-facing endpoint
      const relRes = await fetch(
        `${DEFAULT_QUANTUM_BASE}/api/quantum-results?patient_id=${encodeURIComponent(payload.patient_id)}`,
        { method: 'GET' }
      );
      const relData = await relRes.json();
      if (relRes.ok && Array.isArray(relData?.results) && relData.results.length > 0) {
        const released = relData.results[0];
        if (released?.request_id === requestInfo.request_id && released?.results) {
          setRequestStatus('released');
          setResult(released.results);
        }
      }
    } catch (e) {
      setError(e?.message || 'Status check failed');
    } finally {
      setChecking(false);
    }
  };

  const ibmJobId = result?.ibm_job?.job_id || null;
  const ibmBackend = result?.ibm_job?.backend || null;
  const interaction = Array.isArray(result?.drug_interactions) ? result.drug_interactions[0] : null;
  const precomputed = PRECOMPUTED_IBM_PROOFS.find(p => p.jobId === selectedPrecomputedProof) || PRECOMPUTED_IBM_PROOFS[1];

  // Priority:
  // 1) Released result proof
  // 2) Manual pasted Job ID
  // 3) Selected precomputed proof
  const displayedJobId = ibmJobId || (manualIbmJobId.trim() ? manualIbmJobId.trim() : precomputed.jobId);
  const displayedBackend = ibmBackend || precomputed.backend;

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 md:p-8">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Submit Intake for Provider Review</h2>
          <p className="text-sm text-gray-600">
            Workflow: you submit medications/supplements/conditions, your provider orders the quantum analysis, then releases results back to you.
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
          onClick={submitToProvider}
          disabled={submitting}
          className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold hover:shadow-lg disabled:opacity-60"
        >
          {submitting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
          {submitting ? 'Submitting…' : 'Submit to Provider for Review'}
        </button>

        <button
          onClick={checkStatus}
          disabled={!requestInfo?.request_id || checking}
          className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl border border-gray-300 text-gray-700 font-semibold hover:bg-gray-50 disabled:opacity-60"
        >
          {checking ? <Loader2 className="w-5 h-5 animate-spin" /> : <CheckCircle2 className="w-5 h-5" />}
          {checking ? 'Checking…' : 'Check Status'}
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

      {requestInfo && (
        <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-blue-900 mb-6">
          <div className="font-semibold mb-1">Request submitted</div>
          <div className="text-sm">
            Request ID: <span className="font-mono">{requestInfo.request_id}</span>
          </div>
          <div className="text-sm mt-1">
            Status: <span className="font-semibold">{requestStatus || requestInfo.status || 'pending'}</span>
            {(requestStatus || requestInfo.status) === 'pending' && (
              <span className="ml-2 text-blue-800">Waiting for provider to order the analysis.</span>
            )}
            {(requestStatus || requestInfo.status) === 'ordered' && (
              <span className="ml-2 text-blue-800">Ordered by provider. Waiting for release.</span>
            )}
            {(requestStatus || requestInfo.status) === 'released' && (
              <span className="ml-2 text-blue-800">Released. Results available below.</span>
            )}
          </div>
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-green-50 border border-green-200">
            <div className="flex items-center gap-2 text-green-800 font-semibold">
              <CheckCircle2 className="w-5 h-5" />
              Results released by provider
            </div>
            <div className="text-sm text-green-800 mt-2">
              Patient: <span className="font-mono">{result.patient_id}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl border border-gray-200 bg-white">
              <h3 className="font-bold text-gray-900 mb-2">IBM Quantum Proof</h3>
              <div className="text-sm text-gray-700 mb-3">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                  Pre-computed on IBM Quantum hardware (demo reliability)
                </span>
              </div>

              <div className="mb-3 grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Choose proof run
                  </label>
                  <select
                    value={selectedPrecomputedProof}
                    onChange={(e) => setSelectedPrecomputedProof(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  >
                    {PRECOMPUTED_IBM_PROOFS.map((p) => (
                      <option key={p.jobId} value={p.jobId}>
                        {p.label} — {p.backend} — {p.date}
                      </option>
                    ))}
                  </select>
                  <div className="text-xs text-gray-500 mt-1">{precomputed.notes}</div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Paste IBM Job ID (optional override)
                  </label>
                  <input
                    value={manualIbmJobId}
                    onChange={(e) => setManualIbmJobId(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-xs"
                    placeholder="e.g. d6957k5bujdc73d1pod0"
                  />
                  <div className="text-xs text-gray-500 mt-1">
                    Use this when you submit a fresh IBM job locally during the demo.
                  </div>
                </div>
              </div>

              <div className="text-sm text-gray-700 mb-2">
                <div>
                  <span className="font-semibold">Job ID:</span>{' '}
                  <span className="font-mono">{displayedJobId}</span>
                  {!ibmJobId && manualIbmJobId.trim() && (
                    <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-700">
                      Pasted
                    </span>
                  )}
                </div>
                <div>
                  <span className="font-semibold">Backend:</span>{' '}
                  <span className="font-mono">{displayedBackend}</span>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => navigator.clipboard.writeText(displayedJobId)}
                  className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
                >
                  <Copy className="w-4 h-4" />
                  Copy Job ID
                </button>
                <button
                  onClick={() => window.open('https://quantum.cloud.ibm.com/', '_blank', 'noopener,noreferrer')}
                  className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
                >
                  <ExternalLink className="w-4 h-4" />
                  Open IBM Quantum Dashboard
                </button>
              </div>

              <div className="text-xs text-gray-500 mt-2">
                Tip: open IBM Quantum, search/paste the Job ID in your recent workloads to verify live on-screen.
              </div>
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


