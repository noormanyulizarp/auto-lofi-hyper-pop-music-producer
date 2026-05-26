import { Cpu } from 'lucide-react'

interface Provider {
  name: string
  status: string
  models: string[]
  description: string
}

const mockProviders: Provider[] = [
  {
    name: 'heartmula',
    status: 'available',
    models: ['heartmula-v1'],
    description: 'Open-source AI music generation',
  },
  {
    name: 'openrouter',
    status: 'available',
    models: ['glm-4.5-air', 'nemotron'],
    description: 'Multi-model AI provider',
  },
]

export function ProviderDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-secondary-900">AI Providers</h2>
        <p className="text-secondary-500 mt-1">Manage and configure AI service providers</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {mockProviders.map((p) => (
          <div key={p.name} className="p-5 rounded-xl border border-secondary-200 hover:shadow-md transition-all">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-purple-500" />
                <h3 className="font-semibold text-secondary-900 capitalize">{p.name}</h3>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                p.status === 'available' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              }`}>
                {p.status}
              </span>
            </div>
            <p className="text-sm text-secondary-500 mb-3">{p.description}</p>
            <div className="flex flex-wrap gap-1">
              {p.models.map((m) => (
                <span key={m} className="px-2 py-0.5 bg-secondary-100 text-secondary-600 rounded text-xs">
                  {m}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
