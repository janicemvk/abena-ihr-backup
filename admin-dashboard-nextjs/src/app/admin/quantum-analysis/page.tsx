'use client'

import { useEffect, useState } from 'react'
import dynamic from 'next/dynamic'

// Loading component
const LoadingSpinner = () => (
  <div className="min-h-screen bg-clinical-bg flex items-center justify-center">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
      <p className="text-gray-600">Loading Quantum Analysis System...</p>
    </div>
  </div>
)

// Dynamically import the component with SSR completely disabled
const QuantumAnalysisContent = dynamic(
  () => import('./QuantumAnalysisContent'),
  { 
    ssr: false,
    loading: () => <LoadingSpinner />
  }
)

export default function QuantumAnalysisCommandCenter() {
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  // Only render content on client side
  if (!isClient) {
    return <LoadingSpinner />
  }

  return <QuantumAnalysisContent />
}
