/**
 * Button — componente reutilizable CICOR ERP
 *
 * Props:
 *   variant  : 'primary' | 'secondary' | 'danger' | 'ghost'
 *   size     : 'sm' | 'md' | 'lg'
 *   color    : hex string para override de color (módulo específico)
 *   loading  : boolean
 *   disabled : boolean
 *   onClick  : fn
 *   type     : 'button' | 'submit' | 'reset'
 *   children
 */
export default function Button({
  children,
  variant  = 'primary',
  size     = 'md',
  color    = '#1E40AF',
  loading  = false,
  disabled = false,
  onClick,
  type     = 'button',
  className = '',
  ...rest
}) {
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  }

  const baseClasses = [
    'inline-flex items-center justify-center gap-2',
    'font-medium rounded-xl',
    'transition-all duration-150',
    'focus-visible:ring-2 focus-visible:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    sizeClasses[size],
    className,
  ].join(' ')

  const styles = {
    primary: {
      background: disabled || loading ? undefined : color,
      color: '#fff',
      border: 'none',
    },
    secondary: {
      background: `${color}15`,
      color,
      border: `1.5px solid ${color}44`,
    },
    danger: {
      background: '#FEF2F2',
      color: '#DC2626',
      border: '1.5px solid #FECACA',
    },
    ghost: {
      background: 'transparent',
      color: '#64748B',
      border: '1.5px solid #E2E8F0',
    },
  }

  return (
    <button
      type={type}
      className={baseClasses}
      style={styles[variant]}
      onClick={onClick}
      disabled={disabled || loading}
      {...rest}
    >
      {loading && (
        <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      )}
      {children}
    </button>
  )
}
