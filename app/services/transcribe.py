import os
from typing import List, Dict, Any

from openai import OpenAI


_client = None

def _get_client() -> OpenAI:
	global _client
	if _client is None:
		_api_key = os.getenv("OPENAI_API_KEY")
		if not _api_key:
			raise RuntimeError("OPENAI_API_KEY is not set")
		_client = OpenAI(api_key=_api_key)
	return _client


def transcribe_audio(audio_wav_path: str) -> List[Dict[str, Any]]:
	client = _get_client()
	with open(audio_wav_path, "rb") as f:
		resp = client.audio.transcriptions.create(
			model="whisper-1",
			file=f,
			temperature=0,
			response_format="verbose_json"
		)
	# Map segments if available; fall back to whole text
	segments: List[Dict[str, Any]] = []
	if hasattr(resp, "segments") and resp.segments:
		for seg in resp.segments:
			segments.append({
				"start": float(seg.get("start", 0.0)),
				"end": float(seg.get("end", 0.0)),
				"text": seg.get("text", "").strip(),
			})
	else:
		segments = [{"start": 0.0, "end": 0.0, "text": resp.text}]
	return segments