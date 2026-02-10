'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Dialog } from '@headlessui/react'
import { 
  ArrowLeftIcon,
  DocumentTextIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  XMarkIcon,
  MagnifyingGlassIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline'
import { treatmentPlanService, TreatmentPlan } from '@/lib/services/treatmentPlanService'
import { format } from 'date-fns'
import { getPatientNames } from '@/lib/utils/patientResolver'

interface TreatmentPlanWithName extends TreatmentPlan {
  patientName?: string
}

export default function TreatmentPlansPage() {
  const [plans, setPlans] = useState<TreatmentPlanWithName[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [selectedPlan, setSelectedPlan] = useState<TreatmentPlan | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [newPlan, setNewPlan] = useState({
    patient_id: '',
    title: '',
    description: '',
    start_date: format(new Date(), 'yyyy-MM-dd'),
    end_date: '',
    status: 'active',
    goals: [] as string[],
    medications: [] as string[],
    interventions: [] as string[],
    monitoring: [] as string[],
    notes: ''
  })

  useEffect(() => {
    loadPlans()
  }, [])

  const loadPlans = async () => {
    setLoading(true)
    try {
      const response = await treatmentPlanService.getAll()
      if (response.success && response.treatment_plans) {
        // Resolve patient names
        const patientIds = Array.from(new Set(response.treatment_plans.map(plan => plan.patient_id)))
        const patientNames = await getPatientNames(patientIds)
        
        // Add patient names to plans
        const plansWithNames: TreatmentPlanWithName[] = response.treatment_plans.map(plan => ({
          ...plan,
          patientName: patientNames.get(plan.patient_id) || plan.patient_id.substring(0, 8) + '...'
        }))
        
        setPlans(plansWithNames)
      }
    } catch (error) {
      console.error('Failed to load treatment plans:', error)
      setPlans([])
    } finally {
      setLoading(false)
    }
  }

  const handleAddPlan = async () => {
    try {
      const planData = {
        patient_id: newPlan.patient_id,
        title: newPlan.title,
        description: newPlan.description || undefined,
        start_date: newPlan.start_date,
        end_date: newPlan.end_date || undefined,
        status: newPlan.status || undefined,
        goals: newPlan.goals.filter(g => g.trim() !== ''),
        medications: newPlan.medications.filter(m => m.trim() !== ''),
        interventions: newPlan.interventions.filter(i => i.trim() !== ''),
        monitoring: newPlan.monitoring.filter(m => m.trim() !== ''),
        notes: newPlan.notes || undefined
      }

      const response = await treatmentPlanService.create(planData)
      if (response.success) {
        await loadPlans()
        setShowAddModal(false)
        setNewPlan({
          patient_id: '',
          title: '',
          description: '',
          start_date: format(new Date(), 'yyyy-MM-dd'),
          end_date: '',
          status: 'active',
          goals: [],
          medications: [],
          interventions: [],
          monitoring: [],
          notes: ''
        })
      }
    } catch (error) {
      console.error('Failed to create treatment plan:', error)
      alert('Failed to create treatment plan. Please try again.')
    }
  }

  const handleEditSave = async () => {
    if (!selectedPlan) return

    try {
      const updateData = {
        title: selectedPlan.title,
        description: selectedPlan.description || undefined,
        start_date: selectedPlan.start_date,
        end_date: selectedPlan.end_date || undefined,
        status: selectedPlan.status || undefined,
        goals: Array.isArray(selectedPlan.goals) ? selectedPlan.goals : [],
        medications: Array.isArray(selectedPlan.medications) ? selectedPlan.medications : [],
        interventions: Array.isArray(selectedPlan.interventions) ? selectedPlan.interventions : [],
        monitoring: Array.isArray(selectedPlan.monitoring) ? selectedPlan.monitoring : [],
        notes: selectedPlan.notes || undefined
      }

      const response = await treatmentPlanService.update(selectedPlan.plan_id, updateData)
      if (response.success) {
        await loadPlans()
        setShowEditModal(false)
        setSelectedPlan(null)
      }
    } catch (error) {
      console.error('Failed to update treatment plan:', error)
      alert('Failed to update treatment plan. Please try again.')
    }
  }

  const handleDelete = async () => {
    if (!selectedPlan) return

    try {
      const response = await treatmentPlanService.delete(selectedPlan.plan_id)
      if (response.success) {
        await loadPlans()
        setShowDeleteModal(false)
        setSelectedPlan(null)
      }
    } catch (error) {
      console.error('Failed to delete treatment plan:', error)
      alert('Failed to delete treatment plan. Please try again.')
    }
  }

  const filteredPlans = plans.filter(plan =>
    plan.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    plan.patient_id.toLowerCase().includes(searchTerm.toLowerCase())
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
              <h1 className="text-3xl font-bold tracking-tight text-gray-900">Treatment Plans Management</h1>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
            >
              <PlusIcon className="h-5 w-5" />
              Add Treatment Plan
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search plans by title or patient ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full rounded-md border-gray-300 pl-10 pr-4 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
        </div>

        {/* Plans List */}
        <div className="bg-white shadow rounded-lg">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading treatment plans...</div>
          ) : filteredPlans.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <DocumentTextIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No treatment plans found</p>
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {filteredPlans.map((plan) => {
                const goals = Array.isArray(plan.goals) ? plan.goals : []
                const medications = Array.isArray(plan.medications) ? plan.medications : []
                return (
                  <li key={plan.plan_id} className="p-6 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">{plan.title}</h3>
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            plan.status === 'active' ? 'bg-green-100 text-green-800' :
                            plan.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {plan.status}
                          </span>
                        </div>
                        {plan.description && (
                          <p className="text-sm text-gray-600 mb-2">{plan.description}</p>
                        )}
                        <div className="grid grid-cols-2 gap-4 text-xs text-gray-500 mb-2">
                          <div>
                            <span className="font-medium">Start:</span> {format(new Date(plan.start_date), 'MMM d, yyyy')}
                          </div>
                          {plan.end_date && (
                            <div>
                              <span className="font-medium">End:</span> {format(new Date(plan.end_date), 'MMM d, yyyy')}
                            </div>
                          )}
                        </div>
                        {goals.length > 0 && (
                          <div className="mb-2">
                            <span className="text-xs font-medium text-gray-700">Goals:</span>
                            <ul className="mt-1 space-y-1">
                              {goals.map((goal, idx) => (
                                <li key={idx} className="text-xs text-gray-600 flex items-center gap-1">
                                  <CheckCircleIcon className="h-3 w-3" />
                                  {goal}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {medications.length > 0 && (
                          <div className="mb-2">
                            <span className="text-xs font-medium text-gray-700">Medications:</span>
                            <p className="text-xs text-gray-600">{medications.join(', ')}</p>
                          </div>
                        )}
                        <div className="text-xs text-gray-500">
                          {plan.patientName || `Patient ID: ${plan.patient_id.substring(0, 8)}...`}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 ml-4">
                        <button
                          onClick={() => {
                            setSelectedPlan(plan)
                            setShowEditModal(true)
                          }}
                          className="p-2 text-blue-600 hover:bg-blue-100 rounded"
                        >
                          <PencilIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => {
                            setSelectedPlan(plan)
                            setShowDeleteModal(true)
                          }}
                          className="p-2 text-red-600 hover:bg-red-100 rounded"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </li>
                )
              })}
            </ul>
          )}
        </div>
      </main>

      {/* Add Plan Modal */}
      <Dialog open={showAddModal} onClose={() => setShowAddModal(false)}>
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" />
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6 max-h-[90vh] overflow-y-auto">
              <div className="absolute right-0 top-0 pr-4 pt-4">
                <button onClick={() => setShowAddModal(false)}>
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              <h3 className="text-lg font-semibold mb-4">Add Treatment Plan</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Patient ID (UUID) *</label>
                  <input
                    type="text"
                    required
                    value={newPlan.patient_id}
                    onChange={(e) => setNewPlan({ ...newPlan, patient_id: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="00000000-0000-0000-0000-000000000000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Title *</label>
                  <input
                    type="text"
                    required
                    value={newPlan.title}
                    onChange={(e) => setNewPlan({ ...newPlan, title: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    rows={3}
                    value={newPlan.description}
                    onChange={(e) => setNewPlan({ ...newPlan, description: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Start Date *</label>
                    <input
                      type="date"
                      required
                      value={newPlan.start_date}
                      onChange={(e) => setNewPlan({ ...newPlan, start_date: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">End Date</label>
                    <input
                      type="date"
                      value={newPlan.end_date}
                      onChange={(e) => setNewPlan({ ...newPlan, end_date: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Goals (one per line)</label>
                  <textarea
                    rows={3}
                    value={newPlan.goals.join('\n')}
                    onChange={(e) => setNewPlan({ ...newPlan, goals: e.target.value.split('\n').filter(g => g.trim()) })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="Goal 1&#10;Goal 2&#10;Goal 3"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Medications (comma-separated)</label>
                  <input
                    type="text"
                    value={newPlan.medications.join(', ')}
                    onChange={(e) => setNewPlan({ ...newPlan, medications: e.target.value.split(',').map(m => m.trim()).filter(m => m) })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="Medication 1, Medication 2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Notes</label>
                  <textarea
                    rows={3}
                    value={newPlan.notes}
                    onChange={(e) => setNewPlan({ ...newPlan, notes: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
              </div>
              <div className="mt-6 flex justify-end gap-3">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddPlan}
                  className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
                >
                  Create Plan
                </button>
              </div>
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>

      {/* Edit Plan Modal - Similar structure, will be simplified for now */}
      <Dialog open={showEditModal} onClose={() => setShowEditModal(false)}>
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" />
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6 max-h-[90vh] overflow-y-auto">
              <div className="absolute right-0 top-0 pr-4 pt-4">
                <button onClick={() => setShowEditModal(false)}>
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              {selectedPlan && (
                <>
                  <h3 className="text-lg font-semibold mb-4">Edit Treatment Plan</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Title *</label>
                      <input
                        type="text"
                        required
                        value={selectedPlan.title}
                        onChange={(e) => setSelectedPlan({ ...selectedPlan, title: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Status</label>
                      <select
                        value={selectedPlan.status}
                        onChange={(e) => setSelectedPlan({ ...selectedPlan, status: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                      >
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                      </select>
                    </div>
                  </div>
                  <div className="mt-6 flex justify-end gap-3">
                    <button
                      onClick={() => setShowEditModal(false)}
                      className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleEditSave}
                      className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
                    >
                      Save Changes
                    </button>
                  </div>
                </>
              )}
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <Dialog open={showDeleteModal} onClose={() => setShowDeleteModal(false)}>
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" />
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <h3 className="text-lg font-semibold mb-2">Delete Treatment Plan</h3>
              <p className="text-sm text-gray-500 mb-6">
                Are you sure you want to delete this treatment plan? This action cannot be undone.
              </p>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDelete}
                  className="rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500"
                >
                  Delete
                </button>
              </div>
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>
    </div>
  )
}


