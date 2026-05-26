import React from 'react'
import { Music, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'

export function HomePage() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-12">
        <div className="flex justify-center mb-4">
          <div className="p-4 bg-purple-100 rounded-full">
            <Music className="w-12 h-12 text-purple-600" />
          </div>
        </div>
        <h2 className="text-3xl font-bold text-secondary-900 mb-3">
          AI-Powered Music Producer
        </h2>
        <p className="text-secondary-600 max-w-md mx-auto">
          Generate LoFi, Hyper Pop, and more with AI. Learn from tutorials and create unique tracks.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/generate"
          className="p-6 rounded-xl border border-secondary-200 hover:border-purple-300 hover:shadow-md transition-all group"
        >
          <Sparkles className="w-8 h-8 text-purple-500 mb-3" />
          <h3 className="font-semibold text-secondary-900 mb-1">Generate Music</h3>
          <p className="text-sm text-secondary-500">
            Create LoFi beats, Hyper Pop tracks, and more using AI
          </p>
        </Link>

        <Link
          to="/learn"
          className="p-6 rounded-xl border border-secondary-200 hover:border-blue-300 hover:shadow-md transition-all group"
        >
          <Music className="w-8 h-8 text-blue-500 mb-3" />
          <h3 className="font-semibold text-secondary-900 mb-1">Learn from Videos</h3>
          <p className="text-sm text-secondary-500">
            Analyze YouTube tutorials and learn production patterns
          </p>
        </Link>

        <Link
          to="/dashboard"
          className="p-6 rounded-xl border border-secondary-200 hover:border-green-300 hover:shadow-md transition-all group"
        >
          <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center mb-3">
            <span className="text-green-600 text-lg">📊</span>
          </div>
          <h3 className="font-semibold text-secondary-900 mb-1">Dashboard</h3>
          <p className="text-sm text-secondary-500">
            View your generated tracks and learning progress
          </p>
        </Link>
      </div>
    </div>
  )
}
