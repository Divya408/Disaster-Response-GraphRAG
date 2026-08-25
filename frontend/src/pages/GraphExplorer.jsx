import React, { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import GraphCanvas from '../components/GraphCanvas.jsx'
import { api } from '../services/api.js'

export default function GraphExplorer() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [graph, setGraph] = useState({ nodes: [], edges: [] })
  const [rebuilding, setRebuilding] = useState(false)
  const [filterType, setFilterType] = useState('all')

  const load = async () => {
    try {
      setLoading(true)
      const data = await api.getGraph()
      setGraph({ nodes: data.nodes, edges: data.edges })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const handleRebuild = async () => {
    setRebuilding(true)
    try {
      await api.buildGraph()
      await load()
    } catch (e) {
      setError(e.message)
    } finally {
      setRebuilding(false)
    }
  }

  const types = ['all', ...new Set(graph.nodes.map((n) => n.type))]
  const filteredNodes = filterType === 'all' ? graph.nodes : graph.nodes.filter((n) => n.type === filterType)
  const filteredIds = new Set(filteredNodes.map((n) => n.id))
  const filteredEdges = graph.edges.filter((e) => filteredIds.has(e.source) && filteredIds.has(e.target))

  return (
    <div>
      <PageHeader
        title="Graph Explorer"
        subtitle={`${graph.nodes.length} nodes · ${graph.edges.length} relationships`}
        action={
          <button
            onClick={handleRebuild}
            disabled={rebuilding}
            className="bg-emergency-600 hover:bg-emergency-700 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-50"
          >
            {rebuilding ? 'Rebuilding...' : 'Rebuild Graph'}
          </button>
        }
      />
      <ErrorBanner message={error} />

      <div className="flex gap-2 mb-4">
        {types.map((t) => (
          <button
            key={t}
            onClick={() => setFilterType(t)}
            className={`text-xs px-3 py-1.5 rounded-full border ${
              filterType === t ? 'bg-emergency-600 text-white border-emergency-600' : 'bg-white text-slate-600 border-slate-300'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingSpinner label="Loading knowledge graph..." />
      ) : (
        <div className="card">
          <GraphCanvas nodes={filteredNodes} edges={filteredEdges} />
        </div>
      )}
    </div>
  )
}
