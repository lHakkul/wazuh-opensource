import { AlertTriangle, X } from 'lucide-react'
import { useState } from 'react'

export function ErrorBanner({ error }) {
  const [dismissed, setDismissed] = useState(false)
  if (!error || dismissed) return null

  return (
    <div className="flex items-center gap-3 px-4 py-3 mb-5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400">
      <AlertTriangle size={16} className="shrink-0" />
      <p className="text-sm flex-1">
        <strong>Error de conexión:</strong> {error}. Verifica que el backend esté corriendo y que las credenciales de Wazuh API sean correctas.
      </p>
      <button onClick={() => setDismissed(true)} className="shrink-0 hover:text-red-300">
        <X size={14} />
      </button>
    </div>
  )
}
