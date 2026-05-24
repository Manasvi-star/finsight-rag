// src/api/api.js — Day 5: Replace mock functions with these real API calls
import axios from 'axios'

const BASE = 'http://localhost:8000'

export const uploadPDF = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return axios.post(`${BASE}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const askQuestion = (question, sessionId) =>
  axios.post(`${BASE}/ask`, { question, session_id: sessionId })

export const getSentiment = (sessionId) =>
  axios.get(`${BASE}/sentiment`, { params: { session_id: sessionId } })

export const getRisks = (sessionId) =>
  axios.get(`${BASE}/risks`, { params: { session_id: sessionId } })

export const getSummary = (sessionId) =>
  axios.get(`${BASE}/summary`, { params: { session_id: sessionId } })
