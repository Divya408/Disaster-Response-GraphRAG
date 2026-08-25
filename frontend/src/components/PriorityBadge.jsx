import React from 'react'

export default function PriorityBadge({ level }) {
  const cls = {
    HIGH: 'badge-high',
    MEDIUM: 'badge-medium',
    LOW: 'badge-low',
  }[level] || 'badge-demo'
  return <span className={`badge ${cls}`}>{level || 'UNKNOWN'}</span>
}
