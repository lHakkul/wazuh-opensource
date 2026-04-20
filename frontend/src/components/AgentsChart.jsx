import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { Card, CardHeader } from './ui/Card'
import { PieChart as PieIcon } from 'lucide-react'

const COLORS = {
  active: '#10b981',
  disconnected: '#ef4444',
  pending: '#f59e0b',
  never_connected: '#6b7280',
}

const LABELS = {
  active: 'Activos',
  disconnected: 'Desconectados',
  pending: 'Pendientes',
  never_connected: 'Sin conectar',
}

export function AgentsChart({ agents }) {
  if (!agents) return null

  const data = [
    { name: LABELS.active, value: agents.active, key: 'active' },
    { name: LABELS.disconnected, value: agents.disconnected, key: 'disconnected' },
    { name: LABELS.pending, value: agents.pending, key: 'pending' },
    { name: LABELS.never_connected, value: agents.never_connected, key: 'never_connected' },
  ].filter(d => d.value > 0)

  return (
    <Card>
      <CardHeader title="Distribución de Agentes" icon={PieIcon} />
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
          >
            {data.map(entry => (
              <Cell key={entry.key} fill={COLORS[entry.key]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ background: '#0f1629', border: '1px solid #1c2647', borderRadius: 8, fontSize: 12 }}
            itemStyle={{ color: '#d1d5db' }}
          />
          <Legend
            formatter={(value) => <span style={{ fontSize: 12, color: '#9ca3af' }}>{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  )
}
