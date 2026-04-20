import clsx from 'clsx'

const variants = {
  green: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  yellow: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  red: 'bg-red-500/20 text-red-400 border-red-500/30',
  unknown: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  blue: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
}

const dots = {
  green: 'bg-emerald-400',
  yellow: 'bg-yellow-400',
  red: 'bg-red-400',
  unknown: 'bg-gray-400',
  blue: 'bg-blue-400',
}

export function StatusBadge({ status, label, pulse = false }) {
  const v = variants[status] || variants.unknown
  const d = dots[status] || dots.unknown
  const text = label || status?.toUpperCase() || 'UNKNOWN'

  return (
    <span className={clsx('inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border font-mono', v)}>
      <span className={clsx('w-1.5 h-1.5 rounded-full', d, pulse && 'animate-pulse')} />
      {text}
    </span>
  )
}

export function Badge({ children, color = 'blue' }) {
  return (
    <span className={clsx('px-2 py-0.5 rounded text-xs font-medium border', variants[color])}>
      {children}
    </span>
  )
}
