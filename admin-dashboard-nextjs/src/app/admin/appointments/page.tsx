'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Dialog } from '@headlessui/react'
import { 
  ArrowLeftIcon,
  CalendarIcon,
  ClockIcon,
  UserIcon,
  XMarkIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  PencilIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isToday, isSameMonth } from 'date-fns'
import { appointmentService, Appointment as ApiAppointment } from '@/lib/services/appointmentService'
import { getPatientNames } from '@/lib/utils/patientResolver'
import { handleApiError, showError, showSuccess } from '@/lib/utils/errorHandler'

interface Appointment {
  id: string
  patient_id: string
  patientName?: string
  appointment_date: string
  appointment_time: string
  duration: number
  appointment_type: string
  location: string
  status: string
  notes?: string
  provider?: string
  payment_status?: string
  payment_amount?: number
  payment_date?: string
  payment_transaction_id?: string
}

// Helper function to format time from HH:MM:SS to HH:MM AM/PM
const formatTime = (time: string): string => {
  if (!time) return ''
  const [hours, minutes] = time.split(':')
  const hour = parseInt(hours)
  const ampm = hour >= 12 ? 'PM' : 'AM'
  const displayHour = hour % 12 || 12
  return `${displayHour}:${minutes} ${ampm}`
}

const appointmentTypes = [
  'Check-up',
  'Follow-up',
  'Consultation',
  'Physical Exam',
  'Lab Work',
]

const providers = [
  'Dr. John Smith',
  'Dr. Sarah Lee',
  'Dr. Michael Brown',
]

const timeSlots = [
  '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM',
  '11:00 AM', '11:30 AM', '01:00 PM', '01:30 PM',
  '02:00 PM', '02:30 PM', '03:00 PM', '03:30 PM',
  '04:00 PM', '04:30 PM'
]

