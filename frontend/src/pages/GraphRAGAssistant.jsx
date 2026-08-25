import React, { useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import { api } from '../services/api.js'

const SAMPLE_QUESTIONS = [
  'Which shelters can accommodate flood victims from Area A?',
  'Which resources are currently insufficient?',
  'Which hospitals have emergency capacity?',
  'Which agencies are responsible for evacuation?',
  'What actions should responders prioritize?',
  'Which affected areas have the highest resource shortage?',
  'Show the relationship between this disaster and available shelters.',
]

export default function GraphRAGAssistant() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])

  const runQuery = async (q) => {
    const finalQuery = q || query
    if (!finalQuery.trim()) return
    setLoading(true)
    setError(null)
    try {
      const res = await api.query(finalQuery)
      setResult(res)
      setHistory((h) => [{ query: finalQuery, intent: res.intent }, ...h].slice(0, 8))
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <PageHeader title="GraphRAG Assistant" subtitle="Ask complex, multi-hop disaster-response questions" />
      <ErrorBanner message={error} />

      <div className="card mb-6">
        <div className="flex gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && runQuery()}
            placeholder="Ask a question, e.g. 'Which shelter should receive displaced people from Area A?'"
            className="flex-1 border border-slate-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emergency-500"
          />
          <button
            onClick={() => runQuery()}
            disabled={loading}
            className="bg-emergency-600 hover:bg-emergency-700 text-white font-medium px-5 py-2.5 rounded-lg text-sm disabled:opacity-50"
          >
            {loading ? 'Thinking...' : 'Ask'}
          </button>
        </div>
        <div className="flex flex-wrap gap-2 mt-3">
          {SAMPLE_QUESTIONS.map((q) => (
            <button
              key={q}
              onClick={() => {
                setQuery(q)
                runQuery(q)
              }}
              className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-full px-3 py-1.5"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {loading && <LoadingSpinner label="Running GraphRAG pipeline: query understanding → graph retrieval → hybrid text retrieval → fusion → answer..." />}

      {result && !loading && (
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2 space-y-4">
            <div className="card">
              <div className="flex items-center justify-between mb-3">
                <span className="badge badge-demo">Intent: {result.intent}</span>
                <div className="flex items-center gap-2">
                  {result.is_demo_mode && <span className="badge badge-medium">DEMO MODE</span>}
                  <span className="text-xs text-slate-400">Confidence: {(result.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
              <div className="whitespace-pre-wrap text-sm text-slate-700 leading-relaxed">{result.answer}</div>
            </div>

            <div className="card">
              <h3 className="font-semibold text-sm mb-2">Reasoning Path</h3>
              <ol className="text-sm text-slate-600 space-y-1.5">
                {result.reasoning_path.map((step, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-emergency-500 font-mono text-xs mt-0.5">{i + 1}.</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ol>
              <div className="text-xs text-slate-400 mt-3">
                This is an AI-generated decision-support path, not an official command.
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="card">
              <h3 className="font-semibold text-sm mb-2">Sources</h3>
              {result.sources.length === 0 && <div className="text-xs text-slate-400">No document sources retrieved.</div>}
              <div className="space-y-2">
                {result.sources.map((s, i) => (
                  <div key={i} className="text-xs border-b border-slate-100 pb-2">
                    <div className="font-medium text-slate-700">{s.document}</div>
                    <div className="text-slate-500">{s.section}</div>
                    <div className="text-slate-400">relevance: {s.relevance_score}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <h3 className="font-semibold text-sm mb-2">Related Entities</h3>
              <div className="flex flex-wrap gap-1.5">
                {result.related_entities.map((e) => (
                  <span key={e} className="badge badge-demo">{e}</span>
                ))}
                {result.related_entities.length === 0 && <div className="text-xs text-slate-400">None identified.</div>}
              </div>
            </div>

            {history.length > 0 && (
              <div className="card">
                <h3 className="font-semibold text-sm mb-2">Recent Queries</h3>
                <div className="space-y-1.5">
                  {history.map((h, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        setQuery(h.query)
                        runQuery(h.query)
                      }}
                      className="text-xs text-left text-slate-500 hover:text-emergency-600 block truncate w-full"
                    >
                      {h.query}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
