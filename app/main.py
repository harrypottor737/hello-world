import os
import uuid
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.utils.media import (
	extract_audio_track,
	get_media_duration_seconds,
	time_stretch_audio,
	merge_video_with_audio,
	convert_audio_to_wav,
)
from app.utils.nlp import (
	transcribe_audio_to_text,
	translate_text,
	synthesize_tts_audio,
)

BASE_DIR = Path("/workspace")
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
OUTPUTS_DIR = DATA_DIR / "outputs"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
STATIC_DIR = BASE_DIR / "app" / "static"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Indic Video Dubbing Tool")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

SUPPORTED_LANGUAGES: Dict[str, str] = {
	"hi": "Hindi",
	"kn": "Kannada",
	"ta": "Tamil",
	"te": "Telugu",
	"mr": "Marathi",
	"bn": "Bengali",
	"ml": "Malayalam",
	"gu": "Gujarati",
	"pa": "Punjabi",
	"ur": "Urdu",
}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
	return templates.TemplateResponse(
		"index.html",
		{
			"request": request,
			"languages": SUPPORTED_LANGUAGES,
		},
	)


@app.post("/process", response_class=HTMLResponse)
async def process(
	request: Request,
	video: UploadFile = File(...),
	target_lang: str = Form(...),
	align_segments: Optional[bool] = Form(False),
):
	if target_lang not in SUPPORTED_LANGUAGES:
		raise HTTPException(status_code=400, detail="Unsupported target language")

	job_id = str(uuid.uuid4())
	job_upload_dir = UPLOADS_DIR / job_id
	job_output_dir = OUTPUTS_DIR / job_id
	job_upload_dir.mkdir(parents=True, exist_ok=True)
	job_output_dir.mkdir(parents=True, exist_ok=True)

	original_video_path = job_upload_dir / video.filename
	with open(original_video_path, "wb") as f:
		f.write(await video.read())

	# Step 2: Extract audio
	original_audio_wav = job_upload_dir / "audio.wav"
	extract_audio_track(str(original_video_path), str(original_audio_wav))

	# Step 3: Transcribe audio -> text
	transcript_text, segments = transcribe_audio_to_text(str(original_audio_wav))

	# Step 4: Translate to target language
	translated_text = translate_text(transcript_text, target_lang)

	# Step 5: Text-to-Speech (voice cloning optional via env)
	tts_wav_path = job_output_dir / "tts.wav"
	synthesize_tts_audio(translated_text, target_lang, str(tts_wav_path), voice_clone_reference=str(original_audio_wav))

	# Optional alignment: tempo-match TTS to the original audio duration
	original_duration = get_media_duration_seconds(str(original_audio_wav))
	tts_duration = get_media_duration_seconds(str(tts_wav_path))

	if tts_duration > 0 and original_duration > 0:
		tempo = original_duration / tts_duration
	else:
		tempo = 1.0

	aligned_tts_wav_path = job_output_dir / "tts_aligned.wav"
	time_stretch_audio(str(tts_wav_path), str(aligned_tts_wav_path), tempo)

	# Step 6: Merge Translated Audio + Video
	output_video_path = job_output_dir / "dubbed.mp4"
	merge_video_with_audio(
		str(original_video_path), str(aligned_tts_wav_path), str(output_video_path)
	)

	# Step 7: Render result page showing both original and dubbed videos
	return templates.TemplateResponse(
		"result.html",
		{
			"request": request,
			"job_id": job_id,
			"original_video_url": f"/uploads/{job_id}/{video.filename}",
			"dubbed_video_url": f"/outputs/{job_id}/dubbed.mp4",
			"target_lang_label": SUPPORTED_LANGUAGES[target_lang],
		},
	)