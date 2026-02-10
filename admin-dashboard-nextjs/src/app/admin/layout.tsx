'use client'

import { Fragment, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Dialog, Transition } from '@headlessui/react'
import {
  Bars3Icon,
  XMarkIcon,
  UserGroupIcon,
  Cog6ToothIcon,
  ChartBarIcon,
  CalendarIcon,
  BanknotesIcon,
  ChatBubbleLeftRightIcon,
  StarIcon,
  ArrowRightOnRectangleIcon,
  DocumentTextIcon,
  ShieldCheckIcon,
  BellIcon,
  UserIcon,
  ClipboardDocumentCheckIcon,
  CpuChipIcon,
} from '@heroicons/react/24/outline'
import { signOut } from 'next-auth/react'

const navigation = [
  { name: 'Dashboard', href: '/admin', icon: ChartBarIcon },
  { name: 'Users', href: '/admin/users', icon: UserGroupIcon },
  { name: 'Appointments', href: '/admin/appointments', icon: CalendarIcon },
  { name: 'Clinical Notes', href: '/admin/clinical-notes', icon: DocumentTextIcon },
  { name: 'Treatment Plans', href: '/admin/treatment-plans', icon: DocumentTextIcon },
  { name: 'Quantum Analysis', href: '/admin/quantum-analysis', icon: CpuChipIcon },
  { name: 'Billing', href: '/admin/billing', icon: BanknotesIcon },
  { name: 'Medical Coding', href: '/admin/medical-coding', icon: ClipboardDocumentCheckIcon },
  { name: 'Analytics', href: '/admin/analytics', icon: ChartBarIcon },
  { name: 'Communications', href: '/admin/communications', icon: ChatBubbleLeftRightIcon },
  { name: 'Feedback', href: '/admin/feedback', icon: StarIcon },
  { name: 'Settings', href: '/admin/config', icon: Cog6ToothIcon },
]

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const pathname = usePathname()

  return (
    <div className="min-h-screen bg-clinical-bg">
      {/* Mobile sidebar backdrop */}
      <Transition.Root show={sidebarOpen} as={Fragment}>
        <Dialog as="div" className="relative z-50 lg:hidden" onClose={setSidebarOpen}>
          <Transition.Child
            as={Fragment}
            enter="transition-opacity ease-linear duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity ease-linear duration-300"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-50" />
          </Transition.Child>

          <div className="fixed inset-0 flex">
            <Transition.Child
              as={Fragment}
              enter="transition ease-in-out duration-300 transform"
              enterFrom="-translate-x-full"
              enterTo="translate-x-0"
              leave="transition ease-in-out duration-300 transform"
              leaveFrom="translate-x-0"
              leaveTo="-translate-x-full"
            >
              <Dialog.Panel className="relative mr-16 flex w-full max-w-xs flex-1">
                <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4 shadow-xl">
                  {/* Logo and brand */}
                  <div className="flex h-16 shrink-0 items-center justify-between border-b border-clinical-border">
                    <Link
                      href="/admin"
                      onClick={() => setSidebarOpen(false)}
                      className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
                    >
                      <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                        <ShieldCheckIcon className="h-8 w-8 text-white" />
                      </div>
                      <div>
                        <h1 className="text-xl font-bold text-gray-900">Abena IHR</h1>
                        <p className="text-xs text-gray-600">Admin Portal</p>
                      </div>
                    </Link>
                    <button
                      onClick={() => setSidebarOpen(false)}
                      className="p-2 rounded-lg hover:bg-gray-100"
                    >
                      <XMarkIcon className="h-5 w-5 text-gray-600" />
                    </button>
                  </div>

                  {/* System Status */}
                  <div className="border-b border-clinical-border pb-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-sm font-medium text-gray-900">System Status</h3>
                      <div className="h-2 w-2 bg-green-500 rounded-full" />
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Services</span>
                        <span className="text-green-600 font-medium">Online</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Database</span>
                        <span className="text-green-600 font-medium">Connected</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">API Gateway</span>
                        <span className="text-green-600 font-medium">Active</span>
                      </div>
                    </div>
                  </div>

                  {/* Navigation */}
                  <nav className="flex-1">
                    <ul role="list" className="space-y-1">
                      {navigation.map((item) => {
                        const isActive = pathname === item.href
                        const IconComponent = item.icon
                        return (
                          <li key={item.name}>
                            <Link
                              href={item.href}
                              onClick={() => setSidebarOpen(false)}
                              className={`
                                flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors
                                ${isActive
                                  ? 'bg-ecbome-primary text-white'
                                  : 'text-gray-700 hover:bg-gray-100'
                                }
                              `}
                            >
                              {IconComponent && <IconComponent className="h-5 w-5 mr-3" />}
                              {item.name}
                            </Link>
                          </li>
                        )
                      })}
                    </ul>
                  </nav>

                  {/* Quick Stats */}
                  <div className="border-t border-clinical-border pt-4">
                    <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Stats</h3>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-ecbome-primary">0</div>
                        <div className="text-xs text-gray-600">Users</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">100%</div>
                        <div className="text-xs text-gray-600">Uptime</div>
                      </div>
                    </div>
                  </div>

                  {/* Logout */}
                  <div className="border-t border-clinical-border pt-4">
                    <button
                      onClick={() => {
                        signOut({ callbackUrl: '/login' })
                        setSidebarOpen(false)
                      }}
                      className="flex items-center w-full px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg"
                    >
                      <ArrowRightOnRectangleIcon className="h-5 w-5 mr-3" />
                      Sign Out
                    </button>
                  </div>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </Dialog>
      </Transition.Root>

      {/* Static sidebar for desktop */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-80 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto border-r border-clinical-border bg-white px-6 pb-4 shadow-sm">
          {/* Logo and brand */}
          <div className="flex h-16 shrink-0 items-center border-b border-clinical-border">
            <Link
              href="/admin"
              className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
            >
              <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                <ShieldCheckIcon className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Abena IHR</h1>
                <p className="text-xs text-gray-600">Admin Portal</p>
              </div>
            </Link>
          </div>

          {/* System Status */}
          <div className="border-b border-clinical-border pb-4 pt-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-900">System Status</h3>
              <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Services</span>
                <span className="text-green-600 font-medium">Online</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Database</span>
                <span className="text-green-600 font-medium">Connected</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">API Gateway</span>
                <span className="text-green-600 font-medium">Active</span>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 pt-4">
            <ul role="list" className="space-y-1">
              {navigation.map((item) => {
                const isActive = pathname === item.href
                const IconComponent = item.icon
                return (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className={`
                        flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors
                        ${isActive
                          ? 'bg-ecbome-primary text-white'
                          : 'text-gray-700 hover:bg-gray-100'
                        }
                      `}
                    >
                      {IconComponent && <IconComponent className="h-5 w-5 mr-3" />}
                      {item.name}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </nav>

          {/* Quick Stats */}
          <div className="border-t border-clinical-border pt-4">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Stats</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="text-center">
                <div className="text-2xl font-bold text-ecbome-primary">0</div>
                <div className="text-xs text-gray-600">Users</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">100%</div>
                <div className="text-xs text-gray-600">Uptime</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">0</div>
                <div className="text-xs text-gray-600">Alerts</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">0</div>
                <div className="text-xs text-gray-600">Records</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-80">
        {/* Top header */}
        <header className="bg-white shadow-sm border-b border-clinical-border sticky top-0 z-30">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              {/* Mobile menu button */}
              <button
                type="button"
                className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
                onClick={() => setSidebarOpen(true)}
              >
                <Bars3Icon className="h-5 w-5 text-gray-600" />
              </button>

              {/* Page title and status */}
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <ShieldCheckIcon className="h-5 w-5 text-ecbome-primary" />
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    Admin Portal
                  </span>
                </div>
              </div>

              {/* Header actions */}
              <div className="flex items-center space-x-4">
                {/* Real-time indicator */}
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
                  <span className="hidden sm:inline">Live</span>
                </div>

                {/* Notifications */}
                <div className="relative">
                  <button className="p-2 text-gray-400 hover:text-gray-600 relative">
                    <BellIcon className="h-5 w-5" />
                  </button>
                </div>

                {/* User menu */}
                <div className="relative">
                  <button
                    onClick={() => setUserMenuOpen(!userMenuOpen)}
                    className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100"
                  >
                    <div className="h-8 w-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <UserIcon className="h-4 w-4 text-white" />
                    </div>
                    <span className="hidden sm:inline text-sm font-medium text-gray-700">
                      Admin
                    </span>
                  </button>

                  {/* User dropdown */}
                  {userMenuOpen && (
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-clinical-border z-50">
                      <div className="p-3 border-b border-clinical-border">
                        <p className="text-sm font-medium text-gray-900">Administrator</p>
                        <p className="text-xs text-gray-600">admin@abena-ihr.com</p>
                      </div>
                      <div className="p-2">
                        <button
                          onClick={() => {
                            signOut({ callbackUrl: '/login' })
                            setUserMenuOpen(false)
                          }}
                          className="flex items-center w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
                        >
                          <ArrowRightOnRectangleIcon className="h-4 w-4 mr-2" />
                          Sign Out
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main content area */}
        <main className="min-h-screen">
          {children}
        </main>
      </div>
    </div>
  )
}
