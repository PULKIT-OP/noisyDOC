const express = require('express');
const Router = express.Router();
const User = require('../models/user');
const { setUser, getUser } = require('../services/user');

async function handleSignupUser (req, res){
    const { fullName, email, password } = req.body;
    const newUser = new User({ fullName, email, password });
    const createdUser = await User.create(newUser);
    if(!createdUser){
        return res.status(500).json({ message: "Failed to create user" });
    }
    res.json({ message: "User created successfully", user: createdUser });
}

async function handleLoginUser (req, res){
    const { email, password } = req.body;
    const user = await User.findOne({ email });
    if (!user) {
        return res.status(404).json({ message: "User not found" });
    }
    if (user.password !== password) {
        return res.status(401).json({ message: "Invalid credentials" });
    }
    const token = await setUser(user);
    res.cookie("cookie", token) // Store the token in the user object
    res.json({ message: "Login successful", user: user, token });
}



module.exports = {
    handleSignupUser,
    handleLoginUser
};
