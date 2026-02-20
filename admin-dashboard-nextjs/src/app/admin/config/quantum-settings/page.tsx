'use client'

import QuantumSettings from '../quantum-settings'
import Link from 'next/link'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'

export default function QuantumSettingsPage() {
  return (
    <div className="min-h-screen bg-clinical-bg">
      <header className="bg-white shadow-sm border-b border-clinical-border sticky top-0 z-30">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link
                href="/admin/config"
                className="p-2 rounded-lg hover:bg-gray-100"
              >
                <ArrowLeftIcon className="h-5 w-5 text-gray-600" />
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Quantum Analysis Settings</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        <QuantumSettings />
      </main>
    </div>
  )
}

