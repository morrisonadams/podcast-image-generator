import express from 'express';
import multer from 'multer';
import fs from 'fs';
import path from 'path';
import { randomUUID } from 'crypto';
import { OpenAI } from 'openai';

const app = express();

// Configure multer storage to place files under /storage/{jobId}/audio
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const jobId = randomUUID();
    const uploadPath = path.join('/storage', jobId, 'audio');
    fs.mkdirSync(uploadPath, { recursive: true });
    req.jobId = jobId;
    cb(null, uploadPath);
  },
  filename: (req, file, cb) => {
    cb(null, file.originalname);
  }
});

const upload = multer({
  storage,
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('audio/')) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type'));
    }
  },
  limits: { fileSize: 25 * 1024 * 1024 } // 25MB limit
});

app.use(express.json());

app.post('/upload', (req, res) => {
  upload.single('audio')(req, res, (err) => {
    if (err) {
      if (err.message === 'Invalid file type') {
        return res.status(400).json({ error: err.message });
      }
      if (err.code === 'LIMIT_FILE_SIZE') {
        return res.status(400).json({ error: 'File too large' });
      }
      return res.status(500).json({ error: 'Upload failed' });
    }

    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    res.json({ jobId: req.jobId });
  });
});

app.post('/gpt', async (req, res) => {
  try {
    const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
    const completion = await client.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'user', content: req.body.prompt ?? 'Hello from API' }
      ]
    });
    res.json(completion.choices[0].message);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`API running on port ${PORT}`);
});
