import { Activity, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react'
import { Card, CardHeader } from './ui/Card'
import { StatusBadge } from './ui/Badge'
import { SkeletonBlock } from './ui/Spinner'

const scoreTone = {
  green: 'text-emerald-400',
  yellow: 'text-yellow-400',
  red: 'text-red-400',
  unknown: 'text-gray-400',
}

const statusIcon = {
  green: CheckCircle2,
  yellow: AlertTriangle,
  red: XCircle,
  unknown: AlertTriangle,
}

function ScoreRow({ item }) {
  const Icon = statusIcon[item.status] || AlertTriangle
  return (
    <div className="py-2.5 border-b border-dark-600 last:border-0">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 min-w-0">
          <Icon size={14} className={scoreTone[item.status] || 'text-gray-400'} />
          <span className="text-sm text-gray-300 truncate">{item.label}</span>
        </div>
        <div className="text-right shrink-0">
          <span className={`font-mono text-sm font-semibold ${scoreTone[item.status] || 'text-white'}`}>
            {item.score}
          </span>
          <span className="text-xs text-gray-600 font-mono"> peso {item.weight}%</span>
        </div>
      </div>
      {item.detail && <p className="text-xs text-gray-500 mt-1 ml-6">{item.detail}</p>}
    </div>
  )
}

export function HealthScore({ healthScore, loading }) {
  const status = healthScore?.status || 'unknown'

  return (
    <Card glow={status === 'green' ? 'green' : status === 'red' ? 'red' : status === 'yellow' ? 'yellow' : undefined}>
      <CardHeader
        title="Health Score"
        subtitle="Puntaje operacional del ecosistema"
        icon={Activity}
        action={loading ? null : <StatusBadge status={status} />}
      />

      {loading ? (
        <div className="space-y-3">
          <SkeletonBlock className="h-16 w-full" />
          {[1, 2, 3, 4].map(i => <SkeletonBlock key={i} className="h-9 w-full" />)}
        </div>
      ) : !healthScore ? (
        <p className="text-gray-500 text-sm py-4 text-center">Sin datos de score</p>
      ) : (
        <div>
          <div className="flex items-end justify-between gap-4 mb-4">
            <div>
              <p className={`font-mono text-5xl font-bold ${scoreTone[status] || 'text-white'}`}>
                {healthScore.score}
              </p>
              <p className="text-xs text-gray-500 mt-1">de 100</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-white font-medium">{healthScore.summary}</p>
              <p className="text-xs text-gray-500 mt-1">
                Latencia API: {healthScore.api_latency_ms ?? '-'} ms
              </p>
              <p className="text-xs text-gray-500">
                Errores backend: {healthScore.backend_errors_recent}
              </p>
            </div>
          </div>

          <div>
            {healthScore.breakdown?.map(item => (
              <ScoreRow key={item.name} item={item} />
            ))}
          </div>
        </div>
      )}
    </Card>
  )
}
