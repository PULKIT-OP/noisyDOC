const express = require('express');
const { handleUploadPDF } = require('../controllers/upload');
const { handleQuery } = require('../controllers/chat');
const Router = express.Router();

Router.post("/upload", handleUploadPDF);
Router.post("/", handleQuery);

module.exports = Router;