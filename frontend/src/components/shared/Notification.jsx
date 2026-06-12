import { useState, useEffect, useCallback } from 'react'

// ── Notification store (singleton) ──────────────────────────
let listeners = []
let queue     = []

function emit(notification) {
  const item = { id: Date.now() + Math.random(), ...notification }
  queue.push(item)
  listeners.forEach(fn => fn([...queue]))
}

export const notify = {
  success: (message, opts = {}) => emit({ type: 'success', message, ...opts }),
  error:   (message, opts = {}) => emit({ type: 'error',   message, ...opts }),
  info:    (message, opts = {}) => emit({ type: 'info',    message, ...opts }),
  warning: (message, opts = {}) => emit({ type: 'warning', message, ...opts }),
}

// ── Toast item ───────────────────────────────────────────────
const TYPE_CONFIG = {
  success: { bg: '#ECFDF5', border: '#A7F3D0', text: '#065F46', icon: '✓' },
  error:   { bg: '#FEF2F2', border: '#FECACA', text: '#991B1B', icon: '✕' },
  info:    { bg: '#EFF6FF', border: '#BFDBFE', text: '#1E40AF', icon: 'i' },
  warning: { bg: '#FFFBEB', border: '#FDE68A', text: '#92400E', icon: '!' },
}

function Toast({ id, type, message, onClose }) {
  const cfg = TYPE_CONFIG[type] || TYPE_CONFIG.info

  useEffect(() => {
    const t = setTimeout(() => onClose(id), 4000)
    return () => clearTimeout(t)
  }, [id, onClose])

  return (
    <div className="flex items-start gap-3 px-4 py-3 rounded-xl shadow-card animate-slide-up max-w-sm w-full"
         style={{ background: cfg.bg, border: `1px solid ${cfg.border}` }}>
      <span className="w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5"
            style={{ background: cfg.border, color: cfg.text }}>
        {cfg.icon}
      </span>
      <p className="text-sm flex-1 leading-snug" style={{ color: cfg.text }}>{message}</p>
      <button onClick={() => onClose(id)}
              className="text-xs opacity-60 hover:opacity-100 flex-shrink-0 mt-0.5 transition-opacity"
              style={{ color: cfg.text }}>
        ✕
      </button>
    </div>
  )
}

// ── Notification container ───────────────────────────────────
export default function Notification() {
  const [toasts, setToasts] = useState([])

  useEffect(() => {
    const handler = (items) => setToasts(items)
    listeners.push(handler)
    return () => {
      listeners = listeners.filter(fn => fn !== handler)
    }
  }, [])

  const remove = useCallback((id) => {
    queue = queue.filter(t => t.id !== id)
    setToasts([...queue])
  }, [])

  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-5 right-5 z-[100] flex flex-col gap-2 items-end">
      {toasts.map(toast => (
        <Toast key={toast.id} {...toast} onClose={remove} />
      ))}
    </div>
  )
}
