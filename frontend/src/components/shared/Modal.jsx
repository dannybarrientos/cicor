import { useEffect, useRef } from 'react'
import Button from './Button.jsx'

/**
 * Modal — componente reutilizable para crear/editar registros
 *
 * Props:
 *   open      : boolean
 *   onClose   : fn
 *   title     : string
 *   color     : hex (color del módulo)
 *   onSubmit  : fn(e)
 *   loading   : boolean
 *   submitLabel : string  (default 'Guardar')
 *   children  : form fields
 */
export default function Modal({
  open,
  onClose,
  title,
  color = '#1E40AF',
  onSubmit,
  loading = false,
  submitLabel = 'Guardar',
  children,
}) {
  const overlayRef = useRef(null)

  // Close on Escape
  useEffect(() => {
    if (!open) return
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [open, onClose])

  // Lock body scroll
  useEffect(() => {
    document.body.style.overflow = open ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [open])

  if (!open) return null

  const handleOverlayClick = (e) => {
    if (e.target === overlayRef.current) onClose()
  }

  return (
    <div
      ref={overlayRef}
      onClick={handleOverlayClick}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(12,30,77,0.45)', backdropFilter: 'blur(4px)' }}
    >
      <div
        className="w-full max-w-md rounded-2xl shadow-xl animate-slide-up"
        style={{ background: '#fff', border: `1px solid ${color}22` }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4"
             style={{ borderBottom: `1px solid ${color}22` }}>
          <div className="flex items-center gap-2">
            <div className="w-1 h-5 rounded-full" style={{ background: color }} />
            <h2 className="font-display font-semibold text-[#0C1E4D] text-base">{title}</h2>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
            aria-label="Cerrar"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <form onSubmit={onSubmit}>
          <div className="px-6 py-5 flex flex-col gap-4">
            {children}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-2 px-6 py-4"
               style={{ borderTop: '1px solid #F1F5F9' }}>
            <Button variant="ghost" onClick={onClose} type="button" disabled={loading}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit" color={color} loading={loading}>
              {submitLabel}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

/**
 * FormField — helper para labels + inputs dentro del modal
 */
export function FormField({ label, error, children }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-slate-600 uppercase tracking-wide">{label}</label>
      {children}
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  )
}

/**
 * Input — styled input
 */
export function Input({ color = '#1E40AF', ...props }) {
  return (
    <input
      className="w-full px-3 py-2 rounded-lg text-sm text-slate-700 outline-none transition-all"
      style={{
        border: '1.5px solid #E2E8F0',
        background: '#FAFAFA',
      }}
      onFocus={e => { e.target.style.borderColor = color; e.target.style.background = '#fff' }}
      onBlur={e  => { e.target.style.borderColor = '#E2E8F0'; e.target.style.background = '#FAFAFA' }}
      {...props}
    />
  )
}

/**
 * Select — styled select
 */
export function Select({ color = '#1E40AF', children, ...props }) {
  return (
    <select
      className="w-full px-3 py-2 rounded-lg text-sm text-slate-700 outline-none transition-all cursor-pointer"
      style={{ border: '1.5px solid #E2E8F0', background: '#FAFAFA' }}
      onFocus={e => { e.target.style.borderColor = color }}
      onBlur={e  => { e.target.style.borderColor = '#E2E8F0' }}
      {...props}
    >
      {children}
    </select>
  )
}
