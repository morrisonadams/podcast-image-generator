import express from 'express';
import multer from 'multer';
import { OpenAI } from 'openai';

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(express.json());

app.post('/upload', upload.single('audio'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }
  res.json({ filename: req.file.filename });
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
