const express = require("express");
const Router = express.Router();
const { handleSignupUser, handleLoginUser } = require("../controllers/user");
const AuthenticateUser = require("../middlewares/user");

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
Router.get("/chat", AuthenticateUser, (req, res) => {
  res.render("chat");
});
Router.get("/chat/upload", AuthenticateUser, (req, res) => {
  res.render("chat-upload");
});

module.exports = Router;
