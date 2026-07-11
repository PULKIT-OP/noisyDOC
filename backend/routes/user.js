const express = require("express");
const Router = express.Router();
const { handleSignupUser, handleLoginUser } = require("../controllers/user");
const AuthenticateUser = require("../middlewares/user");
const PDF = require("../models/pdf");

Router.post("/user/signup", handleSignupUser);
Router.post("/user/login", handleLoginUser);
Router.get("/logout", (req, res) => {
  res.clearCookie("cookie");
  res.redirect("/login");
});

Router.get("/signup", (req, res) => {
  res.render("signup");
});
Router.get("/login", (req, res) => {
  res.render("login");
});
Router.get("/", (req, res) => {
  res.render("home");
});
Router.get("/my-pdfs", AuthenticateUser, (req, res) => {
  res.render("my-pdfs");
});

Router.get("/my-pdfs-data", AuthenticateUser, async (req, res) => {
  try {
    const user = req.user; // AuthenticateUser middleware should set this
    const pdfs = await PDF.find({ createdBy: user._id });
    res.json(
      pdfs.map((pdf) => ({
        id: pdf._id,
        filename: pdf.name,
        uploadDate: pdf.createdAt,
        description: "Document indexed for search.",
      })),
    );
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch PDFs" });
  }
});
Router.get("/chat", AuthenticateUser, (req, res) => {
  res.render("chat");
});

module.exports = Router;
