'use client'

import Link from 'next/link'
import { 
  BeakerIcon,
  ChartBarIcon,
  ChatBubbleLeftRightIcon,
  CpuChipIcon,
  CircleStackIcon,
  ServerIcon,
} from '@heroicons/react/24/outline'
import { config } from '@/config'

const ecbomeFeatures = [
  {
    name: 'Test Suite',
    description: 'Comprehensive testing and validation of eCBome analysis',
    icon: BeakerIcon,
    href: `${config.urls.ecbomeBase}/ecbome-test`,
    color: 'from-blue-500 to-blue-600'
  },
  {
    name: 'Analysis Dashboard',
    description: 'Real-time endocannabinoid system analysis and insights',
    icon: ChartBarIcon,
    href: `${config.urls.ecbomeBase}/ecbome-analysis`,
    color: 'from-green-500 to-green-600'
  },
  {
    name: 'AI Assistant',
    description: 'Intelligent chatbot for eCBome system queries',
    icon: ChatBubbleLeftRightIcon,
    href: `${config.urls.ecbomeBase}/chatbot`,
    color: 'from-purple-500 to-purple-600'
  }
]

const systemFeatures = [
  {
    name: 'Quantum Healthcare',
    description: 'Quantum computing powered healthcare analysis',
    icon: CpuChipIcon,
    href: '#quantum',
    color: 'from-indigo-500 to-indigo-600'
  },
  {
    name: 'Integration Bridge',
    description: 'API gateway and authentication service',
    icon: ServerIcon,
    href: config.urls.integrationBridge,
    color: 'from-orange-500 to-orange-600',
    external: true
  },
  {
    name: 'Unified Integration',
    description: 'Central hub for all system integrations',
    icon: CircleStackIcon,
    href: config.urls.unifiedIntegration,
    color: 'from-pink-500 to-pink-600',
    external: true
  }
]

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">IHR System Dashboard</h1>
              <p className="mt-1 text-sm text-gray-600">
                Integrated Healthcare Records - Admin Portal
              </p>
            </div>
            <Link
              href="/"
              className="text-sm font-semibold text-indigo-600 hover:text-indigo-500"
            >
              ← Back to Home
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* eCBome Intelligence System */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            eCBome Intelligence System
          </h2>
          <p className="text-gray-600 mb-6">
            Endocannabinoid system analysis and monitoring tools
          </p>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {ecbomeFeatures.map((feature) => {
              const IconComponent = feature.icon
              return (
                <a
                  key={feature.name}
                  href={feature.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow group"
                >
                  <div className="flex items-start space-x-4">
                    <div className={`p-3 bg-gradient-to-br ${feature.color} rounded-lg`}>
                      <IconComponent className="h-6 w-6 text-white" aria-hidden="true" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1 group-hover:text-indigo-600 transition-colors">
                        {feature.name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {feature.description}
                      </p>
                    </div>
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                      <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </div>
                  </div>
                </a>
              )
            })}
          </div>
        </div>

        {/* System Services */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            System Services
          </h2>
          <p className="text-gray-600 mb-6">
            Core infrastructure and integration services
          </p>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {systemFeatures.map((feature) => {
              const IconComponent = feature.icon
              const Component = feature.external ? 'a' : Link
              const linkProps = feature.external 
                ? { target: "_blank", rel: "noopener noreferrer" }
                : {}
              
              return (
                <Component
                  key={feature.name}
                  href={feature.href}
                  {...linkProps}
                  className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow group"
                >
                  <div className="flex items-start space-x-4">
                    <div className={`p-3 bg-gradient-to-br ${feature.color} rounded-lg`}>
                      <IconComponent className="h-6 w-6 text-white" aria-hidden="true" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1 group-hover:text-indigo-600 transition-colors">
                        {feature.name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {feature.description}
                      </p>
                    </div>
                    {feature.external && (
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                        <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </div>
                    )}
                  </div>
                </Component>
              )
            })}
          </div>
        </div>
      </main>
    </div>
  )
}
