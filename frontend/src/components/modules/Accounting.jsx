import { useState, useEffect, useCallback } from 'react'
import Table                                from '../shared/Table.jsx'
import Modal, { FormField, Input, Select }  from '../shared/Modal.jsx'
import Notification, { notify }             from '../shared/Notification.jsx'
import { accountingApi }                    from '../../utils/api.js'
import { ENTRY_STATUSES }                   from '../../utils/constants.js'
import { ModuleHeader }                     from './Commercial.jsx'

const COLOR = '#EF4444'
const BG    = '#FEF2F2'

const MOCK_ENTRIES = [
  { id: 1, account_code: '1000', account_name: 'Assets',      debit: 1000.00, credit: null,   description: 'Initial entry',    entry_date: '2024-01-15', status: 'DRAFT'  },
  { id: 2, account_code: '2000', account_name: 'Liabilities', debit: null,    credit: 500.00, description: 'Invoice payment',  entry_date: '2024-01-16', status: 'POSTED' },
]

const EMPTY_FORM = { account_code: '', account_name: '', debit: '', credit: '', description: '', entry_date: '', status: 'DRAFT' }

const normalizeEntry = (row) => ({
  ...row,
  debit: row.debit != null ? Number(row.debit) : null,
  credit: row.credit != null ? Number(row.credit) : null,
})

const COLUMNS = [
  { key: 'id',           label: 'ID'         },
  { key: 'account_code', label: 'Código'     },
  { key: 'account_name', label: 'Cuenta'     },
  { key: 'debit',        label: 'Débito',  render: v => v != null ? <span className="font-mono text-green-700">${Number(v).toFixed(2)}</span> : '—' },
  { key: 'credit',       label: 'Crédito', render: v => v != null ? <span className="font-mono text-red-600">${Number(v).toFixed(2)}</span>   : '—' },
  { key: 'entry_date',   label: 'Fecha',   render: v => v?.slice(0, 10) },
  { key: 'status',       label: 'Estado'     },
]

