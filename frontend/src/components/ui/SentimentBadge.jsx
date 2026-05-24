import { colors } from '../../theme/colors'

const sentimentStyles = {
  bullish: {
    background: 'linear-gradient(135deg, #D1FAE5, #A7F3D0)',
    color: '#065F46',
    border: '1px solid #6EE7B7',
  },
  bearish: {
    background: 'linear-gradient(135deg, #FEE2E2, #FECACA)',
    color: '#991B1B',
    border: '1px solid #FCA5A5',
  },
  neutral: {
    background: 'linear-gradient(135deg, #F1F5F9, #E2E8F0)',
    color: '#475569',
    border: '1px solid #CBD5E1',
  },
}

export default function SentimentBadge({ sentiment, size = 'small' }) {
  const style = sentimentStyles[sentiment] || sentimentStyles.neutral
  const isLarge = size === 'large'

  return (
    <span
      style={{
        ...style,
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: isLarge ? '7px 18px' : '4px 12px',
        borderRadius: '50px',
        fontSize: isLarge ? '13px' : '11px',
        fontWeight: 600,
        lineHeight: 1,
        textTransform: 'capitalize',
        whiteSpace: 'nowrap',
        letterSpacing: '0.3px',
      }}
    >
      <span
        style={{
          width: isLarge ? '7px' : '5px',
          height: isLarge ? '7px' : '5px',
          borderRadius: '50%',
          backgroundColor: style.color,
          flexShrink: 0,
          boxShadow: `0 0 4px ${style.color}40`,
        }}
      />
      {sentiment}
    </span>
  )
}
