import React, { useState, useEffect } from 'react'
import { Settings, Plus, Trash2, RefreshCw, CheckCircle, XCircle, Loader2, Key, Server, Cpu } from 'lucide-react'

interface Model {
  id: string
  name: string
}

interface Provider {
  id: string
  name: string
  display_name: string
  provider_type: string
  status: string
  api_base_url: string
  models: Model[]
  default_model: string | null
  max_tokens: number
  temperature: number
  supports_music_generation: boolean
  supports_lyrics_enhancement: boolean
  supports_audio_analysis: boolean
  description: string | null
  total_requests: number
  successful_requests: number
  failed_requests: number
  last_used_at: string | null
  last_error: string | null
}

const API_BASE = 'http://localhost:8001/api/v1'

export function ProviderDashboard() {
  const [providers, setProviders] = useState<Provider[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedProvider, setSelectedProvider] = useState<Provider | null>(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [testing, setTesting] = useState<string | null>(null)
  const [testResult, setTestResult] = useState<Record<string, { status: string; message: string }>>({})

  const fetchProviders = async () => {
    try {
      const res = await fetch(`${API_BASE}/providers`)
      const data = await res.json()
      setProviders(data.providers || [])
    } catch (err) {
      console.error('Failed to fetch providers:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProviders()
  }, [])

  const testConnection = async (name: string) => {
    setTesting(name)
    try {
      const res = await fetch(`${API_BASE}/providers/${name}/test`, { method: 'POST' })
      const data = await res.json()
      setTestResult((prev) => ({ ...prev, [name]: data }))
    } catch {
      setTestResult((prev) => ({ ...prev, [name]: { status: 'error', message: 'Connection failed' } }))
    } finally {
      setTesting(null)
    }
  }

  const deleteProvider = async (name: string) => {
    if (!confirm(`Delete provider "${name}"?`)) return
    await fetch(`${API_BASE}/providers/${name}`, { method: 'DELETE' })
    fetchProviders()
    if (selectedProvider?.name === name) setSelectedProvider(null)
  }

  const typeColors: Record<string, string> = {
    llm: 'bg-blue-100 text-blue-700',
    music: 'bg-purple-100 text-purple-700',
    video: 'bg-green-100 text-green-700',
  }

  const statusColors: Record<string, string> = {
    active: 'bg-green-100 text-green-700',
    inactive: 'bg-gray-100 text-gray-600',
    error: 'bg-red-100 text-red-700',
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-secondary-900 flex items-center gap-2">
            <Settings className="w-7 h-7" />
            AI Provider Dashboard
          </h2>
          <p className="text-secondary-500 mt-1">Configure and manage AI model providers</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium text-sm"
        >
          <Plus className="w-4 h-4" />
          Add Provider
        </button>
      </div>

      {/* Provider Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {providers.map((p) => {
          const result = testResult[p.name]
          return (
            <div
              key={p.id}
              className={`p-5 rounded-xl border-2 cursor-pointer transition-all ${
                selectedProvider?.id === p.id
                  ? 'border-purple-400 shadow-md'
                  : 'border-secondary-200 hover:border-secondary-300'
              }`}
              onClick={() => setSelectedProvider(p)}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-secondary-900">{p.display_name}</h3>
                  <p className="text-xs text-secondary-400">{p.name}</p>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[p.status] || statusColors.inactive}`}>
                  {p.status}
                </span>
              </div>

              <div className="flex gap-2 mb-3">
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${typeColors[p.provider_type] || typeColors.llm}`}>
                  {p.provider_type}
                </span>
                <span className="text-xs text-secondary-400">
                  {p.models?.length || 0} model{(p.models?.length || 0) !== 1 ? 's' : ''}
                </span>
              </div>

              {/* Feature badges */}
              <div className="flex flex-wrap gap-1 mb-3">
                {p.supports_music_generation && (
                  <span className="px-2 py-0.5 bg-purple-50 text-purple-600 rounded text-xs">🎵 Music</span>
                )}
                {p.supports_lyrics_enhancement && (
                  <span className="px-2 py-0.5 bg-blue-50 text-blue-600 rounded text-xs">✍️ Lyrics</span>
                )}
                {p.supports_audio_analysis && (
                  <span className="px-2 py-0.5 bg-green-50 text-green-600 rounded text-xs">📊 Analysis</span>
                )}
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-2 text-center text-xs text-secondary-500 mb-3">
                <div>
                  <div className="font-semibold text-secondary-900">{p.total_requests}</div>
                  <div>Total</div>
                </div>
                <div>
                  <div className="font-semibold text-green-600">{p.successful_requests}</div>
                  <div>Success</div>
                </div>
                <div>
                  <div className="font-semibold text-red-500">{p.failed_requests}</div>
                  <div>Failed</div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={(e) => { e.stopPropagation(); testConnection(p.name) }}
                  disabled={testing === p.name}
                  className="flex-1 flex items-center justify-center gap-1 py-1.5 text-xs rounded-lg border border-secondary-200 hover:bg-secondary-50 disabled:opacity-50"
                >
                  {testing === p.name ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : result?.status === 'ok' ? (
                    <CheckCircle className="w-3 h-3 text-green-500" />
                  ) : result?.status === 'error' ? (
                    <XCircle className="w-3 h-3 text-red-500" />
                  ) : (
                    <RefreshCw className="w-3 h-3" />
                  )}
                  Test
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); deleteProvider(p.name) }}
                  className="p-1.5 text-xs rounded-lg border border-red-200 text-red-500 hover:bg-red-50"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>

              {result && (
                <p className={`text-xs mt-2 ${result.status === 'ok' ? 'text-green-600' : 'text-red-500'}`}>
                  {result.message}
                </p>
              )}
            </div>
          )
        })}
      </div>

      {/* Provider Detail */}
      {selectedProvider && (
        <ProviderDetail
          provider={selectedProvider}
          onUpdate={() => fetchProviders()}
          onClose={() => setSelectedProvider(null)}
        />
      )}

      {/* Add Modal */}
      {showAddModal && (
        <AddProviderModal
          onCreated={() => { fetchProviders(); setShowAddModal(false) }}
          onClose={() => setShowAddModal(false)}
        />
      )}
    </div>
  )
}


