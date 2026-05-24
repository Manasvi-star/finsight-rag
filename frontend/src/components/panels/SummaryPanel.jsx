import { Zap, TrendingUp, TrendingDown, FileText } from 'lucide-react'
import { colors } from '../../theme/colors'
import SentimentBadge from '../ui/SentimentBadge'
import LoadingSkeleton from '../ui/LoadingSkeleton'

const kpiAccents = [
  { gradient: 'linear-gradient(135deg, #3B82F6, #2563EB)', iconBg: '#EFF6FF', iconColor: '#2563EB' },
  { gradient: 'linear-gradient(135deg, #10B981, #059669)', iconBg: '#D1FAE5', iconColor: '#059669' },
  { gradient: 'linear-gradient(135deg, #F59E0B, #D97706)', iconBg: '#FEF3C7', iconColor: '#D97706' },
  { gradient: 'linear-gradient(135deg, #8B5CF6, #7C3AED)', iconBg: '#EDE9FE', iconColor: '#7C3AED' },
  { gradient: 'linear-gradient(135deg, #06B6D4, #0891B2)', iconBg: '#CFFAFE', iconColor: '#0891B2' },
  { gradient: 'linear-gradient(135deg, #EC4899, #DB2777)', iconBg: '#FCE7F3', iconColor: '#DB2777' },
]

export default function SummaryPanel({ data }) {
  if (!data) {
    return (
      <div style={{ padding: '24px' }}>
        <LoadingSkeleton variant="line" count={3} />
        <div style={{ marginTop: '24px', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
          <LoadingSkeleton variant="card" />
          <LoadingSkeleton variant="card" />
          <LoadingSkeleton variant="card" />
        </div>
      </div>
    )
  }

  return (
    <div style={{ padding: '24px', overflowY: 'auto', height: '100%', background: '#FAFBFC' }}>
      {/* Executive Summary Card */}
      <div
        className="fade-in-up"
        style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '16px',
          border: `1px solid ${colors.border}`,
          boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
          padding: '24px',
          marginBottom: '24px',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Top accent */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '3px',
            background: 'linear-gradient(90deg, #3B82F6, #8B5CF6, #EC4899)',
          }}
        />

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #EEF2FF, #E0E7FF)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <FileText size={18} color="#4F46E5" />
          </div>
          <div>
            <div style={{ fontSize: '15px', fontWeight: 600, color: '#0F172A' }}>
              Executive Summary
            </div>
            <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '2px' }}>
              AI-generated analysis
            </div>
          </div>
          <div style={{ marginLeft: 'auto' }}>
            <SentimentBadge sentiment={data.overall} size="large" />
          </div>
        </div>

        <p
          style={{
            fontSize: '14px',
            lineHeight: 1.75,
            color: '#334155',
          }}
        >
          {data.text}
        </p>
      </div>

      {/* KPI Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '16px',
        }}
      >
        {data.kpis.map((kpi, i) => {
          const isUp = kpi.direction === 'up'
          const accent = kpiAccents[i] || kpiAccents[0]
          return (
            <div
              key={i}
              className="card-hover fade-in-up"
              style={{
                backgroundColor: '#FFFFFF',
                border: `1px solid ${colors.border}`,
                borderRadius: '14px',
                padding: '20px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
                position: 'relative',
                overflow: 'hidden',
                animationDelay: `${i * 0.08}s`,
              }}
            >
              {/* Left accent bar */}
              <div
                style={{
                  position: 'absolute',
                  top: '12px',
                  left: 0,
                  bottom: '12px',
                  width: '3px',
                  borderRadius: '0 2px 2px 0',
                  background: accent.gradient,
                }}
              />

              <div
                style={{
                  fontSize: '24px',
                  fontWeight: 700,
                  color: '#0F172A',
                  lineHeight: 1.2,
                  letterSpacing: '-0.5px',
                  paddingLeft: '8px',
                }}
              >
                {kpi.value}
              </div>
              <div
                style={{
                  fontSize: '12px',
                  color: '#94A3B8',
                  marginTop: '4px',
                  fontWeight: 500,
                  paddingLeft: '8px',
                }}
              >
                {kpi.label}
              </div>
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  marginTop: '12px',
                  marginLeft: '8px',
                  fontSize: '13px',
                  fontWeight: 600,
                  color: isUp ? '#059669' : '#DC2626',
                  backgroundColor: isUp ? '#D1FAE5' : '#FEE2E2',
                  padding: '3px 10px',
                  borderRadius: '50px',
                }}
              >
                {isUp ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
                {kpi.change}
              </div>
            </div>
          )
        })}
      </div>

      {/* Footer */}
      <div
        style={{
          marginTop: '32px',
          textAlign: 'center',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          fontSize: '12px',
          color: '#94A3B8',
          padding: '12px',
        }}
      >
        <div
          style={{
            width: '20px',
            height: '20px',
            borderRadius: '5px',
            background: 'linear-gradient(135deg, #FEF3C7, #FDE68A)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Zap size={11} color="#D97706" />
        </div>
        Powered by GPT-3.5 + FinBERT
      </div>
    </div>
  )
}
