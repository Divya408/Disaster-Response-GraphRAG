import React from 'react'
import { NavLink } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: '📊' },
  { to: '/events', label: 'Disaster Events', icon: '🌊' },
  { to: '/graph', label: 'Graph Explorer', icon: '🕸️' },
  { to: '/assistant', label: 'GraphRAG Assistant', icon: '💬' },
  { to: '/shelters', label: 'Shelters', icon: '🏠' },
  { to: '/resources', label: 'Resources', icon: '📦' },
  { to: '/hospitals', label: 'Hospitals', icon: '🏥' },
  { to: '/agencies', label: 'Agencies', icon: '🧑‍🚒' },
  { to: '/documents', label: 'Documents', icon: '📄' },
  { to: '/offline', label: 'Offline Mode', icon: '📶' },
  { to: '/reports', label: 'Reports', icon: '📑' },
]

export default function Sidebar({ health }) {
  return (
    <aside className="w-64 shrink-0 bg-emergency-900 text-white flex flex-col h-screen sticky top-0">
      <div className="p-5 border-b border-white/10">
        <div className="text-lg font-bold tracking-tight">DisasterGraph AI</div>
        <div className="text-xs text-white/60 mt-0.5">GraphRAG Disaster Response</div>
      </div>
      <nav className="flex-1 overflow-y-auto py-3">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-5 py-2.5 text-sm transition-colors ${
                isActive ? 'bg-white/10 text-white font-medium border-r-2 border-emergency-500' : 'text-white/70 hover:bg-white/5 hover:text-white'
              }`
            }
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-white/10 text-xs text-white/50 space-y-1">
        {health && (
          <>
            <div className="flex items-center gap-1.5">
              <span className={`inline-block w-2 h-2 rounded-full ${health.status === 'ok' ? 'bg-emerald-400' : 'bg-red-400'}`} />
              API {health.status === 'ok' ? 'Connected' : 'Offline'}
            </div>
            {health.demo_mode && <div className="badge badge-demo !text-[10px]">DEMO MODE</div>}
            <div>Graph: {health.graph_backend}</div>
          </>
        )}
      </div>
    </aside>
  )
}
