import os
import json
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

ENABLE_TRANSCRIPTION = os.getenv("ENABLE_TRANSCRIPTION", "true").lower() == "true"
ENABLE_IMAGE_GEN = os.getenv("ENABLE_IMAGE_GEN", "true").lower() == "true"

TRANSCRIBE_MODEL = os.getenv("TRANSCRIBE_MODEL", "whisper-1")
TOPIC_MODEL = os.getenv("TOPIC_MODEL", "gpt-4o-mini")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gpt-image-1")

client = OpenAI()

def process_audio(audio_path: str, job_dir: str) -> None:
    """
    Full pipeline: transcribe -> topic segments -> image prompts -> images.
    Writes results to segments.json in the job_dir.
    """
    job = Path(job_dir)
    seg_json = job / "segments.json"
    try:
        transcript = transcribe(audio_path) if ENABLE_TRANSCRIPTION else "(transcription disabled)"
        segments = propose_segments(transcript, audio_path)

        # Generate images per segment
        for seg in segments:
            prompt = seg.get("prompt") or seg.get("title", "topic illustration")
            image_path = generate_image(prompt, job) if ENABLE_IMAGE_GEN else create_placeholder(job, prompt)
            seg["image_path"] = str(image_path)

        payload = {"status":"ready", "segments": segments}
        seg_json.write_text(json.dumps(payload), encoding="utf-8")
    except Exception as e:
        seg_json.write_text(json.dumps({"status":"error","error": str(e)}), encoding="utf-8")

def transcribe(audio_path: str) -> str:
    if not ENABLE_TRANSCRIPTION:
        return ""
    with open(audio_path, "rb") as f:
        # Whisper speech to text
        # Note: the OpenAI SDK uses "audio.transcriptions.create" for Whisper v1.
        transcript = client.audio.transcriptions.create(model=TRANSCRIBE_MODEL, file=f)
    text = transcript.text if hasattr(transcript, "text") else str(transcript)
    return text

def propose_segments(transcript: str, audio_path: str) -> List[Dict[str, Any]]:
    """
    Ask GPT to produce coarse segments with start and end times plus an image prompt.
    If transcript is empty, fall back to naive time slicing.
    """
    import math
    # Fallback: naive 30-second slices if we do not have a transcript
    if not transcript or len(transcript.strip()) < 40:
        # Try to probe duration using pydub
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_path)
            duration_sec = len(audio) / 1000.0
        except Exception:
            duration_sec = 300.0
        seg_len = 30.0
        n = max(1, math.ceil(duration_sec / seg_len))
        segments = []
        for i in range(n):
            start = i * seg_len
            end = min(duration_sec, (i+1)*seg_len)
            segments.append({
                "start": round(start, 2),
                "end": round(end, 2),
                "title": f"Section {i+1}",
                "prompt": "A simple abstract illustration for this section."
            })
        return segments

    # Use GPT to create segments
    sys = (
        "You create timecoded topic segments for an audio transcript. "
        "Return concise JSON with fields: start, end, title, prompt. "
        "Limit to 6 to 10 segments. start/end are in seconds. "
        "Prompts should be concrete, specific, and safe for general audiences. "
        "If the topic references entities like 'Roman phalanx', write a helpful image prompt."
    )
    user = f"Transcript:\n{transcript[:12000]}\n\nReturn JSON only as a list of segments."

    resp = client.chat.completions.create(
        model=TOPIC_MODEL,
        messages=[{"role":"system","content":sys},{"role":"user","content":user}],
        temperature=0.4,
    )
    content = resp.choices[0].message.content.strip()
    # Try to parse JSON list
    try:
        data = json.loads(content)
    except Exception:
        # Heuristic extraction
        import re
        m = re.search(r'\[.*\]', content, re.S)
        data = json.loads(m.group(0)) if m else []

    # Clamp and sanitize
    cleaned = []
    for i, seg in enumerate(data):
        try:
            start = max(0.0, float(seg.get("start", 0)))
            end = max(start + 1.0, float(seg.get("end", start + 30)))
            title = str(seg.get("title", f"Segment {i+1}"))[:120]
            prompt = str(seg.get("prompt", title))[:400]
            cleaned.append({"start": round(start,2), "end": round(end,2), "title": title, "prompt": prompt})
        except Exception:
            continue
    if not cleaned:
        # Fallback to naive slicing if parsing failed
        return propose_segments("", audio_path)
    return cleaned

def generate_image(prompt: str, job: Path) -> Path:
    """
    Generate one 1024x1024 image using the Images API and save it under the job dir.
    """
    img = client.images.generate(
        model=IMAGE_MODEL,
        prompt=prompt,
        size="1024x1024",
        n=1,
    )
    b64 = img.data[0].b64_json
    import base64
    raw = base64.b64decode(b64)
    out = job / f"{safe_name(prompt)[:40]}_{len(list(job.glob('*.png'))):02d}.png"
    out.write_bytes(raw)
    return out

def create_placeholder(job: Path, prompt: str) -> Path:
    """
    Create a tiny placeholder PNG so the UI still works without image gen.
    """
    from PIL import Image, ImageDraw, ImageFont
    out = job / f"{safe_name(prompt)[:40]}_{len(list(job.glob('*.png'))):02d}.png"
    img = Image.new("RGB", (800, 600), (240, 240, 240))
    d = ImageDraw.Draw(img)
    text = f"Placeholder\\n{prompt[:80]}"
    d.multiline_text((20, 20), text, fill=(0,0,0))
    img.save(out)
    return out

def safe_name(s: str) -> str:
    return "".join(c for c in s if c.isalnum() or c in ("-","_"," ")).strip().replace(" ","_")
