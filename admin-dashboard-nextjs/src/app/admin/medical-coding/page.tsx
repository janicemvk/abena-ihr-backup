'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Dialog } from '@headlessui/react'
import { 
  ArrowLeftIcon,
  ClipboardDocumentCheckIcon,
  MagnifyingGlassIcon,
  LightBulbIcon,
  BookOpenIcon,
  CheckCircleIcon,
  XMarkIcon,
  InformationCircleIcon,
} from '@heroicons/react/24/outline'

// Medical coding database (in production, this would come from an API)
const cptCodes = [
  { code: '99213', description: 'Office or other outpatient visit, established patient', category: 'Evaluation & Management' },
  { code: '99214', description: 'Office or other outpatient visit, established patient (detailed)', category: 'Evaluation & Management' },
  { code: '99215', description: 'Office or other outpatient visit, established patient (comprehensive)', category: 'Evaluation & Management' },
  { code: '99203', description: 'Office or other outpatient visit, new patient', category: 'Evaluation & Management' },
  { code: '99204', description: 'Office or other outpatient visit, new patient (detailed)', category: 'Evaluation & Management' },
  { code: '80053', description: 'Comprehensive metabolic panel', category: 'Laboratory' },
  { code: '85025', description: 'Complete blood count (CBC)', category: 'Laboratory' },
  { code: '93000', description: 'Electrocardiogram, routine ECG', category: 'Cardiology' },
  { code: '71020', description: 'Chest X-ray, 2 views', category: 'Radiology' },
  { code: '97110', description: 'Therapeutic exercise', category: 'Physical Therapy' },
  { code: '97112', description: 'Neuromuscular reeducation', category: 'Physical Therapy' },
  { code: '90834', description: 'Psychotherapy, 45 minutes', category: 'Mental Health' },
]

const icd10Codes = [
  { code: 'Z00.00', description: 'Encounter for general adult medical examination without abnormal findings', category: 'Preventive' },
  { code: 'Z00.01', description: 'Encounter for general adult medical examination with abnormal findings', category: 'Preventive' },
  { code: 'R07.9', description: 'Chest pain, unspecified', category: 'Symptoms' },
  { code: 'R73.03', description: 'Prediabetes', category: 'Metabolic' },
  { code: 'E11.9', description: 'Type 2 diabetes mellitus without complications', category: 'Metabolic' },
  { code: 'I10', description: 'Essential (primary) hypertension', category: 'Cardiovascular' },
  { code: 'M54.5', description: 'Low back pain', category: 'Musculoskeletal' },
  { code: 'J06.9', description: 'Acute upper respiratory infection, unspecified', category: 'Respiratory' },
  { code: 'F41.1', description: 'Generalized anxiety disorder', category: 'Mental Health' },
  { code: 'G89.29', description: 'Other chronic pain', category: 'Pain' },
]

const codeModifiers = [
  { code: '25', description: 'Significant, separately identifiable evaluation and management service' },
  { code: '59', description: 'Distinct procedural service' },
  { code: 'LT', description: 'Left side' },
  { code: 'RT', description: 'Right side' },
  { code: 'TC', description: 'Technical component' },
  { code: '26', description: 'Professional component' },
]

interface CodeSuggestion {
  code: string
  description: string
  category: string
  matchScore: number
}

