// ── API Base URL ────────────────────────────────────────────
// En Kubernetes: tráfico va por el Ingress Nginx hacia cada módulo
// En Docker Compose: proxy de Vite redirige /api
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// ── Module API Paths ────────────────────────────────────────
export const API_PATHS = {
  commercial: `${API_BASE_URL}/api/commercial`,
  inventory:  `${API_BASE_URL}/api/inventory`,
  accounting: `${API_BASE_URL}/api/accounting`,
  operations: `${API_BASE_URL}/api/operations`,
  hr:         `${API_BASE_URL}/api/hr`,
}

// ── Module Colors (matches tailwind.config.js) ──────────────
export const MODULE_COLORS = {
  commercial: '#10B981',
  inventory:  '#3B82F6',
  accounting: '#EF4444',
  operations: '#F97316',
  hr:         '#A855F7',
}

// ── Module Labels ───────────────────────────────────────────
export const MODULE_LABELS = {
  commercial: 'Comercial',
  inventory:  'Inventario',
  accounting: 'Contabilidad',
  operations: 'Operaciones',
  hr:         'Recursos Humanos',
}

// ── Status badges ───────────────────────────────────────────
export const SALE_STATUSES    = ['PENDING', 'CONFIRMED', 'CANCELLED', 'PENDING_INVENTORY']
export const ENTRY_STATUSES   = ['DRAFT', 'POSTED', 'REVERSED']
export const PROCESS_STATUSES = ['PLANNING', 'IN_PROGRESS', 'COMPLETED', 'ON_HOLD']
export const EMPLOYEE_STATUSES = ['ACTIVE', 'INACTIVE', 'ON_LEAVE']

// ── Status → color map (Tailwind classes) ───────────────────
export const STATUS_COLORS = {
  // Sales
  PENDING:           'bg-yellow-100 text-yellow-800',
  CONFIRMED:         'bg-green-100 text-green-800',
  CANCELLED:         'bg-red-100 text-red-800',
  PENDING_INVENTORY: 'bg-orange-100 text-orange-800',
  // Accounting
  DRAFT:             'bg-gray-100 text-gray-700',
  POSTED:            'bg-blue-100 text-blue-800',
  REVERSED:          'bg-red-100 text-red-800',
  // Operations
  PLANNING:          'bg-purple-100 text-purple-800',
  IN_PROGRESS:       'bg-blue-100 text-blue-800',
  COMPLETED:         'bg-green-100 text-green-800',
  ON_HOLD:           'bg-yellow-100 text-yellow-800',
  // HR
  ACTIVE:            'bg-green-100 text-green-800',
  INACTIVE:          'bg-gray-100 text-gray-700',
  ON_LEAVE:          'bg-orange-100 text-orange-800',
}

// ── Environment ─────────────────────────────────────────────
export const APP_ENV = import.meta.env.VITE_ENVIRONMENT || 'local'
