import { colors } from '../../theme/colors'

const severityStyles = {
  high: {
    background: 'linear-gradient(135deg, #FEE2E2, #FECACA)',
    color: '#991B1B',
    border: '1px solid #FCA5A5',
  },
  medium: {
    background: 'linear-gradient(135deg, #FEF3C7, #FDE68A)',
    color: '#92400E',
    border: '1px solid #FCD34D',
  },
  low: {
    background: 'linear-gradient(135deg, #D1FAE5, #A7F3D0)',
    color: '#065F46',
    border: '1px solid #6EE7B7',
  },
}

export default function RiskTag({ severity }) {
  const style = severityStyles[severity] || severityStyles.medium

  return (
    <span
      style={{
        ...style,
        display: 'inline-block',
        padding: '4px 12px',
        borderRadius: '50px',
        fontSize: '11px',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.6px',
        lineHeight: 1,
        whiteSpace: 'nowrap',
      }}
    >
      {severity}
    </span>
  )
}
