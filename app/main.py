import os
import uuid
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.templating import Jinja2Templates
from starlette.requests import Request

from app.services.media import extract_audio_for_asr, merge_video_and_audio, ensure_directory
from app.services.transcribe import transcribe_audio
from app.services.translate import resolve_language, translate_segments
from app.services.tts import synthesize_timeline

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
OUTPUTS_DIR = DATA_DIR / "outputs"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
STATIC_DIR = BASE_DIR / "app" / "static"

for d in [UPLOADS_DIR, OUTPUTS_DIR]:
	ensure_directory(d)

app = FastAPI(title="Video Dubbing Tool", version="0.1.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
	return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/dub")
async def dub_video(
	video: UploadFile = File(...),
	language: str = Form(...),
	voice: str = Form("")
) -> JSONResponse:
	try:
		job_id = str(uuid.uuid4())
		job_dir = OUTPUTS_DIR / job_id
		ensure_directory(job_dir)

		upload_path = UPLOADS_DIR / f"{job_id}_{video.filename}"
		with open(upload_path, "wb") as f:
			f.write(await video.read())

		# Step 2: Extract audio for ASR
		asr_audio_path = job_dir / "asr_audio.wav"
		extract_audio_for_asr(str(upload_path), str(asr_audio_path))

		# Step 3: Transcribe
		segments = transcribe_audio(str(asr_audio_path))

		# Step 4: Translate
		lang = resolve_language(language)
		translated_segments = translate_segments(segments, lang.google_code)

		# Step 5: TTS and timeline synthesis
		dubbed_wav_path = job_dir / "dubbed.wav"
		synthesize_timeline(translated_segments, dubbed_wav_path, lang)

		# Step 6: Merge translated audio + video
		output_video_path = job_dir / "dubbed.mp4"
		merge_video_and_audio(
			video_input=str(upload_path),
			audio_input=str(dubbed_wav_path),
			output_path=str(output_video_path)
		)

		return JSONResponse({
			"jobId": job_id,
			"originalVideoUrl": f"/data/uploads/{upload_path.name}",
			"dubbedVideoUrl": f"/data/outputs/{job_id}/dubbed.mp4",
			"transcript": [
				{"start": s["start"], "end": s["end"], "text": s["text"]}
				for s in segments
			]
		})
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))