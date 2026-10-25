const express = require("express");
const { streamQueryDocument } = require("../services/ragServices");

async function handleQuery(req, res) {
  const question = req.body.question;
  const pdfId = req.body.pdfId || req.body.pdf_id;
  if (!question) {
    return res.status(400).json({ message: "Question is required" });
  }
  if (!pdfId) {
    return res.status(400).json({ message: "Document id is required" });
  }
  // Call the RAG service to get the answer
  try {
    const response = await streamQueryDocument(question, pdfId);
    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    response.data.pipe(res);
  } catch (error) {
    res
      .status(500)
      .json({ message: "Error occurred while processing the query" });
  }
}

module.exports = {
  handleQuery,
};
