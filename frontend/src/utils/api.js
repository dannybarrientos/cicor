import { API_PATHS } from './constants.js'

// ── Generic fetcher ─────────────────────────────────────────
//async function request(url, options = {}) {
//  const defaultHeaders = { 'Content-Type': 'application/json' }
//
//  const response = await fetch(url, {
//    ...options,
//    headers: { ...defaultHeaders, ...options.headers },
//  })
//
//  if (!response.ok) {
//    const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
//    throw new Error(error.detail || `Error ${response.status}`)
//  }
//
//  // 204 No Content
//  if (response.status === 204) return null
//  return response.json()
//}

// ── Generic fetcher con mejor manejo de errores ─────────────
async function request(url, options = {}) {
  const defaultHeaders = { 'Content-Type': 'application/json' }

  try {
    console.log(`🔵 [API] GET/POST: ${url}`)  // LOG 1
    
    const response = await fetch(url, {
      ...options,
      headers: { ...defaultHeaders, ...options.headers },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
      console.error(`❌ [API] Error ${response.status}:`, error)  // LOG 2
      throw new Error(error.detail || `Error ${response.status}`)
    }

    if (response.status === 204) return null
    
    const data = await response.json()
    console.log(`✅ [API] Success:`, data)  // LOG 3
    return data
    
  } catch (err) {
    console.error(`🔴 [API] Request failed:`, err.message, `URL: ${url}`)  // LOG 4
    throw err
  }
}

// ──────────────────────────────────────────────────────────────
// COMERCIAL
// ──────────────────────────────────────────────────────────────
export const commercialApi = {
  getSales:     ()        => request(`${API_PATHS.commercial}/sales`),
  createSale:   (body)    => request(`${API_PATHS.commercial}/sales`, { method: 'POST', body: JSON.stringify(body) }),
  updateSale:   (id, body) => request(`${API_PATHS.commercial}/sales/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteSale:   (id)      => request(`${API_PATHS.commercial}/sales/${id}`, { method: 'DELETE' }),
  getInfo:      ()        => request(`${API_PATHS.commercial}/info`),
}

// ──────────────────────────────────────────────────────────────
// INVENTARIO
// ──────────────────────────────────────────────────────────────
export const inventoryApi = {
  getProducts:    ()         => request(`${API_PATHS.inventory}/products`),
  createProduct:  (body)     => request(`${API_PATHS.inventory}/products`, { method: 'POST', body: JSON.stringify(body) }),
  updateProduct:  (id, body) => request(`${API_PATHS.inventory}/products/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteProduct:  (id)       => request(`${API_PATHS.inventory}/products/${id}`, { method: 'DELETE' }),
  reserveStock:   (body)     => request(`${API_PATHS.inventory}/reserve`, { method: 'POST', body: JSON.stringify(body) }),
  getInfo:        ()         => request(`${API_PATHS.inventory}/info`),
}

// ──────────────────────────────────────────────────────────────
// CONTABILIDAD
// ──────────────────────────────────────────────────────────────
export const accountingApi = {
  getEntries:    ()         => request(`${API_PATHS.accounting}/entries`),
  createEntry:   (body)     => request(`${API_PATHS.accounting}/entries`, { method: 'POST', body: JSON.stringify(body) }),
  updateEntry:   (id, body) => request(`${API_PATHS.accounting}/entries/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteEntry:   (id)       => request(`${API_PATHS.accounting}/entries/${id}`, { method: 'DELETE' }),
  getInfo:       ()         => request(`${API_PATHS.accounting}/info`),
}

// ──────────────────────────────────────────────────────────────
// OPERACIONES
// ──────────────────────────────────────────────────────────────
export const operationsApi = {
  getProcesses:   ()         => request(`${API_PATHS.operations}/processes`),
  createProcess:  (body)     => request(`${API_PATHS.operations}/processes`, { method: 'POST', body: JSON.stringify(body) }),
  updateProcess:  (id, body) => request(`${API_PATHS.operations}/processes/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteProcess:  (id)       => request(`${API_PATHS.operations}/processes/${id}`, { method: 'DELETE' }),
  getInfo:        ()         => request(`${API_PATHS.operations}/info`),
}

// ──────────────────────────────────────────────────────────────
// RRHH
// ──────────────────────────────────────────────────────────────
export const hrApi = {
  getEmployees:   ()         => request(`${API_PATHS.hr}/employees`),
  createEmployee: (body)     => request(`${API_PATHS.hr}/employees`, { method: 'POST', body: JSON.stringify(body) }),
  updateEmployee: (id, body) => request(`${API_PATHS.hr}/employees/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteEmployee: (id)       => request(`${API_PATHS.hr}/employees/${id}`, { method: 'DELETE' }),
  getInfo:        ()         => request(`${API_PATHS.hr}/info`),
}

// ──────────────────────────────────────────────────────────────
// Health checks
// ──────────────────────────────────────────────────────────────
export async function checkHealth(module) {
  const base = API_PATHS[module]
  try {
    const res = await fetch(`${base.replace(`/api/${module}`, '')}/health/ready`)
    return res.ok
  } catch {
    return false
  }
}
