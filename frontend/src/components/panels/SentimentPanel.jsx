import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Doughnut } from 'react-chartjs-2'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { colors, chartColors } from '../../theme/colors'
import SentimentBadge from '../ui/SentimentBadge'
import LoadingSkeleton from '../ui/LoadingSkeleton'

ChartJS.register(ArcElement, Tooltip, Legend)

export default function SentimentPanel({ data }) {
  if (!data) {
    return (
      <div style={{ padding: '24px' }}>
        <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
          <LoadingSkeleton variant="circle" />
          <LoadingSkeleton variant="line" count={3} />
        </div>
        <div style={{ marginTop: '32px' }}>
          <LoadingSkeleton variant="card" count={2} />
        </div>
      </div>
    )
  }

  const doughnutData = {
    labels: ['Bullish', 'Neutral', 'Bearish'],
    datasets: [
      {
        data: [data.scores.bullish, data.scores.neutral, data.scores.bearish],
        backgroundColor: ['#22C55E', '#94A3B8', '#EF4444'],
        borderWidth: 3,
        borderColor: '#FFFFFF',
        hoverOffset: 8,
        hoverBorderWidth: 0,
      },
    ],
  }

  const doughnutOptions = {
    cutout: '72%',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#0F172A',
        padding: 12,
        cornerRadius: 10,
        titleFont: { size: 12, weight: '600', family: 'Inter' },
        bodyFont: { size: 13, family: 'Inter' },
        callbacks: {
          label: (ctx) => ` ${ctx.label}: ${ctx.parsed}%`,
        },
      },
    },
    animation: {
      animateRotate: true,
      duration: 800,
    },
  }

  const legendItems = [
    { label: 'Bullish', value: data.scores.bullish, color: '#22C55E', bg: '#D1FAE5' },
    { label: 'Neutral', value: data.scores.neutral, color: '#94A3B8', bg: '#F1F5F9' },
    { label: 'Bearish', value: data.scores.bearish, color: '#EF4444', bg: '#FEE2E2' },
  ]

  return (
    <div style={{ padding: '24px', overflowY: 'auto', height: '100%', background: '#FAFBFC' }}>
      {/* Top section: Doughnut + Legend + Overall */}
      <div
        className="fade-in-up"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '40px',
          padding: '24px',
          backgroundColor: '#FFFFFF',
          borderRadius: '16px',
          border: `1px solid ${colors.border}`,
          boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
          marginBottom: '24px',
        }}
      >
        {/* Chart */}
        <div
          style={{
            width: '180px',
            height: '180px',
            position: 'relative',
            flexShrink: 0,
          }}
        >
          <Doughnut data={doughnutData} options={doughnutOptions} />
          {/* Center label */}
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '28px', fontWeight: 700, color: '#0F172A', lineHeight: 1 }}>
              {data.scores.bullish}%
            </div>
            <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '4px', fontWeight: 500 }}>
              Bullish
            </div>
          </div>
        </div>

        {/* Legend + Overall */}
        <div style={{ flex: 1 }}>
          <div style={{ marginBottom: '16px' }}>
            <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '8px' }}>
              Overall Sentiment
            </div>
            <SentimentBadge sentiment={data.overall} size="large" />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {legendItems.map((item) => (
              <div
                key={item.label}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '8px 12px',
                  borderRadius: '10px',
                  backgroundColor: item.bg,
                  transition: 'transform 0.15s ease',
                }}
              >
                <span
                  style={{
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    backgroundColor: item.color,
                    flexShrink: 0,
                    boxShadow: `0 0 6px ${item.color}40`,
                  }}
                />
                <span style={{ fontSize: '13px', color: '#334155', fontWeight: 500, flex: 1 }}>
                  {item.label}
                </span>
                <span style={{ fontSize: '15px', fontWeight: 700, color: '#0F172A' }}>
                  {item.value}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sentiment by Section */}
      <div
        className="fade-in-up"
        style={{
          backgroundColor: '#FFFFFF',
          border: `1px solid ${colors.border}`,
          borderRadius: '16px',
          padding: '24px',
          boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
          animationDelay: '0.15s',
        }}
      >
        <div
          style={{
            fontSize: '15px',
            fontWeight: 600,
            color: '#0F172A',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <div style={{ width: '3px', height: '16px', borderRadius: '2px', background: 'linear-gradient(180deg, #3B82F6, #6366F1)' }} />
          Sentiment by Section
        </div>

        <div style={{ display: 'flex', flexDirection: 'column' }}>
          {data.sections.map((section, idx) => {
            const scoreNum = parseFloat(section.score)
            const isPositive = scoreNum > 0
            const isNegative = scoreNum < 0

            return (
              <div
                key={section.name}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  padding: '14px 0',
                  borderBottom:
                    idx < data.sections.length - 1
                      ? `1px solid #F1F5F9`
                      : 'none',
                  transition: 'background 0.15s ease',
                }}
              >
                {/* Section name */}
                <div
                  style={{
                    minWidth: '140px',
                    fontSize: '13px',
                    color: '#334155',
                    fontWeight: 500,
                    flexShrink: 0,
                  }}
                >
                  {section.name}
                </div>

                {/* Stacked bar */}
                <div
                  style={{
                    flex: 1,
                    display: 'flex',
                    height: '10px',
                    borderRadius: '5px',
                    overflow: 'hidden',
                    boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.06)',
                  }}
                >
                  <div
                    className="bar-segment"
                    style={{
                      width: `${section.bullish}%`,
                      backgroundColor: '#22C55E',
                      transition: 'width 0.5s ease',
                    }}
                  />
                  <div
                    className="bar-segment"
                    style={{
                      width: `${section.neutral}%`,
                      backgroundColor: '#CBD5E1',
                      transition: 'width 0.5s ease',
                    }}
                  />
                  <div
                    className="bar-segment"
                    style={{
                      width: `${section.bearish}%`,
                      backgroundColor: '#EF4444',
                      transition: 'width 0.5s ease',
                    }}
                  />
                </div>

                {/* Score */}
                <div
                  style={{
                    minWidth: '70px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'flex-end',
                    gap: '4px',
                    fontSize: '13px',
                    fontWeight: 600,
                    color: isPositive ? '#059669' : isNegative ? '#DC2626' : '#64748B',
                    flexShrink: 0,
                  }}
                >
                  {isPositive ? <TrendingUp size={13} /> : isNegative ? <TrendingDown size={13} /> : <Minus size={13} />}
                  {section.score}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
