import { TrendingUp, TrendingDown } from 'lucide-react'
import { colors } from '../../theme/colors'

const accentGradients = [
  'linear-gradient(135deg, #3B82F6, #2563EB)',
  'linear-gradient(135deg, #10B981, #059669)',
  'linear-gradient(135deg, #F59E0B, #D97706)',
  'linear-gradient(135deg, #8B5CF6, #7C3AED)',
  'linear-gradient(135deg, #06B6D4, #0891B2)',
  'linear-gradient(135deg, #EC4899, #DB2777)',
]

export default function MetricCard({ label, value, change, direction, index = 0 }) {
  const isUp = direction === 'up'
  const gradient = accentGradients[index % accentGradients.length]

  return (
    <div
      className="card-hover"
      style={{
        backgroundColor: '#FFFFFF',
        border: `1px solid ${colors.border}`,
        borderRadius: '14px',
        padding: '20px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Top accent bar */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: gradient,
        }}
      />
      <div
        style={{
          fontSize: '24px',
          fontWeight: 700,
          color: '#0F172A',
          lineHeight: 1.2,
          letterSpacing: '-0.5px',
        }}
      >
        {value}
      </div>
      <div
        style={{
          fontSize: '12px',
          color: '#94A3B8',
          marginTop: '4px',
          fontWeight: 500,
        }}
      >
        {label}
      </div>
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          marginTop: '10px',
          fontSize: '13px',
          fontWeight: 600,
          color: isUp ? '#059669' : '#DC2626',
          backgroundColor: isUp ? '#D1FAE5' : '#FEE2E2',
          padding: '3px 10px',
          borderRadius: '50px',
        }}
      >
        {isUp ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
        {change}
      </div>
    </div>
  )
}
