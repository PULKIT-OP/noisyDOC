const axios = require("axios");
const fs = require("fs");
const FormData = require("form-data");

const RAG_URL = process.env.RAG_SERVICE_URL || "http://127.0.0.1:8000";
const RAG_STARTUP_RETRIES = 10;
const RAG_RETRY_DELAY_MS = 1000;

const wait = (milliseconds) =>
  new Promise((resolve) => setTimeout(resolve, milliseconds));

// called when user uploads a PDF
const ingestDocument = async (filePath, fileName, pdfId, progressToken) => {
  for (let attempt = 1; attempt <= RAG_STARTUP_RETRIES; attempt += 1) {
    const formData = new FormData();
    formData.append("file", fs.createReadStream(filePath), fileName);
    formData.append("pdf_id", pdfId);
    formData.append("progress_token", progressToken);

    try {
      const response = await axios.post(`${RAG_URL}/ingest`, formData, {
        headers: formData.getHeaders(),
      });
      return response.data;
    } catch (error) {
      const isConnectionFailure =
        error.code === "ECONNREFUSED" || error.code === "ECONNRESET";
      if (!isConnectionFailure || attempt === RAG_STARTUP_RETRIES) {
        throw error;
      }

      console.log(
        `RAG service is not ready; retrying ingestion (${attempt}/${RAG_STARTUP_RETRIES - 1})...`,
      );
      await wait(RAG_RETRY_DELAY_MS);
    }
  }
};

const getIngestStatus = async (progressToken) => {
  const response = await axios.get(`${RAG_URL}/status/${encodeURIComponent(progressToken)}`);
  return response.data;
};

// called when user sends a chat message
const queryDocument = async (question, pdfId) => {
  const response = await axios.post(`${RAG_URL}/query`, {
    question,
    pdf_id: pdfId,
    top_k: 8,
  });
  return response.data.answer;
};

module.exports = { ingestDocument, getIngestStatus, queryDocument };
