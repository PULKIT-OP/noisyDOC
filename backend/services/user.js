const JWT = require('jsonwebtoken');
const secretKey = process.env.JWT_SECRET;
async function setUser(user){
    return JWT.sign(
    {
      _id: user._id,
      email: user.email,
    },
    secretKey,
  );
}

async function getUser(token){
    if (!token) {
    return null;
  }
  try {
    return JWT.verify(token, secretKey);
  } catch (err) {
    return null;
  }
}

module.exports = {
    setUser,
    getUser
};