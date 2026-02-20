'use client'

import { useState } from 'react'
import Link from 'next/link'
import { 
  ArrowLeftIcon,
  BanknotesIcon,
  DocumentCheckIcon,
  CreditCardIcon,
  DocumentChartBarIcon,
  DocumentDuplicateIcon,
  DocumentArrowDownIcon,
  ClipboardDocumentCheckIcon,
} from '@heroicons/react/24/outline'
import { format } from 'date-fns'

// Mock data for demonstration
const claims = [
  { 
    id: 'CLM001',
    patient: 'Alice Johnson',
    provider: 'Dr. John Smith',
    service: 'Annual Check-up',
    codes: {
      cpt: '99214',
      icd10: 'Z00.00',
      modifiers: ['25'],
    },
    amount: 250.00,
    status: 'Pending',
    submitted: '2024-02-15',
  },
  { 
    id: 'CLM002',
    patient: 'Bob Wilson',
    provider: 'Dr. Sarah Lee',
    service: 'Consultation',
    codes: {
      cpt: '99213',
      icd10: 'R07.9',
      modifiers: [],
    },
    amount: 175.00,
    status: 'Approved',
    submitted: '2024-02-14',
  },
  { 
    id: 'CLM003',
    patient: 'Carol Brown',
    provider: 'Dr. John Smith',
    service: 'Lab Tests',
    codes: {
      cpt: '80053',
      icd10: 'R73.03',
      modifiers: [],
    },
    amount: 450.00,
    status: 'Paid',
    submitted: '2024-02-13',
  },
]

const providers = [
  'Dr. John Smith',
  'Dr. Sarah Lee',
  'Dr. Michael Brown',
  'Dr. Emily Chen',
  'Dr. David Wilson'
]

const services = [
  'Annual Check-up',
  'Consultation',
  'Lab Tests',
  'Physical Therapy',
  'X-Ray',
  'MRI',
  'Vaccination',
  'Follow-up Visit'
]

const stats = [
  { name: 'Total Claims', value: '$12,450.00', icon: DocumentChartBarIcon },
  { name: 'Pending Claims', value: '5', icon: DocumentCheckIcon },
  { name: 'Approved Claims', value: '12', icon: BanknotesIcon },
  { name: 'This Month', value: '$4,250.00', icon: CreditCardIcon },
]

