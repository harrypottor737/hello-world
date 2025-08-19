# Indic Video Dubbing Tool

## Quickstart

1. Ensure system deps are installed (already scripted): ffmpeg, espeak-ng
2. Create venv and install deps:

```bash
python3 -m venv /workspace/venv
. /workspace/venv/bin/activate
pip install -r /workspace/requirements.txt
```

3. Run the server:

```bash
. /workspace/venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

4. Open http://localhost:8000 and upload a video, choose target language (e.g. hi, kn).

## Notes
- Transcription uses Vosk; at first run it downloads a model ZIP to `/workspace/data`.
- Translation uses Google Translator (deep-translator). For offline translation, swap in your provider.
- TTS defaults to gTTS; set `TTS_PROVIDER=coqui` to enable Coqui XTTS v2 (install `TTS` and set `TTS_MODEL_ID`).
- Audio is tempo-matched to the original using FFmpeg `atempo` and muxed back.
