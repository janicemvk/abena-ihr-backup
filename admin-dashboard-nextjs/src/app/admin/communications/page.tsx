'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Dialog } from '@headlessui/react'
import { 
  ArrowLeftIcon,
  ChatBubbleLeftRightIcon,
  EnvelopeIcon,
  PhoneIcon,
  BellIcon,
  PaperAirplaneIcon,
  PlusIcon,
  XMarkIcon,
  UserGroupIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline'

interface Message {
  id: number
  sender: string
  recipient: string
  subject: string
  content: string
  timestamp: Date
  read: boolean
  type: 'internal' | 'patient' | 'notification'
}

interface Template {
  id: number
  name: string
  subject: string
  content: string
  category: string
}

// Mock data for demonstration
const mockMessages: Message[] = [
  {
    id: 1,
    sender: 'Dr. Sarah Lee',
    recipient: 'Dr. John Smith',
    subject: 'Patient Referral - Alice Johnson',
    content: 'Please review the attached patient records for Alice Johnson. She needs a cardiology consultation.',
    timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
    read: false,
    type: 'internal'
  },
  {
    id: 2,
    sender: 'System',
    recipient: 'All Staff',
    subject: 'EMR System Update',
    content: 'The EMR system will be undergoing maintenance tonight from 11 PM to 2 AM.',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
    read: true,
    type: 'notification'
  },
  {
    id: 3,
    sender: 'Bob Wilson',
    recipient: 'Dr. Sarah Lee',
    subject: 'Appointment Confirmation',
    content: 'Thank you for confirming my appointment for next Tuesday at 2 PM.',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4), // 4 hours ago
    read: true,
    type: 'patient'
  },
]

const messageTemplates: Template[] = [
  {
    id: 1,
    name: 'Appointment Reminder',
    subject: 'Upcoming Appointment Reminder',
    content: 'This is a reminder that you have an appointment scheduled for [DATE] at [TIME] with [PROVIDER].',
    category: 'Patient Communication'
  },
  {
    id: 2,
    name: 'Test Results Ready',
    subject: 'Your Test Results Are Ready',
    content: 'Your recent test results are now available. Please log in to your patient portal to view them.',
    category: 'Patient Communication'
  },
  {
    id: 3,
    name: 'Prescription Renewal',
    subject: 'Prescription Renewal Request',
    content: 'Your prescription for [MEDICATION] is due for renewal. Please contact our office to schedule a review.',
    category: 'Patient Communication'
  },
]

