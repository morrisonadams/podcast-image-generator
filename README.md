# Audio to Illustrations (Barebones)

A tiny FastAPI app that lets you upload an audio file, plays it in the browser, and uses GPT to:
1) transcribe
2) detect topic shifts with timestamps
3) generate image prompts
4) create images for those prompts

It then shows the images at the right time as the audio plays.

## What this is
- A minimal scaffold so you can take it further.
- Works locally.
- Uses the OpenAI Python SDK for Whisper transcription, GPT topic segmentation, and image generation.
- Stores outputs to `app/storage/<job_id>/...`

## What you need
- Python 3.10+
- An OpenAI API key

## Quick start
```bash
# 1) Create and activate venv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Add your API key
cp .env.example .env
# edit .env and set OPENAI_API_KEY

# 4) Run
uvicorn app.main:app --reload
```

Then open http://localhost:8000.

## How it works
1. Upload an audio file on the home page.
2. The server saves it to `app/storage/<job_id>/audio.<ext>`
3. `pipeline.process_audio()` does:
   - Transcribe with Whisper.
   - Ask a GPT model to propose timecoded "key moments" as JSON with a short title and an image prompt per moment.
   - Generate an image per prompt with the Images API.
4. The browser polls `/segments/<job_id>` for the JSON list.
5. As the audio plays, client code checks the current time against the segments and swaps in the relevant image.

## Notes
- This is intentionally barebones. Expect to improve the segmentation prompt, fallback logic, caching, and error handling.
- For a fast first run, you can set `ENABLE_IMAGE_GEN=false` in `.env` to skip image generation and use placeholders.
- Supported audio types depend on your local ffmpeg support for Whisper. WAV/MP3/M4A are usually fine.

## Docker (optional)
```bash
docker build -t audio2pics .
docker run -it --rm -p 8000:8000 --env-file .env -v ${PWD}/app/storage:/app/app/storage audio2pics
```

## License
MIT
# podcast-image-generator
