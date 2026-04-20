import { useState, useMemo } from 'react'
import { Users, Search, ChevronUp, ChevronDown } from 'lucide-react'
import { Card, CardHeader } from './ui/Card'
import { StatusBadge } from './ui/Badge'
import { SkeletonBlock } from './ui/Spinner'
import { formatDistanceToNow } from 'date-fns'
import { es } from 'date-fns/locale'

const STATUS_COLORS = {
  active: 'green',
  disconnected: 'red',
  pending: 'yellow',
  never_connected: 'unknown',
}

const STATUS_LABELS = {
  active: 'Activo',
  disconnected: 'Desconectado',
  pending: 'Pendiente',
  never_connected: 'Sin conectar',
}

function AgentRow({ agent }) {
  const lastSeen = agent.last_keepalive
    ? formatDistanceToNow(new Date(agent.last_keepalive), { addSuffix: true, locale: es })
    : '—'

  return (
    <tr className="border-b border-dark-600 hover:bg-dark-700/50 transition-colors">
      <td className="px-4 py-3 font-mono text-xs text-gray-400">{agent.id.padStart(3, '0')}</td>
      <td className="px-4 py-3">
        <span className="text-sm text-white font-medium">{agent.name}</span>
      </td>
      <td className="px-4 py-3 text-xs text-gray-400 font-mono">{agent.ip || '—'}</td>
      <td className="px-4 py-3">
        <span className="text-xs text-gray-400">{agent.os_name || agent.os_platform || '—'}</span>
      </td>
      <td className="px-4 py-3 text-xs text-gray-500 font-mono">{lastSeen}</td>
      <td className="px-4 py-3">
        <StatusBadge
          status={STATUS_COLORS[agent.status] || 'unknown'}
          label={STATUS_LABELS[agent.status] || agent.status}
        />
      </td>
    </tr>
  )
}

export function AgentsTable({ agents, loading }) {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')
  const [sortField, setSortField] = useState('name')
  const [sortDir, setSortDir] = useState('asc')

  const filtered = useMemo(() => {
    if (!agents?.agents) return []
    return agents.agents
      .filter(a => filter === 'all' || a.status === filter)
      .filter(a =>
        !search ||
        a.name.toLowerCase().includes(search.toLowerCase()) ||
        (a.ip || '').includes(search)
      )
      .sort((a, b) => {
        const va = a[sortField] || ''
        const vb = b[sortField] || ''
        return sortDir === 'asc' ? String(va).localeCompare(String(vb)) : String(vb).localeCompare(String(va))
      })
  }, [agents, search, filter, sortField, sortDir])

  const toggle = (field) => {
    if (sortField === field) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortField(field); setSortDir('asc') }
  }

  const SortIcon = ({ field }) => {
    if (sortField !== field) return null
    return sortDir === 'asc' ? <ChevronUp size={12} /> : <ChevronDown size={12} />
  }

  return (
    <Card>
      <CardHeader
        title="Agentes"
        subtitle={`${filtered.length} de ${agents?.total || 0} agentes`}
        icon={Users}
      />

      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder="Buscar por nombre o IP..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full bg-dark-700 border border-dark-500 rounded-lg pl-9 pr-4 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-brand-500"
          />
        </div>
        <div className="flex gap-2">
          {['all', 'active', 'disconnected', 'pending'].map(s => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                filter === s
                  ? 'bg-brand-500 text-white'
                  : 'bg-dark-700 text-gray-400 hover:text-white'
              }`}
            >
              {s === 'all' ? 'Todos' : STATUS_LABELS[s]}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="space-y-2">
          {[1, 2, 3, 4, 5].map(i => <SkeletonBlock key={i} className="h-10 w-full" />)}
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-dark-600">
          <table className="w-full">
            <thead>
              <tr className="bg-dark-700 text-left">
                <th className="px-4 py-2.5 text-xs font-medium text-gray-500">ID</th>
                <th
                  className="px-4 py-2.5 text-xs font-medium text-gray-500 cursor-pointer hover:text-gray-300 select-none"
                  onClick={() => toggle('name')}
                >
                  <div className="flex items-center gap-1">Nombre <SortIcon field="name" /></div>
                </th>
                <th className="px-4 py-2.5 text-xs font-medium text-gray-500">IP</th>
                <th className="px-4 py-2.5 text-xs font-medium text-gray-500">OS</th>
                <th className="px-4 py-2.5 text-xs font-medium text-gray-500">Último contacto</th>
                <th className="px-4 py-2.5 text-xs font-medium text-gray-500">Estado</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500 text-sm">
                    No se encontraron agentes
                  </td>
                </tr>
              ) : (
                filtered.map(a => <AgentRow key={a.id} agent={a} />)
              )}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  )
}
