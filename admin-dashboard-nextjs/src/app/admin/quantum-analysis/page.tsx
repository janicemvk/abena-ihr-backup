'use client'

import dynamic from 'next/dynamic'

// Dynamically import the component with SSR disabled
const QuantumAnalysisContent = dynamic(
  () => import('./QuantumAnalysisContent'),
  { 
    ssr: false,
    loading: () => (
      <div className="min-h-screen bg-clinical-bg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Quantum Analysis System...</p>
        </div>
      </div>
    )
  }
)

export default function QuantumAnalysisCommandCenter() {
  return <QuantumAnalysisContent />
}
