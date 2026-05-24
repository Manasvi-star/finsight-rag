export default function LoadingSkeleton({ variant = 'line', count = 1 }) {
  const renderSkeleton = (i) => {
    switch (variant) {
      case 'card':
        return (
          <div
            key={i}
            className="skeleton-pulse"
            style={{
              height: '110px',
              borderRadius: '14px',
              marginBottom: '12px',
            }}
          />
        )
      case 'circle':
        return (
          <div
            key={i}
            className="skeleton-pulse"
            style={{
              width: '180px',
              height: '180px',
              borderRadius: '50%',
            }}
          />
        )
      case 'bar':
        return (
          <div
            key={i}
            className="skeleton-pulse"
            style={{
              height: '10px',
              width: '100%',
              borderRadius: '5px',
              marginBottom: '14px',
            }}
          />
        )
      case 'line':
      default:
        return (
          <div
            key={i}
            className="skeleton-pulse"
            style={{
              height: '16px',
              width: i === count - 1 ? '55%' : i % 2 === 0 ? '100%' : '80%',
              marginBottom: '12px',
              borderRadius: '8px',
            }}
          />
        )
    }
  }

  return (
    <div style={{ padding: '4px 0' }}>
      {Array.from({ length: count }, (_, i) => renderSkeleton(i))}
    </div>
  )
}
