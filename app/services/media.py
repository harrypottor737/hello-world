import os
import subprocess
from pathlib import Path
import imageio_ffmpeg


def ensure_directory(path: Path) -> None:
	Path(path).mkdir(parents=True, exist_ok=True)


def run_command(command: list) -> None:
	process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if process.returncode != 0:
		raise RuntimeError(process.stderr.decode("utf-8", errors="ignore"))


def _ffmpeg_bin() -> str:
	return imageio_ffmpeg.get_ffmpeg_exe()


def extract_audio_for_asr(video_input: str, audio_output_wav: str) -> None:
	# 16k mono wav for ASR stability
	cmd = [
		_ffmpeg_bin(), "-y", "-i", video_input,
		"-ac", "1", "-ar", "16000",
		"-vn",
		audio_output_wav
	]
	run_command(cmd)


def merge_video_and_audio(video_input: str, audio_input: str, output_path: str) -> None:
	# Keep video codec, replace audio with dubbed, stop at shortest
	cmd = [
		_ffmpeg_bin(), "-y",
		"-i", video_input,
		"-i", audio_input,
		"-map", "0:v:0",
		"-map", "1:a:0",
		"-c:v", "copy",
		"-shortest",
		output_path
	]
	run_command(cmd)