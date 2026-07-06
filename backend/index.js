require("dotenv").config({ path: "../.env" });
const express = require("express");
const mongoose = require("mongoose");
const User = require("./models/user");
const UserRouter = require("./routes/user");
const AuthenticateUser = require("./middlewares/user");
const ChatRouter = require("./routes/chat");
const cookieParser = require("cookie-parser");
const multer = require("multer");
const path = require("path");
const { getUser } = require("./services/user");

// MongoDB Connection
mongoose
  .connect("mongodb://127.0.0.1:27017/pdf-chat-app")
  .then(console.log("MongoDb Connected"))
  .catch((err) => {
    console.log("MongoDb Connection Error:", err);
  });

// Express App Setup
const app = express();
const PORT = 3000;

// Middlewares
app.set("view engine", "ejs");
app.set("views", "../frontend");
app.use(express.static("../frontend"));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(async (req, res, next) => {
  const token = req.cookies.cookie;
  res.locals.currentUser = token ? await getUser(token) : null;
  next();
});

// Routes
app.use("/", UserRouter);
app.use("/chat", AuthenticateUser, ChatRouter);

app.listen(PORT, () => {
  console.log(`Server is running on PORT:${PORT}`);
});
