import { useState, useCallback } from 'react'
import Navbar from './components/layout/Navbar'
import Sidebar from './components/layout/Sidebar'
import QAPanel from './components/panels/QAPanel'
import SentimentPanel from './components/panels/SentimentPanel'
import RiskPanel from './components/panels/RiskPanel'
import SummaryPanel from './components/panels/SummaryPanel'
import {
  mockUpload,
  mockAsk,
  mockSentiment,
  mockRisks,
  mockSummary,
} from './mock/mockApi'

export default function App() {
  const [activeTab, setActiveTab] = useState('qa')
  const [uploadState, setUploadState] = useState('empty')
  const [fileInfo, setFileInfo] = useState(null)
  const [messages, setMessages] = useState([])
  const [sentimentData, setSentimentData] = useState(null)
  const [riskData, setRiskData] = useState(null)
  const [summaryData, setSummaryData] = useState(null)
  const [isAsking, setIsAsking] = useState(false)

  const handleUpload = useCallback(async (file) => {
    setUploadState('processing')
    try {
      const result = await mockUpload(file)
      setFileInfo(result)
      setUploadState('ready')

      // Auto-fetch all data in parallel
      const [sentiment, risks, summary] = await Promise.all([
        mockSentiment(),
        mockRisks(),
        mockSummary(),
      ])
      setSentimentData(sentiment)
      setRiskData(risks)
      setSummaryData(summary)
    } catch (err) {
      console.error('Upload failed:', err)
      setUploadState('empty')
    }
  }, [])

  const handleSendMessage = useCallback(
    async (text) => {
      setMessages((prev) => [...prev, { role: 'user', content: text }])
      setIsAsking(true)

      try {
        const response = await mockAsk(text)
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: response.answer,
            sentiment: response.sentiment,
            confidence: response.confidence,
            sources: response.sources,
          },
        ])
      } catch (err) {
        console.error('Ask failed:', err)
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: 'Sorry, something went wrong. Please try again.',
            sentiment: 'neutral',
            confidence: 0,
            sources: [],
          },
        ])
      } finally {
        setIsAsking(false)
      }
    },
    []
  )

  const renderPanel = () => {
    switch (activeTab) {
      case 'qa':
        return (
          <QAPanel
            messages={messages}
            onSendMessage={handleSendMessage}
            isAsking={isAsking}
            summaryData={summaryData}
          />
        )
      case 'summary':
        return <SummaryPanel data={summaryData} />
      case 'sentiment':
        return <SentimentPanel data={sentimentData} />
      case 'risk':
        return <RiskPanel data={riskData} />
      default:
        return null
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        width: '100vw',
        overflow: 'hidden',
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        backgroundColor: '#F0F2F5',
      }}
    >
      <Navbar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        fileName={fileInfo?.fileName}
      />
      <div
        style={{
          display: 'flex',
          flex: 1,
          overflow: 'hidden',
        }}
      >
        <Sidebar
          uploadState={uploadState}
          fileInfo={fileInfo}
          onUpload={handleUpload}
          riskData={riskData}
        />
        <main
          style={{
            flex: 1,
            overflow: 'hidden',
            backgroundColor: '#FAFBFC',
          }}
        >
          {renderPanel()}
        </main>
      </div>
    </div>
  )
}
