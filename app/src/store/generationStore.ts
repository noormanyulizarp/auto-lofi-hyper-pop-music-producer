import { create } from 'zustand'

interface GenerationState {
  taskId: string | null
  status: string
  progress: number
  error: string | null
  audioUrl: string | null
  isGenerating: boolean

  startGeneration: (taskId: string) => void
  updateProgress: (status: string, progress: number) => void
  setComplete: (audioUrl: string) => void
  setError: (error: string) => void
  reset: () => void
}

export const useGenerationStore = create<GenerationState>((set) => ({
  taskId: null,
  status: 'idle',
  progress: 0,
  error: null,
  audioUrl: null,
  isGenerating: false,

  startGeneration: (taskId) =>
    set({ taskId, status: 'pending', progress: 0, error: null, audioUrl: null, isGenerating: true }),

  updateProgress: (status, progress) =>
    set({ status, progress }),

  setComplete: (audioUrl) =>
    set({ status: 'completed', progress: 100, audioUrl, isGenerating: false }),

  setError: (error) =>
    set({ status: 'failed', error, isGenerating: false }),

  reset: () =>
    set({ taskId: null, status: 'idle', progress: 0, error: null, audioUrl: null, isGenerating: false }),
}))
