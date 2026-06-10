import { useState, useEffect, useCallback } from 'react'
import Table                                from '../shared/Table.jsx'
import Modal, { FormField, Input, Select }  from '../shared/Modal.jsx'
import Notification, { notify }             from '../shared/Notification.jsx'
import { operationsApi }                    from '../../utils/api.js'
import { PROCESS_STATUSES }                 from '../../utils/constants.js'
import { ModuleHeader }                     from './Commercial.jsx'

const COLOR = '#F97316'
const BG    = '#FFF7ED'

const MOCK_PROCESSES = [
  { id: 1, process_name: 'Supply Chain',      description: 'End-to-end supply chain', owner: 'John Manager', status: 'IN_PROGRESS', start_date: '2024-01-01', expected_end_date: '2024-03-15', actual_end_date: null },
  { id: 2, process_name: 'Quality Assurance', description: 'QA process',              owner: 'Jane Tester',  status: 'PLANNING',     start_date: '2024-02-01', expected_end_date: '2024-04-01', actual_end_date: null },
]

const EMPTY_FORM = { process_name: '', description: '', owner: '', status: 'PLANNING', start_date: '', expected_end_date: '', actual_end_date: '' }

const COLUMNS = [
  { key: 'id',                label: 'ID'          },
  { key: 'process_name',      label: 'Proceso'     },
  { key: 'owner',             label: 'Responsable' },
  { key: 'status',            label: 'Estado'      },
  { key: 'start_date',        label: 'Inicio',     render: v => v?.slice(0,10) },
  { key: 'expected_end_date', label: 'Fin Esperado', render: v => v?.slice(0,10) },
  { key: 'actual_end_date',   label: 'Fin Real',   render: v => v?.slice(0,10) || '—' },
]