export default function MedicalCodingPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [codeType, setCodeType] = useState<'cpt' | 'icd10'>('cpt')
  const [showCodeDetails, setShowCodeDetails] = useState(false)
  const [selectedCode, setSelectedCode] = useState<any>(null)
  const [suggestions, setSuggestions] = useState<CodeSuggestion[]>([])

  const categories = ['all', 'Evaluation & Management', 'Laboratory', 'Radiology', 'Cardiology', 'Physical Therapy', 'Mental Health', 'Preventive', 'Symptoms', 'Metabolic', 'Cardiovascular', 'Musculoskeletal', 'Respiratory', 'Pain']

  const searchCodes = (term: string) => {
    if (!term.trim()) {
      setSuggestions([])
      return
    }

    const searchLower = term.toLowerCase()
    const codeList = codeType === 'cpt' ? cptCodes : icd10Codes
    
    const results = codeList
      .filter(code => {
        const matchesCategory = selectedCategory === 'all' || code.category === selectedCategory
        const matchesSearch = 
          code.code.toLowerCase().includes(searchLower) ||
          code.description.toLowerCase().includes(searchLower) ||
          code.category.toLowerCase().includes(searchLower)
        return matchesCategory && matchesSearch
      })
      .map(code => {
        // Calculate match score
        let score = 0
        if (code.code.toLowerCase().includes(searchLower)) score += 10
        if (code.description.toLowerCase().includes(searchLower)) score += 5
        if (code.category.toLowerCase().includes(searchLower)) score += 2
        return { ...code, matchScore: score }
      })
      .sort((a, b) => b.matchScore - a.matchScore)
      .slice(0, 10)

    setSuggestions(results)
  }

  const handleSearchChange = (value: string) => {
    setSearchTerm(value)
    searchCodes(value)
  }

  const handleCodeSelect = (code: any) => {
    setSelectedCode(code)
    setShowCodeDetails(true)
  }

  const displayCodes = codeType === 'cpt' ? cptCodes : icd10Codes
  const filteredCodes = displayCodes.filter(code => 
    selectedCategory === 'all' || code.category === selectedCategory
  )

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
              <div className="flex items-center space-x-3">
                <ClipboardDocumentCheckIcon className="h-8 w-8 text-indigo-600" />
                <h1 className="text-3xl font-bold tracking-tight text-gray-900">Medical Coding Assistant</h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
        {/* Search Section */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <div className="flex items-center space-x-4 mb-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search {codeType.toUpperCase()} Codes
              </label>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder={`Search by code, description, or category...`}
                  value={searchTerm}
                  onChange={(e) => handleSearchChange(e.target.value)}
                  className="w-full rounded-md border-gray-300 pl-10 pr-4 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  setCodeType('cpt')
                  setSearchTerm('')
                  setSuggestions([])
                }}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  codeType === 'cpt'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                CPT Codes
              </button>
              <button
                onClick={() => {
                  setCodeType('icd10')
                  setSearchTerm('')
                  setSuggestions([])
                }}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  codeType === 'icd10'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                ICD-10 Codes
              </button>
            </div>
          </div>

          {/* Category Filter */}
          <div className="flex items-center space-x-2 flex-wrap gap-2">
            <span className="text-sm font-medium text-gray-700">Category:</span>
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => {
                  setSelectedCategory(cat)
                  searchCodes(searchTerm)
                }}
                className={`px-3 py-1 rounded-full text-xs font-medium ${
                  selectedCategory === cat
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Search Suggestions */}
          {suggestions.length > 0 && (
            <div className="mt-4 border-t pt-4">
              <div className="flex items-center space-x-2 mb-2">
                <LightBulbIcon className="h-5 w-5 text-yellow-500" />
                <h3 className="text-sm font-medium text-gray-900">Suggestions</h3>
              </div>
              <div className="space-y-2">
                {suggestions.map((suggestion) => (
                  <button
                    key={suggestion.code}
                    onClick={() => handleCodeSelect(suggestion)}
                    className="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="font-mono font-semibold text-indigo-600">{suggestion.code}</span>
                        <p className="text-sm text-gray-600 mt-1">{suggestion.description}</p>
                        <span className="text-xs text-gray-500">{suggestion.category}</span>
                      </div>
                      <CheckCircleIcon className="h-5 w-5 text-green-500" />
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Code Reference Table */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">
                {codeType.toUpperCase()} Code Reference
              </h2>
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <BookOpenIcon className="h-5 w-5" />
                <span>{filteredCodes.length} codes</span>
              </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Code
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredCodes.map((code) => (
                  <tr key={code.code} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="font-mono font-semibold text-indigo-600">{code.code}</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{code.description}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                        {code.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleCodeSelect(code)}
                        className="text-indigo-600 hover:text-indigo-900"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Modifiers Reference */}
        {codeType === 'cpt' && (
          <div className="mt-6 bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Common CPT Modifiers</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {codeModifiers.map((modifier) => (
                <div key={modifier.code} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-semibold text-indigo-600">{modifier.code}</span>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">{modifier.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Code Details Modal */}
      <Dialog open={showCodeDetails} onClose={() => setShowCodeDetails(false)}>
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" />
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div className="absolute right-0 top-0 pr-4 pt-4">
                <button onClick={() => setShowCodeDetails(false)}>
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              {selectedCode && (
                <>
                  <div className="flex items-center space-x-3 mb-4">
                    <ClipboardDocumentCheckIcon className="h-8 w-8 text-indigo-600" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {selectedCode.code}
                      </h3>
                      <span className="text-sm text-gray-500">{selectedCode.category}</span>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Description</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedCode.description}</p>
                    </div>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <div className="flex items-start">
                        <InformationCircleIcon className="h-5 w-5 text-blue-600 mt-0.5 mr-2" />
                        <div className="text-sm text-blue-800">
                          <p className="font-medium mb-1">Usage Tip:</p>
                          <p>This code is commonly used for {selectedCode.category.toLowerCase()} procedures. Make sure to verify the code is appropriate for the specific service provided.</p>
                        </div>
                      </div>
                    </div>
                    <div className="flex space-x-3 pt-4 border-t">
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(selectedCode.code)
                          alert('Code copied to clipboard!')
                        }}
                        className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700"
                      >
                        Copy Code
                      </button>
                      <button
                        onClick={() => setShowCodeDetails(false)}
                        className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-300"
                      >
                        Close
                      </button>
                    </div>
                  </div>
                </>
              )}
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>
    </div>
  )
}

