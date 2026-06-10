import { useState, useEffect, useCallback } from 'react'
import Table                                from '../shared/Table.jsx'
import Modal, { FormField, Input, Select }  from '../shared/Modal.jsx'
import Notification, { notify }             from '../shared/Notification.jsx'
import { hrApi }                            from '../../utils/api.js'
import { EMPLOYEE_STATUSES }                from '../../utils/constants.js'
import { ModuleHeader }                     from './Commercial.jsx'

const COLOR = '#A855F7'
const BG    = '#FAF5FF'

const MOCK_EMPLOYEES = [
  { id: 1, full_name: 'Jane Smith', email: 'jane@cicor.com', phone: '+1234567890', position: 'Senior Developer', department: 'Engineering',       hire_date: '2022-01-15', salary: 120000, status: 'ACTIVE' },
  { id: 2, full_name: 'John Doe',   email: 'john@cicor.com', phone: '+0987654321', position: 'HR Manager',       department: 'Human Resources',   hire_date: '2021-06-01', salary: 80000,  status: 'ACTIVE' },
]

const EMPTY_FORM = { full_name: '', email: '', phone: '', position: '', department: '', hire_date: '', salary: '', status: 'ACTIVE' }

const COLUMNS = [
  { key: 'id',         label: 'ID'           },
  { key: 'full_name',  label: 'Nombre'       },
  { key: 'email',      label: 'Email',       render: v => <span className="font-mono text-xs text-purple-700">{v}</span> },
  { key: 'position',   label: 'Cargo'        },
  { key: 'department', label: 'Departamento' },
  { key: 'hire_date',  label: 'Ingreso',     render: v => v?.slice(0,10) },
  { key: 'salary',     label: 'Salario',     render: v => `$${Number(v).toLocaleString()}` },
  { key: 'status',     label: 'Estado'       },
]

