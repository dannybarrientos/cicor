import { useState, useEffect, useCallback } from 'react'
import Table                          from '../shared/Table.jsx'
import Modal, { FormField, Input }    from '../shared/Modal.jsx'
import Notification, { notify }       from '../shared/Notification.jsx'
import { inventoryApi }               from '../../utils/api.js'
import { ModuleHeader }               from './Commercial.jsx'

const COLOR = '#3B82F6'
const BG    = '#EFF6FF'

const MOCK_PRODUCTS = [
  { id: 1, name: 'Laptop', sku: 'LAP-001', description: 'High-performance laptop', category: 'Electronics',  stock_quantity: 15,  reorder_level: 10, unit_price: 500.00 },
  { id: 2, name: 'Mouse',  sku: 'MOU-001', description: 'Wireless mouse',          category: 'Accessories', stock_quantity: 150, reorder_level: 50, unit_price: 25.00  },
]

const EMPTY_FORM = { name: '', sku: '', description: '', category: '', stock_quantity: '', reorder_level: '10', unit_price: '' }

const COLUMNS = [
  { key: 'id',             label: 'ID'       },
  { key: 'name',           label: 'Nombre'   },
  { key: 'sku',            label: 'SKU',     render: v => <code className="font-mono text-xs bg-blue-50 px-1.5 py-0.5 rounded text-blue-700">{v}</code> },
  { key: 'category',       label: 'Categoría' },
  { key: 'stock_quantity', label: 'Stock',   render: (v) => (
    <span className={`font-semibold ${v <= 10 ? 'text-red-500' : v <= 30 ? 'text-orange-500' : 'text-green-600'}`}>{v}</span>
  )},
  { key: 'reorder_level',  label: 'Reorden'  },
  { key: 'unit_price',     label: 'Precio',  render: v => `$${Number(v).toFixed(2)}` },
]

