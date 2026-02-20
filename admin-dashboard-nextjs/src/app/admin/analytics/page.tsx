'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  ArrowLeftIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  UsersIcon,
  ClockIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  CalendarIcon,
  CreditCardIcon,
  UserPlusIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline'
import { formatDistanceToNow } from 'date-fns'
import { Dialog } from '@headlessui/react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import RelationshipIntelligence from './relationship-intelligence'

const stats = [
  {
    name: 'Total Patients',
    value: '2,451',
    change: '+12.5%',
    changeType: 'increase',
    icon: UsersIcon,
  },
  {
    name: 'Average Wait Time',
    value: '14.3 min',
    change: '-8.1%',
    changeType: 'decrease',
    icon: ClockIcon,
  },
  {
    name: 'Revenue',
    value: '$542,897',
    change: '+18.2%',
    changeType: 'increase',
    icon: CurrencyDollarIcon,
  },
  {
    name: 'Patient Satisfaction',
    value: '94.8%',
    change: '+4.3%',
    changeType: 'increase',
    icon: ChartBarIcon,
  },
]

interface ActivityType {
  name: string
  icon: any // Using any for icon type as it's a React component
  color: string
}

interface ActivityTypes {
  [key: string]: ActivityType
}

interface Activity {
  id: number
  type: string
  description: string
  timestamp: Date
}

const activityTypes: ActivityTypes = {
  APPOINTMENT: {
    name: 'Appointment',
    icon: CalendarIcon,
    color: 'bg-blue-100 text-blue-800'
  },
  BILLING: {
    name: 'Billing',
    icon: CreditCardIcon,
    color: 'bg-green-100 text-green-800'
  },
  PATIENT: {
    name: 'Patient',
    icon: UserPlusIcon,
    color: 'bg-purple-100 text-purple-800'
  },
  RECORD: {
    name: 'Medical Record',
    icon: DocumentTextIcon,
    color: 'bg-yellow-100 text-yellow-800'
  }
}

// Function to generate mock recent activities
function generateRecentActivities() {
  const activities = [
    {
      id: Date.now(),
      type: 'APPOINTMENT',
      description: 'Dr. Sarah Johnson: New appointment with Alice Brown',
      timestamp: new Date(),
    },
    {
      id: Date.now() - 1,
      type: 'BILLING',
      description: 'Insurance claim #CLM123 processed for $450.00',
      timestamp: new Date(Date.now() - 30 * 60000), // 30 minutes ago
    },
    {
      id: Date.now() - 2,
      type: 'PATIENT',
      description: 'New patient registration: Michael Chen',
      timestamp: new Date(Date.now() - 2 * 3600000), // 2 hours ago
    },
    {
      id: Date.now() - 3,
      type: 'RECORD',
      description: 'Medical records updated for patient ID #12345',
      timestamp: new Date(Date.now() - 4 * 3600000), // 4 hours ago
    },
    {
      id: Date.now() - 4,
      type: 'APPOINTMENT',
      description: 'Dr. David Kim: Appointment rescheduled with John Doe',
      timestamp: new Date(Date.now() - 5 * 3600000), // 5 hours ago
    }
  ]
  return activities
}

