export function Spinner({ size = 20 }) {
  return (
    <div
      className="border-2 border-dark-600 border-t-brand-400 rounded-full animate-spin"
      style={{ width: size, height: size }}
    />
  )
}

export function SkeletonBlock({ className = 'h-4 w-full' }) {
  return <div className={`bg-dark-600 rounded animate-pulse ${className}`} />
}
