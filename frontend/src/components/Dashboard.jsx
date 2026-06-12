import { Link } from 'react-router-dom'

const MODULES = [
  {
    path:        '/commercial',
    code:        'C',
    label:       'Comercial',
    description: 'Gestión de ventas y relación con inventario',
    color:       '#10B981',
    bg:          '#ECFDF5',
    stat:        'CRUD: Ventas',
    extra:       '→ Integra con Inventario',
  },
  {
    path:        '/inventory',
    code:        'I',
    label:       'Inventario',
    description: 'Gestión de productos y control de stock',
    color:       '#3B82F6',
    bg:          '#EFF6FF',
    stat:        'CRUD: Productos',
    extra:       '← Reservas desde Comercial',
  },
  {
    path:        '/accounting',
    code:        'C',
    label:       'Contabilidad',
    description: 'Registro y control de asientos contables',
    color:       '#EF4444',
    bg:          '#FEF2F2',
    stat:        'CRUD: Asientos',
    extra:       'Status: DRAFT / POSTED',
  },
  {
    path:        '/operations',
    code:        'O',
    label:       'Operaciones',
    description: 'Gestión de procesos operacionales',
    color:       '#F97316',
    bg:          '#FFF7ED',
    stat:        'CRUD: Procesos',
    extra:       'Status: PLANNING / IN_PROGRESS',
  },
  {
    path:        '/hr',
    code:        'R',
    label:       'Recursos Humanos',
    description: 'Gestión de empleados y nómina',
    color:       '#A855F7',
    bg:          '#FAF5FF',
    stat:        'CRUD: Empleados',
    extra:       'Status: ACTIVE / ON_LEAVE',
  },
]

export default function Dashboard() {
  return (
    <div className="max-w-7xl mx-auto px-4 lg:px-6 py-8 animate-fade-in">

      {/* Header */}
      <div className="mb-10">
        <p className="text-xs font-mono uppercase tracking-widest text-blue-400 mb-2">
          Plataforma ERP Modular
        </p>
        <h1 className="font-display font-bold text-3xl text-[#0C1E4D] leading-tight">
          Bienvenido a <span style={{ color: '#1E40AF' }}>CICOR</span>
        </h1>
        <p className="text-slate-500 mt-2 text-sm max-w-xl">
          5 módulos independientes · 5 APIs FastAPI · 5 bases de datos PostgreSQL · Kubernetes + Minikube
        </p>
      </div>

      {/* Architecture banner */}
      <div className="rounded-2xl p-5 mb-8 flex flex-wrap gap-4 items-center justify-between"
           style={{ background: 'linear-gradient(135deg, #0C1E4D 0%, #1E40AF 100%)' }}>
        <div>
          <p className="text-blue-200 text-xs font-mono uppercase tracking-wider mb-1">Arquitectura activa</p>
          <p className="text-white font-display font-semibold text-lg">Minikube + Docker · Local</p>
        </div>
        <div className="flex flex-wrap gap-3">
          {['Nginx Ingress', 'RBAC', 'NetworkPolicies', 'Prometheus', 'Grafana'].map(tag => (
            <span key={tag}
                  className="text-xs font-mono px-2.5 py-1 rounded-full"
                  style={{ background: 'rgba(255,255,255,0.12)', color: '#93C5FD', border: '1px solid rgba(255,255,255,0.15)' }}>
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Module cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {MODULES.map(({ path, code, label, description, color, bg, stat, extra }, i) => (
          <Link key={path} to={path}
                className="group block rounded-2xl p-5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-module"
                style={{ background: '#fff', border: `1px solid ${color}22`, animationDelay: `${i * 60}ms` }}>

            {/* Card header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center font-display font-bold text-base"
                     style={{ background: bg, color, border: `2px solid ${color}33` }}>
                  {code}
                </div>
                <div>
                  <h3 className="font-display font-semibold text-[#0C1E4D] text-base leading-tight">{label}</h3>
                  <p className="text-xs text-slate-400 mt-0.5">{stat}</p>
                </div>
              </div>
              <svg className="w-4 h-4 text-slate-300 group-hover:text-slate-500 transition-colors mt-1"
                   fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </div>

            {/* Description */}
            <p className="text-sm text-slate-500 leading-relaxed mb-3">{description}</p>

            {/* Extra tag */}
            <span className="inline-block text-xs font-mono px-2 py-0.5 rounded-full"
                  style={{ background: bg, color }}>
              {extra}
            </span>
          </Link>
        ))}

        {/* Info card */}
        <div className="rounded-2xl p-5 flex flex-col justify-between"
             style={{ background: '#F8FAFF', border: '1px solid #E2E8F0' }}>
          <div>
            <p className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-2">Accesos rápidos</p>
            <h3 className="font-display font-semibold text-[#0C1E4D] mb-3">Monitoreo</h3>
            <div className="flex flex-col gap-2">
              {[
                { label: 'Prometheus', url: 'http://localhost:30090', color: '#F97316' },
                { label: 'Grafana',    url: 'http://localhost:30300', color: '#1E40AF' },
              ].map(({ label, url, color }) => (
                <a key={label} href={url} target="_blank" rel="noopener noreferrer"
                   className="flex items-center justify-between px-3 py-2 rounded-xl text-sm transition-colors hover:bg-white"
                   style={{ border: '1px solid #E2E8F0' }}>
                  <span className="font-medium" style={{ color }}>{label}</span>
                  <span className="text-xs text-slate-400 font-mono">{url.split('//')[1]}</span>
                </a>
              ))}
            </div>
          </div>
          <p className="text-xs text-slate-400 mt-4 font-mono">
            minikube ip → reemplaza localhost
          </p>
        </div>
      </div>

      {/* Interaction note */}
      <div className="mt-6 rounded-xl px-5 py-4 flex items-center gap-3"
           style={{ background: '#ECFDF5', border: '1px solid #A7F3D0' }}>
        <svg className="w-5 h-5 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <p className="text-sm text-emerald-800">
          <span className="font-semibold">Interacción activa:</span>{' '}
          Al crear una venta en Comercial, se hace automáticamente un <code className="font-mono bg-emerald-100 px-1 rounded">POST /api/inventory/reserve</code> para reservar stock.
        </p>
      </div>
    </div>
  )
}
