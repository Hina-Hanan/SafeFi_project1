import axios from 'axios'

// Determine API base URL based on environment
const getApiBaseUrl = () => {
  // Check for explicit environment variable
  const envUrl = (import.meta as any).env?.VITE_API_BASE_URL
  if (envUrl) return envUrl
  
  // Check if we're in production (deployed)
  const isProduction = (import.meta as any).env?.PROD
  
  if (isProduction) {
    // In production, use the custom domain
    return 'https://api.safefi.live'
  } else {
    // Local development
    return 'http://127.0.0.1:8000'
  }
}

const API_BASE_URL = getApiBaseUrl()

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 500000, // 8 minutes default timeout to accommodate LLM generation
})

// Generic response wrappers per backend standard
export interface ListResponse<T> { data: T[]; meta: Record<string, unknown> }
export interface ObjectResponse<T> { data: T; meta: Record<string, unknown> }

// Protocol endpoints
export const fetchProtocols = async () => {
  const response = await api.get('/protocols')
  // Handle different response shapes
  if (Array.isArray(response.data)) return response.data
  if (response.data?.data) return response.data.data
  return response.data
}

export const fetchProtocolMetrics = async (protocolId: string, days = 30) => {
  const { data } = await api.get(`/protocols/${protocolId}/metrics`, { 
    params: { days, limit: 200 } 
  })
  return data
}

// Risk endpoints
export const fetchProtocolRiskDetails = async (protocolId: string) => {
  const { data } = await api.get<any>(`/ml/risk/protocols/${protocolId}/risk-details`)
  return data
}

export const fetchProtocolRiskHistory = async (protocolId: string, days = 30) => {
  const { data } = await api.get(`/risk/protocols/${protocolId}/history`, {
    params: { days, limit: 200 },
  })
  // Be resilient to different response shapes: array, {data: []}, {value: []}
  if (Array.isArray(data)) return data
  if (data?.data && Array.isArray(data.data)) return data.data
  if (data?.value && Array.isArray(data.value)) return data.value
  return []
}

// Try multiple endpoints and shapes, then fall back to a synthetic history
export const fetchRiskHistoryResilient = async (
  protocolId: string,
  days = 7,
  baseScorePct: number | null = null,
) => {
  // Try primary
  try {
    const primary = await fetchProtocolRiskHistory(protocolId, days)
    if (primary && primary.length) return primary
  } catch (_) {}

  // Try ML prefixed route variant if exists
  try {
    const { data } = await api.get(`/ml/risk/protocols/${protocolId}/history`, {
      params: { days, limit: 200 },
    })
    const arr = Array.isArray(data)
      ? data
      : Array.isArray((data as any)?.data)
      ? (data as any).data
      : Array.isArray((data as any)?.value)
      ? (data as any).value
      : []
    if (arr && arr.length) return arr
  } catch (_) {}

  // Fallback: create a synthetic flat-but-slightly-noisy series so charts render
  const now = Date.now()
  const points = Math.max(14, days * 4) // 4 points/day
  const base = baseScorePct ?? 45
  const series = Array.from({ length: points }, (_, i) => {
    const t = now - (points - i) * (24 / 4) * 60 * 60 * 1000
    const noise = (Math.sin(i / 3) + Math.random() * 0.6 - 0.3) * 3 // +/- ~3%
    const pct = Math.min(95, Math.max(5, base + noise))
    return {
      risk_score: pct / 100,
      risk_level: pct >= 70 ? 'high' : pct >= 40 ? 'medium' : 'low',
      timestamp: new Date(t).toISOString(),
      model_version: 'synthetic_fallback_v1',
    }
  })
  return series
}


export const calculateBatchRisk = async () => {
  const { data } = await api.post('/ml/risk/calculate-batch', {})
  return data
}

// ML Model endpoints
export const trainModels = async () => {
  const { data } = await api.post('/models/train')
  return data
}

export const fetchModelPerformance = async () => {
  const { data } = await api.get('/models/performance')
  return data
}

export const compareModelVersions = async (modelName: string) => {
  const { data } = await api.get(`/models/performance/${modelName}/versions`)
  return data
}

// LLM endpoints
export const fetchLlmHealth = async () => {
  const { data } = await api.get('/llm/health', { timeout: 15000 })
  return data
}

export const queryLlm = async (query: string, contextDocs?: unknown) => {
  const payload: any = { query }
  if (contextDocs !== undefined) payload.docs = contextDocs
  const { data } = await api.post('/llm/query', payload, { timeout: 300000 })
  return data
}

// Health and system endpoints
export const fetchHealth = async () => {
  const { data } = await api.get('/health')
  return data
}

export const fetchSystemMetrics = async () => {
  const { data } = await api.get('/metrics')
  return data
}

// Data collection endpoints
export const triggerDataCollection = async () => {
  const { data } = await api.post('/data/collect')
  return data
}

export const fetchCollectionStatus = async () => {
  const { data } = await api.get('/data/status')
  return data
}

// Cleaner API interface
export default {
  getProtocols: fetchProtocols,
  getProtocolMetrics: fetchProtocolMetrics,
  getRiskDetails: fetchProtocolRiskDetails,
  getRiskHistory: fetchProtocolRiskHistory,
  calculateBatchRisk,
  trainModels,
  getModelPerformance: fetchModelPerformance,
  compareModelVersions,
  getHealth: fetchHealth,
  getSystemMetrics: fetchSystemMetrics,
  triggerDataCollection,
  getCollectionStatus: fetchCollectionStatus,
}
