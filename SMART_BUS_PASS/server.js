const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
const port = 5000;

app.use(cors());
app.use(express.json());

// MongoDB Connection
mongoose.connect('mongodb://localhost:27017/Smart_bus', {
  useNewUrlParser: true,
  useUnifiedTopology: true
}).then(() => console.log('MongoDB connected'))
  .catch(err => console.error(err));

// Mongoose Schema
const studentSchema = new mongoose.Schema({
  name: String,
  email: String,
  college: String,
  id: String,
  pass: String,
  route: String,
  validTill: String
});

const Student = mongoose.model('Student', studentSchema);

// API Endpoint to validate/save student bus pass
app.post('/api/student', async (req, res) => {
  const { name, email, college, id, pass, route, validTill } = req.body;

  if (!name || !email || !college || !id || !pass || !route || !validTill) {
    return res.status(400).json({ message: 'Missing fields in QR data' });
  }

  try {
    // Check if student already exists
    const existing = await Student.findOne({ id, pass });
    if (existing) {
      return res.status(200).json({ message: 'Student already exists', student: existing });
    }

    // Save new student
    const student = new Student({ name, email, college, id, pass, route, validTill });
    await student.save();
    return res.status(201).json({ message: 'Student saved', student });
  } catch (err) {
    return res.status(500).json({ message: 'Server error', error: err.message });
  }
});

app.listen(port, () => {
  console.log(`🚀 Server running at http://localhost:${port}`);
});
