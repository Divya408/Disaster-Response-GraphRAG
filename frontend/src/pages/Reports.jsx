import React, { useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import { api } from '../services/api.js'

const AREAS = ['Area A', 'Area B', 'Area C']

export default function Reports() {
  const [area, setArea] = useState(AREAS[0])
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState(null)
  const [lastReport, setLastReport] = useState(null)

  const handleGenerate = async () => {
    setGenerating(true)
    setError(null)
    try {
      const blob = await api.generateReport(area)
      const url = URL.createObjectURL(blob)
      setLastReport({ url, area, generatedAt: new Date().toLocaleString() })
    } catch (e) {
      setError(e.message)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div>
      <PageHeader title="Disaster Response Reports" subtitle="Generate a downloadable PDF situation report" />
      <ErrorBanner message={error} />

      <div className="card max-w-xl">
        <label className="text-xs font-medium text-slate-600 block mb-1">Affected Area</label>
        <select value={area} onChange={(e) => setArea(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm mb-4">
          {AREAS.map((a) => (
            <option key={a}>{a}</option>
          ))}
        </select>

        <button
          onClick={handleGenerate}
          disabled={generating}
          className="bg-emergency-600 hover:bg-emergency-700 text-white text-sm font-medium px-4 py-2.5 rounded-lg w-full disabled:opacity-50"
        >
          {generating ? 'Generating Report...' : 'Generate PDF Report'}
        </button>

        <div className="text-xs text-slate-400 mt-3">
          The report includes: disaster situation, shelter recommendations, resource availability
          &amp; shortages, hospital availability, responsible agencies, recommended actions,
          GraphRAG evidence, source documents, reasoning path, and the mandatory disclaimer.
        </div>

        {lastReport && (
          <div className="mt-5 bg-emerald-50 border border-emerald-200 rounded-lg p-4">
            <div className="text-sm font-medium text-emerald-800 mb-1">Report ready — {lastReport.area}</div>
            <div className="text-xs text-emerald-600 mb-3">Generated {lastReport.generatedAt}</div>
            <a
              href={lastReport.url}
              download={`disaster_report_${lastReport.area.replace(' ', '_')}.pdf`}
              className="inline-block bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
            >
              Download PDF
            </a>
          </div>
        )}
      </div>
    </div>
  )
}
