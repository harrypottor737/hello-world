import os
import tempfile
import subprocess
from typing import List, Tuple

from deep_translator import GoogleTranslator
from app.utils.media import convert_audio_to_wav

# Transcription via Vosk
from vosk import Model, KaldiRecognizer
import json
import wave

_VOSK_MODEL = None


def _ensure_vosk_model() -> str:
	global _VOSK_MODEL
	model_dir = os.getenv("VOSK_MODEL_DIR", "/workspace/data/vosk-model-small-multilingual")
	if _VOSK_MODEL is None:
		if not os.path.isdir(model_dir):
			# Download minimal multilingual model (approx 50-100MB). We use a static URL mirror.
			# If the environment blocks outbound downloads, instruct user to place the model.
			url = os.getenv("VOSK_MODEL_URL", "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip")
			# Note: There isn't an official small multilingual; user can swap with Hindi model e.g. vosk-model-small-hi-0.22
			# We'll fetch the specified URL; if it fails, we raise with guidance.
			os.makedirs(os.path.dirname(model_dir), exist_ok=True)
			zip_path = model_dir + ".zip"
			try:
				subprocess.run(["bash", "-lc", f"curl -L --fail -o '{zip_path}' '{url}'"], check=True)
				subprocess.run(["bash", "-lc", f"unzip -q '{zip_path}' -d '/workspace/data'"], check=True)
				# Find extracted folder
				for name in os.listdir("/workspace/data"):
					if name.startswith("vosk-model") and os.path.isdir(os.path.join("/workspace/data", name)):
						os.rename(os.path.join("/workspace/data", name), model_dir)
						break
			finally:
				if os.path.exists(zip_path):
					try:
						os.remove(zip_path)
					except Exception:
						pass
		_VOSK_MODEL = model_dir
	return model_dir


def transcribe_audio_to_text(audio_wav_path: str) -> Tuple[str, List[dict]]:
	model_path = _ensure_vosk_model()
	model = Model(model_path)
	with wave.open(audio_wav_path, "rb") as wf:
		rec = KaldiRecognizer(model, wf.getframerate())
		rec.SetWords(True)
		full_text_parts: List[str] = []
		segments: List[dict] = []
		while True:
			data = wf.readframes(4000)
			if len(data) == 0:
				break
			if rec.AcceptWaveform(data):
				res = json.loads(rec.Result())
				if "text" in res and res["text"]:
					full_text_parts.append(res["text"]) 
					if "result" in res:
						for w in res["result"]:
							segments.append({
								"start": w.get("start", 0.0),
								"end": w.get("end", 0.0),
								"text": w.get("word", ""),
							})
		# Final partial
		final_res = json.loads(rec.FinalResult())
		if "text" in final_res and final_res["text"]:
			full_text_parts.append(final_res["text"]) 
			if "result" in final_res:
				for w in final_res["result"]:
					segments.append({
						"start": w.get("start", 0.0),
						"end": w.get("end", 0.0),
						"text": w.get("word", ""),
					})
	full_text = " ".join(full_text_parts).strip()
	return full_text, segments


def translate_text(text: str, target_lang: str) -> str:
	if not text:
		return ""
	# Chunk text to avoid limits
	chunks: List[str] = []
	current: List[str] = []
	current_len = 0
	for part in text.split(" "):
		l = len(part) + 1
		if current_len + l > 4000:
			chunks.append(" ".join(current))
			current = [part]
			current_len = l
		else:
			current.append(part)
			current_len += l
	if current:
		chunks.append(" ".join(current))
	translated_chunks = [GoogleTranslator(source="auto", target=target_lang).translate(c) for c in chunks]
	return " ".join(translated_chunks)


def _tts_with_gtts(text: str, lang: str, out_wav_path: str) -> None:
	from gtts import gTTS
	with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
		tmp_mp3_path = tmp_mp3.name
	tts = gTTS(text=text, lang=lang)
	tts.save(tmp_mp3_path)
	convert_audio_to_wav(tmp_mp3_path, out_wav_path, sample_rate=16000)
	try:
		os.remove(tmp_mp3_path)
	except Exception:
		pass


def _tts_with_espeak(text: str, lang: str, out_wav_path: str) -> None:
	voice = lang
	cmd = [
		"espeak-ng",
		"-v", voice,
		"-s", "185",
		"-p", "50",
		"-a", "200",
		"-w", out_wav_path,
		text,
	]
	subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


def _tts_with_coqui(text: str, lang: str, out_wav_path: str, voice_clone_reference: str | None) -> bool:
	if os.getenv("TTS_PROVIDER", "").lower() != "coqui":
		return False
	try:
		from TTS.api import TTS  # type: ignore
	except Exception:
		return False
	model_id = os.getenv("TTS_MODEL_ID", "tts_models/multilingual/multi-dataset/xtts_v2")
	try:
		tts = TTS(model_id)
		tts.tts_to_file(
			text=text,
			file_path=out_wav_path,
			language=lang,
			speaker_wav=voice_clone_reference,
		)
		return True
	except Exception:
		return False


def synthesize_tts_audio(text: str, lang: str, out_wav_path: str, voice_clone_reference: str | None = None) -> None:
	if not text:
		cmd = [
			"ffmpeg", "-y",
			"-f", "lavfi",
			"-i", "anullsrc=r=16000:cl=mono",
			"-t", "0.1",
			out_wav_path,
		]
		subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
		return
	if _tts_with_coqui(text, lang, out_wav_path, voice_clone_reference):
		return
	try:
		_tts_with_gtts(text, lang, out_wav_path)
		return
	except Exception:
		pass
	_tts_with_espeak(text, lang, out_wav_path)