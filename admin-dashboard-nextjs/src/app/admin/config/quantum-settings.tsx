'use client'

import { useState, useEffect } from 'react'
import { CpuChipIcon, CurrencyDollarIcon, ClockIcon } from '@heroicons/react/24/outline'
import { config } from '@/config'

interface QuantumSettings {
  setting_type: string
  entity_id: string | null
  auto_trigger: boolean
  hybrid_mode: boolean
  hybrid_rules: any
  cost_limit_per_month: number | null
  enabled: boolean
}

export default function QuantumSettings() {
  const [settings, setSettings] = useState<QuantumSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      const response = await fetch(`${config.urls.integrationBridge}/api/quantum/settings?type=system`)
      const data = await response.json()
      if (data.success) {
        setSettings(data.settings)
      }
    } catch (error) {
      console.error('Error fetching settings:', error)
      setMessage({ type: 'error', text: 'Failed to load settings' })
    } finally {
      setLoading(false)
    }
  }

  const saveSettings = async (newSettings: Partial<QuantumSettings>) => {
    setSaving(true)
    setMessage(null)
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${config.urls.integrationBridge}/api/quantum/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          setting_type: 'system',
          ...newSettings
        })
      })

      const data = await response.json()
      
      if (data.success) {
        setSettings(data.settings)
        setMessage({ type: 'success', text: 'Settings saved successfully!' })
      } else {
        setMessage({ type: 'error', text: data.error || 'Failed to save settings' })
      }
    } catch (error) {
      console.error('Error saving settings:', error)
      setMessage({ type: 'error', text: 'Failed to save settings' })
    } finally {
      setSaving(false)
    }
  }

  const handleModeChange = (autoTrigger: boolean) => {
    saveSettings({ auto_trigger: autoTrigger })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-600">Loading settings...</div>
      </div>
    )
  }

  const currentMode = settings?.auto_trigger ? 'automatic' : 'manual'

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Quantum Analysis Settings</h2>
        <p className="text-gray-600">
          Configure when quantum analysis should run automatically after eCBome analysis completes.
        </p>
      </div>

      {message && (
        <div className={`p-4 rounded-lg ${
          message.type === 'success' 
            ? 'bg-green-50 text-green-800 border border-green-200' 
            : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}

      {/* Mode Selection */}
      <div className="dashboard-card">
        <div className="flex items-center space-x-3 mb-4">
          <CpuChipIcon className="h-6 w-6 text-ecbome-primary" />
          <h3 className="text-lg font-semibold text-gray-900">Trigger Mode</h3>
        </div>

        <div className="space-y-4">
          {/* Automatic Mode */}
          <div 
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
              currentMode === 'automatic'
                ? 'border-ecbome-primary bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => handleModeChange(true)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <input
                    type="radio"
                    name="mode"
                    checked={currentMode === 'automatic'}
                    onChange={() => handleModeChange(true)}
                    className="h-4 w-4 text-ecbome-primary"
                  />
                  <label className="text-lg font-semibold text-gray-900">
                    Automatic Mode
                  </label>
                </div>
                <p className="text-sm text-gray-600 mb-3">
                  Quantum analysis runs automatically after every eCBome analysis completes.
                </p>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-sm">
                    <span className="font-medium text-gray-700">Benefits:</span>
                    <span className="text-gray-600">Most accurate analysis for every patient</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm">
                    <CurrencyDollarIcon className="h-4 w-4 text-yellow-600" />
                    <span className="text-gray-600">
                      Estimated cost: $900 - $4,500/month (100 patients/day)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Manual Mode */}
          <div 
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
              currentMode === 'manual'
                ? 'border-ecbome-primary bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => handleModeChange(false)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <input
                    type="radio"
                    name="mode"
                    checked={currentMode === 'manual'}
                    onChange={() => handleModeChange(false)}
                    className="h-4 w-4 text-ecbome-primary"
                  />
                  <label className="text-lg font-semibold text-gray-900">
                    Manual Mode
                  </label>
                </div>
                <p className="text-sm text-gray-600 mb-3">
                  Quantum analysis only runs when explicitly requested by providers.
                </p>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-sm">
                    <span className="font-medium text-gray-700">Benefits:</span>
                    <span className="text-gray-600">Cost-effective, provider-controlled</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm">
                    <CurrencyDollarIcon className="h-4 w-4 text-green-600" />
                    <span className="text-gray-600">
                      Estimated cost: $180 - $900/month (100 patients/day, 20% request rate)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Current Status */}
      <div className="dashboard-card">
        <div className="flex items-center space-x-3 mb-4">
          <ClockIcon className="h-6 w-6 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Current Status</h3>
        </div>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-gray-600">Mode:</span>
            <span className="font-medium text-gray-900 capitalize">{currentMode}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Status:</span>
            <span className={`font-medium ${settings?.enabled ? 'text-green-600' : 'text-red-600'}`}>
              {settings?.enabled ? 'Enabled' : 'Disabled'}
            </span>
          </div>
        </div>
      </div>

      {/* Cost Information */}
      <div className="dashboard-card bg-yellow-50 border-yellow-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Cost Information</h3>
        <div className="space-y-2 text-sm text-gray-700">
          <p>
            <strong>Current (Simulator Mode):</strong> $0 - No cost while using quantum simulators
          </p>
          <p>
            <strong>Future (Real Hardware):</strong> Costs will apply when using IBM Quantum hardware.
            See <a href="/admin/config" className="text-ecbome-primary hover:underline">Cost Analysis</a> for details.
          </p>
        </div>
      </div>

      {saving && (
        <div className="text-center text-gray-600">Saving settings...</div>
      )}
    </div>
  )
}

