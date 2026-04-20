import { Bell, Send } from 'lucide-react'
import { useState } from 'react'
import { Card, CardHeader } from './ui/Card'
import { Badge } from './ui/Badge'
import { api } from '../services/api'

export function AlertsConfig({ config }) {
  const [testing, setTesting] = useState(null)
  const [result, setResult] = useState(null)

  const testChannel = async (channel) => {
    setTesting(channel)
    setResult(null)
    try {
      if (channel === 'telegram') await api.testTelegram()
      else await api.testSlack()
      setResult({ channel, ok: true })
    } catch (e) {
      setResult({ channel, ok: false, error: e.message })
    } finally {
      setTesting(null)
    }
  }

  return (
    <Card>
      <CardHeader title="Notificaciones" subtitle="Canales de alerta configurados" icon={Bell} />

      <div className="space-y-3">
        <div className="flex items-center justify-between p-3 rounded-lg bg-dark-700/60 border border-dark-600">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-300">Telegram</span>
            <Badge color={config?.telegram_enabled ? 'green' : 'unknown'}>
              {config?.telegram_enabled ? 'Activo' : 'Inactivo'}
            </Badge>
          </div>
          {config?.telegram_enabled && (
            <button
              onClick={() => testChannel('telegram')}
              disabled={testing === 'telegram'}
              className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-brand-500/20 hover:bg-brand-500/30 text-brand-400 text-xs transition-colors disabled:opacity-50"
            >
              <Send size={11} />
              Probar
            </button>
          )}
        </div>

        <div className="flex items-center justify-between p-3 rounded-lg bg-dark-700/60 border border-dark-600">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-300">Slack</span>
            <Badge color={config?.slack_enabled ? 'green' : 'unknown'}>
              {config?.slack_enabled ? 'Activo' : 'Inactivo'}
            </Badge>
          </div>
          {config?.slack_enabled && (
            <button
              onClick={() => testChannel('slack')}
              disabled={testing === 'slack'}
              className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-brand-500/20 hover:bg-brand-500/30 text-brand-400 text-xs transition-colors disabled:opacity-50"
            >
              <Send size={11} />
              Probar
            </button>
          )}
        </div>

        {result && (
          <p className={`text-xs px-3 py-1.5 rounded-lg ${result.ok ? 'text-emerald-400 bg-emerald-500/10' : 'text-red-400 bg-red-500/10'}`}>
            {result.ok ? `✓ Notificación de prueba enviada a ${result.channel}` : `✗ Error: ${result.error}`}
          </p>
        )}

        {!config?.telegram_enabled && !config?.slack_enabled && (
          <p className="text-xs text-gray-600 text-center py-2">
            Configura TELEGRAM_BOT_TOKEN o SLACK_WEBHOOK_URL en el .env para activar alertas
          </p>
        )}
      </div>
    </Card>
  )
}