export default function CommunicationsPage() {
  const [messages, setMessages] = useState<Message[]>(mockMessages)
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null)
  const [showNewMessageModal, setShowNewMessageModal] = useState(false)
  const [showTemplateModal, setShowTemplateModal] = useState(false)
  const [messageFilter, setMessageFilter] = useState<'all' | 'internal' | 'patient' | 'notification'>('all')
  const [newMessage, setNewMessage] = useState({
    recipient: '',
    subject: '',
    content: '',
    type: 'internal' as 'internal' | 'patient' | 'notification'
  })

  const filteredMessages = messages.filter(message => 
    messageFilter === 'all' || message.type === messageFilter
  ).sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())

  const handleSendMessage = () => {
    const message: Message = {
      id: Date.now(),
      sender: 'Dr. John Smith', // Would come from auth context in real app
      recipient: newMessage.recipient,
      subject: newMessage.subject,
      content: newMessage.content,
      timestamp: new Date(),
      read: false,
      type: newMessage.type
    }

    setMessages(prev => [message, ...prev])
    setShowNewMessageModal(false)
    setNewMessage({
      recipient: '',
      subject: '',
      content: '',
      type: 'internal'
    })
  }

  const handleMarkAsRead = (messageId: number) => {
    setMessages(prev =>
      prev.map(msg =>
        msg.id === messageId ? { ...msg, read: true } : msg
      )
    )
  }

  const handleUseTemplate = (template: Template) => {
    setNewMessage(prev => ({
      ...prev,
      subject: template.subject,
      content: template.content
    }))
    setShowTemplateModal(false)
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
              <h1 className="text-3xl font-bold tracking-tight text-gray-900">Communications Hub</h1>
            </div>
            <button
              onClick={() => setShowNewMessageModal(true)}
              className="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              New Message
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
          {/* Navigation Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white shadow rounded-lg">
              <nav className="space-y-1 p-4">
                <button
                  onClick={() => setMessageFilter('all')}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                    messageFilter === 'all' 
                      ? 'bg-indigo-50 text-indigo-600' 
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <ChatBubbleLeftRightIcon className="h-5 w-5 mr-3" />
                  All Messages
                </button>
                <button
                  onClick={() => setMessageFilter('internal')}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                    messageFilter === 'internal' 
                      ? 'bg-indigo-50 text-indigo-600' 
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <UserGroupIcon className="h-5 w-5 mr-3" />
                  Internal
                </button>
                <button
                  onClick={() => setMessageFilter('patient')}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                    messageFilter === 'patient' 
                      ? 'bg-indigo-50 text-indigo-600' 
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <EnvelopeIcon className="h-5 w-5 mr-3" />
                  Patient
                </button>
                <button
                  onClick={() => setMessageFilter('notification')}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                    messageFilter === 'notification' 
                      ? 'bg-indigo-50 text-indigo-600' 
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <BellIcon className="h-5 w-5 mr-3" />
                  Notifications
                </button>
                <button
                  onClick={() => setShowTemplateModal(true)}
                  className="w-full flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50"
                >
                  <DocumentTextIcon className="h-5 w-5 mr-3" />
                  Templates
                </button>
              </nav>
            </div>
          </div>

          {/* Message List and Detail View */}
          <div className="lg:col-span-3">
            <div className="bg-white shadow rounded-lg divide-y divide-gray-200">
              {filteredMessages.map((message) => (
                <div
                  key={message.id}
                  className={`p-4 hover:bg-gray-50 cursor-pointer ${!message.read ? 'bg-indigo-50' : ''}`}
                  onClick={() => {
                    setSelectedMessage(message)
                    handleMarkAsRead(message.id)
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-full ${
                        message.type === 'internal' ? 'bg-blue-100 text-blue-600' :
                        message.type === 'patient' ? 'bg-green-100 text-green-600' :
                        'bg-yellow-100 text-yellow-600'
                      }`}>
                        {message.type === 'internal' ? <UserGroupIcon className="h-5 w-5" /> :
                         message.type === 'patient' ? <EnvelopeIcon className="h-5 w-5" /> :
                         <BellIcon className="h-5 w-5" />}
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">
                          {message.subject}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {message.sender} → {message.recipient}
                        </p>
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(message.timestamp).toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </div>
                  </div>
                  {selectedMessage?.id === message.id && (
                    <div className="mt-4 text-sm text-gray-600">
                      {message.content}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>

      {/* New Message Modal */}
      <Dialog
        as="div"
        className="relative z-50"
        open={showNewMessageModal}
        onClose={() => setShowNewMessageModal(false)}
      >
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                <button
                  type="button"
                  className="rounded-md bg-white text-gray-400 hover:text-gray-500"
                  onClick={() => setShowNewMessageModal(false)}
                >
                  <span className="sr-only">Close</span>
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              <div>
                <div className="mt-3 text-center sm:mt-0 sm:text-left">
                  <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                    New Message
                  </Dialog.Title>
                  <div className="mt-4 space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Message Type
                      </label>
                      <select
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newMessage.type}
                        onChange={(e) => setNewMessage({ ...newMessage, type: e.target.value as 'internal' | 'patient' | 'notification' })}
                      >
                        <option value="internal">Internal Message</option>
                        <option value="patient">Patient Message</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Recipient
                      </label>
                      <input
                        type="text"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newMessage.recipient}
                        onChange={(e) => setNewMessage({ ...newMessage, recipient: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Subject
                      </label>
                      <input
                        type="text"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newMessage.subject}
                        onChange={(e) => setNewMessage({ ...newMessage, subject: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Message
                      </label>
                      <textarea
                        rows={4}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newMessage.content}
                        onChange={(e) => setNewMessage({ ...newMessage, content: e.target.value })}
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 sm:ml-3 sm:w-auto"
                  onClick={handleSendMessage}
                >
                  Send Message
                </button>
                <button
                  type="button"
                  className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                  onClick={() => setShowNewMessageModal(false)}
                >
                  Cancel
                </button>
              </div>
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>

      {/* Templates Modal */}
      <Dialog
        as="div"
        className="relative z-50"
        open={showTemplateModal}
        onClose={() => setShowTemplateModal(false)}
      >
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                <button
                  type="button"
                  className="rounded-md bg-white text-gray-400 hover:text-gray-500"
                  onClick={() => setShowTemplateModal(false)}
                >
                  <span className="sr-only">Close</span>
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              <div>
                <div className="mt-3 text-center sm:mt-0 sm:text-left">
                  <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                    Message Templates
                  </Dialog.Title>
                  <div className="mt-4">
                    <div className="space-y-4">
                      {messageTemplates.map((template) => (
                        <div
                          key={template.id}
                          className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                          onClick={() => handleUseTemplate(template)}
                        >
                          <h4 className="text-sm font-medium text-gray-900">{template.name}</h4>
                          <p className="mt-1 text-sm text-gray-500">{template.subject}</p>
                          <p className="mt-2 text-sm text-gray-600">{template.content}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                  onClick={() => setShowTemplateModal(false)}
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