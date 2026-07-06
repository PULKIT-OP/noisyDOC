const {getUser} = require("../services/user");
async function AuthenticateUser(req, res, next){
    const token = req.cookies.cookie;
    if(!token){
        return res.status(401).render("login", { message: "Please log in to access this page" });
    }
    const user = await getUser(token);
    if (!user) {
        return res.status(401).render("login", { message: "Invalid token" });
    }
    req.user = user;
    next();
}

module.exports = AuthenticateUser;