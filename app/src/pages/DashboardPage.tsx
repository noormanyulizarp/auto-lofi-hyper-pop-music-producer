import { BarChart3 } from 'lucide-react'

export function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-secondary-900">Dashboard</h2>
        <p className="text-secondary-500 mt-1">Your music generation history and stats</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl border border-secondary-200">
          <p className="text-sm text-secondary-500">Tracks Generated</p>
          <p className="text-2xl font-bold text-secondary-900 mt-1">0</p>
        </div>
        <div className="p-4 rounded-xl border border-secondary-200">
          <p className="text-sm text-secondary-500">Total Duration</p>
          <p className="text-2xl font-bold text-secondary-900 mt-1">0m</p>
        </div>
        <div className="p-4 rounded-xl border border-secondary-200">
          <p className="text-sm text-secondary-500">Videos Analyzed</p>
          <p className="text-2xl font-bold text-secondary-900 mt-1">0</p>
        </div>
      </div>

      {/* Recent Tracks */}
      <div className="p-6 rounded-xl border border-secondary-200">
        <div className="flex flex-col items-center justify-center py-8 text-secondary-400">
          <BarChart3 className="w-16 h-16 mb-3" />
          <p>No tracks generated yet. Start creating!</p>
        </div>
      </div>
    </div>
  )
}
