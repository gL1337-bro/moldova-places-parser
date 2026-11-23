import { useState, useEffect, useCallback } from 'react'
import { api, PipelineStatus, PlacesResponse, Stats, Place } from '@/api/client'

export function usePipelineStatus() {
  const [status, setStatus] = useState<PipelineStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchStatus = useCallback(async () => {
    try {
      const data = await api.getStatus()
      setStatus(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch status')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 2000)
    return () => clearInterval(interval)
  }, [fetchStatus])

  const startPipeline = useCallback(async () => {
    try {
      await api.startPipeline()
      fetchStatus()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start pipeline')
    }
  }, [fetchStatus])

  return { status, loading, error, refetch: fetchStatus, startPipeline }
}

export function usePlaces(params: {
  group: string
  priority: string
  page: number
  per_page: number
  search: string
}) {
  const [data, setData] = useState<PlacesResponse>({
    places: [],
    total: 0,
    page: 1,
    per_page: 50,
    total_pages: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchPlaces = useCallback(async () => {
    setLoading(true)
    try {
      const result = await api.getPlaces(params)
      setData(result)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch places')
      setData({ places: [], total: 0, page: 1, per_page: 50, total_pages: 0 })
    } finally {
      setLoading(false)
    }
  }, [params])

  useEffect(() => {
    fetchPlaces()
  }, [fetchPlaces])

  return { ...data, loading, error, refetch: fetchPlaces }
}

export function useStats() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = useCallback(async () => {
    try {
      const data = await api.getStats()
      setStats(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stats')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 10000)
    return () => clearInterval(interval)
  }, [fetchStats])

  return { stats, loading, error, refetch: fetchStats }
}

export function useExport() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const exportData = async (format: 'excel' | 'csv', group: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.exportData(format, group)
      if (response.ok) {
        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `places_${group}.${format === 'excel' ? 'xlsx' : 'csv'}`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      } else {
        throw new Error('Export failed')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed')
    } finally {
      setLoading(false)
    }
  }

  return { exportData, loading, error }
}