const express = require('express');
const mongoose = require('mongoose');
const User = require('./models/user');

mongoose.connect('"mongodb://127.0.0.1:27017/pdf-chat-app"')
.then(
    console.log("MongoDb Connected")
)
.catch((err) => {
    console.log("MongoDb Connection Error:", err)
})

const app = express();
const PORT = 3000;

app.set('view engine', 'ejs');
app.set('views', '../frontend');
app.use(express.static('../frontend'));

app.get('/', (req, res) => {
    res.json({ message: "Welcome to the PDF Chat App API" });
});
app.get('/signup', async (req, res) => {
    const { fullName, email, password } = req.body;
    // Create a new user instance
    const newUser = new User({ fullName, email, password });
    await User.create(newUser)
    res.json({ message: "User created successfully" });
});
app.get('/login', async (req, res) => {
    const { email, password } = req.body;
    // Find the user by email
    const user = await User.findOne({ email });
    if (!user) {
        return res.status(404).json({ message: "User not found" });
    }
    // Check if the password is correct
    if (password !== user.password) {
        return res.status(401).json({ message: "Invalid credentials" });
    }
    res.json({ message: "Login Successful" });
});

app.listen(PORT, () => {
    console.log(`Server is running on PORT:${PORT}`);
});