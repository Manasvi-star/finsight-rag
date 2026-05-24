import { BarChart3, Sparkles } from 'lucide-react'

const tabs = [
  { id: 'qa', label: 'Q&A' },
  { id: 'summary', label: 'Summary' },
  { id: 'sentiment', label: 'Sentiment' },
  { id: 'risk', label: 'Risk' },
]

export default function Navbar({ activeTab, onTabChange, fileName }) {
  return (
    <nav
      style={{
        height: '56px',
        background: 'linear-gradient(135deg, #0B1628 0%, #162544 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        flexShrink: 0,
        boxShadow: '0 2px 12px rgba(0, 0, 0, 0.15)',
        position: 'relative',
        zIndex: 10,
      }}
    >
      {/* Left — Logo */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          flexShrink: 0,
        }}
      >
        <div
          style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'linear-gradient(135deg, #3B82F6, #1D4ED8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 8px rgba(59, 130, 246, 0.4)',
          }}
        >
          <BarChart3 size={18} color="#FFFFFF" />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span
            style={{
              fontSize: '17px',
              fontWeight: 600,
              color: '#FFFFFF',
              letterSpacing: '-0.3px',
            }}
          >
            FinSight
          </span>
          <span
            style={{
              fontSize: '11px',
              fontWeight: 500,
              color: '#3B82F6',
              background: 'rgba(59, 130, 246, 0.15)',
              padding: '2px 8px',
              borderRadius: '4px',
              letterSpacing: '0.5px',
            }}
          >
            RAG
          </span>
        </div>
      </div>

      {/* Center — Tabs */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          background: 'rgba(255, 255, 255, 0.06)',
          borderRadius: '50px',
          padding: '4px',
        }}
      >
        {tabs.map((tab) => {
          const isActive = tab.id === activeTab
          return (
            <button
              key={tab.id}
              id={`nav-tab-${tab.id}`}
              onClick={() => onTabChange(tab.id)}
              style={{
                padding: '7px 20px',
                borderRadius: '50px',
                border: 'none',
                backgroundColor: isActive
                  ? 'rgba(59, 130, 246, 0.2)'
                  : 'transparent',
                color: isActive ? '#93C5FD' : 'rgba(255, 255, 255, 0.5)',
                fontSize: '13px',
                fontWeight: 500,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                outline: 'none',
                position: 'relative',
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.08)'
                  e.target.style.color = 'rgba(255, 255, 255, 0.8)'
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.target.style.backgroundColor = 'transparent'
                  e.target.style.color = 'rgba(255, 255, 255, 0.5)'
                }
              }}
            >
              {tab.label}
              {isActive && (
                <span
                  style={{
                    position: 'absolute',
                    bottom: '2px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    width: '16px',
                    height: '2px',
                    borderRadius: '1px',
                    background: '#3B82F6',
                  }}
                />
              )}
            </button>
          )
        })}
      </div>

      {/* Right — File indicator */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '12px',
          color: 'rgba(255, 255, 255, 0.5)',
          flexShrink: 0,
        }}
      >
        {fileName ? (
          <>
            <Sparkles size={12} color="#3B82F6" />
            <span
              style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                backgroundColor: '#34D399',
                boxShadow: '0 0 6px rgba(52, 211, 153, 0.5)',
                flexShrink: 0,
              }}
            />
            <span style={{ color: 'rgba(255, 255, 255, 0.7)', maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {fileName}
            </span>
          </>
        ) : (
          <span>No file loaded</span>
        )}
      </div>
    </nav>
  )
}
