import React, { useEffect, useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar.jsx'
import { api } from './services/api.js'

import Dashboard from './pages/Dashboard.jsx'
import DisasterEvents from './pages/DisasterEvents.jsx'
import GraphExplorer from './pages/GraphExplorer.jsx'
import GraphRAGAssistant from './pages/GraphRAGAssistant.jsx'
import Shelters from './pages/Shelters.jsx'
import Resources from './pages/Resources.jsx'
import Hospitals from './pages/Hospitals.jsx'
import Agencies from './pages/Agencies.jsx'
import Documents from './pages/Documents.jsx'
import OfflineMode from './pages/OfflineMode.jsx'
import Reports from './pages/Reports.jsx'

export default function App() {
  const [health, setHealth] = useState(null)

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth({ status: 'error' }))
    const interval = setInterval(() => {
      api.health().then(setHealth).catch(() => setHealth({ status: 'error' }))
    }, 15000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex min-h-screen">
      <Sidebar health={health} />
      <main className="flex-1 p-8 max-w-[1400px]">
        {health && health.status === 'error' && (
          <div className="bg-amber-50 border border-amber-300 text-amber-800 text-sm rounded-lg px-4 py-3 mb-6">
            Could not reach the backend API. Make sure it's running (see README: <code>uvicorn app.main:app --reload</code>)
            and that <code>VITE_API_BASE_URL</code> in <code>frontend/.env</code> points to it.
          </div>
        )}
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/events" element={<DisasterEvents />} />
          <Route path="/graph" element={<GraphExplorer />} />
          <Route path="/assistant" element={<GraphRAGAssistant />} />
          <Route path="/shelters" element={<Shelters />} />
          <Route path="/resources" element={<Resources />} />
          <Route path="/hospitals" element={<Hospitals />} />
          <Route path="/agencies" element={<Agencies />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/offline" element={<OfflineMode />} />
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </main>
    </div>
  )
}
