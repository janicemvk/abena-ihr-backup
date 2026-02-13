'use client'

import Link from 'next/link'
import {
  Brain,
  Activity,
  Shield,
  Users,
  Sparkles,
  ArrowRight,
  CheckCircle,
  Cpu,
  Zap
} from 'lucide-react'

export default function MVPCoverPage() {
  const features = [
    {
      icon: Cpu,
      title: 'Quantum Computing',
      description: 'Real IBM quantum hardware for treatment optimization',
      color: 'from-blue-500 to-purple-600'
    },
    {
      icon: Activity,
      title: 'eCBome Analysis',
      description: 'Endocannabinoid system insights and personalized recommendations',
      color: 'from-green-500 to-emerald-600'
    },
    {
      icon: Brain,
      title: 'AI-Powered Insights',
      description: 'Advanced pattern recognition and predictive analytics',
      color: 'from-purple-500 to-pink-600'
    },
    {
      icon: Shield,
      title: 'Blockchain Security',
      description: 'HIPAA-compliant with blockchain transaction logging',
      color: 'from-indigo-500 to-blue-600'
    }
  ]

  const portals = [
    {
      name: 'Admin Dashboard',
      description: 'System management and quantum analysis oversight',
      href: '/admin',
      icon: Shield,
      color: 'bg-blue-600 hover:bg-blue-700',
      badge: 'System Control'
    },
    {
      name: 'Provider Portal',
      description: 'Clinical dashboard with telemedicine and quantum insights',
      href: 'https://provider-portal-va15.onrender.com',
      icon: Users,
      color: 'bg-green-600 hover:bg-green-700',
      badge: 'Clinical Tools',
      external: true
    },
    {
      name: 'Patient Portal',
      description: 'eCBome monitoring with gamified health data collection',
      href: 'https://patient-portal-9pt9.onrender.com',
      icon: Activity,
      color: 'bg-purple-600 hover:bg-purple-700',
      badge: 'Patient Engagement',
      external: true
    },
    {
      name: 'Quantum Analysis',
      description: 'Live quantum computing results from IBM hardware',
      href: 'https://abena-quantum-healthcare-platform.onrender.com',
      icon: Cpu,
      color: 'bg-indigo-600 hover:bg-indigo-700',
      badge: 'Quantum Computing',
      external: true
    }
  ]

  const stats = [
    { label: 'Integrated Services', value: '7', suffix: '+' },
    { label: 'Quantum Algorithms', value: '3', suffix: '' },
    { label: 'Patient Engagement', value: '300', suffix: '%' },
    { label: 'HIPAA Compliant', value: '100', suffix: '%' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  ABENA IHR
                </h1>
                <p className="text-xs text-gray-600">Intelligent Healthcare Reimagined</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 bg-green-100 text-green-700 text-sm font-semibold rounded-full flex items-center gap-1">
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                MVP Live
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-20">
        {/* Animated Background Elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
          <div className="absolute top-40 right-10 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
          <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-green-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="animate-fadeIn">
            <h2 className="text-5xl md:text-6xl font-bold mb-6">
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-green-600 bg-clip-text text-transparent">
                The Future of Healthcare
              </span>
              <br />
              <span className="text-gray-900">Is Here</span>
            </h2>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Integrating quantum computing, AI-powered insights, and gamified patient engagement
              to deliver personalized, proactive healthcare at scale.
            </p>
            <div className="flex items-center justify-center gap-2 mb-12">
              <Sparkles className="h-5 w-5 text-yellow-500" />
              <span className="text-sm font-semibold text-gray-700">
                Running on real IBM quantum hardware • 128x speedup
              </span>
              <Sparkles className="h-5 w-5 text-yellow-500" />
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16 animate-fadeIn">
            {stats.map((stat, index) => (
              <div key={index} className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
                <div className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
                  {stat.value}{stat.suffix}
                </div>
                <div className="text-sm text-gray-600 font-medium">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h3 className="text-3xl font-bold text-center mb-12 text-gray-900 animate-fadeIn">
            Revolutionary Technology Stack
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200 hover:shadow-xl transition-all hover:-translate-y-1 animate-fadeIn"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className={`h-12 w-12 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center mb-4`}>
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h4 className="text-lg font-bold text-gray-900 mb-2">{feature.title}</h4>
                <p className="text-sm text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Portals Section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 animate-fadeIn">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Access Your Portal
            </h3>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Choose your role to access the integrated healthcare platform with quantum-powered insights.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {portals.map((portal, index) => (
              <div
                key={index}
                className="animate-fadeIn"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                {portal.external ? (
                  <a
                    href={portal.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block bg-white rounded-2xl p-8 shadow-lg border border-gray-200 hover:shadow-2xl transition-all transform hover:-translate-y-1"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className={`h-14 w-14 ${portal.color} rounded-xl flex items-center justify-center`}>
                        <portal.icon className="h-7 w-7 text-white" />
                      </div>
                      <span className="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-semibold rounded-full">
                        {portal.badge}
                      </span>
                    </div>
                    <h4 className="text-2xl font-bold text-gray-900 mb-2">{portal.name}</h4>
                    <p className="text-gray-600 mb-4">{portal.description}</p>
                    <div className="flex items-center text-blue-600 font-semibold">
                      <span>Access Portal</span>
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </div>
                  </a>
                ) : (
                  <Link
                    href={portal.href}
                    className="block bg-white rounded-2xl p-8 shadow-lg border border-gray-200 hover:shadow-2xl transition-all transform hover:-translate-y-1"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className={`h-14 w-14 ${portal.color} rounded-xl flex items-center justify-center`}>
                        <portal.icon className="h-7 w-7 text-white" />
                      </div>
                      <span className="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-semibold rounded-full">
                        {portal.badge}
                      </span>
                    </div>
                    <h4 className="text-2xl font-bold text-gray-900 mb-2">{portal.name}</h4>
                    <p className="text-gray-600 mb-4">{portal.description}</p>
                    <div className="flex items-center text-blue-600 font-semibold">
                      <span>Access Portal</span>
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </div>
                  </Link>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white/50 backdrop-blur-sm py-8 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center gap-2 mb-4 md:mb-0">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span className="text-sm text-gray-600">
                HIPAA Compliant • Blockchain Secured • Quantum Enhanced
              </span>
            </div>
            <div className="text-sm text-gray-500">
              © 2026 ABENA IHR. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

