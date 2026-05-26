import { Home, Music, BookOpen, BarChart3, Cpu } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', icon: Home, label: 'Home' },
  { to: '/generate', icon: Music, label: 'Generate' },
  { to: '/learn', icon: BookOpen, label: 'Learn' },
  { to: '/dashboard', icon: BarChart3, label: 'Dashboard' },
  { to: '/providers', icon: Cpu, label: 'Providers' },
]

export function Sidebar() {
  return (
    <aside className="hidden lg:flex lg:w-64 lg:flex-col lg:border-r border-secondary-200 bg-white">
      <div className="p-6">
        <nav className="space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-purple-100 text-purple-700'
                    : 'text-secondary-600 hover:bg-secondary-100'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
    </aside>
  )
}
