// API client for communicating with the Flask backend
const API_BASE = 'http://127.0.0.1:5000/api'

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }

  return response.json()
}

export const api = {
  getStatus: () => request<PipelineStatus>('/status'),
  startPipeline: () => request<{ status: string }>('/start', { method: 'POST' }),
  getPlaces: (params: PlacesParams) => {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        searchParams.append(key, String(value))
      }
    })
    return request<PlacesResponse>(`/places?${searchParams.toString()}`)
  },
  getStats: () => request<Stats>('/stats'),
  exportData: (format: 'excel' | 'csv', group: string) => {
    const params = new URLSearchParams({ format, group })
    return fetch(`${API_BASE}/export?${params.toString()}`)
  },
  getConfig: () => request<Config>('/config'),
}

export interface PipelineStatus {
  status: 'idle' | 'running' | 'completed' | 'error'
  current_step: number
  total_steps: number
  progress: number
  message: string
  places_count: number
  groups: Record<string, number>
  priority_distribution: Record<string, number>
  error: string | null
  places: Place[]
}

export interface Place {
  name: string
  category: string
  city: string
  address: string
  phone: string
  opening_hours: string
  mobile: string
  email: string
  contact_name: string
  operator: string
  brand: string
  social_url: string
  website: string
  contact_website: string
  contact_facebook: string
  contact_instagram: string
  contact_telegram: string
  contact_whatsapp: string
  group: 'A' | 'B'
  priority_score: number
  priority_level: 'high' | 'medium' | 'low'
  google_maps_link: string
  verified: string
  notes: string
  contact_person: string
  contact_phone: string
  contact_email: string
  status: string
  osm_id: string
  lat: number
  lon: number
  street: string
  housenumber: string
  suburb: string
  postcode: string
  cuisine: string
  wheelchair: string
  outdoor_seating: string
  takeaway: string
  delivery: string
  fetched_at: string
}

export interface PlacesParams {
  group?: 'all' | 'A' | 'B'
  priority?: 'all' | 'high' | 'medium' | 'low'
  page?: number
  per_page?: number
  search?: string
}

export interface PlacesResponse {
  places: Place[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface Stats {
  total: number
  by_group: Record<string, number>
  by_category: Record<string, number>
  by_city: Record<string, number>
  by_priority_level: Record<string, number>
  avg_priority_score: number
  with_phone: number
  with_email: number
  with_social: number
  with_opening_hours: number
}

export interface Config {
  categories: Record<string, string[]>
  category_labels: Record<string, string>
  scoring_weights: Record<string, number>
  social_domains: string[]
  regions: Region[]
}

export interface Region {
  name: string
  bbox: number[]
  type: string
  city_filter: string[]
}