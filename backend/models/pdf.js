const mongoose = require('mongoose');

const pdfSchema = new mongoose.Schema({
    name:{
        type: String,
        required: true
    },
    createdAt: {
        type: Date,
        default: Date.now
    },
    createdBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'users',
        required: true
    }
}, { timestamps: true });

const PDF = mongoose.model("pdf", pdfSchema);

module.exports = PDF;