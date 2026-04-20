import { useState } from 'react'
import { Navbar } from './components/Navbar'
import { StatsBar } from './components/StatsBar'
import { ClusterStatus } from './components/ClusterStatus'
import { ManagerStatus } from './components/ManagerStatus'
import { AgentsTable } from './components/AgentsTable'
import { AgentsChart } from './components/AgentsChart'
import { EventHistory } from './components/EventHistory'
import { AlertsConfig } from './components/AlertsConfig'
import { HealthScore } from './components/HealthScore'
import { SlaAvailability } from './components/SlaAvailability'
import { ErrorBanner } from './components/ErrorBanner'
import { useOverview, useAgents, useHistory, useAlertConfig } from './hooks/useWazuh'
import { LayoutDashboard, Users, History, Bell } from 'lucide-react'
import clsx from 'clsx'

const TABS = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'agents', label: 'Agentes', icon: Users },
  { id: 'history', label: 'Historial', icon: History },
  { id: 'alerts', label: 'Alertas', icon: Bell },
]

export default function App() {
  const [tab, setTab] = useState('overview')
  const { data: overview, loading: ovLoading, error, lastUpdated, refetch } = useOverview(30_000)
  const { data: agents, loading: agLoading } = useAgents(30_000)
  const { data: history, loading: histLoading, refetch: refetchHistory } = useHistory()
  const alertConfig = useAlertConfig()

  const connected = !error && !!overview

  return (
    <div className="min-h-screen bg-dark-900">
      <Navbar
        lastUpdated={lastUpdated}
        onRefresh={refetch}
        loading={ovLoading}
        connected={connected}
      />

      <main className="max-w-[1600px] mx-auto px-4 sm:px-6 py-6">
        <ErrorBanner error={error} />

        {/* Tabs */}
        <div className="flex gap-1 mb-6 p-1 bg-dark-800 rounded-xl border border-dark-600 w-fit">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={clsx(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                tab === id
                  ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/20'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Icon size={15} />
              {label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {tab === 'overview' && (
          <div className="space-y-5">
            <StatsBar overview={overview} loading={ovLoading} />
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
              <HealthScore healthScore={overview?.health_score} loading={ovLoading} />
              <SlaAvailability sla={overview?.sla} loading={ovLoading} />
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              <div className="lg:col-span-2">
                <ClusterStatus cluster={overview?.cluster} loading={ovLoading} />
              </div>
              <div>
                <AgentsChart agents={overview?.agents} />
              </div>
            </div>
            <ManagerStatus manager={overview?.manager} loading={ovLoading} />
          </div>
        )}

        {/* Agents Tab */}
        {tab === 'agents' && (
          <AgentsTable agents={agents} loading={agLoading} />
        )}

        {/* History Tab */}
        {tab === 'history' && (
          <EventHistory
            events={history}
            loading={histLoading}
            onClear={refetchHistory}
          />
        )}

        {/* Alerts Tab */}
        {tab === 'alerts' && (
          <div className="max-w-md">
            <AlertsConfig config={alertConfig} />
          </div>
        )}
      </main>
    </div>
  )
}
