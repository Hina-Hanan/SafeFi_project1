export type RiskLevel = 'low' | 'medium' | 'high'

export interface Protocol {
  id: string
  name: string
  symbol?: string
  chain: string
  category: string
  description?: string
  website?: string
  twitter?: string
  discord?: string
  github?: string
  logo_url?: string
  created_at: string
  updated_at: string
}

export interface ProtocolMetric {
  id: string
  protocol_id: string
  timestamp: string
  tvl_usd: number
  price_usd: number
  market_cap_usd: number
  volume_24h_usd: number
  price_change_24h: number
  price_change_7d: number
  price_change_30d: number
  created_at: string
}

export interface RiskScore {
  id: string
  protocol_id: string
  risk_score: number
  risk_level: RiskLevel
  volatility_score?: number | null
  liquidity_score?: number | null
  model_version: string
  created_at: string
}

export interface RiskPrediction {
  protocol_id: string
  risk_score: number
  risk_level: RiskLevel
  confidence: number
  features: Record<string, number>
  model_version: string
  explanation: Record<string, unknown>
  timestamp?: string
}

export interface RiskHistoryPoint {
  timestamp: string
  risk_score: number
  risk_level: RiskLevel
  volatility_score?: number | null
  liquidity_score?: number | null
  model_version: string
}

export interface ModelPerformance {
  model_name: string
  f1: number
  accuracy: number
  precision: number
  recall: number
  run_id: string
  model_uri: string
  classification_report: Record<string, unknown>
}

export interface ProtocolWithRisk {
  protocol: Protocol
  latest_risk?: RiskScore
  latest_metrics?: ProtocolMetric
}

export interface HeatmapData {
  protocol_id: string
  protocol_name: string
  risk_score: number
  risk_level: RiskLevel
  tvl_usd: number
  price_change_24h: number
  volume_24h_usd: number
  volatility_score?: number
  liquidity_score?: number
}

export interface SystemHealth {
  status: string
  timestamp: string
  database_connected: boolean
  mlflow_connected: boolean
  last_data_collection: string
  total_protocols: number
  total_metrics: number
  total_risk_scores: number
}



