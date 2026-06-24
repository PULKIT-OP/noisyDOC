const express = require('express');
const Router = express.Router();

Router.get("/upload", (req, res) => {
    res.json({ message: "Upload endpoint" });
})

module.exports = Router;