const {getUser} = require("../services/user");
async function AuthenticateUser(req, res, next){
    const token = req.cookies.cookie;
    if(!token){
        return res.status(401).json({ message: "Unauthorized" });
    }
    const user = await getUser(token);
    if (!user) {
        return res.status(401).json({ message: "Invalid token" });
    }
    req.user = user;
    next();
}

module.exports = AuthenticateUser;