import clsx from 'clsx'

export function Card({ children, className, glow }) {
  const glowClass = glow === 'green' ? 'glow-green' : glow === 'red' ? 'glow-red' : glow === 'yellow' ? 'glow-yellow' : ''
  return (
    <div className={clsx('glass rounded-xl p-5', glowClass, className)}>
      {children}
    </div>
  )
}

export function CardHeader({ title, subtitle, icon: Icon, action }) {
  return (
    <div className="flex items-start justify-between mb-4">
      <div className="flex items-center gap-3">
        {Icon && (
          <div className="w-9 h-9 rounded-lg bg-brand-500/20 flex items-center justify-center">
            <Icon size={18} className="text-brand-400" />
          </div>
        )}
        <div>
          <h3 className="text-sm font-semibold text-white">{title}</h3>
          {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
        </div>
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}
