import { colors } from '../../theme/colors'

export default function ConfidenceBar({ value }) {
  const percent = Math.round(value * 100)

  // Color shifts based on confidence level
  const barColor = percent >= 75 ? '#2563EB' : percent >= 50 ? '#F59E0B' : '#EF4444'
  const barBg = percent >= 75 ? 'rgba(37, 99, 235, 0.12)' : percent >= 50 ? 'rgba(245, 158, 11, 0.12)' : 'rgba(239, 68, 68, 0.12)'

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <div
        style={{
          width: '80px',
          height: '6px',
          backgroundColor: barBg,
          borderRadius: '3px',
          overflow: 'hidden',
          flexShrink: 0,
        }}
      >
        <div
          className="bar-animate"
          style={{
            width: `${percent}%`,
            height: '100%',
            background: `linear-gradient(90deg, ${barColor}, ${barColor}CC)`,
            borderRadius: '3px',
            transition: 'width 0.5s ease',
          }}
        />
      </div>
      <span
        style={{
          fontSize: '11px',
          color: '#64748B',
          whiteSpace: 'nowrap',
          fontWeight: 500,
        }}
      >
        {percent}% confident
      </span>
    </div>
  )
}
