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
} from '@heroicons/react/24/outline'
import { clinicalNotesService, ClinicalNote } from '@/lib/services/clinicalNotesService'
import { format } from 'date-fns'
import { getPatientNames } from '@/lib/utils/patientResolver'

interface ClinicalNoteWithName extends ClinicalNote {
  patientName?: string
}

export default function ClinicalNotesPage() {
  const [notes, setNotes] = useState<ClinicalNoteWithName[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [selectedNote, setSelectedNote] = useState<ClinicalNote | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [newNote, setNewNote] = useState({
    patient_id: '',
    title: '',
    content: '',
    note_type: 'general',
    tags: [] as string[],
    is_important: false
  })

  useEffect(() => {
    loadNotes()
  }, [])

  const loadNotes = async () => {
    setLoading(true)
    try {
      const response = await clinicalNotesService.getAll()
      if (response.success && response.clinical_notes) {
        // Resolve patient names
        const patientIds = Array.from(new Set(response.clinical_notes.map(note => note.patient_id)))
        const patientNames = await getPatientNames(patientIds)
        
        // Add patient names to notes
        const notesWithNames: ClinicalNoteWithName[] = response.clinical_notes.map(note => ({
          ...note,
          patientName: patientNames.get(note.patient_id) || note.patient_id.substring(0, 8) + '...'
        }))
        
        setNotes(notesWithNames)
      }
    } catch (error) {
      console.error('Failed to load clinical notes:', error)
      setNotes([])
    } finally {
      setLoading(false)
    }
  }

  const handleAddNote = async () => {
    try {
      const response = await clinicalNotesService.create(newNote)
      if (response.success) {
        await loadNotes()
        setShowAddModal(false)
        setNewNote({
          patient_id: '',
          title: '',
          content: '',
          note_type: 'general',
          tags: [],
          is_important: false
        })
      }
    } catch (error) {
      console.error('Failed to create note:', error)
      alert('Failed to create note. Please try again.')
    }
  }

  const handleEditSave = async () => {
    if (!selectedNote) return

    try {
      const updateData = {
        title: selectedNote.title,
        content: selectedNote.content,
        note_type: selectedNote.note_type,
        tags: Array.isArray(selectedNote.tags) ? selectedNote.tags : [],
        is_important: selectedNote.is_important
      }

      const response = await clinicalNotesService.update(selectedNote.note_id, updateData)
      if (response.success) {
        await loadNotes()
        setShowEditModal(false)
        setSelectedNote(null)
      }
    } catch (error) {
      console.error('Failed to update note:', error)
      alert('Failed to update note. Please try again.')
    }
  }

  const handleDelete = async () => {
    if (!selectedNote) return

    try {
      const response = await clinicalNotesService.delete(selectedNote.note_id)
      if (response.success) {
        await loadNotes()
        setShowDeleteModal(false)
        setSelectedNote(null)
      }
    } catch (error) {
      console.error('Failed to delete note:', error)
      alert('Failed to delete note. Please try again.')
    }
  }

  const filteredNotes = notes.filter(note => {
    const searchLower = searchTerm.toLowerCase()
    return (
      (note.title?.toLowerCase() || '').includes(searchLower) ||
      (note.content?.toLowerCase() || '').includes(searchLower) ||
      (note.patient_id?.toLowerCase() || '').includes(searchLower) ||
      (note.patientName?.toLowerCase() || '').includes(searchLower)
    )
  });

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
              <h1 className="text-3xl font-bold tracking-tight text-gray-900">Clinical Notes Management</h1>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
            >
              <PlusIcon className="h-5 w-5" />
              Add Note
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
              placeholder="Search notes by title, content, or patient ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full rounded-md border-gray-300 pl-10 pr-4 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
        </div>

        {/* Notes List */}
        <div className="bg-white shadow rounded-lg">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading notes...</div>
          ) : filteredNotes.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <DocumentTextIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No clinical notes found</p>
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {filteredNotes.map((note) => (
                <li key={note.note_id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{note.title}</h3>
                        {note.is_important && (
                          <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
                            Important
                          </span>
                        )}
                        <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                          {note.note_type}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{note.content}</p>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span>{note.patientName || `Patient ID: ${note.patient_id.substring(0, 8)}...`}</span>
                        <span>Created: {format(new Date(note.created_at), 'MMM d, yyyy')}</span>
                        {Array.isArray(note.tags) && note.tags.length > 0 && (
                          <span>Tags: {note.tags.join(', ')}</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => {
                          setSelectedNote(note)
                          setShowEditModal(true)
                        }}
                        className="p-2 text-blue-600 hover:bg-blue-100 rounded"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => {
                          setSelectedNote(note)
                          setShowDeleteModal(true)
                        }}
                        className="p-2 text-red-600 hover:bg-red-100 rounded"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>

      {/* Add Note Modal */}
      <Dialog open={showAddModal} onClose={() => setShowAddModal(false)}>
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" />
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div className="absolute right-0 top-0 pr-4 pt-4">
                <button onClick={() => setShowAddModal(false)}>
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              <h3 className="text-lg font-semibold mb-4">Add Clinical Note</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Patient ID (UUID) *</label>
                  <input
                    type="text"
                    required
                    value={newNote.patient_id}
                    onChange={(e) => setNewNote({ ...newNote, patient_id: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="00000000-0000-0000-0000-000000000000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Title *</label>
                  <input
                    type="text"
                    required
                    value={newNote.title}
                    onChange={(e) => setNewNote({ ...newNote, title: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Content *</label>
                  <textarea
                    required
                    rows={4}
                    value={newNote.content}
                    onChange={(e) => setNewNote({ ...newNote, content: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Note Type</label>
                  <select
                    value={newNote.note_type}
                    onChange={(e) => setNewNote({ ...newNote, note_type: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  >
                    <option value="general">General</option>
                    <option value="assessment">Assessment</option>
                    <option value="treatment">Treatment</option>
                    <option value="follow_up">Follow-up</option>
                  </select>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newNote.is_important}
                    onChange={(e) => setNewNote({ ...newNote, is_important: e.target.checked })}
                    className="rounded"
                  />
                  <label className="ml-2 text-sm text-gray-700">Mark as important</label>
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
                  onClick={handleAddNote}
                  className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
                >
                  Create Note
                </button>
              </div>
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>

      {/* Edit Note Modal */}
      <Dialog open={showEditModal} onClose={() => setShowEditModal(false)}>
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" />
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div className="absolute right-0 top-0 pr-4 pt-4">
                <button onClick={() => setShowEditModal(false)}>
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              {selectedNote && (
                <>
                  <h3 className="text-lg font-semibold mb-4">Edit Clinical Note</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Title *</label>
                      <input
                        type="text"
                        required
                        value={selectedNote.title}
                        onChange={(e) => setSelectedNote({ ...selectedNote, title: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Content *</label>
                      <textarea
                        required
                        rows={4}
                        value={selectedNote.content}
                        onChange={(e) => setSelectedNote({ ...selectedNote, content: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Note Type</label>
                      <select
                        value={selectedNote.note_type}
                        onChange={(e) => setSelectedNote({ ...selectedNote, note_type: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                      >
                        <option value="general">General</option>
                        <option value="assessment">Assessment</option>
                        <option value="treatment">Treatment</option>
                        <option value="follow_up">Follow-up</option>
                      </select>
                    </div>
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedNote.is_important}
                        onChange={(e) => setSelectedNote({ ...selectedNote, is_important: e.target.checked })}
                        className="rounded"
                      />
                      <label className="ml-2 text-sm text-gray-700">Mark as important</label>
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
              <h3 className="text-lg font-semibold mb-2">Delete Clinical Note</h3>
              <p className="text-sm text-gray-500 mb-6">
                Are you sure you want to delete this note? This action cannot be undone.
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


