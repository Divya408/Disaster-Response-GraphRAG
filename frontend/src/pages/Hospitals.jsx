import React, { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import { api } from '../services/api.js'

export default function Hospitals() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [hospitals, setHospitals] = useState([])

  useEffect(() => {
    api
      .listHospitals()
      .then((res) => setHospitals(res.hospitals || []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  return (
    <div>
      <PageHeader title="Hospitals" subtitle="Emergency bed capacity by facility" />
      <ErrorBanner message={error} />

      <div className="grid grid-cols-3 gap-4">
        {hospitals.map((h) => (
          <div key={h.id} className="card">
            <div className="font-semibold text-slate-800 mb-2">{h.id}</div>
            <div className="text-sm text-slate-500 mb-3">Total beds: {h.total_beds}</div>

            <div className="flex items-baseline gap-2 mb-1">
              <span className="text-2xl font-bold text-emergency-700">{h.available_emergency_beds}</span>
              <span className="text-sm text-slate-400">/ {h.emergency_beds} emergency beds available</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2 mb-3">
              <div
                className="bg-emerald-500 h-2 rounded-full"
                style={{ width: `${Math.min(100, (h.available_emergency_beds / (h.emergency_beds || 1)) * 100)}%` }}
              />
            </div>

            <div className="flex flex-wrap gap-1.5">
              {(h.facilities || []).map((f) => (
                <span key={f} className="badge badge-demo">{f}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
