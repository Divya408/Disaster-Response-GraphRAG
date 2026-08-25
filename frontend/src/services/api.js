const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const data = await res.json()
      detail = data.detail || JSON.stringify(data)
    } catch (e) {
      /* ignore parse errors */
    }
    throw new Error(`${res.status}: ${detail}`)
  }
  const contentType = res.headers.get('content-type') || ''
  if (contentType.includes('application/pdf')) {
    return res.blob()
  }
  return res.json()
}

export const api = {
  health: () => request('/api/health'),

  // Documents
  listDocuments: () => request('/api/documents'),
  uploadDocument: (file) => {
    const form = new FormData()
    form.append('file', file)
    return request('/api/documents/upload', { method: 'POST', body: form })
  },
  indexDocuments: () => request('/api/documents/index', { method: 'POST' }),
  deleteDocument: (filename) => request(`/api/documents/${encodeURIComponent(filename)}`, { method: 'DELETE' }),

  // Graph
  buildGraph: () => request('/api/graph/build', { method: 'POST' }),
  getGraph: () => request('/api/graph'),
  getNode: (nodeId, depth = 1) => request(`/api/graph/node/${encodeURIComponent(nodeId)}?depth=${depth}`),

  // GraphRAG query
  query: (query, top_k = 5) => request('/api/query', { method: 'POST', body: JSON.stringify({ query, top_k }) }),

  // Disaster analysis
  analyzeDisaster: (area) => request('/api/disaster/analyze', { method: 'POST', body: JSON.stringify({ area }) }),

  // Domain data
  listShelters: (area) => request(`/api/shelters${area ? `?area=${encodeURIComponent(area)}` : ''}`),
  listResources: () => request('/api/resources'),
  listHospitals: (area) => request(`/api/hospitals${area ? `?area=${encodeURIComponent(area)}` : ''}`),
  listAgencies: (responsibleFor) => request(`/api/agencies${responsibleFor ? `?responsible_for=${encodeURIComponent(responsibleFor)}` : ''}`),

  // Offline mode
  createOfflineRecord: (record_type, payload) =>
    request('/api/offline/records', { method: 'POST', body: JSON.stringify({ record_type, payload }) }),
  offlineStatus: () => request('/api/offline/status'),
  syncOffline: () => request('/api/offline/sync', { method: 'POST' }),

  // Reports
  generateReport: (area) => request('/api/report/generate', { method: 'POST', body: JSON.stringify({ area }) }),
}

export { API_BASE_URL }
