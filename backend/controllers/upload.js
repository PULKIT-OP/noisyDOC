const axios = require('axios');
const fs = require('fs');
const express = require('express');
const multer = require('multer');
const { ingestDocument } = require('../services/ragServices');
const path = require('path');
const PDF = require('../models/pdf');


const uploadDir = path.join(__dirname, '../uploads');
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
    file.mimetype === "application/octet-stream"  // for postman testing
  ) {
    cb(null, true);
  } else {
    cb(new Error('Invalid file type. Only TXT, DOC, and PDF files are allowed.'), false);
  }
}

const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: { fileSize: 10 * 1024 * 1024 },
});

async function handleUploadPDF(req, res){
    upload.single("document")(req, res, async function (err) {
    if (err instanceof multer.MulterError) {        // specifically checks for multer errors
      return res.status(400).json({ multerError: err.message });
    } else if (err) {                                               // checks for errors made by user
      return res.status(400).json({ message: err.message });
    }
    if (!req.file) {        // if no file is uploaded or file type is invalid, multer will not add the file to req object and hence we can check for that
      return res
        .status(400)
        .json({ message: "No file uploaded or invalid file type" });
    }

    // now saving to mongoDB
    const newPDF = await PDF.create({
        name: req.file.filename,
        createdBy: req.user._id,
    })
    if(!newPDF){
        return res.status(500).json({ message: "Failed to upload PDF" });
    }

    try {
      await ingestDocument(req.file.path, req.file.filename);
    } catch (ragErr) {
      console.error("RAG ingestion failed:", ragErr.response?.data || ragErr.message || ragErr);
      // don't block the response — file is uploaded, RAG failed silently
      return res.status(500).json({ message: "File uploaded but RAG ingestion failed" });
    }

    return res.status(200).json({   // FIX 3: return JSON not redirect (this is an API)
      message: "File uploaded and ingested successfully",
      file: req.file.filename,
      id: newPDF._id
    });
  });
}

module.exports = {
    handleUploadPDF,
};