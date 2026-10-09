const axios = require("axios");
const fs = require("fs");
const express = require("express");
const multer = require("multer");
const { ingestDocument, getIngestStatus } = require("../services/ragServices");
const path = require("path");
const PDF = require("../models/pdf");

const uploadDir = path.join(__dirname, "../uploads");
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    return cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    return cb(null, `${Date.now()}-${file.originalname}`);
  },
});

function fileFilter(req, file, cb) {
  console.log("MimeType Coming : ", file.mimetype);
  if (
    file.mimetype === "plain/text" ||
    file.mimetype === "application/msword" ||
    file.mimetype === "application/pdf" ||
    file.mimetype === "application/octet-stream" // for postman testing
  ) {
    cb(null, true);
  } else {
    cb(
      new Error("Invalid file type. Only TXT, DOC, and PDF files are allowed."),
      false,
    );
  }
}

const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: { fileSize: 10 * 1024 * 1024 },
});

const uploadStatuses = new Map();

function setUploadStatus(token, status) {
  if (token) {
    uploadStatuses.set(token, { ...status, updatedAt: Date.now() });
  }
}

function getUploadStatus(req, res) {
  const status = uploadStatuses.get(req.params.token);
  if (!status) {
    return res.status(404).json({ status: "not_found", message: "Upload status not found." });
  }
  return res.json(status);
}

async function handleUploadPDF(req, res) {
  const progressToken = req.get("X-Upload-Token");
  setUploadStatus(progressToken, {
    status: "uploading",
    progress: 5,
    message: "Uploading document...",
  });
  upload.single("document")(req, res, async function (err) {
    if (err instanceof multer.MulterError) {
      setUploadStatus(progressToken, { status: "failed", progress: 0, message: err.message });
      // specifically checks for multer errors
      return res.status(400).json({ multerError: err.message });
    } else if (err) {
      setUploadStatus(progressToken, { status: "failed", progress: 0, message: err.message });
      // checks for errors made by user
      return res.status(400).json({ message: err.message });
    }
    if (!req.file) {
      setUploadStatus(progressToken, { status: "failed", progress: 0, message: "No file uploaded or invalid file type." });
      // if no file is uploaded or file type is invalid, multer will not add the file to req object and hence we can check for that
      return res
        .status(400)
        .json({ message: "No file uploaded or invalid file type" });
    }
    setUploadStatus(progressToken, {
      status: "processing",
      progress: 25,
      message: "Document uploaded. Preparing it for indexing...",
    });
    const statusPoll = setInterval(async () => {
      if (!progressToken) return;
      try {
        const ragStatus = await getIngestStatus(progressToken);
        setUploadStatus(progressToken, ragStatus);
      } catch (statusError) {
        console.warn("Unable to read RAG ingestion status:", statusError.message);
      }
    }, 500);

    // now saving to mongoDB
    const newPDF = await PDF.create({
      name: req.file.filename,
      createdBy: req.user._id,
    });
    if (!newPDF) {
      return res.status(500).json({ message: "Failed to upload PDF" });
    }

    try {
      await ingestDocument(
        req.file.path,
        req.file.filename,
        newPDF._id.toString(),
        progressToken,
      );
    } catch (ragErr) {
      console.error(
        "RAG ingestion failed:",
        ragErr.response?.data || ragErr.message || ragErr,
      );
      setUploadStatus(progressToken, {
        status: "failed",
        progress: 0,
        message: ragErr.response?.data?.detail?.message ||
          ragErr.response?.data?.message ||
          "Document processing failed.",
      });
      // don't block the response — file is uploaded, RAG failed silently
      return res
        .status(500)
        .json({ message: "File uploaded but RAG ingestion failed" });
    } finally {
      clearInterval(statusPoll);
    }

    setUploadStatus(progressToken, {
      status: "complete",
      progress: 100,
      message: "Document is ready to chat with.",
    });
    return res.status(200).json({
      // FIX 3: return JSON not redirect (this is an API)
      message: "File uploaded and ingested successfully",
      file: req.file.filename,
      id: newPDF._id,
    });
  });
}

module.exports = {
  handleUploadPDF,
  getUploadStatus,
};
