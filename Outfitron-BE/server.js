const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { log } = require('console');
const cors =  require('cors')
const otpGenerator = require("otp-generator");
const OTP = require("./models/OTP");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const User = require("./models/User");
const db = require("./dbconnector");
const { sendOtp, signup, login, auth } = require('./controllers');

db.connect();
const app = express();
const PORT = 3000;
app.use(cors())
app.use(express.json());
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}

// Multer config
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, './uploads'),
  filename: (req, file, cb) => {
    if (file.fieldname === 'selfie') cb(null, 'selfie.jpg');
    else if (file.fieldname === 'fullbody') cb(null, 'fullbody.jpg');
    else cb(null, file.originalname);
  }
});

const upload = multer({ storage });

// Upload + Run ML Python Script
app.post('/upload' , upload.fields([
  { name: 'selfie', maxCount: 1 },
  { name: 'fullbody', maxCount: 1 }
]), auth , (req, res) => {
  if (!req.files?.selfie || !req.files?.fullbody) {
    return res.status(400).json({ error: 'Both images are required.' });
  }

  const selfiePath = path.join(__dirname, 'uploads', 'selfie.jpg');
  const fullbodyPath = path.join(__dirname, 'uploads', 'fullbody.jpg');

  const python = spawn('python', [
    path.join(__dirname, './', 'script.py'),
    '--selfie', selfiePath,
    '--fullbody', fullbodyPath
  ]);
  

  const outputPath = path.join(__dirname, 'output.txt');
  const outputStream = fs.createWriteStream(outputPath);

  python.stdout.pipe(outputStream);
  python.stderr.pipe(process.stderr);

  python.on('close', (code) => {
    if (code === 0) {
      return res.status(200).json({ message: 'Images uploaded and analysis completed!' });
    } else {
      return res.status(500).json({ error: 'Python script failed.', code });
    }
  });
});

app.get('/output', auth , (req, res) => {
  const filePath = path.join(__dirname, 'output.txt');
  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) return res.status(500).send('Could not read output file.');
    console.log(data)
    res.send(data);
  });
});


app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});

app.get("/" , (req , res) => {
  res.send(`<h1>Server started sucessfully</h1>`);
})

app.post('/sendotp' , sendOtp);
app.post("/signup" , signup);
app.post("/login" , login);