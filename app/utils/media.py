import subprocess


def _run_cmd(cmd: list[str]) -> None:
	proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if proc.returncode != 0:
		raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDERR: {proc.stderr.decode(errors='ignore')}")


def extract_audio_track(video_path: str, out_audio_wav: str) -> None:
	# Extract mono 16k WAV for ASR quality
	cmd = [
		"ffmpeg", "-y",
		"-i", video_path,
		"-q:a", "0",
		"-map", "a",
		"-ac", "1",
		"-ar", "16000",
		out_audio_wav,
	]
	_run_cmd(cmd)


def get_media_duration_seconds(media_path: str) -> float:
	cmd = [
		"ffprobe", "-v", "quiet",
		"-show_entries", "format=duration",
		"-of", "default=noprint_wrappers=1:nokey=1",
		media_path,
	]
	proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if proc.returncode != 0:
		return 0.0
	try:
		return float(proc.stdout.decode().strip())
	except Exception:
		return 0.0


def _compose_atempo_chain(target_tempo: float) -> list[str]:
	# ffmpeg atempo supports 0.5..2.0 per filter; chain filters to approximate
	if target_tempo <= 0:
		target_tempo = 1.0
	chain: list[float] = []
	remaining = target_tempo
	while remaining > 2.0:
		chain.append(2.0)
		remaining /= 2.0
	while remaining < 0.5:
		chain.append(0.5)
		remaining /= 0.5
	chain.append(remaining)
	filters = [f"atempo={mult:.5f}" for mult in chain]
	return ["-filter:a", ",".join(filters)]


def time_stretch_audio(input_wav: str, output_wav: str, tempo: float) -> None:
	if abs(tempo - 1.0) < 1e-2:
		cmd = ["ffmpeg", "-y", "-i", input_wav, output_wav]
		_run_cmd(cmd)
		return
	filter_args = _compose_atempo_chain(tempo)
	cmd = ["ffmpeg", "-y", "-i", input_wav] + filter_args + [output_wav]
	_run_cmd(cmd)


def merge_video_with_audio(video_path: str, audio_wav_path: str, out_video_path: str) -> None:
	cmd = [
		"ffmpeg", "-y",
		"-i", video_path,
		"-i", audio_wav_path,
		"-map", "0:v:0",
		"-map", "1:a:0",
		"-c:v", "copy",
		"-c:a", "aac",
		"-b:a", "192k",
		"-shortest",
		"-movflags", "+faststart",
		out_video_path,
	]
	_run_cmd(cmd)


def convert_audio_to_wav(input_audio_path: str, out_wav_path: str, sample_rate: int = 16000) -> None:
	cmd = [
		"ffmpeg", "-y",
		"-i", input_audio_path,
		"-ac", "1",
		"-ar", str(sample_rate),
		out_wav_path,
	]
	_run_cmd(cmd)