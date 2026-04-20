import { Users, Wifi, WifiOff, Clock, Server } from 'lucide-react'
import { StatusBadge } from './ui/Badge'
import { SkeletonBlock } from './ui/Spinner'

function Stat({ icon: Icon, label, value, color = 'text-white', loading }) {
  return (
    <div className="flex items-center gap-3 px-5 py-3 border-r border-dark-600 last:border-0">
      <div className="w-8 h-8 rounded-lg bg-dark-600 flex items-center justify-center">
        <Icon size={15} className="text-gray-400" />
      </div>
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        {loading ? (
          <SkeletonBlock className="h-4 w-12 mt-0.5" />
        ) : (
          <p className={`text-sm font-semibold font-mono ${color}`}>{value ?? '—'}</p>
        )}
      </div>
    </div>
  )
}

export function StatsBar({ overview, loading }) {
  const agents = overview?.agents
  const globalStatus = overview?.global_status || 'unknown'

  return (
    <div className="glass rounded-xl flex flex-wrap divide-y divide-dark-600 sm:divide-y-0 sm:divide-x sm:divide-dark-600 mb-6">
      <div className="flex items-center gap-3 px-5 py-3 border-r border-dark-600">
        <span className="text-xs text-gray-500">Estado global</span>
        {loading ? <SkeletonBlock className="h-5 w-16" /> : (
          <StatusBadge status={globalStatus} pulse={globalStatus === 'green'} />
        )}
      </div>

      <Stat icon={Users} label="Agentes totales" value={agents?.total} loading={loading} />
      <Stat
        icon={Wifi}
        label="Activos"
        value={agents?.active}
        color="text-emerald-400"
        loading={loading}
      />
      <Stat
        icon={WifiOff}
        label="Desconectados"
        value={agents?.disconnected}
        color={agents?.disconnected > 0 ? 'text-yellow-400' : 'text-gray-400'}
        loading={loading}
      />
      <Stat icon={Clock} label="Pendientes" value={agents?.pending} loading={loading} />
    </div>
  )
}
