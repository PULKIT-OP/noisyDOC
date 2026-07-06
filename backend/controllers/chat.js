const express = require('express');
const { queryDocument } = require('../services/ragServices');

async function handleQuery(req, res){
    const question = req.body.question;
    if(!question){
        return res.status(400).json({ message: "Question is required" });
    }
    // Call the RAG service to get the answer
    try{
        const answer = await queryDocument(question);
        res.json({ answer });
    } catch (error) {
        res.status(500).json({ message: "Error occurred while processing the query" });
    }
}

module.exports = {
    handleQuery
};