export default function Operations() {
  const [processes,    setProcesses]    = useState(MOCK_PROCESSES)
  const [loading,      setLoading]      = useState(false)
  const [apiAvailable, setApiAvailable] = useState(false)
  const [modalOpen,    setModalOpen]    = useState(false)
  const [editRow,      setEditRow]      = useState(null)
  const [form,         setForm]         = useState(EMPTY_FORM)
  const [submitting,   setSubmitting]   = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  //const fetchProcesses = useCallback(async () => {
  //  setLoading(true)
  //  try {
  //    const data = await operationsApi.getProcesses()
  //    setProcesses(data)
  //    setApiAvailable(true)
  //  } catch {
  //    setApiAvailable(false)
  //    setProcesses(MOCK_PROCESSES)
  //  } finally {
  //    setLoading(false)
  //  }
  //}, [])

  const fetchProcesses = useCallback(async () => {
    setLoading(true)
    try {
      console.log('⚙️ [Operations] Fetching processes...')
      const data = await operationsApi.getProcesses()
      
      console.log('✅ [Operations] Datos recibidos de API:', data)
      console.log(`   └─ Total de procesos: ${data.length}`)
      setProcesses(data)
      setApiAvailable(true)
    } catch (error) {
      console.error('❌ [Operations] Error al traer procesos:', error.message)
      console.warn('⚠️ [Operations] Usando datos MOCK como fallback')
      setApiAvailable(false)
      setProcesses(MOCK_PROCESSES)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchProcesses() }, [fetchProcesses])

  const openCreate = () => {
    setEditRow(null)
    setForm({ ...EMPTY_FORM, start_date: new Date().toISOString().slice(0,10) })
    setModalOpen(true)
  }
  const openEdit = (row) => {
    setEditRow(row)
    setForm({
      process_name: row.process_name, description: row.description || '', owner: row.owner || '',
      status: row.status, start_date: row.start_date, expected_end_date: row.expected_end_date || '',
      actual_end_date: row.actual_end_date || '',
    })
    setModalOpen(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    const payload = {
      process_name:      form.process_name,
      description:       form.description,
      owner:             form.owner,
      status:            form.status,
      start_date:        form.start_date,
      expected_end_date: form.expected_end_date || null,
      actual_end_date:   form.actual_end_date   || null,
    }
    try {
      if (editRow) {
        if (apiAvailable) {
          const u = await operationsApi.updateProcess(editRow.id, payload)
          setProcesses(p => p.map(r => r.id === editRow.id ? u : r))
        } else {
          setProcesses(p => p.map(r => r.id === editRow.id ? { ...r, ...payload } : r))
        }
        notify.success('Proceso actualizado')
      } else {
        if (apiAvailable) {
          const c = await operationsApi.createProcess(payload)
          setProcesses(p => [...p, c])
        } else {
          setProcesses(p => [...p, { ...payload, id: p.length + 1 }])
        }
        notify.success('Proceso creado')
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
      if (apiAvailable) await operationsApi.deleteProcess(row.id)
      setProcesses(p => p.filter(r => r.id !== row.id))
      notify.success('Proceso eliminado')
    } catch (err) {
      notify.error(`Error: ${err.message}`)
    } finally {
      setDeleteConfirm(null)
    }
  }

  const field = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const byStatus = PROCESS_STATUSES.reduce((acc, s) => {
    acc[s] = processes.filter(p => p.status === s).length
    return acc
  }, {})

  return (
    <div className="max-w-7xl mx-auto px-4 lg:px-6 py-8 animate-fade-in">
      <Notification />

      <ModuleHeader
        code="O" label="Operaciones" color={COLOR} bg={BG}
        description="Gestión y seguimiento de procesos operacionales"
        apiAvailable={apiAvailable}
        onRefresh={fetchProcesses}
        onNew={openCreate}
        newLabel="Nuevo Proceso"
      />

      {/* Status summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
        {PROCESS_STATUSES.map(s => (
          <div key={s} className="bg-white rounded-xl p-4 shadow-card">
            <p className="text-xs text-slate-500 mb-1">{s.replace('_', ' ')}</p>
            <p className="font-display font-bold text-2xl" style={{ color: COLOR }}>{byStatus[s] || 0}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-2xl shadow-card p-5">
        <Table
          columns={COLUMNS}
          data={processes}
          color={COLOR}
          loading={loading}
          onEdit={openEdit}
          onDelete={(row) => setDeleteConfirm(row)}
          emptyText="No hay procesos registrados"
        />
      </div>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editRow ? 'Editar Proceso' : 'Nuevo Proceso'}
        color={COLOR}
        onSubmit={handleSubmit}
        loading={submitting}
      >
        <FormField label="Nombre del Proceso">
          <Input color={COLOR} value={form.process_name} onChange={field('process_name')} placeholder="Supply Chain" required />
        </FormField>
        <FormField label="Descripción">
          <Input color={COLOR} value={form.description} onChange={field('description')} placeholder="Descripción del proceso" />
        </FormField>
        <FormField label="Responsable">
          <Input color={COLOR} value={form.owner} onChange={field('owner')} placeholder="Nombre del responsable" />
        </FormField>
        <FormField label="Estado">
          <Select color={COLOR} value={form.status} onChange={field('status')}>
            {PROCESS_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
          </Select>
        </FormField>
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Fecha Inicio">
            <Input color={COLOR} type="date" value={form.start_date} onChange={field('start_date')} required />
          </FormField>
          <FormField label="Fin Esperado">
            <Input color={COLOR} type="date" value={form.expected_end_date} onChange={field('expected_end_date')} />
          </FormField>
        </div>
        {editRow && (
          <FormField label="Fin Real">
            <Input color={COLOR} type="date" value={form.actual_end_date} onChange={field('actual_end_date')} />
          </FormField>
        )}
      </Modal>

      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
             style={{ background: 'rgba(12,30,77,0.45)', backdropFilter: 'blur(4px)' }}>
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full animate-slide-up">
            <h3 className="font-display font-semibold mb-2">¿Eliminar proceso?</h3>
            <p className="text-sm text-slate-500 mb-4"><strong>{deleteConfirm.process_name}</strong> será eliminado.</p>
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
