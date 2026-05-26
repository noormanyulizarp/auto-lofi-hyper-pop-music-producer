import React, { useState } from 'react'
import { Music, Loader2 } from 'lucide-react'

interface GenerationParams {
  genre: string
  mood: string
  tempo: number
  duration: number
}

export function GeneratePage() {
  const [params, setParams] = useState<GenerationParams>({
    genre: 'lofi',
    mood: 'chill',
    tempo: 85,
    duration: 30,
  })
  const [generating, setGenerating] = useState(false)
  const [result, setResult] = useState<string | null>(null)

  const genres = ['lofi', 'hyper-pop', 'ambient', 'synthwave', 'trap']
  const moods = ['chill', 'energetic', 'melancholic', 'upbeat', 'dark']

  const handleGenerate = async () => {
    setGenerating(true)
    setResult(null)
    try {
      // TODO: Connect to actual AI service
      await new Promise((r) => setTimeout(r, 2000))
      setResult('Music generation will connect to HeartMuLa AI service.')
    } catch (err) {
      setResult('Error generating music. Please try again.')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-secondary-900">Generate Music</h2>
        <p className="text-secondary-500 mt-1">Create AI-powered tracks in any style</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Generation Form */}
        <div className="p-6 rounded-xl border border-secondary-200 space-y-5">
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">Genre</label>
            <div className="flex flex-wrap gap-2">
              {genres.map((g) => (
                <button
                  key={g}
                  onClick={() => setParams({ ...params, genre: g })}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    params.genre === g
                      ? 'bg-purple-600 text-white'
                      : 'bg-secondary-100 text-secondary-600 hover:bg-secondary-200'
                  }`}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">Mood</label>
            <div className="flex flex-wrap gap-2">
              {moods.map((m) => (
                <button
                  key={m}
                  onClick={() => setParams({ ...params, mood: m })}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    params.mood === m
                      ? 'bg-purple-600 text-white'
                      : 'bg-secondary-100 text-secondary-600 hover:bg-secondary-200'
                  }`}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Tempo: {params.tempo} BPM
            </label>
            <input
              type="range"
              min={60}
              max={180}
              value={params.tempo}
              onChange={(e) => setParams({ ...params, tempo: Number(e.target.value) })}
              className="w-full accent-purple-600"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Duration: {params.duration}s
            </label>
            <input
              type="range"
              min={10}
              max={120}
              value={params.duration}
              onChange={(e) => setParams({ ...params, duration: Number(e.target.value) })}
              className="w-full accent-purple-600"
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={generating}
            className="w-full py-3 px-4 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {generating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Music className="w-5 h-5" />
                Generate Track
              </>
            )}
          </button>
        </div>

        {/* Result / Preview */}
        <div className="p-6 rounded-xl border border-secondary-200">
          <h3 className="font-semibold text-secondary-900 mb-4">Preview</h3>
          {result ? (
            <div className="text-secondary-600">{result}</div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-secondary-400">
              <Music className="w-16 h-16 mb-3" />
              <p>Configure settings and generate a track</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
