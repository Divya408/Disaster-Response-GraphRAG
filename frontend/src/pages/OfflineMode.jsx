import React, { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import { api } from '../services/api.js'

const RECORD_TYPES = ['Shelter Assessment', 'Resource Count', 'Population Count', 'Medical Need', 'General Note']

export default function OfflineMode() {
  const [recordType, setRecordType] = useState(RECORD_TYPES[0])
  const [note, setNote] = useState('')
  const [location, setLocation] = useState('')
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)
  const [syncing, setSyncing] = useState(false)
  const [isOnline, setIsOnline] = useState(navigator.onLine)

  const refreshStatus = async () => {
    try {
      const res = await api.offlineStatus()
      setStatus(res)
    } catch (e) {
      setError(e.message)
    }
  }

  useEffect(() => {
    refreshStatus()
    const onOnline = () => setIsOnline(true)
    const onOffline = () => setIsOnline(false)
    window.addEventListener('online', onOnline)
    window.addEventListener('offline', onOffline)
    return () => {
      window.removeEventListener('online', onOnline)
      window.removeEventListener('offline', onOffline)
    }
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.createOfflineRecord(recordType, { location, note, submitted_at: new Date().toISOString() })
      setNote('')
      setLocation('')
      await refreshStatus()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleSync = async () => {
    setSyncing(true)
    try {
      await api.syncOffline()
      await refreshStatus()
    } catch (e) {
      setError(e.message)
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div>
      <PageHeader
        title="Offline Data Entry"
        subtitle="Responder-side data collection — works without victim smartphones, GPS, or connectivity"
      />
      <ErrorBanner message={error} />

      <div className="flex items-center gap-2 mb-6">
        <span className={`inline-block w-2.5 h-2.5 rounded-full ${isOnline ? 'bg-emerald-500' : 'bg-red-500'}`} />
        <span className="text-sm font-medium">{isOnline ? 'Online' : 'Offline Mode'}</span>
        {status && (
          <span className="badge badge-medium ml-2">Pending synchronization: {status.pending_sync_count} records</span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold mb-3">Record Field Assessment</h3>
          <p className="text-xs text-slate-500 mb-4">
            This form is designed for responders — volunteers, shelter staff, hospital staff, police,
            fire &amp; rescue — not disaster victims. Data submitted here is stored locally as
            "Pending Sync" and synchronized to the central system once connectivity is available,
            simulated below.
          </p>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="text-xs font-medium text-slate-600 block mb-1">Record Type</label>
              <select value={recordType} onChange={(e) => setRecordType(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                {RECORD_TYPES.map((t) => (
                  <option key={t}>{t}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 block mb-1">Location / Area</label>
              <input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="e.g. Area A" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 block mb-1">Notes</label>
              <textarea value={note} onChange={(e) => setNote(e.target.value)} rows={4} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="e.g. 40 additional people arrived, shelter nearing capacity" />
            </div>
            <button type="submit" className="bg-emergency-600 hover:bg-emergency-700 text-white text-sm font-medium px-4 py-2 rounded-lg w-full">
              Save Record Locally
            </button>
          </form>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold">Pending Synchronization</h3>
            <button onClick={handleSync} disabled={syncing} className="bg-slate-700 hover:bg-slate-800 text-white text-xs font-medium px-3 py-1.5 rounded-lg disabled:opacity-50">
              {syncing ? 'Syncing...' : 'Sync Now'}
            </button>
          </div>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {status?.records?.map((r) => {
              const payload = JSON.parse(r.payload)
              return (
                <div key={r.id} className="border border-slate-100 rounded-lg p-3 text-xs">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-slate-700">{r.record_type}</span>
                    <span className="badge badge-medium">{r.status}</span>
                  </div>
                  <div className="text-slate-500">{payload.location}</div>
                  <div className="text-slate-400">{payload.note}</div>
                </div>
              )
            })}
            {(!status || status.records.length === 0) && (
              <div className="text-xs text-slate-400 text-center py-6">No pending records.</div>
            )}
          </div>
        </div>
      </div>

      <div className="card mt-6">
        <h3 className="font-semibold mb-2 text-sm">Why this design? (Viva question)</h3>
        <p className="text-sm text-slate-600">
          "What if the victim's phone has no battery?" — This system does not depend on the
          victim's smartphone. The primary data-collection model is responder-side: Volunteer /
          Shelter / Police / Hospital / Responder → Offline Data Collection → Synchronization →
          Central Disaster Intelligence System. A dead phone is therefore not a single point of failure.
        </p>
      </div>
    </div>
  )
}
