const express = require("express");
const Router = express.Router();
const User = require("../models/user");
const { setUser, getUser } = require("../services/user");
const { createHmac, randomBytes } = require("node:crypto");

function generateHash(salt, password) {
  const hashedPassword = createHmac("sha256", salt)
    .update(password)
    .digest("hex");
  return hashedPassword;
}

async function handleSignupUser(req, res) {
  const { fullName, email, password } = req.body;
  try {
    const salt = randomBytes(16).toString("hex");
    const hashedPassword = generateHash(salt, password);

    const newUser = new User({
      fullName,
      email,
      password: hashedPassword,
      salt,
    });
    await User.create(newUser);
    return res.redirect("/login");
  } catch (err) {
    if (err && err.code === 11000) {
      return res
        .status(400)
        .render("signup", { message: "Email already registered" });
    }
    return res.status(500).render("signup", { message: "Error creating user" });
  }
}

async function handleLoginUser(req, res) {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (!user) {
    return res.status(404).render("login", { message: "Wrong email or password" });
  }
  const salt = user.salt;
  if (!salt) {
    return res
      .status(500)
      .render("login", { message: "User password data is incomplete" });
  }
  const hashedPassword = generateHash(salt, password);
  if (user.password !== hashedPassword) {
    return res.status(401).render("login", { message: "Wrong email or password" });
  }
  const token = await setUser(user);
  res.cookie("cookie", token, { httpOnly: true, sameSite: "strict" }); // Store the token in the user object
  res.redirect("/");
}

module.exports = {
  handleSignupUser,
  handleLoginUser,
};
