/**
 * API client — connects React frontend to Python AI service.
 * 
 * Dev: Vite proxies /ai → http://localhost:8001
 * Prod: Go API gateway proxies /api/v1/* → Python AI
 */

import axios from 'axios'

const api = axios.create({
  baseURL: '/ai/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// ─── Types ────────────────────────────────────────────────

export interface GenerateRequest {
  title: string
  genre: string
  mood: string
  duration: number
  tempo?: number
  key?: string
  instruments?: string[]
  prompt?: string
}

export interface GenerateResponse {
  task_id: string
  status: string
  message: string
  title: string
  genre: string
  mood: string
  duration: number
}

export interface TaskStatus {
  task_id: string
  status: string
  progress: number
  message?: string
  audio_url?: string
}

export interface Preset {
  id: string
  name: string
  genre: string
  mood: string
  tempo_min: number
  tempo_max: number
  key_signature: string
  duration_default: number
  instruments: string[]
  tags: string
  prompt_template: string
  is_default: boolean
  icon: string
  description: string
}

export interface Provider {
  id: string
  name: string
  display_name: string
  provider_type: string
  status: string
  api_base_url: string
  models: string[]
  supports_music_generation: boolean
  description: string
}

// ─── Music API ────────────────────────────────────────────

export const musicApi = {
  /** Generate a new music track */
  generate: (data: GenerateRequest) =>
    api.post<GenerateResponse>('/generate', data).then(r => r.data),

  /** Check generation task status */
  getStatus: (taskId: string) =>
    api.get<TaskStatus>(`/status/${taskId}`).then(r => r.data),

  /** Get available genres and moods */
  getGenres: () =>
    api.get<{ genres: string[]; moods: string[] }>('/genres').then(r => r.data),

  /** Get generation history */
  getHistory: (limit = 20, offset = 0) =>
    api.get('/history', { params: { limit, offset } }).then(r => r.data),
}

// ─── Presets API ──────────────────────────────────────────

export const presetsApi = {
  /** List all presets */
  list: () =>
    api.get<Preset[]>('/music/presets').then(r => r.data),

  /** List presets grouped by genre */
  listByGenre: () =>
    api.get('/music/presets/genres/list').then(r => r.data),

  /** Get a single preset */
  get: (presetId: string) =>
    api.get<Preset>(`/music/presets/${presetId}`).then(r => r.data),
}

// ─── Providers API ────────────────────────────────────────

export const providersApi = {
  /** List all AI providers */
  list: () =>
    api.get<Provider[]>('/providers').then(r => r.data),

  /** Get stats summary */
  getStats: () =>
    api.get('/providers/stats/summary').then(r => r.data),

  /** Test a provider connection */
  test: (providerName: string) =>
    api.post(`/providers/${providerName}/test`).then(r => r.data),
}

// ─── Health ───────────────────────────────────────────────

export const healthApi = {
  check: () =>
    api.get('/health').then(r => r.data),
}

export default api