export default function RRHH() {
  const [employees,    setEmployees]    = useState(MOCK_EMPLOYEES)
  const [loading,      setLoading]      = useState(false)
  const [apiAvailable, setApiAvailable] = useState(false)
  const [modalOpen,    setModalOpen]    = useState(false)
  const [editRow,      setEditRow]      = useState(null)
  const [form,         setForm]         = useState(EMPTY_FORM)
  const [submitting,   setSubmitting]   = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  //const fetchEmployees = useCallback(async () => {
  //  setLoading(true)
  //  try {
  //    const data = await hrApi.getEmployees()
  //    setEmployees(data)
  //    setApiAvailable(true)
  //  } catch {
  //    setApiAvailable(false)
  //    setEmployees(MOCK_EMPLOYEES)
  //  } finally {
  //    setLoading(false)
  //  }
  //}, [])

  const fetchEmployees = useCallback(async () => {
    setLoading(true)
    try {
      console.log('👥 [HR] Fetching employees...')
      const data = await hrApi.getEmployees()
      
      console.log('✅ [HR] Datos recibidos de API:', data)
      console.log(`   └─ Total de empleados: ${data.length}`)
      setEmployees(data)
      setApiAvailable(true)
    } catch (error) {
      console.error('❌ [HR] Error al traer empleados:', error.message)
      console.warn('⚠️ [HR] Usando datos MOCK como fallback')
      setApiAvailable(false)
      setEmployees(MOCK_EMPLOYEES)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchEmployees() }, [fetchEmployees])

  const openCreate = () => {
    setEditRow(null)
    setForm({ ...EMPTY_FORM, hire_date: new Date().toISOString().slice(0,10) })
    setModalOpen(true)
  }
  const openEdit = (row) => {
    setEditRow(row)
    setForm({
      full_name:  row.full_name, email:    row.email,
      phone:      row.phone || '', position: row.position || '',
      department: row.department || '', hire_date: row.hire_date,
      salary:     row.salary, status: row.status,
    })
    setModalOpen(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    const payload = {
      full_name:  form.full_name,
      email:      form.email,
      phone:      form.phone,
      position:   form.position,
      department: form.department,
      hire_date:  form.hire_date,
      salary:     Number(form.salary),
      status:     form.status,
    }
    try {
      if (editRow) {
        if (apiAvailable) {
          const u = await hrApi.updateEmployee(editRow.id, payload)
          setEmployees(e => e.map(r => r.id === editRow.id ? u : r))
        } else {
          setEmployees(e => e.map(r => r.id === editRow.id ? { ...r, ...payload } : r))
        }
        notify.success('Empleado actualizado')
      } else {
        if (apiAvailable) {
          const c = await hrApi.createEmployee(payload)
          setEmployees(e => [...e, c])
        } else {
          setEmployees(e => [...e, { ...payload, id: e.length + 1 }])
        }
        notify.success('Empleado creado')
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
      if (apiAvailable) await hrApi.deleteEmployee(row.id)
      setEmployees(e => e.filter(r => r.id !== row.id))
      notify.success('Empleado eliminado')
    } catch (err) {
      notify.error(`Error: ${err.message}`)
    } finally {
      setDeleteConfirm(null)
    }
  }

  const field = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const active    = employees.filter(e => e.status === 'ACTIVE').length
  const avgSalary = employees.length ? employees.reduce((a, e) => a + Number(e.salary), 0) / employees.length : 0
  const depts     = [...new Set(employees.map(e => e.department).filter(Boolean))].length

  return (
    <div className="max-w-7xl mx-auto px-4 lg:px-6 py-8 animate-fade-in">
      <Notification />

      <ModuleHeader
        code="R" label="Recursos Humanos" color={COLOR} bg={BG}
        description="Gestión de empleados, cargos y nómina"
        apiAvailable={apiAvailable}
        onRefresh={fetchEmployees}
        onNew={openCreate}
        newLabel="Nuevo Empleado"
      />

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
        {[
          { label: 'Total empleados', value: employees.length },
          { label: 'Activos',         value: active,          color: '#10B981' },
          { label: 'Departamentos',   value: depts             },
          { label: 'Salario promedio',value: `$${Math.round(avgSalary).toLocaleString()}` },
        ].map(s => (
          <div key={s.label} className="bg-white rounded-xl p-4 shadow-card">
            <p className="text-xs text-slate-500 mb-1">{s.label}</p>
            <p className="font-display font-bold text-xl" style={{ color: s.color ?? COLOR }}>{s.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-2xl shadow-card p-5">
        <Table
          columns={COLUMNS}
          data={employees}
          color={COLOR}
          loading={loading}
          onEdit={openEdit}
          onDelete={(row) => setDeleteConfirm(row)}
          emptyText="No hay empleados registrados"
        />
      </div>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editRow ? 'Editar Empleado' : 'Nuevo Empleado'}
        color={COLOR}
        onSubmit={handleSubmit}
        loading={submitting}
      >
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Nombre completo">
            <Input color={COLOR} value={form.full_name} onChange={field('full_name')} placeholder="Jane Smith" required />
          </FormField>
          <FormField label="Email">
            <Input color={COLOR} type="email" value={form.email} onChange={field('email')} placeholder="jane@cicor.com" required />
          </FormField>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Teléfono">
            <Input color={COLOR} value={form.phone} onChange={field('phone')} placeholder="+1234567890" />
          </FormField>
          <FormField label="Cargo">
            <Input color={COLOR} value={form.position} onChange={field('position')} placeholder="Senior Developer" />
          </FormField>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Departamento">
            <Input color={COLOR} value={form.department} onChange={field('department')} placeholder="Engineering" />
          </FormField>
          <FormField label="Fecha de ingreso">
            <Input color={COLOR} type="date" value={form.hire_date} onChange={field('hire_date')} required />
          </FormField>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <FormField label="Salario">
            <Input color={COLOR} type="number" min="0" step="0.01" value={form.salary} onChange={field('salary')} placeholder="80000" />
          </FormField>
          <FormField label="Estado">
            <Select color={COLOR} value={form.status} onChange={field('status')}>
              {EMPLOYEE_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
            </Select>
          </FormField>
        </div>
      </Modal>

      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
             style={{ background: 'rgba(12,30,77,0.45)', backdropFilter: 'blur(4px)' }}>
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full animate-slide-up">
            <h3 className="font-display font-semibold mb-2">¿Eliminar empleado?</h3>
            <p className="text-sm text-slate-500 mb-4">
              <strong>{deleteConfirm.full_name}</strong> será eliminado del sistema.
            </p>
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
