import { FileText, Database, Clock, Shield, AlertTriangle, Layers } from 'lucide-react'
import { colors } from '../../theme/colors'
import UploadZone from '../ui/UploadZone'
import RiskTag from '../ui/RiskTag'

export default function Sidebar({
  uploadState,
  fileInfo,
  onUpload,
  riskData,
}) {
  return (
    <aside
      style={{
        width: '300px',
        minWidth: '300px',
        background: 'linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%)',
        borderRight: `1px solid ${colors.border}`,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px',
        }}
      >
        {/* Upload Section */}
        <SectionHeading icon={<Layers size={12} />}>Document</SectionHeading>
        <UploadZone
          uploadState={uploadState}
          fileInfo={fileInfo}
          onUpload={onUpload}
        />

        {/* Document Stats */}
        {fileInfo && (
          <>
            <SectionHeading icon={<Database size={12} />} style={{ marginTop: '28px' }}>
              Document Stats
            </SectionHeading>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '10px',
              }}
            >
              <StatCard
                icon={<Database size={14} />}
                iconBg="#EEF2FF"
                iconColor="#4F46E5"
                label="Chunks"
                value={fileInfo.chunks?.toLocaleString() || '—'}
              />
              <StatCard
                icon={<FileText size={14} />}
                iconBg="#FEF3C7"
                iconColor="#D97706"
                label="Pages"
                value={fileInfo.pages || '—'}
              />
              <StatCard
                icon={<Clock size={14} />}
                iconBg="#E0F2FE"
                iconColor="#0284C7"
                label="Retrieval"
                value="~1.2s"
              />
              <StatCard
                icon={<Shield size={14} />}
                iconBg="#D1FAE5"
                iconColor="#059669"
                label="Confidence"
                value="82%"
              />
            </div>
          </>
        )}

        {/* Risk Flags Preview */}
        {riskData && riskData.length > 0 && (
          <>
            <SectionHeading icon={<AlertTriangle size={12} />} style={{ marginTop: '28px' }}>
              Risk Flags
            </SectionHeading>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {riskData.slice(0, 3).map((risk, idx) => {
                const borderColor =
                  risk.severity === 'high' ? '#EF4444'
                  : risk.severity === 'medium' ? '#F59E0B'
                  : '#22C55E'

                return (
                  <div
                    key={risk.id}
                    className="fade-in-up"
                    style={{
                      backgroundColor: '#FFFFFF',
                      border: `1px solid ${colors.border}`,
                      borderLeft: `3px solid ${borderColor}`,
                      borderRadius: '8px',
                      padding: '12px',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '10px',
                      transition: 'all 0.15s ease',
                      animationDelay: `${idx * 0.1}s`,
                      cursor: 'default',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)'
                      e.currentTarget.style.transform = 'translateX(2px)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.boxShadow = 'none'
                      e.currentTarget.style.transform = 'translateX(0)'
                    }}
                  >
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div
                        style={{
                          fontSize: '12px',
                          color: colors.textPrimary,
                          lineHeight: 1.5,
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                        }}
                      >
                        {risk.text}
                      </div>
                      <div style={{ marginTop: '8px' }}>
                        <RiskTag severity={risk.severity} />
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </>
        )}
      </div>

      {/* Sidebar Footer */}
      <div
        style={{
          padding: '12px 20px',
          borderTop: `1px solid ${colors.border}`,
          background: 'rgba(255,255,255,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '6px',
          fontSize: '11px',
          color: colors.textHint,
        }}
      >
        <div
          style={{
            width: '4px',
            height: '4px',
            borderRadius: '50%',
            backgroundColor: '#34D399',
          }}
        />
        Connected to FinSight Engine
      </div>
    </aside>
  )
}

function SectionHeading({ children, icon, style = {} }) {
  return (
    <div
      style={{
        fontSize: '11px',
        fontWeight: 600,
        color: '#64748B',
        textTransform: 'uppercase',
        letterSpacing: '1px',
        marginBottom: '12px',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        ...style,
      }}
    >
      {icon && <span style={{ color: '#94A3B8' }}>{icon}</span>}
      {children}
    </div>
  )
}

function StatCard({ icon, iconBg, iconColor, label, value }) {
  return (
    <div
      className="card-hover"
      style={{
        backgroundColor: '#FFFFFF',
        border: `1px solid ${colors.border}`,
        borderRadius: '10px',
        padding: '14px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
        cursor: 'default',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div
          style={{
            width: '28px',
            height: '28px',
            borderRadius: '7px',
            backgroundColor: iconBg,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: iconColor,
          }}
        >
          {icon}
        </div>
      </div>
      <div>
        <div
          style={{
            fontSize: '18px',
            fontWeight: 600,
            color: colors.textPrimary,
            lineHeight: 1,
          }}
        >
          {value}
        </div>
        <div
          style={{
            fontSize: '11px',
            color: '#94A3B8',
            marginTop: '4px',
            fontWeight: 500,
          }}
        >
          {label}
        </div>
      </div>
    </div>
  )
}
