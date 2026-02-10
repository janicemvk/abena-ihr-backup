'use client'

import Link from 'next/link'
import { 
  UserGroupIcon, 
  Cog6ToothIcon, 
  ChartBarIcon,
  CalendarIcon,
  BanknotesIcon,
  ChatBubbleLeftRightIcon,
  StarIcon,
  DocumentTextIcon,
  ShieldCheckIcon,
  ClockIcon,
  ClipboardDocumentCheckIcon,
  CpuChipIcon,
} from '@heroicons/react/24/outline'

const features = [
  {
    name: 'Manage User Accounts',
    description: 'Create, edit, and manage user accounts and permissions',
    icon: UserGroupIcon,
    href: '/admin/users',
    color: 'from-blue-500 to-blue-600'
  },
  {
    name: 'System Configuration',
    description: 'Configure system settings and preferences',
    icon: Cog6ToothIcon,
    href: '/admin/config',
    color: 'from-gray-500 to-gray-600'
  },
  {
    name: 'Data Analytics',
    description: 'View and analyze system performance metrics',
    icon: ChartBarIcon,
    href: '/admin/analytics',
    color: 'from-green-500 to-green-600'
  },
  {
    name: 'Appointment Management',
    description: 'Manage and sync calendar appointments',
    icon: CalendarIcon,
    href: '/admin/appointments',
    color: 'from-purple-500 to-purple-600'
  },
  {
    name: 'Clinical Notes',
    description: 'View and manage patient clinical notes',
    icon: DocumentTextIcon,
    href: '/admin/clinical-notes',
    color: 'from-indigo-500 to-indigo-600'
  },
  {
    name: 'Treatment Plans',
    description: 'Create and manage patient treatment plans',
    icon: DocumentTextIcon,
    href: '/admin/treatment-plans',
    color: 'from-pink-500 to-pink-600'
  },
  {
    name: 'Quantum Analysis',
    description: 'Monitor quantum healthcare analysis system and blockchain',
    icon: CpuChipIcon,
    href: '/admin/quantum-analysis',
    color: 'from-purple-500 to-indigo-600'
  },
  {
    name: 'Billing & Insurance',
    description: 'Process claims and manage financial transactions',
    icon: BanknotesIcon,
    href: '/admin/billing',
    color: 'from-yellow-500 to-yellow-600'
  },
  {
    name: 'Medical Coding Assistant',
    description: 'Lookup CPT and ICD-10 codes with intelligent suggestions',
    icon: ClipboardDocumentCheckIcon,
    href: '/admin/medical-coding',
    color: 'from-teal-500 to-teal-600'
  },
  {
    name: 'Communication Hub',
    description: 'Manage provider and patient communications',
    icon: ChatBubbleLeftRightIcon,
    href: '/admin/communications',
    color: 'from-cyan-500 to-cyan-600'
  },
  {
    name: 'Patient Feedback',
    description: 'Track and analyze patient satisfaction',
    icon: StarIcon,
    href: '/admin/feedback',
    color: 'from-orange-500 to-orange-600'
  }
]

export default function AdminDashboard() {
  return (
    <div className="min-h-screen bg-clinical-bg">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <ShieldCheckIcon className="h-8 w-8 text-ecbome-primary" />
            <h1 className="text-3xl font-bold tracking-tight text-gray-900">Administrator Dashboard</h1>
          </div>
          <p className="text-gray-600">Manage all aspects of the Abena IHR system</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <div className="dashboard-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Users</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">0</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <UserGroupIcon className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>
          <div className="dashboard-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Appointments</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">0</p>
              </div>
              <div className="p-3 bg-purple-100 rounded-lg">
                <CalendarIcon className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>
          <div className="dashboard-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">System Uptime</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">100%</p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <ClockIcon className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>
          <div className="dashboard-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Alerts</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">0</p>
              </div>
              <div className="p-3 bg-yellow-100 rounded-lg">
                <StarIcon className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Feature Cards */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Access</h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => {
              const IconComponent = feature.icon
              return (
              <Link
                key={feature.name}
                href={feature.href}
                className="dashboard-card group"
              >
                <div className="flex items-start space-x-4">
                  <div className={`p-3 bg-gradient-to-br ${feature.color} rounded-lg`}>
                    {IconComponent && <IconComponent className="h-6 w-6 text-white" aria-hidden="true" />}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1 group-hover:text-ecbome-primary transition-colors">
                      {feature.name}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {feature.description}
                    </p>
                  </div>
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </Link>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
