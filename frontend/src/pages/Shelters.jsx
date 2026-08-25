import React, { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import { api } from '../services/api.js'

export default function Shelters() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [shelters, setShelters] = useState([])
  const [area, setArea] = useState('')

  const load = async (areaFilter) => {
    try {
      setLoading(true)
      const res = await api.listShelters(areaFilter || undefined)
      setShelters(res.shelters || [])
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <div>
      <PageHeader title="Shelters" subtitle="Capacity, occupancy, and facility availability" />
      <ErrorBanner message={error} />

      <div className="flex gap-2 mb-4">
        <input
          value={area}
          onChange={(e) => setArea(e.target.value)}
          placeholder="Filter/rank by area, e.g. Area A"
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm w-64"
        />
        <button onClick={() => load(area)} className="bg-emergency-600 text-white text-sm px-4 py-2 rounded-lg">
          Apply
        </button>
        <button
          onClick={() => {
            setArea('')
            load()
          }}
          className="bg-slate-200 text-slate-700 text-sm px-4 py-2 rounded-lg"
        >
          Clear
        </button>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {shelters.map((s) => (
            <div key={s.id} className="card">
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-semibold text-slate-800">{s.id}</div>
                  <div className="text-xs text-slate-400">{s.contact}</div>
                </div>
                {s.suitability_percent !== undefined && (
                  <span className="badge badge-medium">{s.suitability_percent}% suitable</span>
                )}
              </div>

              <div className="grid grid-cols-3 gap-2 my-3 text-center">
                <div>
                  <div className="text-lg font-bold text-slate-800">{s.capacity}</div>
                  <div className="text-[10px] uppercase text-slate-400">Capacity</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-slate-800">{s.occupied}</div>
                  <div className="text-[10px] uppercase text-slate-400">Occupied</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-emerald-600">{s.available_capacity}</div>
                  <div className="text-[10px] uppercase text-slate-400">Available</div>
                </div>
              </div>

              <div className="w-full bg-slate-100 rounded-full h-2 mb-3">
                <div
                  className="bg-emergency-500 h-2 rounded-full"
                  style={{ width: `${Math.min(100, (s.occupied / (s.capacity || 1)) * 100)}%` }}
                />
              </div>

              <div className="flex gap-2 flex-wrap">
                <span className={`badge ${s.drinking_water ? 'badge-low' : 'badge-demo'}`}>💧 Drinking Water {s.drinking_water ? '✓' : '✗'}</span>
                <span className={`badge ${s.food_available ? 'badge-low' : 'badge-demo'}`}>🍞 Food {s.food_available ? '✓' : '✗'}</span>
                <span className={`badge ${s.medical_support ? 'badge-low' : 'badge-demo'}`}>⚕️ Medical {s.medical_support ? '✓' : '✗'}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
