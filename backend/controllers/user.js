const express = require("express");
const Router = express.Router();
const User = require("../models/user");
const { setUser, getUser } = require("../services/user");

async function handleSignupUser(req, res) {
  const { fullName, email, password } = req.body;
  const newUser = new User({ fullName, email, password });
  const createdUser = await User.create(newUser);
  if (!createdUser) {
    return res.status(500).render("signup", { message: "Error creating user" });
  }
  res.redirect("/login");
}

async function handleLoginUser(req, res) {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (!user) {
    return res.status(404).render("login", { message: "User not found" });
  }
  if (user.password !== password) {
    return res.status(401).render("login", { message: "Invalid credentials" });
  }
  const token = await setUser(user);
  res.cookie("cookie", token, { httpOnly: true, sameSite: "strict" }); // Store the token in the user object
  res.redirect("/");
}

module.exports = {
  handleSignupUser,
  handleLoginUser,
};
