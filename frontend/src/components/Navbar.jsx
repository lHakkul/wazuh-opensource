import { Shield, RefreshCw, Wifi, WifiOff } from 'lucide-react'
import { format } from 'date-fns'

export function Navbar({ lastUpdated, onRefresh, loading, connected }) {
  return (
    <header className="border-b border-dark-600 bg-dark-800/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-[1600px] mx-auto px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-brand-500 flex items-center justify-center">
            <Shield size={16} className="text-white" />
          </div>
          <div>
            <span className="font-semibold text-white text-sm">Wazuh</span>
            <span className="text-brand-400 font-semibold text-sm"> Pulse Monitor</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {lastUpdated && (
            <span className="text-xs text-gray-500 font-mono hidden sm:block">
              Actualizado: {format(lastUpdated, 'HH:mm:ss')}
            </span>
          )}

          <div className={`flex items-center gap-1.5 text-xs font-mono ${connected ? 'text-emerald-400' : 'text-red-400'}`}>
            {connected ? <Wifi size={14} /> : <WifiOff size={14} />}
            <span className="hidden sm:inline">{connected ? 'Conectado' : 'Sin conexión'}</span>
          </div>

          <button
            onClick={onRefresh}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-dark-600 hover:bg-dark-500 text-gray-300 hover:text-white text-xs transition-colors disabled:opacity-50"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            <span>Actualizar</span>
          </button>
        </div>
      </div>
    </header>
  )
}
