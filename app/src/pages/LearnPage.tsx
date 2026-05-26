import { Video } from 'lucide-react'

export function LearnPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-secondary-900">Learn from Videos</h2>
        <p className="text-secondary-500 mt-1">
          Analyze YouTube tutorials and extract production patterns
        </p>
      </div>

      <div className="p-6 rounded-xl border border-secondary-200">
        <div className="flex flex-col items-center justify-center py-12 text-secondary-400">
          <Video className="w-16 h-16 mb-3" />
          <p className="text-lg font-medium text-secondary-600">Video Analysis</p>
          <p className="text-sm mt-1">Coming soon — paste a YouTube URL to analyze production techniques</p>
        </div>
      </div>
    </div>
  )
}
