'use client'

import { useState, useEffect } from 'react'
import { 
  HeartIcon, 
  ChatBubbleLeftRightIcon, 
  ClockIcon,
  ArrowTrendingUpIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline'

interface RelationshipMetrics {
  patient_id: string
  provider_id: string
  relationship_score: number
  communication_frequency: number
  avg_response_time_hours: number
  engagement_level: 'high' | 'medium' | 'low'
  recommendations: string[]
}

// Mock data - in real app, this would come from API
const mockRelationships: RelationshipMetrics[] = [
  {
    patient_id: 'PAT-001',
    provider_id: 'PROV-001',
    relationship_score: 87,
    communication_frequency: 12, // messages per month
    avg_response_time_hours: 2.5,
    engagement_level: 'high',
    recommendations: [
      'Continue proactive communication - patient responds well',
      'Consider scheduling quarterly wellness check-ins',
      'Patient engagement is strong - leverage for treatment adherence'
    ]
  },
  {
    patient_id: 'PAT-002',
    provider_id: 'PROV-001',
    relationship_score: 62,
    communication_frequency: 4,
    avg_response_time_hours: 18,
    engagement_level: 'low',
    recommendations: [
      'Increase communication frequency - patient may need more support',
      'Response time is slow - consider automated reminders',
      'Engagement is low - reach out proactively to strengthen bond'
    ]
  },
  {
    patient_id: 'PAT-003',
    provider_id: 'PROV-002',
    relationship_score: 94,
    communication_frequency: 18,
    avg_response_time_hours: 1.2,
    engagement_level: 'high',
    recommendations: [
      'Excellent relationship - use as model for other patients',
      'Patient is highly engaged - consider advanced treatment options',
      'Strong bond - leverage for preventive care initiatives'
    ]
  }
]

export default function RelationshipIntelligence() {
  const [relationships, setRelationships] = useState<RelationshipMetrics[]>(mockRelationships)
  const [selectedRelationship, setSelectedRelationship] = useState<RelationshipMetrics | null>(null)

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100'
    if (score >= 60) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const getEngagementColor = (level: string) => {
    if (level === 'high') return 'text-green-600'
    if (level === 'medium') return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Relationship Intelligence AI</h2>
        <p className="text-gray-600">
          AI-powered analysis of patient-provider relationships to identify and strengthen healing bonds
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="dashboard-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Relationship Score</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">81</p>
            </div>
            <HeartIcon className="h-8 w-8 text-ecbome-primary" />
          </div>
        </div>
        <div className="dashboard-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Relationships</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{relationships.length}</p>
            </div>
            <ChatBubbleLeftRightIcon className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        <div className="dashboard-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">7.2h</p>
            </div>
            <ClockIcon className="h-8 w-8 text-purple-600" />
          </div>
        </div>
        <div className="dashboard-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">High Engagement</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">67%</p>
            </div>
            <ArrowTrendingUpIcon className="h-8 w-8 text-green-600" />
          </div>
        </div>
      </div>

      {/* Relationship List */}
      <div className="dashboard-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Patient-Provider Relationships</h3>
        <div className="space-y-3">
          {relationships.map((rel) => (
            <div
              key={`${rel.patient_id}-${rel.provider_id}`}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => setSelectedRelationship(rel)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(rel.relationship_score)}`}>
                    {rel.relationship_score}/100
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">
                      Patient {rel.patient_id} ↔ Provider {rel.provider_id}
                    </p>
                    <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
                      <span className="flex items-center">
                        <ChatBubbleLeftRightIcon className="h-4 w-4 mr-1" />
                        {rel.communication_frequency} msgs/month
                      </span>
                      <span className="flex items-center">
                        <ClockIcon className="h-4 w-4 mr-1" />
                        {rel.avg_response_time_hours}h avg response
                      </span>
                      <span className={`font-medium ${getEngagementColor(rel.engagement_level)}`}>
                        {rel.engagement_level.toUpperCase()} Engagement
                      </span>
                    </div>
                  </div>
                </div>
                <ArrowTrendingUpIcon className="h-5 w-5 text-gray-400" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Recommendations */}
      {selectedRelationship && (
        <div className="dashboard-card bg-blue-50 border-blue-200">
          <div className="flex items-center space-x-3 mb-4">
            <LightBulbIcon className="h-6 w-6 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              AI Recommendations to Strengthen Bond
            </h3>
          </div>
          <div className="space-y-2">
            {selectedRelationship.recommendations.map((rec, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-white rounded-lg">
                <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 text-sm font-semibold">{index + 1}</span>
                </div>
                <p className="text-sm text-gray-700">{rec}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t border-blue-200">
            <p className="text-sm text-gray-600">
              <strong>Relationship Score:</strong> {selectedRelationship.relationship_score}/100
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Calculated from communication frequency, response times, engagement patterns, and treatment adherence
            </p>
          </div>
        </div>
      )}

      {/* How It Works */}
      <div className="dashboard-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">How Relationship Intelligence Works</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">1. Data Collection</h4>
            <p className="text-sm text-gray-600">
              AI analyzes every patient-provider interaction: messages, appointments, treatment responses, and engagement patterns.
            </p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">2. Relationship Scoring</h4>
            <p className="text-sm text-gray-600">
              Machine learning algorithms calculate relationship strength based on communication quality, frequency, and outcomes.
            </p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">3. Bond Strengthening</h4>
            <p className="text-sm text-gray-600">
              AI provides personalized recommendations to strengthen bonds, improve communication, and enhance healing partnerships.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

