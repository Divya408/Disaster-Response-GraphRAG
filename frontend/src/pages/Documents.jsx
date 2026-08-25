import React, { useEffect, useRef, useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import { api } from '../services/api.js'

export default function Documents() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [documents, setDocuments] = useState([])
  const [uploading, setUploading] = useState(false)
  const [indexing, setIndexing] = useState(false)
  const [rebuilding, setRebuilding] = useState(false)
  const [status, setStatus] = useState(null)
  const fileInputRef = useRef(null)

  const load = async () => {
    try {
      setLoading(true)
      const res = await api.listDocuments()
      setDocuments(res.documents || [])
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setUploading(true)
    setError(null)
    try {
      await api.uploadDocument(file)
      await load()
      setStatus(`Uploaded ${file.name}. Click "Rebuild Index" and "Rebuild Graph" to include it.`)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleDelete = async (filename) => {
    try {
      await api.deleteDocument(filename)
      await load()
    } catch (e) {
      setError(e.message)
    }
  }

  const handleIndex = async () => {
    setIndexing(true)
    try {
      const res = await api.indexDocuments()
      setStatus(`Indexed ${res.total_chunks} chunks across ${res.documents_indexed.length} documents.`)
    } catch (e) {
      setError(e.message)
    } finally {
      setIndexing(false)
    }
  }

  const handleRebuildGraph = async () => {
    setRebuilding(true)
    try {
      const res = await api.buildGraph()
      setStatus(`Graph rebuilt: ${res.node_count} nodes, ${res.edge_count} edges (backend: ${res.backend}).`)
    } catch (e) {
      setError(e.message)
    } finally {
      setRebuilding(false)
    }
  }

  return (
    <div>
      <PageHeader
        title="Document Management"
        subtitle="Upload disaster-related documents (PDF, DOCX, TXT, MD, CSV)"
        action={
          <div className="flex gap-2">
            <label className="bg-emergency-600 hover:bg-emergency-700 text-white text-sm font-medium px-4 py-2 rounded-lg cursor-pointer">
              {uploading ? 'Uploading...' : 'Upload Document'}
              <input ref={fileInputRef} type="file" className="hidden" onChange={handleUpload} accept=".pdf,.docx,.txt,.md,.csv" />
            </label>
          </div>
        }
      />
      <ErrorBanner message={error} />
      {status && <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm rounded-lg px-4 py-3 mb-4">{status}</div>}

      <div className="flex gap-2 mb-6">
        <button onClick={handleIndex} disabled={indexing} className="bg-slate-700 hover:bg-slate-800 text-white text-sm px-4 py-2 rounded-lg disabled:opacity-50">
          {indexing ? 'Indexing...' : 'Rebuild Vector Index'}
        </button>
        <button onClick={handleRebuildGraph} disabled={rebuilding} className="bg-slate-700 hover:bg-slate-800 text-white text-sm px-4 py-2 rounded-lg disabled:opacity-50">
          {rebuilding ? 'Rebuilding...' : 'Rebuild Knowledge Graph'}
        </button>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="card">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase text-slate-400 border-b border-slate-200">
                <th className="py-2">Filename</th>
                <th className="py-2">Size</th>
                <th className="py-2"></th>
              </tr>
            </thead>
            <tbody>
              {documents.map((d) => (
                <tr key={d.filename} className="border-b border-slate-100">
                  <td className="py-2.5 font-medium text-slate-700">{d.filename}</td>
                  <td className="py-2.5 text-slate-500">{(d.size_bytes / 1024).toFixed(1)} KB</td>
                  <td className="py-2.5 text-right">
                    <button onClick={() => handleDelete(d.filename)} className="text-red-500 hover:text-red-700 text-xs font-medium">
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {documents.length === 0 && <div className="text-sm text-slate-400 py-4 text-center">No documents found.</div>}
        </div>
      )}
    </div>
  )
}
