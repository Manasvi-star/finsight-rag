import axios from 'axios'

const BASE = 'http://localhost:8000'

// Get auth headers helper
const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

// Automatically register and login a default user on load
export const loginOrCreateUser = async () => {
  const defaultCredentials = {
    email: 'defaultuser@finsight.com',
    password: 'securepassword123'
  }

  try {
    // 1. Try to login
    const loginRes = await axios.post(`${BASE}/auth/login`, defaultCredentials)
    if (loginRes.data?.access_token) {
      localStorage.setItem('token', loginRes.data.access_token)
      return loginRes.data.access_token
    }
  } catch (err) {
    if (err.response?.status === 401 || err.response?.status === 404 || err.response?.status === 422) {
      // 2. If login fails, try to register
      try {
        await axios.post(`${BASE}/auth/register`, defaultCredentials)
        const loginRes = await axios.post(`${BASE}/auth/login`, defaultCredentials)
        if (loginRes.data?.access_token) {
          localStorage.setItem('token', loginRes.data.access_token)
          return loginRes.data.access_token
        }
      } catch (regErr) {
        console.error('Auto-registration failed:', regErr)
      }
    } else {
      console.error('Auto-login failed:', err)
    }
  }
  return null
}

export const uploadPDF = async (file) => {
  // Ensure token exists
  await loginOrCreateUser()

  const formData = new FormData()
  formData.append('file', file)

  // 1. Upload file
  const response = await axios.post(`${BASE}/documents/upload`, formData, {
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'multipart/form-data'
    }
  })

  const { document_id, job_id } = response.data

  // 2. Poll job status
  let isDone = false
  let pollAttempts = 0
  const maxAttempts = 60 // 2 minutes max

  while (!isDone && pollAttempts < maxAttempts) {
    await new Promise((resolve) => setTimeout(resolve, 2000))
    pollAttempts++

    const statusRes = await axios.get(`${BASE}/jobs/${job_id}/status`, {
      headers: getAuthHeaders()
    })

    if (statusRes.data.status === 'ready') {
      isDone = true
    } else if (statusRes.data.status === 'failed') {
      throw new Error('PDF Ingestion job failed.')
    }
  }

  if (!isDone) {
    throw new Error('PDF Ingestion timed out.')
  }

  // 3. Fetch document details to get page and chunk count
  const docsRes = await axios.get(`${BASE}/documents`, {
    headers: getAuthHeaders()
  })

  const doc = docsRes.data.documents.find((d) => d.id === document_id)
  if (!doc) {
    throw new Error('Ingested document not found.')
  }

  return {
    sessionId: document_id,
    fileName: doc.filename,
    pages: doc.page_count,
    chunks: doc.chunk_count,
    status: doc.status
  }
}

// SSE stream reader for Q&A
export const askQuestionStream = async (question, documentId, onToken, onFinal) => {
  let token = localStorage.getItem('token')
  if (!token) {
    token = await loginOrCreateUser()
  }

  const response = await fetch(`${BASE}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      question,
      document_id: documentId,
      history: []
    })
  })

  if (!response.ok) {
    throw new Error('Query failed')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop()

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed.startsWith('data: ')) continue
      try {
        const jsonStr = trimmed.slice(6)
        const parsed = JSON.parse(jsonStr)
        if (parsed.token) {
          onToken(parsed.token)
        } else if (parsed.answer) {
          onFinal(parsed)
        }
      } catch (err) {
        console.error('Failed to parse SSE line:', line, err)
      }
    }
  }
}

export const getSentiment = async (documentId) => {
  const response = await axios.post(`${BASE}/analysis/sentiment`, { document_id: documentId }, {
    headers: getAuthHeaders()
  })
  return response.data
}

export const getRisks = async (documentId) => {
  const response = await axios.post(`${BASE}/analysis/risk`, { document_id: documentId }, {
    headers: getAuthHeaders()
  })

  const risksList = []
  let idCounter = 1
  const sections = response.data.sections || []

  for (const sec of sections) {
    const pageMatch = sec.heading.match(/Page\s+(\d+)/i)
    const page = pageMatch ? parseInt(pageMatch[1], 10) : 1
    const sectionName = sec.heading.split(':').pop().trim()

    let severity = 'low'
    if (sec.score >= 0.6) severity = 'high'
    else if (sec.score >= 0.25) severity = 'medium'

    if (sec.flags && sec.flags.length > 0) {
      for (const flag of sec.flags) {
        risksList.push({
          id: idCounter++,
          severity: severity,
          text: `${flag}: ${sec.excerpt}`,
          page: page,
          section: sectionName
        })
      }
    } else if (sec.score > 0) {
      risksList.push({
        id: idCounter++,
        severity: severity,
        text: sec.excerpt,
        page: page,
        section: sectionName
      })
    }
  }

  return risksList
}

export const getSummary = async (documentId) => {
  const response = await axios.post(`${BASE}/analysis/summary`, { document_id: documentId }, {
    headers: getAuthHeaders()
  })

  const { summary, highlights } = response.data

  // Calculate overall sentiment based on highlights text keywords
  let overall = 'neutral'
  const combinedText = (summary + ' ' + highlights.join(' ')).toLowerCase()
  const positiveCount = (combinedText.match(/growth|strong|increase|up|higher|improve|positive/g) || []).length
  const negativeCount = (combinedText.match(/decline|risk|loss|down|lower|decrease|negative/g) || []).length

  if (positiveCount > negativeCount + 2) overall = 'bullish'
  else if (negativeCount > positiveCount + 2) overall = 'bearish'

  // Map highlights list to KPIs
  const kpis = (highlights || []).map((highlight) => {
    let label = 'Financial Highlight'
    let value = 'Active'
    let change = ''
    let direction = 'up'

    // Extract label
    if (highlight.toLowerCase().includes('revenue')) {
      label = 'Revenue Performance'
      direction = highlight.toLowerCase().includes('growth') || !highlight.toLowerCase().includes('decline') ? 'up' : 'down'
    } else if (highlight.toLowerCase().includes('margin')) {
      label = 'Operating Margin'
      direction = highlight.toLowerCase().includes('improved') || !highlight.toLowerCase().includes('decrease') ? 'up' : 'down'
    } else if (highlight.toLowerCase().includes('net income') || highlight.toLowerCase().includes('profit')) {
      label = 'Net Income'
      direction = 'up'
    } else {
      label = highlight.split(',')[0].slice(0, 30)
    }

    // Extract change (percentage)
    const pctMatch = highlight.match(/([+-]?[0-9.]+\%)/)
    if (pctMatch) {
      change = pctMatch[1]
      if (change.startsWith('-')) direction = 'down'
      else if (change.startsWith('+')) direction = 'up'
    }

    // Extract value
    const numMatch = highlight.match(/([₹$]?[0-9,.]+\s*(?:crore|billion|million|INR|USD|Cr|B|M)?)/i)
    if (numMatch) {
      value = numMatch[1]
    }

    if (change === '') {
      change = direction === 'up' ? '+0.0%' : '-0.0%'
    }

    return {
      label: label.trim(),
      value: value.trim(),
      change: change,
      direction: direction
    }
  })

  // Ensure we have at least 3 KPIs for visual layout
  while (kpis.length < 3) {
    kpis.push({
      label: 'Financial Performance',
      value: 'Verified',
      change: '+0.0%',
      direction: 'up'
    })
  }

  return {
    overall: overall,
    text: summary,
    kpis: kpis
  }
}
