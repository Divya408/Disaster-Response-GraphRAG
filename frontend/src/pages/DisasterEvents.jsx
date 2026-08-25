import React, { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import PriorityBadge from '../components/PriorityBadge.jsx'
import { api } from '../services/api.js'

const AREAS = ['Area A', 'Area B', 'Area C']

export default function DisasterEvents() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [analyses, setAnalyses] = useState([])
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        setLoading(true)
        const results = await Promise.all(AREAS.map((a) => api.analyzeDisaster(a)))
        setAnalyses(results)
        setSelected(results[0])
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <LoadingSpinner label="Loading disaster events..." />

  return (
    <div>
      <PageHeader title="Disaster Events" subtitle="Flood — Salem District (Synthetic Demo Scenario)" />
      <ErrorBanner message={error} />

      <div className="grid grid-cols-3 gap-4 mb-6">
        {analyses.map((a) => (
          <button
            key={a.situation.area}
            onClick={() => setSelected(a)}
            className={`card text-left transition-all ${selected?.situation.area === a.situation.area ? 'ring-2 ring-emergency-500' : ''}`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold">{a.situation.area}</div>
              <PriorityBadge level={a.priority.priority_level} />
            </div>
            <div className="text-sm text-slate-500">Population affected: {a.situation.affected_population}</div>
          </button>
        ))}
      </div>

      {selected && (
        <div className="grid grid-cols-2 gap-6">
          <div className="card">
            <h3 className="font-semibold mb-3">Priority Calculation (Demo Heuristic)</h3>
            <div className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2 mb-3">
              {selected.priority.disclaimer}
            </div>
            <table className="w-full text-sm">
              <tbody>
                {Object.entries(selected.priority.calculation).map(([k, v]) => (
                  <tr key={k} className="border-b border-slate-100">
                    <td className="py-1.5 text-slate-500 capitalize">{k.replaceAll('_', ' ')}</td>
                    <td className="py-1.5 text-right font-medium text-slate-800">{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="mt-3 text-sm font-semibold">
              Total Score: {selected.priority.priority_score}/100 → {selected.priority.priority_level}
            </div>
          </div>

          <div className="card">
            <h3 className="font-semibold mb-3">Recommended Response</h3>
            {selected.recommended_shelter && (
              <div className="text-sm mb-3">
                <span className="text-slate-500">Recommended shelter:</span>{' '}
                <span className="font-medium">{selected.recommended_shelter.id}</span> (
                {selected.recommended_shelter.suitability_percent}% suitable, {selected.recommended_shelter.available_capacity} capacity)
              </div>
            )}
            <div className="text-sm font-medium mb-1">Recommended Actions:</div>
            <ul className="text-sm text-slate-600 list-disc list-inside space-y-1 mb-3">
              {selected.recommended_actions.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
            <div className="text-sm font-medium mb-1">Responsible Agencies:</div>
            <div className="flex flex-wrap gap-1.5">
              {selected.responsible_agencies.map((a) => (
                <span key={a} className="badge badge-demo">{a}</span>
              ))}
            </div>
            <div className="text-xs text-slate-400 mt-4">{selected.disclaimer}</div>
          </div>
        </div>
      )}
    </div>
  )
}
