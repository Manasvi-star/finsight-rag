import { useState } from 'react'
import { AlertTriangle, Shield, Filter } from 'lucide-react'
import { colors } from '../../theme/colors'
import RiskTag from '../ui/RiskTag'
import LoadingSkeleton from '../ui/LoadingSkeleton'

const severityBorderColors = {
  high: '#EF4444',
  medium: '#F59E0B',
  low: '#22C55E',
}

const severityBgColors = {
  high: 'rgba(239, 68, 68, 0.03)',
  medium: 'rgba(245, 158, 11, 0.03)',
  low: 'rgba(34, 197, 94, 0.03)',
}

const filterOptions = ['all', 'high', 'medium', 'low']

export default function RiskPanel({ data }) {
  const [activeFilter, setActiveFilter] = useState('all')

  if (!data) {
    return (
      <div style={{ padding: '24px' }}>
        <LoadingSkeleton variant="card" count={3} />
      </div>
    )
  }

  const filteredData =
    activeFilter === 'all'
      ? data
      : data.filter((r) => r.severity === activeFilter)

  const highCount = data.filter((r) => r.severity === 'high').length
  const mediumCount = data.filter((r) => r.severity === 'medium').length
  const lowCount = data.filter((r) => r.severity === 'low').length

  return (
    <div style={{ padding: '24px', overflowY: 'auto', height: '100%', background: '#FAFBFC' }}>
      {/* Header Card */}
      <div
        className="fade-in-up"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '20px 24px',
          backgroundColor: '#FFFFFF',
          borderRadius: '16px',
          border: `1px solid ${colors.border}`,
          boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
          marginBottom: '20px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #FEF3C7, #FDE68A)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Shield size={20} color="#D97706" />
          </div>
          <div>
            <div style={{ fontSize: '16px', fontWeight: 600, color: '#0F172A' }}>
              {data.length} Risk Statement{data.length !== 1 ? 's' : ''} Flagged
            </div>
            <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '2px' }}>
              Extracted from annual report sections
            </div>
          </div>
        </div>

        {/* Summary pills */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <CountPill count={highCount} label="High" color="#EF4444" bg="#FEE2E2" />
          <CountPill count={mediumCount} label="Med" color="#F59E0B" bg="#FEF3C7" />
          <CountPill count={lowCount} label="Low" color="#22C55E" bg="#D1FAE5" />
        </div>
      </div>

      {/* Filter Pills */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          marginBottom: '16px',
          alignItems: 'center',
        }}
      >
        <Filter size={14} color="#94A3B8" style={{ marginRight: '4px' }} />
        {filterOptions.map((filter) => {
          const isActive = filter === activeFilter
          return (
            <button
              key={filter}
              id={`risk-filter-${filter}`}
              onClick={() => setActiveFilter(filter)}
              style={{
                padding: '7px 18px',
                borderRadius: '50px',
                border: isActive ? 'none' : `1px solid ${colors.border}`,
                background: isActive
                  ? 'linear-gradient(135deg, #3B82F6, #1D4ED8)'
                  : '#FFFFFF',
                color: isActive ? '#FFFFFF' : '#64748B',
                fontSize: '13px',
                fontWeight: 500,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                textTransform: 'capitalize',
                outline: 'none',
                boxShadow: isActive ? '0 2px 8px rgba(29, 78, 216, 0.3)' : '0 1px 2px rgba(0,0,0,0.04)',
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.target.style.borderColor = '#93C5FD'
                  e.target.style.color = '#1D4ED8'
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.target.style.borderColor = colors.border
                  e.target.style.color = '#64748B'
                }
              }}
            >
              {filter}
            </button>
          )
        })}
      </div>

      {/* Risk Rows */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {filteredData.map((risk, idx) => (
          <div
            key={risk.id}
            className="fade-in-up card-hover"
            style={{
              backgroundColor: '#FFFFFF',
              border: `1px solid ${colors.border}`,
              borderRadius: '14px',
              padding: '18px 20px',
              borderLeft: `4px solid ${severityBorderColors[risk.severity] || colors.border}`,
              display: 'flex',
              alignItems: 'flex-start',
              gap: '14px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
              animationDelay: `${idx * 0.05}s`,
            }}
          >
            {/* Severity Tag */}
            <div style={{ flexShrink: 0, paddingTop: '2px' }}>
              <RiskTag severity={risk.severity} />
            </div>

            {/* Statement */}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div
                style={{
                  fontSize: '14px',
                  color: '#1E293B',
                  lineHeight: 1.65,
                  fontWeight: 400,
                }}
              >
                {risk.text}
              </div>
              <div
                style={{
                  fontSize: '12px',
                  color: '#94A3B8',
                  marginTop: '8px',
                  fontWeight: 500,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <span
                  style={{
                    width: '4px',
                    height: '4px',
                    borderRadius: '50%',
                    backgroundColor: '#CBD5E1',
                  }}
                />
                {risk.section}
              </div>
            </div>

            {/* Page Badge */}
            <div
              style={{
                flexShrink: 0,
                background: 'linear-gradient(135deg, #EEF2FF, #E0E7FF)',
                color: '#4338CA',
                border: '1px solid #C7D2FE',
                padding: '5px 14px',
                borderRadius: '50px',
                fontSize: '12px',
                fontWeight: 600,
                whiteSpace: 'nowrap',
              }}
            >
              p.{risk.page}
            </div>
          </div>
        ))}

        {filteredData.length === 0 && (
          <div
            style={{
              textAlign: 'center',
              padding: '40px',
              color: '#94A3B8',
              fontSize: '14px',
              backgroundColor: '#FFFFFF',
              borderRadius: '14px',
              border: `1px solid ${colors.border}`,
            }}
          >
            No {activeFilter} severity risks found
          </div>
        )}
      </div>
    </div>
  )
}

function CountPill({ count, label, color, bg }) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        padding: '4px 12px',
        borderRadius: '50px',
        backgroundColor: bg,
        fontSize: '12px',
        fontWeight: 600,
        color,
      }}
    >
      <span style={{ fontSize: '14px', fontWeight: 700 }}>{count}</span>
      {label}
    </div>
  )
}
