import os
import uuid
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dotenv import load_dotenv

from .pipeline import process_audio

load_dotenv()

app = FastAPI(title="Audio to Illustrations")

BASE_DIR = Path(__file__).resolve().parent
STORAGE = BASE_DIR / "storage"
STATIC = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=STATIC), name="static")
app.mount("/files", StaticFiles(directory=STORAGE), name="files")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())[:8]
    job_dir = STORAGE / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename).suffix.lower() or ".mp3"
    audio_path = job_dir / f"audio{suffix}"
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    # Seed skeleton segments file for UI
    segments_path = job_dir / "segments.json"
    with open(segments_path, "w", encoding="utf-8") as f:
        json.dump({"status":"processing","segments":[]}, f)

    # Run processing in a background thread to keep response snappy
    import threading
    t = threading.Thread(target=process_audio, args=(str(audio_path), str(job_dir)), daemon=True)
    t.start()

    # Return URLs for client
    audio_url = f"/files/{job_id}/{audio_path.name}"
    return JSONResponse({"job_id": job_id, "audio_url": audio_url})

@app.get("/segments/{job_id}")
async def get_segments(job_id: str):
    job_dir = STORAGE / job_id
    segments_path = job_dir / "segments.json"
    if not segments_path.exists():
        return JSONResponse({"status":"missing","segments":[]})
    with open(segments_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Convert file paths to served URLs
    for seg in data.get("segments", []):
        if seg.get("image_path"):
            seg["image_url"] = f"/files/{job_id}/{Path(seg['image_path']).name}"
    return JSONResponse(data)
