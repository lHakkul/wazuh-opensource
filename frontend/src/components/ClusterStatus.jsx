import { Network, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { Card, CardHeader } from './ui/Card'
import { StatusBadge } from './ui/Badge'
import { SkeletonBlock } from './ui/Spinner'

function NodeRow({ node }) {
  const isConnected = node.status === 'connected'
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-dark-600 last:border-0">
      <div className="flex items-center gap-2.5">
        {isConnected
          ? <CheckCircle size={14} className="text-emerald-400 shrink-0" />
          : <XCircle size={14} className="text-red-400 shrink-0" />
        }
        <div>
          <p className="text-sm font-medium text-white font-mono">{node.name}</p>
          <p className="text-xs text-gray-500">{node.address}</p>
        </div>
      </div>
      <div className="flex items-center gap-2 text-right">
        <div>
          <span className="text-xs text-gray-400 font-mono">{node.type}</span>
          <p className="text-xs text-gray-600">v{node.version}</p>
        </div>
        <StatusBadge status={isConnected ? 'green' : 'red'} label={isConnected ? 'online' : 'offline'} />
      </div>
    </div>
  )
}

export function ClusterStatus({ cluster, loading }) {
  const glow = cluster?.status === 'green' ? 'green' : cluster?.status === 'red' ? 'red' : cluster?.status === 'yellow' ? 'yellow' : undefined

  return (
    <Card glow={glow}>
      <CardHeader
        title="Clúster Wazuh"
        subtitle="Nodos del clúster"
        icon={Network}
        action={loading ? null : <StatusBadge status={cluster?.status || 'unknown'} pulse={cluster?.status === 'green'} />}
      />

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => <SkeletonBlock key={i} className="h-10 w-full" />)}
        </div>
      ) : !cluster ? (
        <div className="flex items-center gap-2 text-yellow-400 text-sm py-4">
          <AlertCircle size={16} />
          <span>No se pudo obtener datos del clúster</span>
        </div>
      ) : (
        <div>
          {cluster.nodes && cluster.nodes.length > 0 ? (
            cluster.nodes.map(n => <NodeRow key={n.name} node={n} />)
          ) : (
            <p className="text-gray-500 text-sm py-4 text-center">Sin nodos en clúster (modo standalone)</p>
          )}
        </div>
      )}
    </Card>
  )
}
