const axios = require('axios')
const fs = require('fs')
const FormData = require('form-data')

const RAG_URL = process.env.RAG_SERVICE_URL || 'http://localhost:8000'

// called when user uploads a PDF
const ingestDocument = async (filePath, fileName) => {
  const formData = new FormData()
  const fileStream = fs.createReadStream(filePath)
  formData.append('file', fileStream, fileName)

  const response = await axios.post(`${RAG_URL}/ingest`, formData, {
    headers: formData.getHeaders()
  })
  return response.data
}

// called when user sends a chat message
const queryDocument = async (question) => {
  const response = await axios.post(`${RAG_URL}/query`, {
    question,
    top_k: 3
  })
  return response.data.answer
}

module.exports = { ingestDocument, queryDocument }