export default function AppointmentsPage() {
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null)
  const [newAppointment, setNewAppointment] = useState({
    patient_id: '',
    appointment_date: format(new Date(), 'yyyy-MM-dd'),
    appointment_time: '09:00',
    duration: 30,
    appointment_type: 'consultation',
    location: 'office',
    status: 'scheduled',
    notes: ''
  })

  // Load appointments from API
  useEffect(() => {
    loadAppointments()
    
    // Auto-refresh every 30 seconds to sync with Provider Dashboard
    const refreshInterval = setInterval(() => {
      loadAppointments()
    }, 30000) // 30 seconds
    
    return () => clearInterval(refreshInterval)
  }, [])

  const loadAppointments = async () => {
    setLoading(true)
    try {
      // Admin Dashboard shows ALL appointments (all providers, all patients)
      // Provider Dashboard will filter by provider_id
      const response = await appointmentService.getAll()
      if (response.success && response.appointments) {
        // Map API appointments to component format
        const mappedAppointments: Appointment[] = response.appointments.map(apt => ({
          id: apt.appointment_id,
          patient_id: apt.patient_id,
          appointment_date: apt.appointment_date,
          appointment_time: apt.appointment_time,
          duration: apt.duration,
          appointment_type: apt.appointment_type,
          location: apt.location,
          status: apt.status,
          notes: apt.notes || '',
          provider: apt.provider_id
        }))
        
        // Resolve patient names
          const patientIds = Array.from(new Set(mappedAppointments.map(apt => apt.patient_id)))
        const patientNames = await getPatientNames(patientIds)
        
        // Add patient names to appointments
        const appointmentsWithNames = mappedAppointments.map(apt => ({
          ...apt,
          patientName: patientNames.get(apt.patient_id) || apt.patient_id.substring(0, 8) + '...'
        }))
        
        setAppointments(appointmentsWithNames)
      }
    } catch (error) {
      const errorMessage = handleApiError(error, 'Failed to load appointments')
      showError(errorMessage)
      setAppointments([])
    } finally {
      setLoading(false)
    }
  }

  const handleAddAppointment = async () => {
    try {
      // Convert time from HH:MM to HH:MM:SS format
      const timeWithSeconds = newAppointment.appointment_time.includes(':') 
        ? (newAppointment.appointment_time.split(':').length === 2 
          ? `${newAppointment.appointment_time}:00` 
          : newAppointment.appointment_time)
        : `${newAppointment.appointment_time}:00:00`

      const appointmentData = {
        patient_id: newAppointment.patient_id,
        appointment_date: newAppointment.appointment_date,
        appointment_time: timeWithSeconds,
        duration: newAppointment.duration,
        appointment_type: newAppointment.appointment_type,
        location: newAppointment.location,
        status: newAppointment.status,
        notes: newAppointment.notes || undefined,
        reminder: true
      }

      const response = await appointmentService.create(appointmentData)
      if (response.success) {
        showSuccess('Appointment created successfully')
        await loadAppointments() // Reload to get the new appointment
        setShowAddModal(false)
        setNewAppointment({
          patient_id: '',
          appointment_date: format(new Date(), 'yyyy-MM-dd'),
          appointment_time: '09:00',
          duration: 30,
          appointment_type: 'consultation',
          location: 'office',
          status: 'scheduled',
          notes: ''
        })
      } else {
        showError(response.error || 'Failed to create appointment')
      }
    } catch (error: any) {
      // Check for conflict errors (409 status)
      if (error.message?.includes('conflict') || error.message?.includes('409')) {
        showError(`Time conflict: ${error.message}. Please choose a different time slot.`)
      } else {
        const errorMessage = handleApiError(error, 'Failed to create appointment')
        showError(errorMessage)
      }
    }
  }

  const handleEditClick = (appointment: Appointment) => {
    setSelectedAppointment(appointment)
    setShowEditModal(true)
  }

  const handleDeleteClick = (appointment: Appointment) => {
    setSelectedAppointment(appointment)
    setShowDeleteModal(true)
  }

  const handleEditSave = async () => {
    if (!selectedAppointment) return

    try {
      // Convert time format if needed
      const timeWithSeconds = selectedAppointment.appointment_time.includes(':') 
        ? (selectedAppointment.appointment_time.split(':').length === 2 
          ? `${selectedAppointment.appointment_time}:00` 
          : selectedAppointment.appointment_time)
        : `${selectedAppointment.appointment_time}:00:00`

      const updateData = {
        appointment_date: selectedAppointment.appointment_date,
        appointment_time: timeWithSeconds,
        duration: selectedAppointment.duration,
        appointment_type: selectedAppointment.appointment_type,
        location: selectedAppointment.location,
        status: selectedAppointment.status,
        notes: selectedAppointment.notes || undefined
      }

      const response = await appointmentService.update(selectedAppointment.id, updateData)
      if (response.success) {
        showSuccess('Appointment updated successfully')
        await loadAppointments() // Reload to get updated data
        setShowEditModal(false)
        setSelectedAppointment(null)
      } else {
        showError(response.error || 'Failed to update appointment')
      }
    } catch (error: any) {
      // Check for conflict errors (409 status)
      if (error.message?.includes('conflict') || error.message?.includes('409')) {
        showError(`Time conflict: ${error.message}. Please choose a different time slot.`)
      } else {
        const errorMessage = handleApiError(error, 'Failed to update appointment')
        showError(errorMessage)
      }
    }
  }

  const handleEditChange = (field: keyof Appointment, value: string | number | boolean) => {
    if (!selectedAppointment) return
    setSelectedAppointment({
      ...selectedAppointment,
      [field]: value
    } as Appointment)
  }

  const handleDelete = async () => {
    if (!selectedAppointment) return

    try {
      const response = await appointmentService.delete(selectedAppointment.id)
      if (response.success) {
        showSuccess('Appointment deleted successfully')
        await loadAppointments() // Reload to reflect deletion
        setShowDeleteModal(false)
        setSelectedAppointment(null)
      } else {
        showError(response.error || 'Failed to delete appointment')
      }
    } catch (error) {
      const errorMessage = handleApiError(error, 'Failed to delete appointment')
      showError(errorMessage)
    }
  }

  const handleStatusChange = async (appointment: Appointment, newStatus: string) => {
    try {
      const response = await appointmentService.update(appointment.id, { status: newStatus })
      if (response.success) {
        await loadAppointments() // Reload to get updated status
      } else {
        showError(response.error || 'Failed to update appointment status')
      }
    } catch (error) {
      const errorMessage = handleApiError(error, 'Failed to update appointment status')
      showError(errorMessage)
    }
  }

  // Calendar logic
  const monthStart = startOfMonth(selectedDate)
  const monthEnd = endOfMonth(selectedDate)
  const days = eachDayOfInterval({ start: monthStart, end: monthEnd })

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
              <h1 className="text-3xl font-bold tracking-tight text-gray-900">Appointment Management</h1>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
            >
              New Appointment
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Calendar Section */}
          <div className="lg:col-span-1">
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Calendar</h2>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setSelectedDate(new Date(selectedDate.getFullYear(), selectedDate.getMonth() - 1))}
                    className="p-2 hover:bg-gray-100 rounded-full"
                  >
                    <ChevronLeftIcon className="h-5 w-5" />
                  </button>
                  <span className="text-sm font-medium">
                    {format(selectedDate, 'MMMM yyyy')}
                  </span>
                  <button
                    onClick={() => setSelectedDate(new Date(selectedDate.getFullYear(), selectedDate.getMonth() + 1))}
                    className="p-2 hover:bg-gray-100 rounded-full"
                  >
                    <ChevronRightIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
              <div className="grid grid-cols-7 gap-1 mb-2">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                  <div key={day} className="text-center text-sm font-medium text-gray-500">
                    {day}
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-7 gap-1">
                {Array.from({ length: monthStart.getDay() }).map((_, index) => (
                  <div key={`empty-${index}`} className="h-10" />
                ))}
                {days.map((day) => {
                  const isSelected = format(selectedDate, 'yyyy-MM-dd') === format(day, 'yyyy-MM-dd')
                  const hasAppointments = appointments.some(apt => apt.appointment_date === format(day, 'yyyy-MM-dd'))
                  
                  return (
                    <button
                      key={day.toString()}
                      onClick={() => setSelectedDate(day)}
                      className={`h-10 rounded-lg flex items-center justify-center text-sm relative
                        ${isToday(day) ? 'font-bold' : ''}
                        ${isSelected ? 'bg-indigo-600 text-white' : 'hover:bg-gray-100'}
                        ${!isSameMonth(day, selectedDate) ? 'text-gray-400' : 'text-gray-900'}
                      `}
                    >
                      {format(day, 'd')}
                      {hasAppointments && !isSelected && (
                        <div className="absolute bottom-1 w-1 h-1 bg-indigo-600 rounded-full"></div>
                      )}
                    </button>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Updated Appointments List */}
          <div className="lg:col-span-2">
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
                <h3 className="text-lg font-medium leading-6 text-gray-900">
                  Appointments for {format(selectedDate, 'MMMM d, yyyy')}
                </h3>
              </div>
              <ul role="list" className="divide-y divide-gray-200">
                {loading ? (
                  <li className="p-4 text-center text-gray-500">Loading appointments...</li>
                ) : appointments
                  .filter(appointment => appointment.appointment_date === format(selectedDate, 'yyyy-MM-dd'))
                  .length === 0 ? (
                  <li className="p-4 text-center text-gray-500">No appointments scheduled for this date</li>
                ) : (
                  appointments
                    .filter(appointment => appointment.appointment_date === format(selectedDate, 'yyyy-MM-dd'))
                    .map((appointment) => (
                      <li key={appointment.id} className="p-4 hover:bg-gray-50">
                        <div className="flex items-center space-x-4">
                          <div className="flex-shrink-0">
                            <UserIcon className="h-6 w-6 text-gray-400" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <p className="text-sm font-medium text-gray-900 truncate">
                                {appointment.patientName || `Patient ID: ${appointment.patient_id.substring(0, 8)}...`}
                              </p>
                              <div className="flex items-center space-x-2">
                                <select
                                  value={appointment.status}
                                  onChange={(e) => handleStatusChange(appointment, e.target.value)}
                                  className={`text-xs rounded-full px-2 py-1 font-medium ${
                                    appointment.status === 'confirmed' || appointment.status === 'Confirmed' ? 'bg-green-100 text-green-800' :
                                    appointment.status === 'cancelled' || appointment.status === 'Cancelled' ? 'bg-red-100 text-red-800' :
                                    'bg-yellow-100 text-yellow-800'
                                  }`}
                                >
                                  <option value="scheduled">Scheduled</option>
                                  <option value="confirmed">Confirmed</option>
                                  <option value="cancelled">Cancelled</option>
                                  <option value="completed">Completed</option>
                                </select>
                                <button
                                  onClick={() => handleEditClick(appointment)}
                                  className="p-1 text-gray-400 hover:text-gray-500"
                                >
                                  <PencilIcon className="h-4 w-4" />
                                </button>
                                <button
                                  onClick={() => handleDeleteClick(appointment)}
                                  className="p-1 text-red-400 hover:text-red-500"
                                >
                                  <TrashIcon className="h-4 w-4" />
                                </button>
                              </div>
                            </div>
                            <div className="mt-1">
                              <p className="text-sm text-gray-500">{appointment.appointment_type} - {appointment.location}</p>
                            </div>
                            <div className="mt-1 flex items-center space-x-4">
                              <div className="flex items-center">
                                <ClockIcon className="h-4 w-4 text-gray-400 mr-1" />
                                <p className="text-sm text-gray-500">{formatTime(appointment.appointment_time)} ({appointment.duration} min)</p>
                              </div>
                              {/* Payment Status */}
                              {appointment.payment_status && (
                                <div className="flex items-center">
                                  {appointment.payment_status === 'prepaid' || appointment.payment_status === 'paid' ? (
                                    <CheckCircleIcon className="h-4 w-4 text-green-500 mr-1" />
                                  ) : appointment.payment_status === 'pending' ? (
                                    <ExclamationTriangleIcon className="h-4 w-4 text-yellow-500 mr-1" />
                                  ) : (
                                    <XCircleIcon className="h-4 w-4 text-red-500 mr-1" />
                                  )}
                                  <span className={`text-xs font-medium px-2 py-1 rounded ${
                                    appointment.payment_status === 'prepaid' || appointment.payment_status === 'paid' 
                                      ? 'bg-green-100 text-green-800' 
                                      : appointment.payment_status === 'pending'
                                      ? 'bg-yellow-100 text-yellow-800'
                                      : 'bg-red-100 text-red-800'
                                  }`}>
                                    {appointment.payment_status === 'prepaid' ? 'Prepaid' :
                                     appointment.payment_status === 'paid' ? 'Paid' :
                                     appointment.payment_status === 'pending' ? 'Payment Pending' :
                                     appointment.payment_status || 'No Payment'}
                                  </span>
                                  {appointment.payment_amount && (
                                    <span className="ml-2 text-xs text-gray-600">
                                      ${parseFloat(appointment.payment_amount.toString()).toFixed(2)}
                                    </span>
                                  )}
                                </div>
                              )}
                            </div>
                            {appointment.notes && (
                              <p className="mt-1 text-sm text-gray-500">Notes: {appointment.notes}</p>
                            )}
                          </div>
                        </div>
                      </li>
                    ))
                )}
              </ul>
            </div>
          </div>
        </div>
      </main>

      {/* New Appointment Modal */}
      <Dialog
        as="div"
        className="relative z-50"
        open={showAddModal}
        onClose={() => setShowAddModal(false)}
      >
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                <button
                  type="button"
                  className="rounded-md bg-white text-gray-400 hover:text-gray-500"
                  onClick={() => setShowAddModal(false)}
                >
                  <span className="sr-only">Close</span>
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              <div className="sm:flex sm:items-start">
                <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                    Schedule New Appointment
                  </Dialog.Title>
                  <div className="mt-6 space-y-6">
                    <div>
                      <label htmlFor="patient_id" className="block text-sm font-medium text-gray-700">
                        Patient ID (UUID) *
                      </label>
                      <input
                        type="text"
                        name="patient_id"
                        id="patient_id"
                        required
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newAppointment.patient_id}
                        onChange={(e) => setNewAppointment({ ...newAppointment, patient_id: e.target.value })}
                        placeholder="00000000-0000-0000-0000-000000000000"
                      />
                      <p className="mt-1 text-xs text-gray-500">Enter the patient UUID from the database</p>
                    </div>
                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                      <div>
                        <label htmlFor="appointment_type" className="block text-sm font-medium text-gray-700">
                          Appointment Type *
                        </label>
                        <select
                          id="appointment_type"
                          required
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          value={newAppointment.appointment_type}
                          onChange={(e) => setNewAppointment({ ...newAppointment, appointment_type: e.target.value })}
                        >
                          <option value="consultation">Consultation</option>
                          <option value="follow_up">Follow-up</option>
                          <option value="telehealth">Telehealth</option>
                          <option value="procedure">Procedure</option>
                          <option value="lab_visit">Lab Visit</option>
                        </select>
                      </div>
                      <div>
                        <label htmlFor="location" className="block text-sm font-medium text-gray-700">
                          Location *
                        </label>
                        <select
                          id="location"
                          required
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          value={newAppointment.location}
                          onChange={(e) => setNewAppointment({ ...newAppointment, location: e.target.value })}
                        >
                          <option value="office">Office</option>
                          <option value="telehealth">Telehealth</option>
                          <option value="home_visit">Home Visit</option>
                          <option value="hospital">Hospital</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <label htmlFor="date" className="block text-sm font-medium text-gray-700">
                        Date
                      </label>
                      <input
                        type="date"
                        id="date"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newAppointment.appointment_date}
                        onChange={(e) => setNewAppointment({ ...newAppointment, appointment_date: e.target.value })}
                      />
                    </div>
                    <div>
                      <label htmlFor="time" className="block text-sm font-medium text-gray-700">
                        Time
                      </label>
                      <select
                        id="time"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newAppointment.appointment_time}
                        onChange={(e) => setNewAppointment({ ...newAppointment, appointment_time: e.target.value })}
                      >
                        {timeSlots.map((time) => (
                          <option key={time} value={time}>
                            {time}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              </div>
              <div className="mt-8 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 sm:ml-3 sm:w-auto"
                  onClick={handleAddAppointment}
                >
                  Schedule Appointment
                </button>
                <button
                  type="button"
                  className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                  onClick={() => setShowAddModal(false)}
                >
                  Cancel
                </button>
              </div>
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>

      {/* Edit Appointment Modal */}
      <Dialog
        as="div"
        className="relative z-50"
        open={showEditModal}
        onClose={() => setShowEditModal(false)}
      >
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                <button
                  type="button"
                  className="rounded-md bg-white text-gray-400 hover:text-gray-500"
                  onClick={() => setShowEditModal(false)}
                >
                  <span className="sr-only">Close</span>
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              {selectedAppointment && (
                <div>
                  <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                    Edit Appointment
                  </Dialog.Title>
                  <div className="mt-4 space-y-4">
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div>
                        <label htmlFor="edit-patientName" className="block text-sm font-medium text-gray-700">
                          Patient Name
                        </label>
                        <input
                          type="text"
                          id="edit-patientName"
                          value={selectedAppointment.patientName || selectedAppointment.patient_id.substring(0, 8) + '...'}
                          disabled
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        />
                      </div>
                      <div>
                        <label htmlFor="edit-medicalRecordNumber" className="block text-sm font-medium text-gray-700">
                          Medical Record Number
                        </label>
                        <input
                          type="text"
                          id="edit-medicalRecordNumber"
                          value={selectedAppointment.patient_id.substring(0, 8) + '...'}
                          disabled
                          className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 shadow-sm sm:text-sm"
                        />
                      </div>
                      <div>
                        <label htmlFor="edit-patientEmail" className="block text-sm font-medium text-gray-700">
                          Patient Email
                        </label>
                        <input
                          type="email"
                          id="edit-patientEmail"
                          value={''}
                          disabled
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        />
                      </div>
                      <div>
                        <label htmlFor="edit-patientPhone" className="block text-sm font-medium text-gray-700">
                          Patient Phone
                        </label>
                        <input
                          type="tel"
                          id="edit-patientPhone"
                          value={''}
                          disabled
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        />
                      </div>
                    </div>

                    <div>
                      <label htmlFor="edit-type" className="block text-sm font-medium text-gray-700">
                        Appointment Type
                      </label>
                      <select
                        id="edit-type"
                        value={selectedAppointment.appointment_type}
                        onChange={(e) => handleEditChange('appointment_type', e.target.value)}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      >
                        {appointmentTypes.map((type) => (
                          <option key={type} value={type}>
                            {type}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label htmlFor="edit-provider" className="block text-sm font-medium text-gray-700">
                        Provider
                      </label>
                      <select
                        id="edit-provider"
                        value={selectedAppointment.provider || ''}
                        disabled
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      >
                        {providers.map((provider) => (
                          <option key={provider} value={provider}>
                            {provider}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div>
                        <label htmlFor="edit-date" className="block text-sm font-medium text-gray-700">
                          Date
                        </label>
                        <input
                          type="date"
                          id="edit-date"
                          value={selectedAppointment.appointment_date}
                          onChange={(e) => handleEditChange('appointment_date', e.target.value)}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        />
                      </div>
                      <div>
                        <label htmlFor="edit-time" className="block text-sm font-medium text-gray-700">
                          Time
                        </label>
                        <select
                          id="edit-time"
                          value={selectedAppointment.appointment_time}
                          onChange={(e) => handleEditChange('appointment_time', e.target.value)}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        >
                          {timeSlots.map((time) => (
                            <option key={time} value={time}>
                              {time}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <div>
                      <label htmlFor="edit-status" className="block text-sm font-medium text-gray-700">
                        Status
                      </label>
                      <select
                        id="edit-status"
                        value={selectedAppointment.status}
                        onChange={(e) => handleEditChange('status', e.target.value as 'Pending' | 'Confirmed' | 'Cancelled')}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      >
                        <option value="Pending">Pending</option>
                        <option value="Confirmed">Confirmed</option>
                        <option value="Cancelled">Cancelled</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="edit-notes" className="block text-sm font-medium text-gray-700">
                        Notes
                      </label>
                      <textarea
                        id="edit-notes"
                        rows={3}
                        value={selectedAppointment.notes || ''}
                        onChange={(e) => handleEditChange('notes', e.target.value)}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>

                    <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                      <button
                        type="button"
                        className="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 sm:ml-3 sm:w-auto"
                        onClick={handleEditSave}
                      >
                        Save Changes
                      </button>
                      <button
                        type="button"
                        className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                        onClick={() => setShowEditModal(false)}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <Dialog
        as="div"
        className="relative z-50"
        open={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
      >
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div>
                <div className="mt-3 text-center sm:mt-0 sm:text-left">
                  <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                    Delete Appointment
                  </Dialog.Title>
                  <div className="mt-2">
                    <p className="text-sm text-gray-500">
                      Are you sure you want to delete this appointment? This action cannot be undone.
                    </p>
                  </div>
                </div>
              </div>
              <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:ml-3 sm:w-auto"
                  onClick={handleDelete}
                >
                  Delete
                </button>
                <button
                  type="button"
                  className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                  onClick={() => setShowDeleteModal(false)}
                >
                  Cancel
                </button>
              </div>
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>
    </div>
  )
} 