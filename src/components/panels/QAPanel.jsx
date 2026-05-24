import { useState, useRef, useEffect } from 'react'
import { Send, ChevronDown, ChevronUp, TrendingUp, TrendingDown, MessageSquare, BookOpen } from 'lucide-react'
import { colors } from '../../theme/colors'
import SentimentBadge from '../ui/SentimentBadge'
import ConfidenceBar from '../ui/ConfidenceBar'

export default function QAPanel({ messages, onSendMessage, isAsking, summaryData }) {
  const [input, setInput] = useState('')
  const [expandedSources, setExpandedSources] = useState({})
  const chatEndRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isAsking])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || isAsking) return
    onSendMessage(input.trim())
    setInput('')
  }

  const toggleSources = (idx) => {
    setExpandedSources((prev) => ({ ...prev, [idx]: !prev[idx] }))
  }

  const kpis = summaryData?.kpis?.slice(0, 3) || []

  const kpiAccents = [
    { gradient: 'linear-gradient(135deg, #3B82F6, #2563EB)', shadow: 'rgba(37, 99, 235, 0.15)' },
    { gradient: 'linear-gradient(135deg, #10B981, #059669)', shadow: 'rgba(5, 150, 105, 0.15)' },
    { gradient: 'linear-gradient(135deg, #F59E0B, #D97706)', shadow: 'rgba(217, 119, 6, 0.15)' },
  ]

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflow: 'hidden',
        background: '#FAFBFC',
      }}
    >
      {/* KPI Cards Row */}
      {kpis.length > 0 && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${kpis.length}, 1fr)`,
            gap: '16px',
            padding: '20px 24px 0',
            flexShrink: 0,
          }}
        >
          {kpis.map((kpi, i) => {
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
                  padding: '18px 20px',
                  boxShadow: `0 1px 3px rgba(0,0,0,0.04), 0 4px 12px ${accent.shadow}`,
                  position: 'relative',
                  overflow: 'hidden',
                  animationDelay: `${i * 0.1}s`,
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
                    background: accent.gradient,
                  }}
                />
                <div
                  style={{
                    fontSize: '24px',
                    fontWeight: 700,
                    color: colors.textPrimary,
                    letterSpacing: '-0.5px',
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
                  }}
                >
                  {kpi.label}
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
                  {kpi.change}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Chat Container */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px 24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
        }}
      >
        {messages.length === 0 && !isAsking && (
          <div
            style={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '12px',
              color: colors.textHint,
            }}
          >
            <div
              style={{
                width: '64px',
                height: '64px',
                borderRadius: '16px',
                background: 'linear-gradient(135deg, #EEF2FF, #E0E7FF)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <MessageSquare size={28} color="#6366F1" style={{ opacity: 0.6 }} />
            </div>
            <div style={{ fontSize: '15px', fontWeight: 500, color: '#64748B' }}>
              Ask a question about the uploaded report
            </div>
            <div style={{ fontSize: '13px', color: '#94A3B8' }}>
              Try: &ldquo;What was the revenue growth?&rdquo; or &ldquo;Summarize key risks&rdquo;
            </div>
          </div>
        )}

        {messages.map((msg, idx) => {
          const isUser = msg.role === 'user'
          const isExpanded = expandedSources[idx]

          return (
            <div
              key={idx}
              className="fade-in-up"
              style={{
                display: 'flex',
                justifyContent: isUser ? 'flex-end' : 'flex-start',
              }}
            >
              <div
                style={{
                  maxWidth: isUser ? '75%' : '88%',
                  backgroundColor: isUser ? '#1E40AF' : '#FFFFFF',
                  color: isUser ? '#FFFFFF' : colors.textPrimary,
                  padding: '14px 18px',
                  borderRadius: isUser
                    ? '16px 16px 4px 16px'
                    : '16px 16px 16px 4px',
                  fontSize: '14px',
                  lineHeight: 1.65,
                  boxShadow: isUser
                    ? '0 2px 12px rgba(30, 64, 175, 0.25)'
                    : '0 1px 4px rgba(0,0,0,0.06)',
                  border: isUser ? 'none' : `1px solid ${colors.border}`,
                }}
              >
                <div>{msg.content}</div>

                {/* AI message extras */}
                {!isUser && msg.sentiment && (
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      marginTop: '14px',
                      paddingTop: '14px',
                      borderTop: `1px solid ${colors.border}`,
                    }}
                  >
                    <SentimentBadge sentiment={msg.sentiment} />
                    <ConfidenceBar value={msg.confidence} />
                  </div>
                )}

                {/* Sources */}
                {!isUser && msg.sources && msg.sources.length > 0 && (
                  <div style={{ marginTop: '10px' }}>
                    <button
                      onClick={() => toggleSources(idx)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '5px',
                        fontSize: '12px',
                        fontWeight: 500,
                        color: '#4F46E5',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        padding: '4px 0',
                        transition: 'color 0.15s ease',
                      }}
                      onMouseEnter={(e) => e.target.style.color = '#3730A3'}
                      onMouseLeave={(e) => e.target.style.color = '#4F46E5'}
                    >
                      <BookOpen size={13} />
                      {isExpanded ? (
                        <ChevronUp size={14} />
                      ) : (
                        <ChevronDown size={14} />
                      )}
                      View {msg.sources.length} source{msg.sources.length > 1 ? 's' : ''}
                    </button>

                    {isExpanded && (
                      <div
                        className="fade-in-up"
                        style={{
                          marginTop: '10px',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '8px',
                          backgroundColor: '#F8FAFC',
                          borderRadius: '10px',
                          padding: '12px',
                          border: `1px solid ${colors.border}`,
                        }}
                      >
                        {msg.sources.map((src, si) => (
                          <div
                            key={si}
                            style={{
                              display: 'flex',
                              alignItems: 'flex-start',
                              gap: '10px',
                              fontSize: '12px',
                              lineHeight: 1.5,
                            }}
                          >
                            <span
                              style={{
                                background: 'linear-gradient(135deg, #EEF2FF, #E0E7FF)',
                                color: '#4338CA',
                                border: `1px solid #C7D2FE`,
                                padding: '3px 10px',
                                borderRadius: '50px',
                                fontSize: '11px',
                                fontWeight: 600,
                                whiteSpace: 'nowrap',
                                flexShrink: 0,
                              }}
                            >
                              p.{src.page}
                            </span>
                            <span style={{ color: '#64748B' }}>
                              {src.text}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )
        })}

        {/* Typing indicator */}
        {isAsking && (
          <div
            className="fade-in-up"
            style={{ display: 'flex', justifyContent: 'flex-start' }}
          >
            <div
              style={{
                backgroundColor: '#FFFFFF',
                border: `1px solid ${colors.border}`,
                padding: '14px 22px',
                borderRadius: '16px 16px 16px 4px',
                display: 'flex',
                alignItems: 'center',
                gap: '2px',
                boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
              }}
            >
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input Bar */}
      <form
        onSubmit={handleSubmit}
        style={{
          padding: '16px 24px',
          borderTop: `1px solid ${colors.border}`,
          backgroundColor: '#FFFFFF',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          flexShrink: 0,
          boxShadow: '0 -2px 8px rgba(0,0,0,0.03)',
        }}
      >
        <input
          id="qa-input"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about the report..."
          disabled={isAsking}
          style={{
            flex: 1,
            padding: '12px 20px',
            fontSize: '14px',
            border: `1.5px solid ${colors.border}`,
            borderRadius: '50px',
            outline: 'none',
            color: colors.textPrimary,
            backgroundColor: '#F8FAFC',
            transition: 'all 0.2s ease',
          }}
          onFocus={(e) => {
            e.target.style.borderColor = '#93C5FD'
            e.target.style.backgroundColor = '#FFFFFF'
            e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)'
          }}
          onBlur={(e) => {
            e.target.style.borderColor = colors.border
            e.target.style.backgroundColor = '#F8FAFC'
            e.target.style.boxShadow = 'none'
          }}
        />
        <button
          id="qa-send-btn"
          type="submit"
          disabled={!input.trim() || isAsking}
          style={{
            width: '42px',
            height: '42px',
            borderRadius: '50%',
            border: 'none',
            background:
              !input.trim() || isAsking
                ? '#E2E8F0'
                : 'linear-gradient(135deg, #3B82F6, #1D4ED8)',
            color: '#FFFFFF',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: !input.trim() || isAsking ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s ease',
            flexShrink: 0,
            boxShadow:
              !input.trim() || isAsking
                ? 'none'
                : '0 2px 8px rgba(29, 78, 216, 0.35)',
          }}
        >
          <Send size={17} />
        </button>
      </form>
    </div>
  )
}
