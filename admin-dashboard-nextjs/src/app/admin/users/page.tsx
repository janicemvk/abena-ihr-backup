'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Dialog } from '@headlessui/react'
import { 
  PlusIcon,
  PencilIcon,
  TrashIcon,
  ArrowLeftIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import { userService, AdminUser } from '@/lib/services/userService'
import { handleApiError, showError, showSuccess } from '@/lib/utils/errorHandler'

interface User extends AdminUser {
  name?: string
  officeNumber?: string
}

const roles = ['admin', 'super_admin', 'billing_admin', 'coding_admin']

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [showPasswordReset, setShowPasswordReset] = useState(false)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [newUser, setNewUser] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'admin',
    status: 'active',
    telephone: '',
    pager: '',
    office_number: ''
  })
  const [editUser, setEditUser] = useState({
    email: '',
    first_name: '',
    last_name: '',
    role: 'admin',
    status: 'active',
    telephone: '',
    pager: '',
    office_number: ''
  })
  const [newPassword, setNewPassword] = useState('')

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    setLoading(true)
    try {
      const response = await userService.getAll()
      if (response.success && response.users) {
        // Map API users to component format
        const mappedUsers: User[] = response.users.map(user => ({
          ...user,
          name: `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.email,
          officeNumber: user.office_number
        }))
        setUsers(mappedUsers)
      }
    } catch (error) {
      const errorMessage = handleApiError(error, 'Failed to load users')
      showError(errorMessage)
      setUsers([])
    } finally {
      setLoading(false)
    }
  }

  const handleAddUser = async () => {
    if (!newUser.email || !newUser.password) {
      showError('Email and password are required')
      return
    }

    try {
      const response = await userService.create(newUser)
      if (response.success) {
        showSuccess('User created successfully')
        await loadUsers()
        setShowAddModal(false)
        setNewUser({
          email: '',
          password: '',
          first_name: '',
          last_name: '',
          role: 'admin',
          status: 'active',
          telephone: '',
          pager: '',
          office_number: ''
        })
      } else {
        showError(response.error || 'Failed to create user')
      }
    } catch (error) {
      const errorMessage = handleApiError(error, 'Failed to create user')
      showError(errorMessage)
    }
  }

  const handleEditClick = (user: User) => {
    setSelectedUser(user)
    setEditUser({
      email: user.email,
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      role: user.role,
      status: user.status,
      telephone: user.telephone || '',
      pager: user.pager || '',
      office_number: user.office_number || ''
    })
    setShowEditModal(true)
  }

  const handleEditSave = async () => {
    if (!selectedUser) return

    try {
      const response = await userService.update(selectedUser.user_id, editUser)
      if (response.success) {
        showSuccess('User updated successfully')
        await loadUsers()
        setShowEditModal(false)
        setSelectedUser(null)
      } else {
        showError(response.error || 'Failed to update user')
      }
    } catch (error) {
      const errorMessage = handleApiError(error, 'Failed to update user')
      showError(errorMessage)
    }
  }

  const handleDeleteClick = (user: User) => {
    setSelectedUser(user)
    setShowDeleteConfirm(true)
  }

  const handleDelete = async () => {
    if (!selectedUser) return

    try {
      const response = await userService.delete(selectedUser.user_id)
      if (response.success) {
        showSuccess('User deactivated successfully')
        await loadUsers()
        setShowDeleteConfirm(false)
        setSelectedUser(null)
      } else {
        showError(response.error || 'Failed to delete user')
      }
    } catch (error) {
      const errorMessage = handleApiError(error, 'Failed to delete user')
      showError(errorMessage)
    }
  }

  const handlePasswordReset = async () => {
    if (!selectedUser || !newPassword) {
      showError('Please enter a new password')
      return
    }

    if (newPassword.length < 8) {
      showError('Password must be at least 8 characters long')
      return
    }

    try {
      const response = await userService.resetPassword(selectedUser.user_id, newPassword)
      if (response.success) {
        showSuccess('Password reset successfully')
        setShowPasswordReset(false)
        setNewPassword('')
        setSelectedUser(null)
      } else {
        showError(response.error || 'Failed to reset password')
      }
    } catch (error) {
      const errorMessage = handleApiError(error, 'Failed to reset password')
      showError(errorMessage)
    }
  }

  const toggleStatus = async (user: User) => {
    try {
      const newStatus = user.status === 'active' ? 'inactive' : 'active'
      const response = await userService.update(user.user_id, { status: newStatus })
      if (response.success) {
        showSuccess(`User ${newStatus === 'active' ? 'activated' : 'deactivated'} successfully`)
        await loadUsers()
      } else {
        showError(response.error || 'Failed to update user status')
      }
    } catch (error) {
      const errorMessage = handleApiError(error, 'Failed to update user status')
      showError(errorMessage)
    }
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
              <h1 className="text-3xl font-bold tracking-tight text-gray-900">User Management</h1>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              Add User
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
        {loading ? (
          <div className="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-lg p-8 text-center text-gray-500">
            Loading users...
          </div>
        ) : (
        <div className="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-lg">
          <table className="min-w-full divide-y divide-gray-300">
            <thead>
              <tr>
                <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                  Name
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Email
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Telephone
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Pager
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Office
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Role
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Status
                </th>
                <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {users.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-8 text-center text-gray-500">
                    No users found
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.user_id}>
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                      {user.name || user.email}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{user.email}</td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{user.telephone || '-'}</td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{user.pager || '-'}</td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{user.officeNumber || user.office_number || '-'}</td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                        {user.role}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                      <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                        user.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {user.status}
                      </span>
                    </td>
                    <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6 flex justify-end items-center space-x-2">
                      <div 
                        className="group relative inline-block"
                        onClick={() => handleEditClick(user)}
                      >
                        <button
                          type="button"
                          className="inline-flex items-center p-2 text-indigo-600 hover:text-indigo-900 bg-indigo-50 rounded-full cursor-pointer"
                        >
                          <PencilIcon className="h-5 w-5" />
                        </button>
                        <span className="absolute bottom-full left-1/2 -translate-x-1/2 bg-gray-900 text-white px-2 py-1 text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity">
                          Edit user
                        </span>
                      </div>
                      <div 
                        className="group relative inline-block"
                        onClick={() => handleDeleteClick(user)}
                      >
                        <button
                          type="button"
                          className="inline-flex items-center p-2 text-red-600 hover:text-red-900 bg-red-50 rounded-full cursor-pointer"
                        >
                          <TrashIcon className="h-5 w-5" />
                        </button>
                        <span className="absolute bottom-full left-1/2 -translate-x-1/2 bg-gray-900 text-white px-2 py-1 text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity">
                          Delete user
                        </span>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        )}
      </main>

      {/* Add User Modal */}
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
                    Add New User
                  </Dialog.Title>
                  <div className="mt-6 space-y-6">
                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                        Email *
                      </label>
                      <input
                        type="email"
                        name="email"
                        id="email"
                        required
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newUser.email}
                        onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                      />
                    </div>
                    <div>
                      <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                        Password *
                      </label>
                      <input
                        type="password"
                        name="password"
                        id="password"
                        required
                        minLength={8}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newUser.password}
                        onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                        placeholder="Minimum 8 characters"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label htmlFor="first_name" className="block text-sm font-medium text-gray-700">
                          First Name
                        </label>
                        <input
                          type="text"
                          name="first_name"
                          id="first_name"
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          value={newUser.first_name}
                          onChange={(e) => setNewUser({ ...newUser, first_name: e.target.value })}
                        />
                      </div>
                      <div>
                        <label htmlFor="last_name" className="block text-sm font-medium text-gray-700">
                          Last Name
                        </label>
                        <input
                          type="text"
                          name="last_name"
                          id="last_name"
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          value={newUser.last_name}
                          onChange={(e) => setNewUser({ ...newUser, last_name: e.target.value })}
                        />
                      </div>
                    </div>
                    <div>
                      <label htmlFor="telephone" className="block text-sm font-medium text-gray-700">
                        Telephone Number
                      </label>
                      <input
                        type="tel"
                        name="telephone"
                        id="telephone"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newUser.telephone}
                        onChange={(e) => setNewUser({ ...newUser, telephone: e.target.value })}
                        placeholder="(123) 456-7890"
                      />
                    </div>
                    <div>
                      <label htmlFor="pager" className="block text-sm font-medium text-gray-700">
                        Pager Number
                      </label>
                      <input
                        type="tel"
                        name="pager"
                        id="pager"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newUser.pager}
                        onChange={(e) => setNewUser({ ...newUser, pager: e.target.value })}
                        placeholder="(123) 456-7890"
                      />
                    </div>
                    <div>
                      <label htmlFor="office_number" className="block text-sm font-medium text-gray-700">
                        Office Number
                      </label>
                      <input
                        type="text"
                        name="office_number"
                        id="office_number"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newUser.office_number}
                        onChange={(e) => setNewUser({ ...newUser, office_number: e.target.value })}
                        placeholder="Room 123"
                      />
                    </div>
                    <div>
                      <label htmlFor="role" className="block text-sm font-medium text-gray-700">
                        Role
                      </label>
                      <select
                        id="role"
                        name="role"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={newUser.role}
                        onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                      >
                        {roles.map((role) => (
                          <option key={role} value={role}>
                            {role}
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
                  onClick={handleAddUser}
                >
                  Add User
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

      {/* Edit User Modal */}
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
              <div className="sm:flex sm:items-start">
                <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                    Edit User
                  </Dialog.Title>
                  <div className="mt-6 space-y-6">
                    <div>
                      <label htmlFor="edit-email" className="block text-sm font-medium text-gray-700">
                        Email
                      </label>
                      <input
                        type="email"
                        name="edit-email"
                        id="edit-email"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={editUser.email}
                        onChange={(e) => setEditUser({ ...editUser, email: e.target.value })}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label htmlFor="edit-first_name" className="block text-sm font-medium text-gray-700">
                          First Name
                        </label>
                        <input
                          type="text"
                          name="edit-first_name"
                          id="edit-first_name"
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          value={editUser.first_name}
                          onChange={(e) => setEditUser({ ...editUser, first_name: e.target.value })}
                        />
                      </div>
                      <div>
                        <label htmlFor="edit-last_name" className="block text-sm font-medium text-gray-700">
                          Last Name
                        </label>
                        <input
                          type="text"
                          name="edit-last_name"
                          id="edit-last_name"
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          value={editUser.last_name}
                          onChange={(e) => setEditUser({ ...editUser, last_name: e.target.value })}
                        />
                      </div>
                    </div>
                    <div>
                      <label htmlFor="edit-telephone" className="block text-sm font-medium text-gray-700">
                        Telephone
                      </label>
                      <input
                        type="tel"
                        name="edit-telephone"
                        id="edit-telephone"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={editUser.telephone}
                        onChange={(e) => setEditUser({ ...editUser, telephone: e.target.value })}
                      />
                    </div>
                    <div>
                      <label htmlFor="edit-pager" className="block text-sm font-medium text-gray-700">
                        Pager
                      </label>
                      <input
                        type="tel"
                        name="edit-pager"
                        id="edit-pager"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={editUser.pager}
                        onChange={(e) => setEditUser({ ...editUser, pager: e.target.value })}
                      />
                    </div>
                    <div>
                      <label htmlFor="edit-office_number" className="block text-sm font-medium text-gray-700">
                        Office Number
                      </label>
                      <input
                        type="text"
                        name="edit-office_number"
                        id="edit-office_number"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={editUser.office_number}
                        onChange={(e) => setEditUser({ ...editUser, office_number: e.target.value })}
                      />
                    </div>
                    <div>
                      <label htmlFor="edit-role" className="block text-sm font-medium text-gray-700">
                        Role
                      </label>
                      <select
                        id="edit-role"
                        name="edit-role"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={editUser.role}
                        onChange={(e) => setEditUser({ ...editUser, role: e.target.value })}
                      >
                        {roles.map((role) => (
                          <option key={role} value={role}>
                            {role}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label htmlFor="edit-status" className="block text-sm font-medium text-gray-700">
                        Status
                      </label>
                      <select
                        id="edit-status"
                        name="edit-status"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        value={editUser.status}
                        onChange={(e) => setEditUser({ ...editUser, status: e.target.value })}
                      >
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                        <option value="suspended">Suspended</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
              <div className="mt-8 sm:flex sm:flex-row-reverse">
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
              <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                <button
                  type="button"
                  className="rounded-md bg-white text-gray-400 hover:text-gray-500"
                  onClick={() => setShowDeleteConfirm(false)}
                >
                  <span className="sr-only">Close</span>
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              <div className="sm:flex sm:items-start">
                <div className="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                  <TrashIcon className="h-6 w-6 text-red-600" aria-hidden="true" />
                </div>
                <div className="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                  <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                    Delete User
                  </Dialog.Title>
                  <div className="mt-2">
                    <p className="text-sm text-gray-500">
                      Are you sure you want to delete <strong>{selectedUser?.email || selectedUser?.name || 'this user'}</strong>? This action cannot be undone.
                    </p>
                  </div>
                </div>
              </div>
              <div className="mt-8 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:ml-3 sm:w-auto"
                  onClick={handleDelete}
                >
                  Delete User
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