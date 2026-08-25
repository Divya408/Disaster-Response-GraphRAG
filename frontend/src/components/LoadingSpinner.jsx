import React from 'react'

export default function LoadingSpinner({ label = 'Loading...' }) {
  return (
    <div className="flex items-center gap-3 text-slate-500 py-8 justify-center">
      <div className="w-5 h-5 border-2 border-emergency-500 border-t-transparent rounded-full animate-spin" />
      <span className="text-sm">{label}</span>
    </div>
  )
}
