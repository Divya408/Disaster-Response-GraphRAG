import React, { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import { api } from '../services/api.js'

export default function Resources() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [resources, setResources] = useState([])

  useEffect(() => {
    api
      .listResources()
      .then((res) => setResources(res.resources || []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  return (
    <div>
      <PageHeader title="Resources" subtitle="Inventory availability and detected shortages" />
      <ErrorBanner message={error} />

      <div className="card">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase text-slate-400 border-b border-slate-200">
              <th className="py-2">Resource</th>
              <th className="py-2">Available</th>
              <th className="py-2">Required</th>
              <th className="py-2">Shortage</th>
              <th className="py-2">Shortage %</th>
              <th className="py-2">Responsible Agencies</th>
            </tr>
          </thead>
          <tbody>
            {resources.map((r) => (
              <tr key={r.resource} className="border-b border-slate-100">
                <td className="py-2.5 font-medium text-slate-800">{r.resource}</td>
                <td className="py-2.5">{r.available} {r.unit}</td>
                <td className="py-2.5">{r.required} {r.unit}</td>
                <td className="py-2.5">
                  <span className={r.shortage > 0 ? 'text-red-600 font-semibold' : 'text-emerald-600'}>
                    {r.shortage} {r.unit}
                  </span>
                </td>
                <td className="py-2.5">
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-slate-100 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${r.shortage_percent > 30 ? 'bg-red-500' : r.shortage_percent > 0 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                        style={{ width: `${Math.min(100, r.shortage_percent)}%` }}
                      />
                    </div>
                    <span className="text-xs text-slate-500">{r.shortage_percent}%</span>
                  </div>
                </td>
                <td className="py-2.5 text-xs text-slate-500">{r.responsible_agencies.join(', ') || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
