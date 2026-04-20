import { Server, Play, Square } from 'lucide-react'
import { Card, CardHeader } from './ui/Card'
import { StatusBadge } from './ui/Badge'
import { SkeletonBlock } from './ui/Spinner'

const DAEMON_LABELS = {
  wazuh: 'Wazuh Manager',
  wazuh_db: 'Wazuh DB',
  wazuh_analysisd: 'Analysis Daemon',
  wazuh_remoted: 'Remote Daemon',
  wazuh_logcollector: 'Log Collector',
  wazuh_integratord: 'Integrator',
  wazuh_monitord: 'Monitor',
  wazuh_syscheckd: 'Syscheck',
  wazuh_maild: 'Mail',
  wazuh_execd: 'Exec',
  wazuh_authd: 'Auth',
  wazuh_clusterd: 'Cluster',
  wazuh_apid: 'API',
  wazuh_modulesd: 'Modules',
}

function DaemonRow({ name, running }) {
  const label = DAEMON_LABELS[name] || name
  return (
    <div className="flex items-center justify-between py-2 border-b border-dark-600 last:border-0">
      <div className="flex items-center gap-2">
        {running
          ? <Play size={12} className="text-emerald-400" />
          : <Square size={12} className="text-red-400" />
        }
        <span className="text-sm text-gray-300 font-mono">{label}</span>
      </div>
      <StatusBadge status={running ? 'green' : 'red'} label={running ? 'running' : 'stopped'} />
    </div>
  )
}

export function ManagerStatus({ manager, loading }) {
  const allDaemons = [
    ...(manager?.running || []).map(n => ({ name: n, running: true })),
    ...(manager?.stopped || []).map(n => ({ name: n, running: false })),
  ].sort((a, b) => a.name.localeCompare(b.name))

  const glow = manager?.status === 'green' ? 'green' : manager?.status === 'red' ? 'red' : undefined

  return (
    <Card glow={glow}>
      <CardHeader
        title="Manager Status"
        subtitle={`${manager?.running?.length || 0} daemons activos`}
        icon={Server}
        action={loading ? null : <StatusBadge status={manager?.status || 'unknown'} pulse={manager?.status === 'green'} />}
      />

      {loading ? (
        <div className="space-y-2">
          {[1, 2, 3, 4, 5].map(i => <SkeletonBlock key={i} className="h-8 w-full" />)}
        </div>
      ) : allDaemons.length === 0 ? (
        <p className="text-gray-500 text-sm py-4 text-center">Sin datos de daemons</p>
      ) : (
        <div className="max-h-72 overflow-y-auto pr-1">
          {allDaemons.map(d => <DaemonRow key={d.name} name={d.name} running={d.running} />)}
        </div>
      )}
    </Card>
  )
}
