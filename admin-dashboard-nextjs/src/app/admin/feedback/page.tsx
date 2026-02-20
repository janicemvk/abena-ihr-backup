'use client'

import { useState } from 'react'
import Link from 'next/link'
import { 
  ArrowLeftIcon,
  StarIcon,
  ChatBubbleLeftIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid'

// Mock feedback data
const feedbackData = [
  {
    id: 1,
    patientName: 'Alice Johnson',
    rating: 5,
    comment: 'Excellent service and care. The staff was very professional and attentive.',
    date: '2024-02-15',
    provider: 'Dr. John Smith',
  },
  {
    id: 2,
    patientName: 'Bob Wilson',
    rating: 4,
    comment: 'Good experience overall. Wait time could be improved.',
    date: '2024-02-14',
    provider: 'Dr. Sarah Lee',
  },
  {
    id: 3,
    patientName: 'Carol Brown',
    rating: 5,
    comment: 'Very satisfied with the treatment and follow-up care.',
    date: '2024-02-13',
    provider: 'Dr. John Smith',
  },
]

const stats = [
  { name: 'Average Rating', value: '4.8', icon: StarIcon },
  { name: 'Total Reviews', value: '1,234', icon: ChatBubbleLeftIcon },
  { name: 'Response Rate', value: '98%', icon: ChartBarIcon },
]

export default function FeedbackPage() {
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
              <h1 className="text-3xl font-bold tracking-tight text-gray-900">Patient Feedback</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
        {/* Stats */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-8">
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

        {/* Feedback List */}
        <div className="bg-white shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 className="text-lg font-medium leading-6 text-gray-900">Recent Feedback</h3>
          </div>
          <ul role="list" className="divide-y divide-gray-200">
            {feedbackData.map((feedback) => (
              <li key={feedback.id} className="p-4">
                <div className="flex space-x-3">
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-medium">{feedback.patientName}</h3>
                      <p className="text-sm text-gray-500">{feedback.date}</p>
                    </div>
                    <div className="flex items-center mt-1">
                      {[0, 1, 2, 3, 4].map((rating) => (
                        <StarIconSolid
                          key={rating}
                          className={`h-5 w-5 flex-shrink-0 ${
                            rating < feedback.rating ? 'text-yellow-400' : 'text-gray-200'
                          }`}
                          aria-hidden="true"
                        />
                      ))}
                    </div>
                    <p className="mt-3 text-sm text-gray-500">{feedback.comment}</p>
                    <p className="mt-2 text-sm text-gray-400">Provider: {feedback.provider}</p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
          <div className="px-4 py-4 sm:px-6 border-t border-gray-200">
            <button
              type="button"
              className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Load More
            </button>
          </div>
        </div>
      </main>
    </div>
  )
} 