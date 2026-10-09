const express = require('express');
const { handleUploadPDF, getUploadStatus } = require('../controllers/upload');
const { handleQuery } = require('../controllers/chat');
const Router = express.Router();

Router.post("/upload", handleUploadPDF);
Router.get("/upload-status/:token", getUploadStatus);
Router.post("/", handleQuery);

module.exports = Router;