export default function BillingPage() {
  const [showCodingModal, setShowCodingModal] = useState(false)
  const [showNewClaimModal, setShowNewClaimModal] = useState(false)
  const [selectedClaim, setSelectedClaim] = useState<any>(null)
  const [newClaim, setNewClaim] = useState({
    patient: '',
    provider: '',
    service: '',
    amount: '',
    codes: {
      cpt: '',
      icd10: '',
      modifiers: []
    }
  })

  const handleAddClaim = () => {
    const claim = {
      id: `CLM${String(claims.length + 1).padStart(3, '0')}`,
      ...newClaim,
      amount: parseFloat(newClaim.amount),
      status: 'Pending',
      submitted: format(new Date(), 'yyyy-MM-dd')
    }
    claims.push(claim)
    setShowNewClaimModal(false)
    setNewClaim({
      patient: '',
      provider: '',
      service: '',
      amount: '',
      codes: {
        cpt: '',
        icd10: '',
        modifiers: []
      }
    })
  }

  const handleGenerateSuperbill = (claim: any) => {
    // In a real app, this would generate a PDF superbill
    alert(`Generating superbill for ${claim.patient}...`)
  }

  const handleViewCoding = (claim: any) => {
    setSelectedClaim(claim)
    setShowCodingModal(true)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Link
                href="/admin"
                className="mr-4 rounded-full p-2 hover:bg-gray-100"
              >
                <ArrowLeftIcon className="h-6 w-6 text-gray-600" />
              </Link>
              <h1 className="text-3xl font-bold tracking-tight text-gray-900">Billing & Insurance</h1>
            </div>
            <button
              onClick={() => setShowNewClaimModal(true)}
              className="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
            >
              New Claim
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
        {/* Stats */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          {stats.map((stat) => {
            const IconComponent = stat.icon
            return (
            <div
              key={stat.name}
              className="bg-white overflow-hidden shadow rounded-lg"
            >
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    {IconComponent && <IconComponent className="h-6 w-6 text-gray-400" aria-hidden="true" />}
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">{stat.name}</dt>
                      <dd className="text-lg font-medium text-gray-900">{stat.value}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
            )
          })}
        </div>

        {/* Claims Table */}
        <div className="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-lg">
          <table className="min-w-full divide-y divide-gray-300">
            <thead>
              <tr>
                <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                  Claim ID
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Patient
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Provider
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Service
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Amount
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Status
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Submitted
                </th>
                <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {claims.map((claim) => (
                <tr key={claim.id}>
                  <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                    {claim.id}
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{claim.patient}</td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{claim.provider}</td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{claim.service}</td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    ${claim.amount.toFixed(2)}
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                      claim.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                      claim.status === 'Approved' ? 'bg-green-100 text-green-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {claim.status}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{claim.submitted}</td>
                  <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => handleViewCoding(claim)}
                        className="text-indigo-600 hover:text-indigo-900"
                        title="View Coding"
                      >
                        <ClipboardDocumentCheckIcon className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => handleGenerateSuperbill(claim)}
                        className="text-indigo-600 hover:text-indigo-900"
                        title="Generate Superbill"
                      >
                        <DocumentArrowDownIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>

      {/* Medical Coding Modal */}
      {showCodingModal && selectedClaim && (
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <div className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                <button
                  type="button"
                  className="rounded-md bg-white text-gray-400 hover:text-gray-500"
                  onClick={() => setShowCodingModal(false)}
                >
                  <span className="sr-only">Close</span>
                  <ArrowLeftIcon className="h-6 w-6" />
                </button>
              </div>
              <div>
                <div className="mt-3 text-center sm:mt-0 sm:text-left">
                  <h3 className="text-lg font-semibold leading-6 text-gray-900">
                    Medical Coding Details
                  </h3>
                  <div className="mt-4 space-y-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">CPT Code</h4>
                      <p className="mt-1 text-sm text-gray-500">{selectedClaim.codes.cpt}</p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">ICD-10 Code</h4>
                      <p className="mt-1 text-sm text-gray-500">{selectedClaim.codes.icd10}</p>
                    </div>
                    {selectedClaim.codes.modifiers.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">Modifiers</h4>
                        <p className="mt-1 text-sm text-gray-500">
                          {selectedClaim.codes.modifiers.join(', ')}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                  onClick={() => setShowCodingModal(false)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* New Claim Modal */}
      {showNewClaimModal && (
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <div className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                <button
                  type="button"
                  className="rounded-md bg-white text-gray-400 hover:text-gray-500"
                  onClick={() => setShowNewClaimModal(false)}
                >
                  <span className="sr-only">Close</span>
                  <ArrowLeftIcon className="h-6 w-6" />
                </button>
              </div>
              <div>
                <div className="mt-3 text-center sm:mt-0 sm:text-left">
                  <h3 className="text-lg font-semibold leading-6 text-gray-900">
                    Create New Claim
                  </h3>
                  <div className="mt-4 space-y-4">
                    <div>
                      <label htmlFor="patient" className="block text-sm font-medium text-gray-700">
                        Patient Name
                      </label>
                      <input
                        type="text"
                        id="patient"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newClaim.patient}
                        onChange={(e) => setNewClaim({ ...newClaim, patient: e.target.value })}
                      />
                    </div>
                    <div>
                      <label htmlFor="provider" className="block text-sm font-medium text-gray-700">
                        Provider
                      </label>
                      <select
                        id="provider"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newClaim.provider}
                        onChange={(e) => setNewClaim({ ...newClaim, provider: e.target.value })}
                      >
                        <option value="">Select a provider</option>
                        {providers.map((provider) => (
                          <option key={provider} value={provider}>
                            {provider}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label htmlFor="service" className="block text-sm font-medium text-gray-700">
                        Service
                      </label>
                      <select
                        id="service"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newClaim.service}
                        onChange={(e) => setNewClaim({ ...newClaim, service: e.target.value })}
                      >
                        <option value="">Select a service</option>
                        {services.map((service) => (
                          <option key={service} value={service}>
                            {service}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label htmlFor="amount" className="block text-sm font-medium text-gray-700">
                        Amount
                      </label>
                      <div className="relative mt-1 rounded-md shadow-sm">
                        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                          <span className="text-gray-500 sm:text-sm">$</span>
                        </div>
                        <input
                          type="number"
                          id="amount"
                          className="block w-full rounded-md border-gray-300 pl-7 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          value={newClaim.amount}
                          onChange={(e) => setNewClaim({ ...newClaim, amount: e.target.value })}
                          placeholder="0.00"
                          step="0.01"
                        />
                      </div>
                    </div>
                    <div>
                      <label htmlFor="cpt" className="block text-sm font-medium text-gray-700">
                        CPT Code
                      </label>
                      <input
                        type="text"
                        id="cpt"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newClaim.codes.cpt}
                        onChange={(e) => setNewClaim({ 
                          ...newClaim, 
                          codes: { ...newClaim.codes, cpt: e.target.value }
                        })}
                      />
                    </div>
                    <div>
                      <label htmlFor="icd10" className="block text-sm font-medium text-gray-700">
                        ICD-10 Code
                      </label>
                      <input
                        type="text"
                        id="icd10"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newClaim.codes.icd10}
                        onChange={(e) => setNewClaim({ 
                          ...newClaim, 
                          codes: { ...newClaim.codes, icd10: e.target.value }
                        })}
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 sm:ml-3 sm:w-auto"
                  onClick={handleAddClaim}
                >
                  Create Claim
                </button>
                <button
                  type="button"
                  className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                  onClick={() => setShowNewClaimModal(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 