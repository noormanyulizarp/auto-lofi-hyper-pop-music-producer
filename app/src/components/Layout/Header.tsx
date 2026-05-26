import { Music, Menu } from 'lucide-react'

interface HeaderProps {
  onToggleSidebar?: () => void
}

export function Header({ onToggleSidebar }: HeaderProps) {
  return (
    <header className="h-16 border-b border-secondary-200 bg-white px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-2 hover:bg-secondary-100 rounded-lg"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-2">
          <Music className="w-6 h-6 text-purple-600" />
          <h1 className="text-lg font-bold text-secondary-900">
            Auto LoFi & Hyper Pop Producer
          </h1>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-secondary-500">v0.1.0</span>
      </div>
    </header>
  )
}
