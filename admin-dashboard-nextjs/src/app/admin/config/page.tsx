'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Dialog } from '@headlessui/react'
import { 
  ArrowLeftIcon,
  BuildingOfficeIcon,
  PhotoIcon,
  DocumentTextIcon,
  ClockIcon,
  PhoneIcon,
  MapPinIcon,
  PlusIcon,
  TrashIcon,
  PencilIcon,
  XMarkIcon,
  CpuChipIcon,
} from '@heroicons/react/24/outline'

interface ClinicInfo {
  name: string
  logo: string | null
  address: string
  telephone: string
  fax: string
  hoursOfOperation: {
    [key: string]: {
      open: string
      close: string
      closed: boolean
    }
  }
}

interface FormDocument {
  id: string
  name: string
  category: string
  lastUpdated: Date
  fileUrl: string
}

const formCategories = [
  'Patient Forms',
  'Insurance Forms',
  'Consent Forms',
  'Privacy Forms',
  'HIPAA Forms',
  'Other Forms'
]

export default function SystemSettingsPage() {
  const [clinicInfo, setClinicInfo] = useState<ClinicInfo>({
    name: 'Knox Medical Center',
    logo: null,
    address: '123 Medical Drive, Suite 100, Knox City, ST 12345',
    telephone: '(555) 123-4567',
    fax: '(555) 123-4568',
    hoursOfOperation: {
      monday: { open: '09:00', close: '17:00', closed: false },
      tuesday: { open: '09:00', close: '17:00', closed: false },
      wednesday: { open: '09:00', close: '17:00', closed: false },
      thursday: { open: '09:00', close: '17:00', closed: false },
      friday: { open: '09:00', close: '17:00', closed: false },
      saturday: { open: '10:00', close: '14:00', closed: false },
      sunday: { open: '09:00', close: '17:00', closed: true },
    }
  })

  const [forms, setForms] = useState<FormDocument[]>([
    {
      id: '1',
      name: 'New Patient Registration',
      category: 'Patient Forms',
      lastUpdated: new Date(),
      fileUrl: '/forms/new-patient.pdf'
    },
    {
      id: '2',
      name: 'Insurance Verification',
      category: 'Insurance Forms',
      lastUpdated: new Date(),
      fileUrl: '/forms/insurance.pdf'
    }
  ])

  const [showUploadModal, setShowUploadModal] = useState(false)
  const [newForm, setNewForm] = useState({
    name: '',
    category: formCategories[0]
  })

  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [selectedForm, setSelectedForm] = useState<FormDocument | null>(null)
  const [editForm, setEditForm] = useState({
    name: '',
    category: formCategories[0]
  })

  const handleLogoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // In a real app, this would upload to a server
      const reader = new FileReader()
      reader.onload = (e) => {
        setClinicInfo({
          ...clinicInfo,
          logo: e.target?.result as string
        })
      }
      reader.readAsDataURL(file)
    }
  }

  const handleClinicInfoUpdate = (field: keyof ClinicInfo, value: string) => {
    setClinicInfo({
      ...clinicInfo,
      [field]: value
    })
  }

  const handleHoursUpdate = (day: string, field: 'open' | 'close' | 'closed', value: string | boolean) => {
    setClinicInfo({
      ...clinicInfo,
      hoursOfOperation: {
        ...clinicInfo.hoursOfOperation,
        [day]: {
          ...clinicInfo.hoursOfOperation[day],
          [field]: value
        }
      }
    })
  }

  const handleFormUpload = () => {
    // In a real app, this would handle file upload
    const newFormDoc: FormDocument = {
      id: String(forms.length + 1),
      name: newForm.name,
      category: newForm.category,
      lastUpdated: new Date(),
      fileUrl: '/forms/placeholder.pdf'
    }
    setForms([...forms, newFormDoc])
    setShowUploadModal(false)
    setNewForm({ name: '', category: formCategories[0] })
  }

  const handleDownload = (form: FormDocument) => {
    // In a real app, this would trigger a file download
    const link = document.createElement('a')
    link.href = form.fileUrl
    link.download = `${form.name}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleEditClick = (form: FormDocument) => {
    setSelectedForm(form)
    setEditForm({
      name: form.name,
      category: form.category
    })
    setShowEditModal(true)
  }

  const handleDeleteClick = (form: FormDocument) => {
    setSelectedForm(form)
    setShowDeleteConfirm(true)
  }

  const handleEditSave = () => {
    if (!selectedForm) return

    const updatedForms = forms.map(form => {
      if (form.id === selectedForm.id) {
        return {
          ...form,
          name: editForm.name,
          category: editForm.category,
          lastUpdated: new Date()
        }
      }
      return form
    })

    setForms(updatedForms)
    setShowEditModal(false)
    setSelectedForm(null)
    setEditForm({ name: '', category: formCategories[0] })
  }

  const handleDelete = () => {
    if (!selectedForm) return

    const updatedForms = forms.filter(form => form.id !== selectedForm.id)
    setForms(updatedForms)
    setShowDeleteConfirm(false)
    setSelectedForm(null)
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
              <h1 className="text-3xl font-bold tracking-tight text-gray-900">System Settings</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {/* Clinic Information */}
          <div className="bg-white shadow rounded-lg">
            <div className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">Clinic Information</h2>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Clinic Logo</label>
                  <div className="mt-2 flex items-center space-x-4">
                    {clinicInfo.logo ? (
                      <img src={clinicInfo.logo} alt="Clinic Logo" className="h-20 w-20 object-contain" />
                    ) : (
                      <div className="h-20 w-20 rounded-lg bg-gray-100 flex items-center justify-center">
                        <PhotoIcon className="h-8 w-8 text-gray-400" />
                      </div>
                    )}
                    <label className="cursor-pointer inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                      Upload Logo
                      <input type="file" className="hidden" accept="image/*" onChange={handleLogoUpload} />
                    </label>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Clinic Name</label>
                  <input
                    type="text"
                    value={clinicInfo.name}
                    onChange={(e) => handleClinicInfoUpdate('name', e.target.value)}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Address</label>
                  <input
                    type="text"
                    value={clinicInfo.address}
                    onChange={(e) => handleClinicInfoUpdate('address', e.target.value)}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                </div>

                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Telephone</label>
                    <input
                      type="tel"
                      value={clinicInfo.telephone}
                      onChange={(e) => handleClinicInfoUpdate('telephone', e.target.value)}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Fax</label>
                    <input
                      type="tel"
                      value={clinicInfo.fax}
                      onChange={(e) => handleClinicInfoUpdate('fax', e.target.value)}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Hours of Operation */}
          <div className="bg-white shadow rounded-lg">
            <div className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">Hours of Operation</h2>
              <div className="space-y-4">
                {Object.entries(clinicInfo.hoursOfOperation).map(([day, hours]) => (
                  <div key={day} className="grid grid-cols-1 gap-4 sm:grid-cols-4 items-center">
                    <div className="font-medium capitalize">{day}</div>
                    <div className="sm:col-span-3 flex items-center space-x-4">
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={hours.closed}
                          onChange={(e) => handleHoursUpdate(day, 'closed', e.target.checked)}
                          className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                        />
                        <span className="ml-2 text-sm text-gray-500">Closed</span>
                      </label>
                      {!hours.closed && (
                        <>
                          <input
                            type="time"
                            value={hours.open}
                            onChange={(e) => handleHoursUpdate(day, 'open', e.target.value)}
                            className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          />
                          <span className="text-gray-500">to</span>
                          <input
                            type="time"
                            value={hours.close}
                            onChange={(e) => handleHoursUpdate(day, 'close', e.target.value)}
                            className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          />
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quantum Analysis Settings */}
          <div className="bg-white shadow rounded-lg">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <CpuChipIcon className="h-6 w-6 text-ecbome-primary" />
                  <h2 className="text-lg font-semibold text-gray-900">Quantum Analysis Settings</h2>
                </div>
                <Link
                  href="/admin/config/quantum-settings"
                  className="inline-flex items-center rounded-md bg-ecbome-primary px-3 py-2 text-sm font-semibold text-white shadow-sm hover:opacity-90"
                >
                  Configure Settings
                </Link>
              </div>
              <p className="text-sm text-gray-600">
                Configure automatic vs manual quantum analysis triggers. Choose whether quantum analysis runs automatically after every eCBome analysis or only when manually requested.
              </p>
            </div>
          </div>

          {/* Forms Management */}
          <div className="bg-white shadow rounded-lg">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-gray-900">Forms Management</h2>
                <button
                  onClick={() => setShowUploadModal(true)}
                  className="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Upload Form
                </button>
              </div>

              <div className="space-y-4">
                {formCategories.map((category) => {
                  const categoryForms = forms.filter(form => form.category === category)
                  if (categoryForms.length === 0) return null

                  return (
                    <div key={category}>
                      <h3 className="text-sm font-medium text-gray-900 mb-3">{category}</h3>
                      <ul className="divide-y divide-gray-200">
                        {categoryForms.map((form) => (
                          <li key={form.id} className="py-3">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="text-sm font-medium text-gray-900">{form.name}</p>
                                <p className="text-sm text-gray-500">
                                  Last updated {form.lastUpdated.toLocaleDateString()}
                                </p>
                              </div>
                              <div className="flex items-center space-x-2">
                                <button
                                  onClick={() => handleDownload(form)}
                                  className="text-indigo-600 hover:text-indigo-900 p-2 rounded-full hover:bg-indigo-50"
                                  title="Download"
                                >
                                  <DocumentTextIcon className="h-5 w-5" />
                                </button>
                                <button
                                  onClick={() => handleEditClick(form)}
                                  className="text-gray-400 hover:text-gray-500 p-2 rounded-full hover:bg-gray-50"
                                  title="Edit"
                                >
                                  <PencilIcon className="h-5 w-5" />
                                </button>
                                <button
                                  onClick={() => handleDeleteClick(form)}
                                  className="text-red-400 hover:text-red-500 p-2 rounded-full hover:bg-red-50"
                                  title="Delete"
                                >
                                  <TrashIcon className="h-5 w-5" />
                                </button>
                              </div>
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Upload Form Modal */}
      <Dialog
        as="div"
        className="relative z-50"
        open={showUploadModal}
        onClose={() => setShowUploadModal(false)}
      >
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div>
                <div className="mt-3 text-center sm:mt-0 sm:text-left">
                  <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                    Upload New Form
                  </Dialog.Title>
                  <div className="mt-4 space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Form Name</label>
                      <input
                        type="text"
                        value={newForm.name}
                        onChange={(e) => setNewForm({ ...newForm, name: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Category</label>
                      <select
                        value={newForm.category}
                        onChange={(e) => setNewForm({ ...newForm, category: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      >
                        {formCategories.map((category) => (
                          <option key={category} value={category}>
                            {category}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">File</label>
                      <div className="mt-1 flex justify-center rounded-md border-2 border-dashed border-gray-300 px-6 pt-5 pb-6">
                        <div className="space-y-1 text-center">
                          <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
                          <div className="flex text-sm text-gray-600">
                            <label className="relative cursor-pointer rounded-md bg-white font-medium text-indigo-600 focus-within:outline-none focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 hover:text-indigo-500">
                              <span>Upload a file</span>
                              <input type="file" className="sr-only" />
                            </label>
                            <p className="pl-1">or drag and drop</p>
                          </div>
                          <p className="text-xs text-gray-500">PDF up to 10MB</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 sm:ml-3 sm:w-auto"
                  onClick={handleFormUpload}
                >
                  Upload
                </button>
                <button
                  type="button"
                  className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                  onClick={() => setShowUploadModal(false)}
                >
                  Cancel
                </button>
              </div>
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>

      {/* Edit Form Modal */}
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
              <div>
                <div className="mt-3 text-center sm:mt-0 sm:text-left">
                  <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                    Edit Form
                  </Dialog.Title>
                  <div className="mt-4 space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Form Name</label>
                      <input
                        type="text"
                        value={editForm.name}
                        onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Category</label>
                      <select
                        value={editForm.category}
                        onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      >
                        {formCategories.map((category) => (
                          <option key={category} value={category}>
                            {category}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
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
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <Dialog
        as="div"
        className="relative z-50"
        open={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
      >
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div>
                <div className="mt-3 text-center sm:mt-0 sm:text-left">
                  <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                    Delete Form
                  </Dialog.Title>
                  <div className="mt-2">
                    <p className="text-sm text-gray-500">
                      Are you sure you want to delete this form? This action cannot be undone.
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
                  onClick={() => setShowDeleteConfirm(false)}
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