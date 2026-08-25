import React, { useEffect, useMemo, useRef, useState } from 'react'

const TYPE_COLORS = {
  Disaster: '#c0392b',
  Location: '#2f6fb0',
  Shelter: '#1e8449',
  Resource: '#d68910',
  Agency: '#8e44ad',
  Hospital: '#16a085',
  Incident: '#7f8c8d',
  ResponseAction: '#2c3e50',
  Entity: '#95a5a6',
}

function colorFor(type) {
  return TYPE_COLORS[type] || TYPE_COLORS.Entity
}

/**
 * A dependency-free force-directed graph visualization built directly on
 * SVG + a small physics simulation (no external graph-viz library
 * required). Supports pan (drag background), zoom (scroll wheel), node
 * dragging, and node selection (click a node to see its properties).
 */
export default function GraphCanvas({ nodes, edges, onSelectNode, height = 560 }) {
  const containerRef = useRef(null)
  const [positions, setPositions] = useState({})
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 })
  const [selected, setSelected] = useState(null)
  const [dragging, setDragging] = useState(null) // { type: 'node'|'canvas', id, startX, startY }
  const width = 900

  const nodeIds = useMemo(() => nodes.map((n) => n.id), [nodes])

  // Initialize positions on a circle, then run a light force simulation.
  useEffect(() => {
    const initial = {}
    nodes.forEach((n, i) => {
      const angle = (i / Math.max(1, nodes.length)) * 2 * Math.PI
      initial[n.id] = {
        x: width / 2 + 260 * Math.cos(angle) + (Math.random() - 0.5) * 20,
        y: height / 2 + 220 * Math.sin(angle) + (Math.random() - 0.5) * 20,
      }
    })
    setPositions(initial)

    let frame
    let ticks = 0
    const simulate = () => {
      ticks += 1
      setPositions((prev) => {
        const next = { ...prev }
        // Repulsion between all node pairs
        for (let i = 0; i < nodeIds.length; i++) {
          for (let j = i + 1; j < nodeIds.length; j++) {
            const a = next[nodeIds[i]]
            const b = next[nodeIds[j]]
            if (!a || !b) continue
            const dx = a.x - b.x
            const dy = a.y - b.y
            const dist = Math.max(30, Math.sqrt(dx * dx + dy * dy))
            const force = 1800 / (dist * dist)
            const fx = (dx / dist) * force
            const fy = (dy / dist) * force
            a.x += fx
            a.y += fy
            b.x -= fx
            b.y -= fy
          }
        }
        // Attraction along edges
        edges.forEach((e) => {
          const a = next[e.source]
          const b = next[e.target]
          if (!a || !b) return
          const dx = b.x - a.x
          const dy = b.y - a.y
          const dist = Math.max(1, Math.sqrt(dx * dx + dy * dy))
          const force = (dist - 140) * 0.01
          const fx = (dx / dist) * force
          const fy = (dy / dist) * force
          a.x += fx
          a.y += fy
          b.x -= fx
          b.y -= fy
        })
        // Pull toward center
        Object.values(next).forEach((p) => {
          p.x += (width / 2 - p.x) * 0.002
          p.y += (height / 2 - p.y) * 0.002
        })
        return next
      })
      if (ticks < 220) {
        frame = requestAnimationFrame(simulate)
      }
    }
    frame = requestAnimationFrame(simulate)
    return () => cancelAnimationFrame(frame)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nodeIds.join(','), edges.length])

  const handleWheel = (e) => {
    e.preventDefault()
    const delta = e.deltaY > 0 ? -0.08 : 0.08
    setTransform((t) => ({ ...t, scale: Math.min(3, Math.max(0.3, t.scale + delta)) }))
  }

  const handleMouseDown = (e, node) => {
    e.stopPropagation()
    if (node) {
      setDragging({ type: 'node', id: node.id })
    } else {
      setDragging({ type: 'canvas', startX: e.clientX - transform.x, startY: e.clientY - transform.y })
    }
  }

  const handleMouseMove = (e) => {
    if (!dragging) return
    if (dragging.type === 'canvas') {
      setTransform((t) => ({ ...t, x: e.clientX - dragging.startX, y: e.clientY - dragging.startY }))
    } else if (dragging.type === 'node') {
      const rect = containerRef.current.getBoundingClientRect()
      const x = (e.clientX - rect.left - transform.x) / transform.scale
      const y = (e.clientY - rect.top - transform.y) / transform.scale
      setPositions((prev) => ({ ...prev, [dragging.id]: { x, y } }))
    }
  }

  const handleMouseUp = () => setDragging(null)

  const handleNodeClick = (node) => {
    setSelected(node)
    onSelectNode && onSelectNode(node)
  }

  return (
    <div className="flex gap-4">
      <div
        ref={containerRef}
        className="relative overflow-hidden bg-slate-50 border border-slate-200 rounded-lg cursor-grab active:cursor-grabbing flex-1"
        style={{ height }}
        onWheel={handleWheel}
        onMouseDown={(e) => handleMouseDown(e, null)}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <svg width="100%" height="100%">
          <g transform={`translate(${transform.x},${transform.y}) scale(${transform.scale})`}>
            {edges.map((e, i) => {
              const a = positions[e.source]
              const b = positions[e.target]
              if (!a || !b) return null
              return (
                <g key={i}>
                  <line x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="#cbd5e1" strokeWidth={1.2} />
                  <text
                    x={(a.x + b.x) / 2}
                    y={(a.y + b.y) / 2}
                    fontSize={9}
                    fill="#94a3b8"
                    textAnchor="middle"
                  >
                    {e.relation}
                  </text>
                </g>
              )
            })}
            {nodes.map((n) => {
              const p = positions[n.id]
              if (!p) return null
              const isSelected = selected && selected.id === n.id
              return (
                <g
                  key={n.id}
                  transform={`translate(${p.x},${p.y})`}
                  onMouseDown={(e) => handleMouseDown(e, n)}
                  onClick={(e) => {
                    e.stopPropagation()
                    handleNodeClick(n)
                  }}
                  className="cursor-pointer"
                >
                  <circle r={isSelected ? 12 : 9} fill={colorFor(n.type)} stroke="#fff" strokeWidth={isSelected ? 3 : 1.5} />
                  <text x={13} y={4} fontSize={10} fill="#334155" style={{ pointerEvents: 'none' }}>
                    {(n.name || n.id || '').toString().slice(0, 28)}
                  </text>
                </g>
              )
            })}
          </g>
        </svg>
        <div className="absolute bottom-2 left-2 text-[11px] text-slate-400 bg-white/80 rounded px-2 py-1">
          Scroll to zoom · Drag background to pan · Drag a node to reposition · Click a node for details
        </div>
      </div>

      <div className="w-64 shrink-0">
        <div className="text-xs font-semibold uppercase text-slate-500 mb-2">Legend</div>
        <div className="space-y-1 mb-4">
          {Object.entries(TYPE_COLORS).map(([type, color]) => (
            <div key={type} className="flex items-center gap-2 text-xs text-slate-600">
              <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ background: color }} />
              {type}
            </div>
          ))}
        </div>
        {selected && (
          <div className="card !p-3">
            <div className="text-xs font-semibold uppercase text-slate-500 mb-1">Selected Node</div>
            <div className="font-semibold text-slate-800 text-sm mb-2">{selected.name || selected.id}</div>
            <div className="text-xs text-slate-500 space-y-1 max-h-72 overflow-y-auto">
              {Object.entries(selected).map(([k, v]) => (
                <div key={k}>
                  <span className="font-medium text-slate-600">{k}:</span> {JSON.stringify(v)}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
