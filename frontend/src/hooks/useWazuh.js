import { useState, useEffect, useCallback, useRef } from 'react'
import { api } from '../services/api'

const DEFAULT_INTERVAL = 30_000

export function useOverview(interval = DEFAULT_INTERVAL) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetch = useCallback(async () => {
    try {
      const result = await api.getOverview()
      setData(result)
      setError(null)
      setLastUpdated(new Date())
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetch()
    const id = setInterval(fetch, interval)
    return () => clearInterval(id)
  }, [fetch, interval])

  return { data, loading, error, lastUpdated, refetch: fetch }
}

export function useAgents(interval = DEFAULT_INTERVAL) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetch = useCallback(async () => {
    try {
      const result = await api.getAgents()
      setData(result)
      setError(null)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetch()
    const id = setInterval(fetch, interval)
    return () => clearInterval(id)
  }, [fetch, interval])

  return { data, loading, error, refetch: fetch }
}

export function useHistory(interval = 15_000) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)

  const fetch = useCallback(async () => {
    try {
      const result = await api.getHistory(100)
      setData(result)
    } catch {
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetch()
    const id = setInterval(fetch, interval)
    return () => clearInterval(id)
  }, [fetch, interval])

  return { data, loading, refetch: fetch }
}

export function useAlertConfig() {
  const [config, setConfig] = useState(null)

  useEffect(() => {
    api.getAlertConfig().then(setConfig).catch(() => {})
  }, [])

  return config
}
