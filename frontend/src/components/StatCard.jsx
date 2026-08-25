import React from 'react'

export default function StatCard({ label, value, sublabel, tone = 'default' }) {
  const toneClasses = {
    default: 'text-emergency-700',
    high: 'text-alert-high',
    medium: 'text-alert-medium',
    low: 'text-alert-low',
  }
  return (
    <div className="card">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</div>
      <div className={`text-3xl font-bold mt-1 ${toneClasses[tone] || toneClasses.default}`}>{value}</div>
      {sublabel && <div className="text-xs text-slate-400 mt-1">{sublabel}</div>}
    </div>
  )
}
