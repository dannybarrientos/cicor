import { useState, useEffect, useCallback } from 'react'
import Table                          from '../shared/Table.jsx'
import Modal, { FormField, Input, Select } from '../shared/Modal.jsx'
import Button                         from '../shared/Button.jsx'
import Notification, { notify }       from '../shared/Notification.jsx'
import { commercialApi, inventoryApi } from '../../utils/api.js'
import { SALE_STATUSES }              from '../../utils/constants.js'

const COLOR = '#10B981'
const BG    = '#ECFDF5'

// ── Mock data (fallback si API no disponible) ────────────────
const MOCK_SALES = [
  { id: 1, product_name: 'Laptop',   quantity: 5,  unit_price: 500, total_amount: 2500, customer_name: 'Acme Corp',       sale_date: '2024-01-15', status: 'CONFIRMED' },
  { id: 2, product_name: 'Mouse',    quantity: 50, unit_price: 25,  total_amount: 1250, customer_name: 'TechStartup Inc', sale_date: '2024-01-16', status: 'PENDING'   },
]

const EMPTY_FORM = { product_name: '', quantity: '', unit_price: '', customer_name: '', status: 'PENDING' }

const COLUMNS = [
  { key: 'id',            label: 'ID'        },
  { key: 'product_name',  label: 'Producto'  },
  { key: 'quantity',      label: 'Cant.'     },
  { key: 'unit_price',    label: 'P. Unit.', render: v => `$${Number(v).toFixed(2)}` },
  { key: 'total_amount',  label: 'Total',    render: v => `$${Number(v).toFixed(2)}` },
  { key: 'customer_name', label: 'Cliente'   },
  { key: 'sale_date',     label: 'Fecha',    render: v => v?.slice(0, 10) },
  { key: 'status',        label: 'Estado'    },
]

