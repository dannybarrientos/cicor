import { STATUS_COLORS } from '../../utils/constants.js'

/**
 * Table — componente reutilizable de datos
 *
 * Props:
 *   columns : [{ key, label, render? }]
 *   data    : array de objetos
 *   color   : hex (color del módulo)
 *   onEdit  : fn(row)
 *   onDelete: fn(row)
 *   loading : boolean
 *   emptyText : string
 */
export default function Table({
  columns,
  data = [],
  color = '#1E40AF',
  onEdit,
  onDelete,
  loading = false,
  emptyText = 'No hay registros',
}) {
  if (loading) {
    return (
      <div className="flex flex-col gap-2 py-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-12 rounded-xl animate-pulse" style={{ background: '#F1F5F9' }} />
        ))}
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="py-16 flex flex-col items-center gap-3 text-slate-400">
        <svg className="w-10 h-10 opacity-40" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round"
                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0H4" />
        </svg>
        <p className="text-sm">{emptyText}</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-xl" style={{ border: '1px solid #E2E8F0' }}>
      <table className="w-full text-sm">
        <thead>
          <tr style={{ background: '#F8FAFF', borderBottom: '1px solid #E2E8F0' }}>
            {columns.map(col => (
              <th key={col.key}
                  className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500 whitespace-nowrap">
                {col.label}
              </th>
            ))}
            {(onEdit || onDelete) && (
              <th className="text-right px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Acciones
              </th>
            )}
          </tr>
        </thead>

        <tbody>
          {data.map((row, i) => (
            <tr key={row.id ?? i}
                className="transition-colors hover:bg-slate-50"
                style={{ borderBottom: i < data.length - 1 ? '1px solid #F1F5F9' : 'none' }}>

              {columns.map(col => (
                <td key={col.key} className="px-4 py-3 text-slate-700 whitespace-nowrap">
                  {col.render
                    ? col.render(row[col.key], row)
                    : col.key === 'status'
                      ? <StatusBadge status={row[col.key]} />
                      : String(row[col.key] ?? '—')}
                </td>
              ))}

              {(onEdit || onDelete) && (
                <td className="px-4 py-3">
                  <div className="flex items-center justify-end gap-2">
                    {onEdit && (
                      <button onClick={() => onEdit(row)}
                              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                              title="Editar">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round"
                                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                    )}
                    {onDelete && (
                      <button onClick={() => onDelete(row)}
                              className="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                              title="Eliminar">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round"
                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    )}
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function StatusBadge({ status }) {
  const classes = STATUS_COLORS[status] || 'bg-gray-100 text-gray-600'
  return (
    <span className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full ${classes}`}>
      {status}
    </span>
  )
}
