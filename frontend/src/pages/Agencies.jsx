import React, { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import { api } from '../services/api.js'

export default function Agencies() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [agencies, setAgencies] = useState([])
  const [graph, setGraph] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const [agencyRes, graphRes] = await Promise.all([api.listAgencies(), api.getGraph()])
        setAgencies(agencyRes.agencies || [])
        setGraph(graphRes)
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <LoadingSpinner />

  const responsibilitiesFor = (agencyId) =>
    (graph?.edges || [])
      .filter((e) => e.source === agencyId && e.relation === 'RESPONSIBLE_FOR')
      .map((e) => e.target)

  return (
    <div>
      <PageHeader title="Agencies" subtitle="Responsibilities and areas of operation" />
      <ErrorBanner message={error} />

      <div className="grid grid-cols-2 gap-4">
        {agencies.map((a) => (
          <div key={a.id} className="card">
            <div className="font-semibold text-slate-800 mb-1">{a.id}</div>
            <div className="text-xs text-slate-400 mb-3">Operates in: {a.operates_in}</div>
            <div className="text-xs font-medium text-slate-600 mb-1.5">Responsible for:</div>
            <div className="flex flex-wrap gap-1.5">
              {responsibilitiesFor(a.id).map((r) => (
                <span key={r} className="badge badge-demo">{r}</span>
              ))}
              {responsibilitiesFor(a.id).length === 0 && <span className="text-xs text-slate-400">None recorded.</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