function ProviderDetail({ provider, onUpdate, onClose }: { provider: Provider; onUpdate: () => void; onClose: () => void }) {
  const [apiKey, setApiKey] = useState('')
  const [baseUrl, setBaseUrl] = useState(provider.api_base_url || '')
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    try {
      await fetch(`${API_BASE}/providers/${provider.name}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey, api_base_url: baseUrl }),
      })
      onUpdate()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="p-6 rounded-xl border border-secondary-200 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Server className="w-5 h-5" />
          {provider.display_name} Configuration
        </h3>
        <button onClick={onClose} className="text-secondary-400 hover:text-secondary-600 text-sm">Close</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-1 flex items-center gap-1">
            <Key className="w-3 h-3" /> API Key
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Enter API key..."
            className="w-full px-3 py-2 border border-secondary-200 rounded-lg text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-1 flex items-center gap-1">
            <Server className="w-3 h-3" /> Base URL
          </label>
          <input
            type="text"
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
            className="w-full px-3 py-2 border border-secondary-200 rounded-lg text-sm"
          />
        </div>
      </div>

      {/* Models */}
      {provider.models && provider.models.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-secondary-700 mb-2 flex items-center gap-1">
            <Cpu className="w-3 h-3" /> Available Models
          </h4>
          <div className="flex flex-wrap gap-2">
            {provider.models.map((m) => (
              <span
                key={m.id}
                className={`px-3 py-1 rounded-full text-xs font-medium ${
                  m.id === provider.default_model
                    ? 'bg-purple-100 text-purple-700 ring-1 ring-purple-300'
                    : 'bg-secondary-100 text-secondary-600'
                }`}
              >
                {m.name || m.id}
                {m.id === provider.default_model && ' ⭐'}
              </span>
            ))}
          </div>
        </div>
      )}

      {provider.description && (
        <p className="text-sm text-secondary-500">{provider.description}</p>
      )}

      <button
        onClick={handleSave}
        disabled={saving}
        className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 disabled:opacity-50"
      >
        {saving ? 'Saving...' : 'Save Configuration'}
      </button>
    </div>
  )
}


function AddProviderModal({ onCreated, onClose }: { onCreated: () => void; onClose: () => void }) {
  const [name, setName] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [type, setType] = useState('llm')
  const [baseUrl, setBaseUrl] = useState('')
  const [saving, setSaving] = useState(false)

  const handleCreate = async () => {
    if (!name || !displayName) return
    setSaving(true)
    try {
      await fetch(`${API_BASE}/providers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          display_name: displayName,
          provider_type: type,
          api_base_url: baseUrl || undefined,
        }),
      })
      onCreated()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-xl p-6 w-full max-w-md space-y-4" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-lg font-semibold">Add AI Provider</h3>

        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-1">Provider Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. replicate"
            className="w-full px-3 py-2 border border-secondary-200 rounded-lg text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-1">Display Name</label>
          <input
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="e.g. Replicate"
            className="w-full px-3 py-2 border border-secondary-200 rounded-lg text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-1">Type</label>
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="w-full px-3 py-2 border border-secondary-200 rounded-lg text-sm"
          >
            <option value="llm">LLM (Text AI)</option>
            <option value="music">Music Generation</option>
            <option value="video">Video Analysis</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-1">API Base URL</label>
          <input
            type="text"
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
            placeholder="https://api.example.com/v1"
            className="w-full px-3 py-2 border border-secondary-200 rounded-lg text-sm"
          />
        </div>

        <div className="flex gap-3">
          <button onClick={onClose} className="flex-1 py-2 border border-secondary-200 rounded-lg text-sm">
            Cancel
          </button>
          <button
            onClick={handleCreate}
            disabled={saving || !name || !displayName}
            className="flex-1 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium disabled:opacity-50"
          >
            {saving ? 'Creating...' : 'Create'}
          </button>
        </div>
      </div>
    </div>
  )
}