export default function Accounting() {
  const [entries,      setEntries]      = useState(MOCK_ENTRIES)
  const [loading,      setLoading]      = useState(false)
  const [apiAvailable, setApiAvailable] = useState(false)
  const [modalOpen,    setModalOpen]    = useState(false)
  const [editRow,      setEditRow]      = useState(null)
  const [form,         setForm]         = useState(EMPTY_FORM)
  const [submitting,   setSubmitting]   = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  //const fetchEntries = useCallback(async () => {
  //  setLoading(true)
  //  try {
  //    const data = await accountingApi.getEntries()
  //    setEntries(data)
  //    setApiAvailable(true)
  //  } catch {
  //    setApiAvailable(false)
  //    setEntries(MOCK_ENTRIES)
  //  } finally {
  //    setLoading(false)
  //  }
  //}, [])

  const fetchEntries = useCallback(async () => {
    setLoading(true)
    try {
      console.log('💰 [Accounting] Fetching entries...')
      const data = await accountingApi.getEntries()
      
      const normalized = Array.isArray(data) ? data.map(normalizeEntry) : []
      console.log('✅ [Accounting] Datos recibidos de API:', normalized)
      console.log(`   └─ Total de asientos: ${normalized.length}`)
      setEntries(normalized)
      setApiAvailable(true)
    } catch (error) {
      console.error('❌ [Accounting] Error al traer asientos:', error.message)
      console.warn('⚠️ [Accounting] Usando datos MOCK como fallback')
      setApiAvailable(false)
      setEntries(MOCK_ENTRIES)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchEntries() }, [fetchEntries])

  const openCreate = () => { setEditRow(null); setForm({ ...EMPTY_FORM, entry_date: new Date().toISOString().slice(0,10) }); setModalOpen(true) }
  const openEdit   = (row) => {
    setEditRow(row)
    setForm({
      account_code: row.account_code, account_name: row.account_name,
      debit:  row.debit  ?? '', credit: row.credit ?? '',
      description: row.description || '', entry_date: row.entry_date, status: row.status,
    })
    setModalOpen(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.debit && !form.credit) {
      notify.error('Debe ingresar Débito O Crédito (no ambos)')
      return
    }
    if (form.debit && form.credit) {
      notify.error('Solo puede tener Débito O Crédito, no ambos')
      return
    }
    setSubmitting(true)
    const payload = {
      account_code: form.account_code,
      account_name: form.account_name,
      debit:        form.debit  ? Number(form.debit)  : null,
      credit:       form.credit ? Number(form.credit) : null,
      description:  form.description,
      entry_date:   form.entry_date,
      status:       form.status,
    }
    try {
      if (editRow) {
        if (apiAvailable) {
          const u = await accountingApi.updateEntry(editRow.id, payload)
          setEntries(s => s.map(r => r.id === editRow.id ? u : r))
        } else {
          setEntries(s => s.map(r => r.id === editRow.id ? { ...r, ...payload } : r))
        }
        notify.success('Asiento actualizado')
      } else {
        if (apiAvailable) {
          const c = await accountingApi.createEntry(payload)
          setEntries(s => [...s, c])
        } else {
          setEntries(s => [...s, { ...payload, id: s.length + 1 }])
        }
        notify.success('Asiento creado')
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
      if (apiAvailable) await accountingApi.deleteEntry(row.id)
      setEntries(s => s.filter(r => r.id !== row.id))
      notify.success('Asiento eliminado')
    } catch (err) {
      notify.error(`Error: ${err.message}`)
    } finally {
      setDeleteConfirm(null)
    }
  }

  const field = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const totalDebits  = entries.reduce((a, e) => a + Number(e.debit ?? 0), 0)
  const totalCredits = entries.reduce((a, e) => a + Number(e.credit ?? 0), 0)

  return (
    <div className="max-w-7xl mx-auto px-4 lg:px-6 py-8 animate-fade-in">
      <Notification />

      <ModuleHeader
        code="C" label="Contabilidad" color={COLOR} bg={BG}
        description="Registro y control de asientos contables"
        apiAvailable={apiAvailable}
        onRefresh={fetchEntries}
        onNew={openCreate}
        newLabel="Nuevo Asiento"
      />

      {/* Balance summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
        {[
          { label: 'Asientos',       value: entries.length },
          { label: 'Total Débitos',  value: `$${totalDebits.toFixed(2)}`,  color: '#15803D' },
          { label: 'Total Créditos', value: `$${totalCredits.toFixed(2)}`, color: '#DC2626' },
          { label: 'Balance',        value: `$${Math.abs(totalDebits - totalCredits).toFixed(2)}`,
            alert: Math.abs(totalDebits - totalCredits) > 0 },
        ].map(s => (
          <div key={s.label} className="bg-white rounded-xl p-4 shadow-card">
            <p className="text-xs text-slate-500 mb-1">{s.label}</p>
            <p className="font-display font-bold text-xl" style={{ color: s.color ?? (s.alert ? '#F97316' : COLOR) }}>
              {s.value}
            </p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-2xl shadow-card p-5">
        <Table
          columns={COLUMNS}
          data={entries}
          color={COLOR}
          loading={loading}
          onEdit={openEdit}
          onDelete={(row) => setDeleteConfirm(row)}
          emptyText="No hay asientos contables"
        />
      </div>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editRow ? 'Editar Asiento' : 'Nuevo Asiento Contable'}
        color={COLOR}
        onSubmit={handleSubmit}
        loading={submitting}
      >
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Código de Cuenta">
            <Input color={COLOR} value={form.account_code} onChange={field('account_code')} placeholder="1000" required />
          </FormField>
          <FormField label="Nombre de Cuenta">
            <Input color={COLOR} value={form.account_name} onChange={field('account_name')} placeholder="Assets" required />
          </FormField>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Débito (o vacío)">
            <Input color={COLOR} type="number" step="0.01" min="0" value={form.debit}  onChange={field('debit')}  placeholder="0.00" />
          </FormField>
          <FormField label="Crédito (o vacío)">
            <Input color={COLOR} type="number" step="0.01" min="0" value={form.credit} onChange={field('credit')} placeholder="0.00" />
          </FormField>
        </div>
        <FormField label="Descripción">
          <Input color={COLOR} value={form.description} onChange={field('description')} placeholder="Descripción del asiento" />
        </FormField>
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Fecha">
            <Input color={COLOR} type="date" value={form.entry_date} onChange={field('entry_date')} required />
          </FormField>
          <FormField label="Estado">
            <Select color={COLOR} value={form.status} onChange={field('status')}>
              {ENTRY_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
            </Select>
          </FormField>
        </div>
        <p className="text-xs text-slate-400">⚠ Debe ingresar Débito O Crédito, nunca ambos.</p>
      </Modal>

      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
             style={{ background: 'rgba(12,30,77,0.45)', backdropFilter: 'blur(4px)' }}>
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full animate-slide-up">
            <h3 className="font-display font-semibold mb-2">¿Eliminar asiento #{deleteConfirm.id}?</h3>
            <p className="text-sm text-slate-500 mb-4">Esta acción no se puede deshacer.</p>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setDeleteConfirm(null)} className="px-4 py-2 text-sm rounded-xl border border-slate-200 text-slate-600">Cancelar</button>
              <button onClick={() => handleDelete(deleteConfirm)} className="px-4 py-2 text-sm rounded-xl bg-red-500 text-white">Eliminar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
