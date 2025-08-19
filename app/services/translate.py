from dataclasses import dataclass
from typing import List, Dict, Any
from deep_translator import GoogleTranslator


_LANGUAGE_MAP = {
	"hi": {"google": "hi", "locale": "hi-IN", "voice": "hi-IN-MadhurNeural"},
	"hindi": {"google": "hi", "locale": "hi-IN", "voice": "hi-IN-MadhurNeural"},
	"kn": {"google": "kn", "locale": "kn-IN", "voice": "kn-IN-SapnaNeural"},
	"kannada": {"google": "kn", "locale": "kn-IN", "voice": "kn-IN-SapnaNeural"},
	"ta": {"google": "ta", "locale": "ta-IN", "voice": "ta-IN-PallaviNeural"},
	"tamil": {"google": "ta", "locale": "ta-IN", "voice": "ta-IN-PallaviNeural"},
	"te": {"google": "te", "locale": "te-IN", "voice": "te-IN-ShrutiNeural"},
	"telugu": {"google": "te", "locale": "te-IN", "voice": "te-IN-ShrutiNeural"},
	"ml": {"google": "ml", "locale": "ml-IN", "voice": "ml-IN-MidhunNeural"},
	"malayalam": {"google": "ml", "locale": "ml-IN", "voice": "ml-IN-MidhunNeural"},
	"bn": {"google": "bn", "locale": "bn-IN", "voice": "bn-IN-TanishaaNeural"},
	"bengali": {"google": "bn", "locale": "bn-IN", "voice": "bn-IN-TanishaaNeural"},
	"mr": {"google": "mr", "locale": "mr-IN", "voice": "mr-IN-AarohiNeural"},
	"marathi": {"google": "mr", "locale": "mr-IN", "voice": "mr-IN-AarohiNeural"},
	"gu": {"google": "gu", "locale": "gu-IN", "voice": "gu-IN-NiranjanNeural"},
	"gujarati": {"google": "gu", "locale": "gu-IN", "voice": "gu-IN-NiranjanNeural"},
	"pa": {"google": "pa", "locale": "pa-IN", "voice": "pa-IN-AvleenNeural"},
	"punjabi": {"google": "pa", "locale": "pa-IN", "voice": "pa-IN-AvleenNeural"},
	"or": {"google": "or", "locale": "or-IN", "voice": "or-IN-LalitaNeural"},
	"odia": {"google": "or", "locale": "or-IN", "voice": "or-IN-LalitaNeural"},
	"as": {"google": "as", "locale": "as-IN", "voice": "as-IN-AnoopaNeural"},
	"assamese": {"google": "as", "locale": "as-IN", "voice": "as-IN-AnoopaNeural"},
	"ur": {"google": "ur", "locale": "ur-IN", "voice": "ur-IN-SalmanNeural"},
	"urdu": {"google": "ur", "locale": "ur-IN", "voice": "ur-IN-SalmanNeural"},
}


@dataclass
class LanguageSpec:
	google_code: str
	locale: str
	voice: str


def resolve_language(user_input: str) -> LanguageSpec:
	key = (user_input or "").strip().lower()
	key = key.replace("_", "-")
	if key in _LANGUAGE_MAP:
		m = _LANGUAGE_MAP[key]
		return LanguageSpec(m["google"], m["locale"], m["voice"])
	# try normalize like kn-in or hi-in -> kn, hi
	prefix = key.split("-")[0]
	if prefix in _LANGUAGE_MAP:
		m = _LANGUAGE_MAP[prefix]
		return LanguageSpec(m["google"], m["locale"], m["voice"])
	raise ValueError(f"Unsupported language: {user_input}")


def translate_segments(segments: List[dict], target_google_code: str) -> List[dict]:
	translator = GoogleTranslator(source="auto", target=target_google_code)
	translated: List[dict] = []
	for s in segments:
		text = s.get("text", "")
		if not text:
			translated_text = ""
		else:
			translated_text = translator.translate(text)
		translated.append({
			"start": s["start"],
			"end": s["end"],
			"text": translated_text
		})
	return translated