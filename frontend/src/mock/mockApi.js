// src/mock/mockApi.js — all fake data lives here

export const mockUpload = async (file) => {
  await new Promise(r => setTimeout(r, 2000))
  return {
    sessionId: 'mock-session-123',
    fileName: file.name,
    pages: 247,
    chunks: 1842,
    status: 'ready'
  }
}

export const mockAsk = async (question) => {
  await new Promise(r => setTimeout(r, 1200))

  const qaBank = {
    revenue: {
      answer: 'TCS reported total revenue of ₹2,40,893 crore in FY2024, reflecting 8.4% year-on-year growth driven by BFSI and retail verticals. North America remained the largest geography at 53.1% of revenue, followed by UK at 15.2% and Continental Europe at 14.8%.',
      sentiment: 'bullish',
      confidence: 0.82,
      sources: [
        { page: 47, text: 'Revenue from operations grew 8.4% YoY to ₹2,40,893 crore...' },
        { page: 112, text: 'Geographic breakdown shows North America at 53.1%...' }
      ]
    },
    profit: {
      answer: 'Net profit for FY2024 stood at ₹46,099 crore, a 9.0% increase over FY2023. The net profit margin improved to 19.1% compared to 18.8% in the prior year, driven by operational efficiencies and improved deal economics in large transformational engagements.',
      sentiment: 'bullish',
      confidence: 0.88,
      sources: [
        { page: 63, text: 'Profit after tax increased 9.0% to ₹46,099 crore...' },
        { page: 65, text: 'Net profit margin expanded 30bps to 19.1%...' }
      ]
    },
    risk: {
      answer: 'Key risk factors include increasing debt obligations that may impact liquidity, volatile macroeconomic conditions affecting revenue guidance, elevated litigation risk across 3 geographies, and uncertainty in discretionary technology spending from enterprise clients. The company has disclosed 14 material risk factors in total.',
      sentiment: 'bearish',
      confidence: 0.76,
      sources: [
        { page: 89, text: 'Increasing debt obligations may impact liquidity...' },
        { page: 94, text: 'Volatile macroeconomic environment poses uncertainty...' }
      ]
    },
    default: {
      answer: 'TCS reported total revenue of ₹2,40,893 crore in FY2024, reflecting 8.4% year-on-year growth driven by BFSI and retail verticals. North America remained the largest geography at 53.1% of revenue. The company secured deal wins worth $42.7B in TCV, signaling a healthy pipeline for FY25.',
      sentiment: 'bullish',
      confidence: 0.82,
      sources: [
        { page: 47, text: 'Revenue from operations grew 8.4% YoY...' },
        { page: 112, text: 'Geographic breakdown shows North America at 53.1%...' }
      ]
    }
  }

  const q = question.toLowerCase()
  if (q.includes('revenue') || q.includes('sales') || q.includes('growth')) return qaBank.revenue
  if (q.includes('profit') || q.includes('margin') || q.includes('earning')) return qaBank.profit
  if (q.includes('risk') || q.includes('threat') || q.includes('danger')) return qaBank.risk
  return qaBank.default
}

export const mockSentiment = async () => {
  await new Promise(r => setTimeout(r, 800))
  return {
    overall: 'bullish',
    scores: { bullish: 54, neutral: 31, bearish: 15 },
    sections: [
      { name: "MD&A",              bullish: 62, neutral: 25, bearish: 13, score: '+0.62' },
      { name: "Risk Factors",      bullish: 12, neutral: 28, bearish: 60, score: '-0.48' },
      { name: "Financials",        bullish: 70, neutral: 22, bearish:  8, score: '+0.71' },
      { name: "Outlook",           bullish: 44, neutral: 40, bearish: 16, score: '+0.22' },
      { name: "Notes to Accounts", bullish: 30, neutral: 55, bearish: 15, score: '+0.05' },
    ]
  }
}

export const mockRisks = async () => {
  await new Promise(r => setTimeout(r, 600))
  return [
    { id: 1, severity: 'high',   text: 'Increasing debt obligations may impact liquidity in adverse market conditions.', page: 89,  section: 'Risk Factors' },
    { id: 2, severity: 'high',   text: 'Volatile macroeconomic environment poses uncertainty to revenue guidance.',       page: 94,  section: 'Risk Factors' },
    { id: 3, severity: 'medium', text: 'Litigation risk remains elevated across 3 geographies.',                         page: 102, section: 'Legal' },
    { id: 4, severity: 'medium', text: 'Uncertainty in discretionary technology spending from enterprise clients.',       page: 97,  section: 'Risk Factors' },
    { id: 5, severity: 'low',    text: 'Currency headwinds expected to moderate by Q3 FY25.',                            page: 51,  section: 'MD&A' },
  ]
}

export const mockSummary = async () => {
  await new Promise(r => setTimeout(r, 1000))
  return {
    overall: 'bullish',
    text: 'TCS delivered strong FY2024 performance with revenue crossing ₹2.4L crore, led by BFSI and Manufacturing verticals. Deal wins at $42.7B TCV signal a healthy pipeline. Margin compression of 0.2% was offset by operational efficiency gains. Cloud and AI-led transformation services now constitute 18% of revenues. Management remains cautiously optimistic for FY25 citing macro uncertainty in North America and Europe.',
    kpis: [
      { label: 'Revenue FY24',  value: '₹2,40,893 Cr', change: '+8.4%',  direction: 'up' },
      { label: 'Net Profit',    value: '₹46,099 Cr',   change: '+9.0%',  direction: 'up' },
      { label: 'EBIT Margin',   value: '24.3%',         change: '-0.2%',  direction: 'down' },
      { label: 'TCV Deal Wins', value: '$42.7B',        change: '+12.1%', direction: 'up' },
      { label: 'Headcount',     value: '6.14L',         change: '+2.3%',  direction: 'up' },
      { label: 'AI/Cloud Mix',  value: '18%',           change: '+4.1pp', direction: 'up' },
    ]
  }
}
