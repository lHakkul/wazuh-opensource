const BASE_URL = import.meta.env.VITE_API_URL || '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  getOverview: () => request('/overview'),
  getClusterHealth: () => request('/cluster/health'),
  getClusterNodes: () => request('/cluster/nodes'),
  getAgents: (limit = 500) => request(`/agents?limit=${limit}`),
  getAgentsSummary: () => request('/agents/summary'),
  getManagerStatus: () => request('/manager/status'),
  getManagerInfo: () => request('/manager/info'),
  getHistory: (limit = 50) => request(`/history?limit=${limit}`),
  clearHistory: () => request('/history', { method: 'DELETE' }),
  getAlertConfig: () => request('/alerts/config'),
  testTelegram: () => request('/alerts/test/telegram', { method: 'POST' }),
  testSlack: () => request('/alerts/test/slack', { method: 'POST' }),
}
