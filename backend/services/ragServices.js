const axios = require("axios");
const fs = require("fs");
const FormData = require("form-data");

const RAG_URL = process.env.RAG_SERVICE_URL || "http://127.0.0.1:8000";
// The FastAPI reloader can take several seconds to import the embedding and
// OCR dependencies before it starts accepting connections.
const RAG_STARTUP_MAX_ATTEMPTS = 30;
const RAG_RETRY_DELAY_MS = 1000;

const wait = (milliseconds) =>
  new Promise((resolve) => setTimeout(resolve, milliseconds));

// called when user uploads a PDF
const ingestDocument = async (filePath, fileName, pdfId, progressToken) => {
  for (let attempt = 1; attempt <= RAG_STARTUP_MAX_ATTEMPTS; attempt += 1) {
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
      if (!isConnectionFailure || attempt === RAG_STARTUP_MAX_ATTEMPTS) {
        throw error;
      }

      console.log(
        `RAG service is not ready; retrying ingestion (${attempt}/${RAG_STARTUP_MAX_ATTEMPTS - 1})...`,
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
const streamQueryDocument = async (question, pdfId) => {
  return axios.post(`${RAG_URL}/query`, {
    question,
    pdf_id: pdfId,
    top_k: 8,
  }, {
    responseType: "stream",
  });
};

module.exports = { ingestDocument, getIngestStatus, streamQueryDocument };