export default function Inventory() {
  const [products,     setProducts]     = useState(MOCK_PRODUCTS)
  const [loading,      setLoading]      = useState(false)
  const [apiAvailable, setApiAvailable] = useState(false)
  const [modalOpen,    setModalOpen]    = useState(false)
  const [editRow,      setEditRow]      = useState(null)
  const [form,         setForm]         = useState(EMPTY_FORM)
  const [submitting,   setSubmitting]   = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  //const fetchProducts = useCallback(async () => {
  //  setLoading(true)
  //  try {
  //    const data = await inventoryApi.getProducts()
  //    setProducts(data)
  //    setApiAvailable(true)
  //  } catch {
  //    setApiAvailable(false)
  //    setProducts(MOCK_PRODUCTS)
  //  } finally {
  //    setLoading(false)
  //  }
  //}, [])

  const fetchProducts = useCallback(async () => {
    setLoading(true)
    try {
      console.log('📦 [Inventory] Fetching products...')
      const data = await inventoryApi.getProducts()
      
      console.log('✅ [Inventory] Datos recibidos de API:', data)
      console.log(`   └─ Total de productos: ${data.length}`)
      setProducts(data)
      setApiAvailable(true)
    } catch (error) {
      console.error('❌ [Inventory] Error al traer productos:', error.message)
      console.warn('⚠️ [Inventory] Usando datos MOCK como fallback')
      setApiAvailable(false)
      setProducts(MOCK_PRODUCTS)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchProducts() }, [fetchProducts])

  const openCreate = () => { setEditRow(null); setForm(EMPTY_FORM); setModalOpen(true) }
  const openEdit   = (row) => {
    setEditRow(row)
    setForm({ name: row.name, sku: row.sku, description: row.description || '', category: row.category || '',
              stock_quantity: row.stock_quantity, reorder_level: row.reorder_level, unit_price: row.unit_price })
    setModalOpen(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    const payload = {
      name:           form.name,
      sku:            form.sku,
      description:    form.description,
      category:       form.category,
      stock_quantity: Number(form.stock_quantity),
      reorder_level:  Number(form.reorder_level),
      unit_price:     Number(form.unit_price),
    }
    try {
      if (editRow) {
        if (apiAvailable) {
          const updated = await inventoryApi.updateProduct(editRow.id, payload)
          setProducts(p => p.map(r => r.id === editRow.id ? updated : r))
        } else {
          setProducts(p => p.map(r => r.id === editRow.id ? { ...r, ...payload } : r))
        }
        notify.success('Producto actualizado')
      } else {
        if (apiAvailable) {
          const created = await inventoryApi.createProduct(payload)
          setProducts(p => [...p, created])
        } else {
          setProducts(p => [...p, { ...payload, id: p.length + 1 }])
        }
        notify.success('Producto creado')
      }
      setModalOpen(false)
    } catch (err) {
      notify.error(`Error: ${err.message}`)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (row) => {
    try {
      if (apiAvailable) await inventoryApi.deleteProduct(row.id)
      setProducts(p => p.filter(r => r.id !== row.id))
      notify.success('Producto eliminado')
    } catch (err) {
      notify.error(`Error: ${err.message}`)
    } finally {
      setDeleteConfirm(null)
    }
  }

  const field = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  // Low stock alert
  const lowStock = products.filter(p => p.stock_quantity <= p.reorder_level)

  return (
    <div className="max-w-7xl mx-auto px-4 lg:px-6 py-8 animate-fade-in">
      <Notification />

      <ModuleHeader
        code="I" label="Inventario" color={COLOR} bg={BG}
        description="Gestión de productos y control de stock"
        apiAvailable={apiAvailable}
        onRefresh={fetchProducts}
        onNew={openCreate}
        newLabel="Nuevo Producto"
      />

      {/* Low stock alert */}
      {lowStock.length > 0 && (
        <div className="mb-5 flex items-center gap-2 px-4 py-3 rounded-xl text-sm"
             style={{ background: '#FFF7ED', border: '1px solid #FED7AA', color: '#C2410C' }}>
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>
            <strong>{lowStock.length}</strong> producto{lowStock.length > 1 ? 's' : ''} con stock bajo o en nivel de reorden:{' '}
            {lowStock.map(p => p.name).join(', ')}
          </span>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
        {[
          { label: 'Total productos', value: products.length },
          { label: 'Stock bajo',      value: lowStock.length, alert: lowStock.length > 0 },
          { label: 'Categorías',      value: [...new Set(products.map(p => p.category).filter(Boolean))].length },
          { label: 'Valor total',     value: `$${products.reduce((acc, p) => acc + p.stock_quantity * p.unit_price, 0).toFixed(0)}` },
        ].map(stat => (
          <div key={stat.label} className="bg-white rounded-xl p-4 shadow-card">
            <p className="text-xs text-slate-500 mb-1">{stat.label}</p>
            <p className="font-display font-bold text-xl" style={{ color: stat.alert ? '#F97316' : COLOR }}>
              {stat.value}
            </p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-2xl shadow-card p-5">
        <Table
          columns={COLUMNS}
          data={products}
          color={COLOR}
          loading={loading}
          onEdit={openEdit}
          onDelete={(row) => setDeleteConfirm(row)}
          emptyText="No hay productos registrados"
        />
      </div>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editRow ? 'Editar Producto' : 'Nuevo Producto'}
        color={COLOR}
        onSubmit={handleSubmit}
        loading={submitting}
      >
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Nombre">
            <Input color={COLOR} value={form.name} onChange={field('name')} placeholder="Nombre del producto" required />
          </FormField>
          <FormField label="SKU">
            <Input color={COLOR} value={form.sku} onChange={field('sku')} placeholder="LAP-001" required />
          </FormField>
        </div>
        <FormField label="Descripción">
          <Input color={COLOR} value={form.description} onChange={field('description')} placeholder="Descripción breve" />
        </FormField>
        <FormField label="Categoría">
          <Input color={COLOR} value={form.category} onChange={field('category')} placeholder="Electronics, Accessories..." />
        </FormField>
        <div className="grid grid-cols-3 gap-3">
          <FormField label="Stock">
            <Input color={COLOR} type="number" min="0" value={form.stock_quantity} onChange={field('stock_quantity')} placeholder="0" required />
          </FormField>
          <FormField label="Reorden">
            <Input color={COLOR} type="number" min="0" value={form.reorder_level} onChange={field('reorder_level')} placeholder="10" />
          </FormField>
          <FormField label="Precio Unit.">
            <Input color={COLOR} type="number" step="0.01" min="0" value={form.unit_price} onChange={field('unit_price')} placeholder="0.00" required />
          </FormField>
        </div>
      </Modal>

      {deleteConfirm && (
        <DeleteConfirm
          label={deleteConfirm.name}
          onConfirm={() => handleDelete(deleteConfirm)}
          onCancel={() => setDeleteConfirm(null)}
        />
      )}
    </div>
  )
}

function DeleteConfirm({ label, onConfirm, onCancel }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
         style={{ background: 'rgba(12,30,77,0.45)', backdropFilter: 'blur(4px)' }}>
      <div className="bg-white rounded-2xl shadow-xl p-6 max-w-sm w-full animate-slide-up">
        <h3 className="font-display font-semibold text-[#0C1E4D] mb-2">¿Eliminar producto?</h3>
        <p className="text-sm text-slate-500 mb-5">
          Se eliminará <strong>{label}</strong>. Esta acción no se puede deshacer.
        </p>
        <div className="flex gap-2 justify-end">
          <button onClick={onCancel}
                  className="px-4 py-2 text-sm rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors">
            Cancelar
          </button>
          <button onClick={onConfirm}
                  className="px-4 py-2 text-sm rounded-xl bg-red-500 text-white hover:bg-red-600 transition-colors">
            Eliminar
          </button>
        </div>
      </div>
    </div>
  )
}
