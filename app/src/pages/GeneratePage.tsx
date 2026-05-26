import { useState, useEffect, useCallback } from 'react'
import { Music, Loader2, CheckCircle, XCircle, Volume2 } from 'lucide-react'
import { musicApi, type GenerateRequest, type GenerateResponse } from '../api/client'
import { useGenerationStore } from '../store/generationStore'

const GENRES = ['lofi', 'hyper-pop', 'ambient', 'synthwave', 'trap', 'chillhop', 'vaporwave'] as const
const MOODS = ['chill', 'energetic', 'melancholic', 'upbeat', 'dark', 'dreamy'] as const

export function GeneratePage() {
  const [genre, setGenre] = useState<string>('lofi')
  const [mood, setMood] = useState<string>('chill')
  const [tempo, setTempo] = useState(85)
  const [duration, setDuration] = useState(30)
  const [title, setTitle] = useState('Untitled Track')

  const { taskId, status, progress, error, audioUrl, isGenerating, startGeneration, updateProgress, setComplete, setError, reset } = useGenerationStore()

  // Poll task status while generating
  useEffect(() => {
    if (!taskId || !isGenerating) return
    const interval = setInterval(async () => {
      try {
        const result = await musicApi.getStatus(taskId)
        updateProgress(result.status, result.progress)

        if (result.status === 'completed' && result.audio_url) {
          setComplete(result.audio_url)
        } else if (result.status === 'failed') {
          setError(result.message || 'Generation failed')
        }
      } catch {
        // Silent retry
      }
    }, 3000)
    return () => clearInterval(interval)
  }, [taskId, isGenerating, updateProgress, setComplete, setError])

  const handleGenerate = async () => {
    reset()
    try {
      const request: GenerateRequest = { title, genre, mood, duration, tempo }
      const response: GenerateResponse = await musicApi.generate(request)
      startGeneration(response.task_id)
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Generation failed')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-secondary-900">Generate Music</h2>
        <p className="text-secondary-500 mt-1">Create AI-powered tracks in any style</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <div className="p-6 rounded-xl border border-secondary-200 space-y-5">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">Track Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter track title..."
              className="w-full px-3 py-2 border border-secondary-200 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          {/* Genre */}
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">Genre</label>
            <div className="flex flex-wrap gap-2">
              {GENRES.map((g) => (
                <button
                  key={g}
                  onClick={() => setGenre(g)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    genre === g
                      ? 'bg-purple-600 text-white'
                      : 'bg-secondary-100 text-secondary-600 hover:bg-secondary-200'
                  }`}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>

          {/* Mood */}
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">Mood</label>
            <div className="flex flex-wrap gap-2">
              {MOODS.map((m) => (
                <button
                  key={m}
                  onClick={() => setMood(m)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    mood === m
                      ? 'bg-purple-600 text-white'
                      : 'bg-secondary-100 text-secondary-600 hover:bg-secondary-200'
                  }`}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          {/* Tempo */}
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Tempo: {tempo} BPM
            </label>
            <input
              type="range"
              min={60}
              max={180}
              value={tempo}
              onChange={(e) => setTempo(Number(e.target.value))}
              className="w-full accent-purple-600"
            />
          </div>

          {/* Duration */}
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Duration: {duration}s
            </label>
            <input
              type="range"
              min={10}
              max={120}
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              className="w-full accent-purple-600"
            />
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !title.trim()}
            className="w-full py-3 px-4 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating... {progress > 0 && `${Math.round(progress)}%`}
              </>
            ) : (
              <>
                <Music className="w-5 h-5" />
                Generate Track
              </>
            )}
          </button>
        </div>

        {/* Status / Preview */}
        <div className="p-6 rounded-xl border border-secondary-200 space-y-4">
          <h3 className="font-semibold text-secondary-900">Preview</h3>

          {/* Status states */}
          {status === 'idle' && !taskId && (
            <div className="flex flex-col items-center justify-center py-12 text-secondary-400">
              <Music className="w-16 h-16 mb-3" />
              <p>Configure settings and generate a track</p>
            </div>
          )}

          {isGenerating && (
            <div className="flex flex-col items-center justify-center py-8">
              <Loader2 className="w-16 h-16 text-purple-500 animate-spin mb-4" />
              <p className="text-lg font-medium text-secondary-700">
                {status === 'pending' ? 'Queuing...' : 'Generating your track...'}
              </p>
              {progress > 0 && (
                <div className="w-full max-w-xs mt-4">
                  <div className="w-full bg-secondary-200 rounded-full h-2">
                    <div
                      className="bg-purple-600 rounded-full h-2 transition-all"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <p className="text-sm text-secondary-500 text-center mt-1">{Math.round(progress)}%</p>
                </div>
              )}
            </div>
          )}

          {status === 'completed' && audioUrl && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-green-600">
                <CheckCircle className="w-5 h-5" />
                <span className="font-medium">Track generated!</span>
              </div>
              <div className="p-4 bg-secondary-50 rounded-lg">
                <div className="flex items-center gap-3 mb-3">
                  <Volume2 className="w-8 h-8 text-purple-500" />
                  <div>
                    <p className="font-medium text-secondary-900">{title}</p>
                    <p className="text-sm text-secondary-500">{genre} · {mood} · {tempo} BPM · {duration}s</p>
                  </div>
                </div>
                <audio controls className="w-full" src={audioUrl}>
                  Your browser does not support audio.
                </audio>
              </div>
            </div>
          )}

          {status === 'failed' && error && (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-red-600">
                <XCircle className="w-5 h-5" />
                <span className="font-medium">Generation failed</span>
              </div>
              <p className="text-sm text-red-500 bg-red-50 p-3 rounded-lg">{error}</p>
              <button
                onClick={handleGenerate}
                className="text-sm text-purple-600 hover:text-purple-800 font-medium"
              >
                Try again →
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
