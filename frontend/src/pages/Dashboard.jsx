import React, { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import StatCard from '../components/StatCard.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import PriorityBadge from '../components/PriorityBadge.jsx'
import { api } from '../services/api.js'

export default function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [shelters, setShelters] = useState([])
  const [resources, setResources] = useState([])
  const [hospitals, setHospitals] = useState([])
  const [analyses, setAnalyses] = useState([])

  useEffect(() => {
    async function load() {
      try {
        setLoading(true)
        const [shelterRes, resourceRes, hospitalRes] = await Promise.all([
          api.listShelters(),
          api.listResources(),
          api.listHospitals(),
        ])
        setShelters(shelterRes.shelters || [])
        setResources(resourceRes.resources || [])
        setHospitals(hospitalRes.hospitals || [])

        const areas = ['Area A', 'Area B', 'Area C']
        const results = await Promise.all(
          areas.map((a) => api.analyzeDisaster(a).catch(() => null))
        )
        setAnalyses(results.filter(Boolean))
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <LoadingSpinner label="Loading disaster situation overview..." />

  const totalAvailableCapacity = shelters.reduce((sum, s) => sum + (s.available_capacity || 0), 0)
  const totalShortages = resources.filter((r) => r.shortage > 0).length
  const totalAvailableBeds = hospitals.reduce((sum, h) => sum + (h.available_emergency_beds || 0), 0)
  const totalAffectedPopulation = analyses.reduce((sum, a) => sum + (a.situation.affected_population || 0), 0)

  return (
    <div>
      <PageHeader
        title="Disaster Situation Dashboard"
        subtitle="Salem District Flood — Synthetic Demo Data — Academic Project"
      />
      <ErrorBanner message={error} />

      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard label="Affected Population" value={totalAffectedPopulation.toLocaleString()} sublabel="Across Area A, B, C" tone="high" />
        <StatCard label="Available Shelter Capacity" value={totalAvailableCapacity.toLocaleString()} sublabel={`${shelters.length} shelters`} />
        <StatCard label="Resource Shortages" value={totalShortages} sublabel={`of ${resources.length} tracked resources`} tone="medium" />
        <StatCard label="Available Emergency Beds" value={totalAvailableBeds} sublabel={`${hospitals.length} hospitals`} tone="low" />
      </div>

      <div className="grid grid-cols-3 gap-4">
        {analyses.map((a) => (
          <div key={a.situation.area} className="card">
            <div className="flex items-center justify-between mb-2">
              <div className="font-semibold text-slate-800">{a.situation.area}</div>
              <PriorityBadge level={a.priority.priority_level} />
            </div>
            <div className="text-sm text-slate-500 mb-3">
              Affected population: {a.situation.affected_population.toLocaleString()}
            </div>
            {a.recommended_shelter && (
              <div className="text-sm mb-2">
                <span className="text-slate-500">Recommended shelter: </span>
                <span className="font-medium text-slate-800">{a.recommended_shelter.id}</span>
                <span className="text-slate-400"> ({a.recommended_shelter.suitability_percent}% suitable)</span>
              </div>
            )}
            <div className="text-xs text-slate-500 mb-1">Priority Score (demo heuristic): {a.priority.priority_score}/100</div>
            <div className="text-xs font-medium text-slate-600 mt-3 mb-1">Top actions:</div>
            <ul className="text-xs text-slate-500 list-disc list-inside space-y-0.5">
              {a.recommended_actions.slice(0, 3).map((act, i) => (
                <li key={i}>{act}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="text-xs text-slate-400 mt-6">
        All figures are synthetic demo data generated for an academic GraphRAG project and do not
        represent a real disaster event. This system provides AI-assisted decision support only.
      </div>
    </div>
  )
}