export default function Commercial() {
  const [sales,        setSales]        = useState(MOCK_SALES)
  const [loading,      setLoading]      = useState(false)
  const [apiAvailable, setApiAvailable] = useState(false)
  const [modalOpen,    setModalOpen]    = useState(false)
  const [editRow,      setEditRow]      = useState(null)
  const [form,         setForm]         = useState(EMPTY_FORM)
  const [submitting,   setSubmitting]   = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  // Fetch from API
  //const fetchSales = useCallback(async () => {
  //  setLoading(true)
  //  try {
  //    const data = await commercialApi.getSales()
  //    setSales(data)
  //    setApiAvailable(true)
  //  } catch {
  //    setApiAvailable(false)
  //    setSales(MOCK_SALES)
  //  } finally {
  //    setLoading(false)
  //  }
  //}, [])

  const fetchSales = useCallback(async () => {
    setLoading(true)
    try {
      console.log('📊 [Commercial] Fetching sales...')
      const data = await commercialApi.getSales()
      
      console.log('✅ [Commercial] Datos recibidos de API:', data)
      console.log(`   └─ Total de ventas: ${data.length}`)
      setSales(data)
      setApiAvailable(true)
    } catch (error) {
      console.error('❌ [Commercial] Error al traer ventas:', error.message)
      console.warn('⚠️ [Commercial] Usando datos MOCK como fallback')
      setApiAvailable(false)
      setSales(MOCK_SALES)
    } finally {
      setLoading(false)
    }
  }, [])

  

  useEffect(() => { fetchSales() }, [fetchSales])

  // Open modal
  const openCreate = () => { setEditRow(null); setForm(EMPTY_FORM); setModalOpen(true) }
  const openEdit   = (row) => {
    setEditRow(row)
    setForm({
      product_name:  row.product_name,
      quantity:      row.quantity,
      unit_price:    row.unit_price,
      customer_name: row.customer_name,
      status:        row.status,
    })
    setModalOpen(true)
  }

  // Submit
  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      const payload = {
        product_name:  form.product_name,
        quantity:      Number(form.quantity),
        unit_price:    Number(form.unit_price),
        customer_name: form.customer_name,
        status:        form.status,
      }

      if (editRow) {
        if (apiAvailable) {
          const updated = await commercialApi.updateSale(editRow.id, payload)
          setSales(s => s.map(r => r.id === editRow.id ? updated : r))
        } else {
          const total = payload.quantity * payload.unit_price
          setSales(s => s.map(r => r.id === editRow.id ? { ...r, ...payload, total_amount: total } : r))
        }
        notify.success('Venta actualizada correctamente')
      } else {
        if (apiAvailable) {
          // Intenta reservar stock en Inventario
          try {
            const reserve = await inventoryApi.reserveStock({
              product_name: payload.product_name,
              quantity:     payload.quantity,
            })
            if (!reserve.success) {
              payload.status = 'PENDING_INVENTORY'
              notify.warning(`Stock insuficiente en Inventario. Venta creada con estado PENDING_INVENTORY.`)
            } else {
              notify.info(`Stock reservado en Inventario. Restante: ${reserve.remaining_stock}`)
            }
          } catch {
            payload.status = 'PENDING_INVENTORY'
            notify.warning('No se pudo conectar con Inventario. Venta marcada como PENDING_INVENTORY.')
          }
          const created = await commercialApi.createSale(payload)
          setSales(s => [...s, created])
        } else {
          // Mock
          const newSale = {
            ...payload,
            id:           sales.length + 1,
            total_amount: payload.quantity * payload.unit_price,
            sale_date:    new Date().toISOString(),
          }
          setSales(s => [...s, newSale])
          notify.info('Modo mock: POST /api/inventory/reserve simulado')
        }
        notify.success('Venta creada correctamente')
      }

      setModalOpen(false)
    } catch (err) {
      notify.error(`Error: ${err.message}`)
    } finally {
      setSubmitting(false)
    }
  }

  // Delete
  const handleDelete = async (row) => {
    try {
      if (apiAvailable) await commercialApi.deleteSale(row.id)
      setSales(s => s.filter(r => r.id !== row.id))
      notify.success('Venta eliminada')
    } catch (err) {
      notify.error(`Error al eliminar: ${err.message}`)
    } finally {
      setDeleteConfirm(null)
    }
  }

  const field = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  return (
    <div className="max-w-7xl mx-auto px-4 lg:px-6 py-8 animate-fade-in">
      <Notification />

      {/* Header */}
      <ModuleHeader
        code="C" label="Comercial" color={COLOR} bg={BG}
        description="Gestión de ventas · Interacción con Inventario"
        apiAvailable={apiAvailable}
        onRefresh={fetchSales}
        onNew={openCreate}
        newLabel="Nueva Venta"
      />

      {/* Interaction badge */}
      <div className="mb-5 flex items-center gap-2 text-xs px-3 py-2 rounded-lg w-fit"
           style={{ background: '#F0FDF4', border: '1px solid #BBF7D0', color: '#15803D' }}>
        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Al crear una venta se hace automáticamente <code className="font-mono mx-1 bg-green-100 px-1 rounded">POST /api/inventory/reserve</code>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl shadow-card p-5">
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm font-medium text-slate-600">
            {sales.length} {sales.length === 1 ? 'venta' : 'ventas'}
          </p>
        </div>
        <Table
          columns={COLUMNS}
          data={sales}
          color={COLOR}
          loading={loading}
          onEdit={openEdit}
          onDelete={(row) => setDeleteConfirm(row)}
          emptyText="No hay ventas registradas"
        />
      </div>

      {/* Create / Edit Modal */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editRow ? 'Editar Venta' : 'Crear Nueva Venta'}
        color={COLOR}
        onSubmit={handleSubmit}
        loading={submitting}
      >
        <FormField label="Producto">
          <Input color={COLOR} value={form.product_name} onChange={field('product_name')} placeholder="Nombre del producto" required />
        </FormField>
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Cantidad">
            <Input color={COLOR} type="number" min="1" value={form.quantity} onChange={field('quantity')} placeholder="0" required />
          </FormField>
          <FormField label="Precio Unitario">
            <Input color={COLOR} type="number" step="0.01" min="0" value={form.unit_price} onChange={field('unit_price')} placeholder="0.00" required />
          </FormField>
        </div>
        <FormField label="Cliente">
          <Input color={COLOR} value={form.customer_name} onChange={field('customer_name')} placeholder="Nombre del cliente" required />
        </FormField>
        {editRow && (
          <FormField label="Estado">
            <Select color={COLOR} value={form.status} onChange={field('status')}>
              {SALE_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
            </Select>
          </FormField>
        )}
        {/* Total preview */}
        {form.quantity && form.unit_price && (
          <div className="flex items-center justify-between px-3 py-2 rounded-lg text-sm"
               style={{ background: BG }}>
            <span className="text-slate-600">Total estimado:</span>
            <span className="font-display font-bold" style={{ color: COLOR }}>
              ${(Number(form.quantity) * Number(form.unit_price)).toFixed(2)}
            </span>
          </div>
        )}
      </Modal>

      {/* Delete confirm */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
             style={{ background: 'rgba(12,30,77,0.45)', backdropFilter: 'blur(4px)' }}>
          <div className="bg-white rounded-2xl shadow-xl p-6 max-w-sm w-full animate-slide-up">
            <h3 className="font-display font-semibold text-[#0C1E4D] mb-2">¿Eliminar venta?</h3>
            <p className="text-sm text-slate-500 mb-5">
              Se eliminará la venta de <strong>{deleteConfirm.product_name}</strong> para{' '}
              <strong>{deleteConfirm.customer_name}</strong>. Esta acción no se puede deshacer.
            </p>
            <div className="flex gap-2 justify-end">
              <Button variant="ghost" onClick={() => setDeleteConfirm(null)}>Cancelar</Button>
              <Button variant="danger" onClick={() => handleDelete(deleteConfirm)}>Eliminar</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Reusable module header ───────────────────────────────────
export function ModuleHeader({ code, label, color, bg, description, apiAvailable, onRefresh, onNew, newLabel }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-2xl flex items-center justify-center font-display font-bold text-xl"
             style={{ background: bg, color, border: `2px solid ${color}33` }}>
          {code}
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-display font-bold text-xl text-[#0C1E4D]">{label}</h1>
            <span className="text-xs font-mono px-2 py-0.5 rounded-full"
                  style={{ background: apiAvailable ? '#ECFDF5' : '#FEF9C3',
                           color: apiAvailable ? '#065F46' : '#854D0E',
                           border: `1px solid ${apiAvailable ? '#A7F3D0' : '#FDE68A'}` }}>
              {apiAvailable ? '● API' : '○ Mock'}
            </span>
          </div>
          <p className="text-sm text-slate-500">{description}</p>
        </div>
      </div>
      <div className="flex gap-2">
        <Button variant="ghost" onClick={onRefresh} size="sm">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Actualizar
        </Button>
        <Button variant="primary" color={color} onClick={onNew} size="sm">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          {newLabel}
        </Button>
      </div>
    </div>
  )
}
