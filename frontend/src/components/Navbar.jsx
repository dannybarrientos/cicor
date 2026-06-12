import { NavLink, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'

const MODULES = [
  { path: '/',            label: 'Dashboard',        code: '⌂',  color: '#1E40AF' },
  { path: '/commercial',  label: 'Comercial',         code: 'C',  color: '#10B981' },
  { path: '/inventory',   label: 'Inventario',        code: 'I',  color: '#3B82F6' },
  { path: '/accounting',  label: 'Contabilidad',      code: 'C',  color: '#EF4444' },
  { path: '/operations',  label: 'Operaciones',       code: 'O',  color: '#F97316' },
  { path: '/hr',          label: 'Rec. Humanos',      code: 'R',  color: '#A855F7' },
]

function isActiveRoute(pathname, path) {
  return path === '/' ? pathname === '/' : pathname.startsWith(path)
}

function EnvBadge({ compact = false }) {
  return (
    <span
      className={`font-mono rounded-full ${
        compact ? 'text-[10px] px-1.5 py-0.5' : 'text-xs px-2 py-0.5'
      }`}
      style={{
        background: 'rgba(16,185,129,0.15)',
        color: '#34D399',
        border: '1px solid rgba(16,185,129,0.3)',
      }}
    >
      <span
        className="inline-block rounded-full bg-emerald-400 align-middle animate-pulse-dot"
        style={{ width: compact ? 5 : 6, height: compact ? 5 : 6, marginRight: compact ? 4 : 6 }}
      />
      LOCAL
    </span>
  )
}

function NavItem({ path, label, code, color, isActive, onClick, layout = 'desktop' }) {
  const isMobile = layout === 'mobile'

  return (
    <NavLink
      to={path}
      onClick={onClick}
      className={[
        'relative flex items-center rounded-lg font-medium transition-all duration-200',
        isMobile ? 'gap-3 px-3 py-3' : 'gap-2 px-3 py-2 lg:px-3.5',
        isMobile ? 'text-sm' : 'text-xs xl:text-sm',
        isActive
          ? 'text-white shadow-sm'
          : 'text-blue-200 hover:text-white hover:bg-white/10',
      ].join(' ')}
      style={
        isActive
          ? {
              background: `${color}28`,
              color,
              boxShadow: `inset 0 -2px 0 ${color}`,
            }
          : undefined
      }
    >
      <span
        className={[
          'rounded flex items-center justify-center font-bold shrink-0',
          isMobile ? 'w-7 h-7 text-xs' : 'w-5 h-5 text-[10px] xl:w-5 xl:h-5 xl:text-xs',
        ].join(' ')}
        style={{
          background: isActive ? color : 'transparent',
          color: isActive ? '#fff' : color,
          border: `1.5px solid ${color}`,
        }}
      >
        {code}
      </span>
      <span className={isMobile ? 'font-medium' : 'hidden xl:inline'}>{label}</span>
      {!isMobile && (
        <span className="xl:hidden sr-only">{label}</span>
      )}
    </NavLink>
  )
}

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()

  useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  useEffect(() => {
    document.body.style.overflow = mobileOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [mobileOpen])

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 h-16 shadow-sm"
      style={{ background: '#0C1E4D', borderBottom: '1px solid rgba(255,255,255,0.08)' }}
    >
      <div className="max-w-7xl mx-auto h-full flex items-center justify-between gap-3 px-4 lg:px-6">

        {/* Logo */}
        <NavLink to="/" className="flex items-center gap-2.5 group shrink-0">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center font-display font-bold text-sm transition-transform duration-200 group-hover:scale-105"
            style={{
              background: 'linear-gradient(135deg, #1E40AF, #3B82F6)',
              color: '#fff',
              letterSpacing: '-0.5px',
            }}
          >
            C
          </div>
          <span className="font-display font-bold text-white text-base sm:text-lg tracking-tight">
            CICOR <span className="text-blue-300 font-light text-xs sm:text-sm">ERP</span>
          </span>
        </NavLink>

        {/* Desktop / tablet nav — iconos en lg, etiquetas en xl */}
        <nav className="hidden lg:flex items-center gap-0.5 xl:gap-1 flex-1 justify-center max-w-2xl xl:max-w-none">
          {MODULES.map((mod) => (
            <NavItem
              key={mod.path}
              {...mod}
              isActive={isActiveRoute(location.pathname, mod.path)}
              layout="desktop"
            />
          ))}
        </nav>

        {/* Right controls */}
        <div className="flex items-center gap-2 shrink-0">
          <div className="hidden sm:block">
            <EnvBadge />
          </div>
          <div className="sm:hidden">
            <EnvBadge compact />
          </div>

          <button
            type="button"
            className={[
              'lg:hidden p-2 rounded-lg text-white transition-colors duration-200',
              mobileOpen ? 'bg-white/15' : 'hover:bg-white/10',
            ].join(' ')}
            onClick={() => setMobileOpen((o) => !o)}
            aria-label={mobileOpen ? 'Cerrar menú' : 'Abrir menú'}
            aria-expanded={mobileOpen}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              {mobileOpen
                ? <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                : <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile / tablet menu */}
      {mobileOpen && (
        <>
          <button
            type="button"
            className="lg:hidden fixed inset-0 top-16 z-40 bg-[#0C1E4D]/60 backdrop-blur-sm animate-fade-in"
            onClick={() => setMobileOpen(false)}
            aria-label="Cerrar menú"
          />

          <div
            className="lg:hidden absolute top-16 left-0 right-0 z-50 shadow-xl animate-nav-slide-down"
            style={{ background: '#0C1E4D', borderBottom: '1px solid rgba(255,255,255,0.1)' }}
          >
            <nav className="p-3 flex flex-col gap-1 max-h-[calc(100vh-4rem)] overflow-y-auto">
              {MODULES.map((mod) => (
                <NavItem
                  key={mod.path}
                  {...mod}
                  isActive={isActiveRoute(location.pathname, mod.path)}
                  onClick={() => setMobileOpen(false)}
                  layout="mobile"
                />
              ))}
            </nav>
          </div>
        </>
      )}
    </header>
  )
}
