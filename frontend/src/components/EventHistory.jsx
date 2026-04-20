import { Clock, Trash2 } from 'lucide-react'
import { Card, CardHeader } from './ui/Card'
import { StatusBadge } from './ui/Badge'
import { SkeletonBlock } from './ui/Spinner'
import { format } from 'date-fns'
import { api } from '../services/api'

const COMPONENT_LABELS = {
  cluster: 'Clúster',
  manager: 'Manager',
  agents: 'Agentes',
  indexer: 'Indexer',
}

export function EventHistory({ events, loading, onClear }) {
  const handleClear = async () => {
    await api.clearHistory()
    if (onClear) onClear()
  }

  return (
    <Card>
      <CardHeader
        title="Historial de Eventos"
        subtitle={`${events?.length || 0} eventos registrados`}
        icon={Clock}
        action={
          <button
            onClick={handleClear}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-dark-600 hover:bg-red-900/30 text-gray-400 hover:text-red-400 text-xs transition-colors"
          >
            <Trash2 size={12} />
            Limpiar
          </button>
        }
      />

      {loading ? (
        <div className="space-y-2">
          {[1, 2, 3].map(i => <SkeletonBlock key={i} className="h-12 w-full" />)}
        </div>
      ) : !events || events.length === 0 ? (
        <div className="text-center py-8 text-gray-500 text-sm">
          <Clock size={24} className="mx-auto mb-2 opacity-30" />
          <p>Sin eventos registrados</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
          {events.map(event => (
            <div
              key={event.id}
              className="flex items-start gap-3 p-3 rounded-lg bg-dark-700/60 border border-dark-600"
            >
              <div className="mt-0.5">
                <StatusBadge status={event.severity} label={event.severity.toUpperCase()} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-medium text-gray-300">
                    {COMPONENT_LABELS[event.component] || event.component}
                  </span>
                  <span className="text-xs text-gray-600">—</span>
                  <span className="text-xs text-gray-400">{event.message}</span>
                </div>
                <p className="text-xs text-gray-600 font-mono mt-1">
                  {format(new Date(event.timestamp), 'dd/MM/yyyy HH:mm:ss')}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
