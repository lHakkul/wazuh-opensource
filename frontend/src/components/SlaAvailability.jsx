import { Gauge, ShieldCheck } from 'lucide-react'
import { Card, CardHeader } from './ui/Card'
import { StatusBadge } from './ui/Badge'
import { SkeletonBlock } from './ui/Spinner'

function formatWindow(hours) {
  return hours >= 168 ? 'últimos 7d' : `últimas ${hours}h`
}

function SlaRow({ metric }) {
  const value = Number(metric.availability ?? 0)
  const barColor = metric.status === 'green'
    ? 'bg-emerald-400'
    : metric.status === 'yellow'
      ? 'bg-yellow-400'
      : 'bg-red-400'

  return (
    <div className="py-3 border-b border-dark-600 last:border-0">
      <div className="flex items-center justify-between gap-3 mb-2">
        <div>
          <p className="text-sm font-medium text-white">{metric.label}</p>
          <p className="text-xs text-gray-500">{metric.detail || formatWindow(metric.window_hours)}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="font-mono text-sm font-semibold text-white">{value.toFixed(1)}%</span>
          <StatusBadge status={metric.status} />
        </div>
      </div>
      <div className="h-2 rounded bg-dark-700 overflow-hidden">
        <div className={barColor} style={{ width: `${Math.max(0, Math.min(100, value))}%`, height: '100%' }} />
      </div>
    </div>
  )
}

export function SlaAvailability({ sla, loading }) {
  const metrics = sla?.metrics || []

  return (
    <Card>
      <CardHeader
        title="SLA / Disponibilidad"
        subtitle="Salud observada por ventana"
        icon={ShieldCheck}
        action={<Gauge size={18} className="text-gray-500" />}
      />

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map(i => <SkeletonBlock key={i} className="h-12 w-full" />)}
        </div>
      ) : metrics.length === 0 ? (
        <p className="text-gray-500 text-sm py-4 text-center">Sin métricas de disponibilidad</p>
      ) : (
        <div>
          {metrics.map(metric => <SlaRow key={metric.name} metric={metric} />)}
        </div>
      )}
    </Card>
  )
}