export default function AnalyticsPage() {
  const [recentActivity, setRecentActivity] = useState<Activity[]>([])
  const [timeFilter, setTimeFilter] = useState('7days')
  const [showAllActivities, setShowAllActivities] = useState(false)
  const [allActivities, setAllActivities] = useState<Activity[]>([])

  useEffect(() => {
    // Initial load
    const activities = generateRecentActivities()
    setRecentActivity(activities)
    setAllActivities(generateMoreActivities()) // Generate more activities for the full list

    // Update activities every minute
    const interval = setInterval(() => {
      const newActivities = generateRecentActivities()
      setRecentActivity(newActivities)
      setAllActivities(generateMoreActivities())
    }, 60000)

    return () => clearInterval(interval)
  }, [])

  // Function to generate more activities for the full list
  function generateMoreActivities(): Activity[] {
    const baseActivities = generateRecentActivities()
    const moreActivities: Activity[] = [
      ...baseActivities,
      {
        id: Date.now() - 5,
        type: 'BILLING',
        description: 'Insurance claim #CLM124 submitted for $275.00',
        timestamp: new Date(Date.now() - 6 * 3600000), // 6 hours ago
      },
      {
        id: Date.now() - 6,
        type: 'RECORD',
        description: 'Lab results uploaded for patient ID #12346',
        timestamp: new Date(Date.now() - 7 * 3600000), // 7 hours ago
      },
      {
        id: Date.now() - 7,
        type: 'APPOINTMENT',
        description: 'Dr. Emily Chen: Follow-up scheduled with Sarah Wilson',
        timestamp: new Date(Date.now() - 8 * 3600000), // 8 hours ago
      },
      {
        id: Date.now() - 8,
        type: 'PATIENT',
        description: 'Patient contact information updated: James Brown',
        timestamp: new Date(Date.now() - 9 * 3600000), // 9 hours ago
      },
      {
        id: Date.now() - 9,
        type: 'BILLING',
        description: 'Payment received: $150.00 from patient ID #12347',
        timestamp: new Date(Date.now() - 10 * 3600000), // 10 hours ago
      }
    ]
    return moreActivities
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
              <h1 className="text-3xl font-bold tracking-tight text-gray-900">Analytics Dashboard</h1>
            </div>
            <div className="flex space-x-4">
              <select 
                className="rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600"
                value={timeFilter}
                onChange={(e) => setTimeFilter(e.target.value)}
              >
                <option value="7days">Last 7 days</option>
                <option value="30days">Last 30 days</option>
                <option value="90days">Last 90 days</option>
                <option value="12months">Last 12 months</option>
              </select>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
        {/* Relationship Intelligence Section */}
        <div className="mb-8">
          <RelationshipIntelligence />
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((item) => {
            const IconComponent = item.icon
            return (
            <div
              key={item.name}
              className="relative overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:px-6 sm:pt-6"
            >
              <dt>
                <div className="absolute rounded-md bg-indigo-500 p-3">
                  {IconComponent && <IconComponent className="h-6 w-6 text-white" aria-hidden="true" />}
                </div>
                <p className="ml-16 truncate text-sm font-medium text-gray-500">{item.name}</p>
              </dt>
              <dd className="ml-16 flex items-baseline">
                <p className="text-2xl font-semibold text-gray-900">{item.value}</p>
                <p
                  className={`ml-2 flex items-baseline text-sm font-semibold ${
                    item.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {item.changeType === 'increase' ? (
                    <ArrowUpIcon className="h-5 w-5 flex-shrink-0 self-center text-green-500" aria-hidden="true" />
                  ) : (
                    <ArrowDownIcon className="h-5 w-5 flex-shrink-0 self-center text-red-500" aria-hidden="true" />
                  )}
                  <span className="sr-only">
                    {item.changeType === 'increase' ? 'Increased' : 'Decreased'} by
                  </span>
                  {item.change}
                </p>
              </dd>
            </div>
            )
          })}
        </div>

        {/* Activity Feed */}
        <div className="mt-8">
          <div className="rounded-lg bg-white shadow">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-semibold leading-6 text-gray-900">Recent Activity</h2>
                <span className="text-sm text-gray-500">Real-time updates</span>
              </div>
              <div className="mt-6 flow-root">
                <ul role="list" className="-my-5 divide-y divide-gray-200">
                  {recentActivity.map((activity) => {
                    const activityType = activityTypes[activity.type]
                    const Icon = activityType.icon
                    
                    return (
                      <li key={activity.id} className="py-5">
                        <div className="relative focus-within:ring-2 focus-within:ring-indigo-500">
                          <div className="flex items-center space-x-4">
                            <div className={`flex-shrink-0 rounded-md p-2 ${activityType.color}`}>
                              <Icon className="h-5 w-5" />
                            </div>
                            <div className="min-w-0 flex-1">
                              <h3 className="text-sm font-semibold text-gray-800">
                                {activityType.name}
                              </h3>
                              <p className="mt-1 text-sm text-gray-600 line-clamp-2">
                                {activity.description}
                              </p>
                              <p className="mt-1 text-sm text-gray-500">
                                {formatDistanceToNow(activity.timestamp, { addSuffix: true })}
                              </p>
                            </div>
                          </div>
                        </div>
                      </li>
                    )
                  })}
                </ul>
              </div>
              <div className="mt-6">
                <button
                  onClick={() => setShowAllActivities(true)}
                  className="flex w-full items-center justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                >
                  View all
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* View All Activities Modal */}
      <Dialog
        as="div"
        className="relative z-50"
        open={showAllActivities}
        onClose={() => setShowAllActivities(false)}
      >
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-4xl sm:p-6">
              <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                <button
                  type="button"
                  className="rounded-md bg-white text-gray-400 hover:text-gray-500"
                  onClick={() => setShowAllActivities(false)}
                >
                  <span className="sr-only">Close</span>
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              <div>
                <div className="mt-3 text-center sm:mt-0 sm:text-left">
                  <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                    All Activities
                  </Dialog.Title>
                  <div className="mt-4">
                    <div className="flow-root">
                      <ul role="list" className="-my-5 divide-y divide-gray-200">
                        {allActivities.map((activity) => {
                          const activityType = activityTypes[activity.type]
                          const Icon = activityType.icon
                          
                          return (
                            <li key={activity.id} className="py-5">
                              <div className="relative">
                                <div className="flex items-center space-x-4">
                                  <div className={`flex-shrink-0 rounded-md p-2 ${activityType.color}`}>
                                    <Icon className="h-5 w-5" />
                                  </div>
                                  <div className="min-w-0 flex-1">
                                    <div className="flex items-center justify-between">
                                      <h3 className="text-sm font-semibold text-gray-800">
                                        {activityType.name}
                                      </h3>
                                      <p className="text-sm text-gray-500">
                                        {formatDistanceToNow(activity.timestamp, { addSuffix: true })}
                                      </p>
                                    </div>
                                    <p className="mt-1 text-sm text-gray-600">
                                      {activity.description}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            </li>
                          )
                        })}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
              <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                  onClick={() => setShowAllActivities(false)}
                >
                  Close
                </button>
              </div>
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>
    </div>
  )
} 