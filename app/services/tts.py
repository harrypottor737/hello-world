import asyncio
from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path

import edge_tts
from pydub import AudioSegment


@dataclass
class LanguageSpec:
	google_code: str
	locale: str
	voice: str


async def _synthesize_to_file_async(text: str, voice: str, outfile: Path) -> None:
	communicate = edge_tts.Communicate(text=text, voice=voice)
	await communicate.save(str(outfile))


def _synthesize_segment_mp3(text: str, voice: str, tmp_dir: Path, idx: int) -> Path:
	mp3_path = tmp_dir / f"seg_{idx:05d}.mp3"
	asyncio.get_event_loop().run_until_complete(_synthesize_to_file_async(text, voice, mp3_path))
	return mp3_path


def synthesize_timeline(segments: List[Dict], out_wav_path: Path, lang: LanguageSpec) -> None:
	tmp_dir = Path(out_wav_path).parent / "tts_tmp"
	tmp_dir.mkdir(parents=True, exist_ok=True)

	# Determine total duration from segments
	last_end = 0.0
	for s in segments:
		if s["end"] > last_end:
			last_end = s["end"]
	base = AudioSegment.silent(duration=int((last_end + 0.5) * 1000))

	cursor = base
	# Overlay per segment
	timeline = base
	for idx, s in enumerate(segments):
		text = s.get("text", "").strip()
		if not text:
			continue
		mp3_path = _synthesize_segment_mp3(text, lang.voice, tmp_dir, idx)
		seg_audio = AudioSegment.from_file(mp3_path, format="mp3")
		start_ms = int(s["start"] * 1000)
		timeline = timeline.overlay(seg_audio, position=start_ms)

	# Export as wav 48k mono for better compatibility
	timeline.set_frame_rate(48000).set_channels(1).export(out_wav_path, format="wav")