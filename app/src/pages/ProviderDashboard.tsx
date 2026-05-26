import { useState, useEffect } from 'react'
import { Cpu, Loader2, CheckCircle, XCircle, RefreshCw } from 'lucide-react'
import { providersApi, type Provider } from '../api/client'

export function ProviderDashboard() {
  const [providers, setProviders] = useState<Provider[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [testingId, setTestingId] = useState<string | null>(null)

  const fetchProviders = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await providersApi.list()
      setProviders(Array.isArray(data) ? data : data.providers || [])
    } catch (err: any) {
      setError(err?.message || 'Failed to load providers')
      // Fallback to mock
      setProviders([
        {
          id: 'heartmula',
          name: 'heartmula',
          display_name: 'HeartMuLa',
          provider_type: 'music_generation',
          status: 'available',
          api_base_url: '',
          models: ['heartmula-v1'],
          supports_music_generation: true,
          description: 'Open-source AI music generation',
        },
        {
          id: 'openrouter',
          name: 'openrouter',
          display_name: 'OpenRouter',
          provider_type: 'llm',
          status: 'available',
          api_base_url: '',
          models: ['glm-4.5-air', 'nemotron'],
          supports_music_generation: false,
          description: 'Multi-model AI provider',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchProviders() }, [])

  const handleTest = async (providerId: string) => {
    setTestingId(providerId)
    try {
      await providersApi.test(providerId)
    } catch {
      // Provider test endpoint may not exist yet
    } finally {
      setTestingId(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-secondary-900">AI Providers</h2>
          <p className="text-secondary-500 mt-1">Manage and configure AI service providers</p>
        </div>
        <button
          onClick={fetchProviders}
          className="p-2 hover:bg-secondary-100 rounded-lg transition-colors"
          title="Refresh"
        >
          <RefreshCw className="w-5 h-5 text-secondary-500" />
        </button>
      </div>

      {error && (
        <p className="text-sm text-amber-600 bg-amber-50 p-3 rounded-lg">
          Using fallback data — API connection pending
        </p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {providers.map((p) => (
          <div key={p.id || p.name} className="p-5 rounded-xl border border-secondary-200 hover:shadow-md transition-all">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-purple-500" />
                <h3 className="font-semibold text-secondary-900">
                  {p.display_name || p.name}
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  p.status === 'available' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                }`}>
                  {p.status}
                </span>
                {p.supports_music_generation && (
                  <span className="px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700">
                    🎵 Music
                  </span>
                )}
              </div>
            </div>
            <p className="text-sm text-secondary-500 mb-3">{p.description}</p>
            <div className="flex flex-wrap gap-1 mb-3">
              {(p.models || []).map((m) => (
                <span key={m} className="px-2 py-0.5 bg-secondary-100 text-secondary-600 rounded text-xs">
                  {m}
                </span>
              ))}
            </div>
            <button
              onClick={() => handleTest(p.id || p.name)}
              disabled={testingId === (p.id || p.name)}
              className="text-sm text-purple-600 hover:text-purple-800 font-medium disabled:opacity-50"
            >
              {testingId === (p.id || p.name) ? 'Testing...' : 'Test connection →'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
