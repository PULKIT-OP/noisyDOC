const express = require('express');
const Router = express.Router();
const { handleSignupUser, handleLoginUser } = require('../controllers/user');

Router.post('/signup', handleSignupUser);
Router.post('/login', handleLoginUser);

Router.get('/signup', (req, res) => {
    res.render("signup");
});
Router.get('/login', (req, res) => {
    res.render("login");
});


module.exports = Router;