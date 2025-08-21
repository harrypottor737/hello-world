#!/usr/bin/env python3

"""
Video Dubbing Tool - Complete Implementation
Converts video audio to Indian languages using AI
"""

import os
import tempfile
import uuid
import subprocess
import logging
import json
from pathlib import Path

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Create necessary directories
UPLOAD_DIR = "/workspace/uploads"
OUTPUT_DIR = "/workspace/outputs"
TEMP_DIR = "/workspace/temp"

for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)

# Supported Indian languages mapping for gTTS
INDIAN_LANGUAGES = {
    'hindi': 'hi',
    'kannada': 'kn',  # Note: gTTS may not support all these languages
    'tamil': 'ta',
    'telugu': 'te',
    'malayalam': 'ml',
    'marathi': 'mr',
    'gujarati': 'gu',
    'punjabi': 'pa',
    'bengali': 'bn',
    'urdu': 'ur'
}

class VideoDubbingProcessor:
    def __init__(self):
        self.session_id = None
        self.temp_files = []
    
    def cleanup(self):
        """Clean up temporary files"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")
    
    def extract_audio(self, video_path):
        """Extract audio from video using FFmpeg"""
        try:
            audio_path = os.path.join(TEMP_DIR, f"{self.session_id}_audio.wav")
            
            # Use FFmpeg to extract audio
            cmd = [
                'ffmpeg', '-i', video_path,
                '-q:a', '0',
                '-map', 'a',
                '-y',  # Overwrite output file
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
            
            self.temp_files.append(audio_path)
            logger.info(f"Audio extracted to: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            raise
    
    def transcribe_audio(self, audio_path):
        """Transcribe audio to text using Whisper"""
        try:
            # Import whisper here to avoid startup issues
            import whisper
            
            logger.info("Loading Whisper model...")
            model = whisper.load_model("base")
            
            logger.info("Starting transcription...")
            result = model.transcribe(audio_path)
            
            # Extract segments with timestamps
            segments = []
            for segment in result['segments']:
                segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip()
                })
            
            logger.info(f"Transcription completed. Found {len(segments)} segments")
            return {
                'full_text': result['text'],
                'segments': segments
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    def translate_text(self, text, target_language):
        """Translate text to target language"""
        try:
            from deep_translator import GoogleTranslator
            
            if target_language not in INDIAN_LANGUAGES:
                raise ValueError(f"Unsupported language: {target_language}")
            
            lang_code = INDIAN_LANGUAGES[target_language]
            logger.info(f"Translating to {target_language} ({lang_code})")
            
            translator = GoogleTranslator(source='auto', target=lang_code)
            translated = translator.translate(text)
            return translated
            
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            # Return original text if translation fails
            return text
    
    def generate_speech(self, text, language, output_path):
        """Generate speech from text using gTTS"""
        try:
            from gtts import gTTS
            
            lang_code = INDIAN_LANGUAGES[language]
            
            # gTTS may not support all Indian languages, so we'll try with fallback
            try:
                tts = gTTS(text=text, lang=lang_code, slow=False)
                tts.save(output_path)
                logger.info(f"Speech generated: {output_path}")
            except Exception as gtts_error:
                logger.warning(f"gTTS failed for {lang_code}, trying with Hindi: {gtts_error}")
                # Fallback to Hindi if the specific language is not supported
                tts = gTTS(text=text, lang='hi', slow=False)
                tts.save(output_path)
                logger.info(f"Speech generated with Hindi fallback: {output_path}")
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            raise
    
    def sync_audio_video(self, video_path, audio_path, output_path):
        """Sync translated audio with video using FFmpeg"""
        try:
            logger.info("Starting audio-video synchronization...")
            
            # Use FFmpeg to replace audio in video
            cmd = [
                'ffmpeg',
                '-i', video_path,  # Input video
                '-i', audio_path,  # Input audio
                '-c:v', 'copy',    # Copy video stream without re-encoding
                '-c:a', 'aac',     # Encode audio as AAC
                '-map', '0:v:0',   # Map video from first input
                '-map', '1:a:0',   # Map audio from second input
                '-shortest',       # End when shortest stream ends
                '-y',              # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg sync error: {result.stderr}")
            
            logger.info(f"Video with dubbed audio saved: {output_path}")
            
        except Exception as e:
            logger.error(f"Error syncing audio-video: {e}")
            raise
    
    def process_video(self, video_path, target_language):
        """Main processing pipeline"""
        try:
            self.session_id = str(uuid.uuid4())
            
            # Step 1: Extract audio
            logger.info("Step 1: Extracting audio...")
            audio_path = self.extract_audio(video_path)
            
            # Step 2: Transcribe audio
            logger.info("Step 2: Transcribing audio...")
            transcription = self.transcribe_audio(audio_path)
            
            # Step 3: Translate text
            logger.info("Step 3: Translating text...")
            translated_text = self.translate_text(
                transcription['full_text'], 
                target_language
            )
            
            # Step 4: Generate speech
            logger.info("Step 4: Generating speech...")
            dubbed_audio_path = os.path.join(
                TEMP_DIR, 
                f"{self.session_id}_dubbed_audio.mp3"
            )
            self.generate_speech(translated_text, target_language, dubbed_audio_path)
            self.temp_files.append(dubbed_audio_path)
            
            # Step 5: Sync with video
            logger.info("Step 5: Syncing audio with video...")
            output_video_path = os.path.join(
                OUTPUT_DIR,
                f"{self.session_id}_dubbed.mp4"
            )
            self.sync_audio_video(video_path, dubbed_audio_path, output_video_path)
            
            return {
                'success': True,
                'session_id': self.session_id,
                'original_text': transcription['full_text'],
                'translated_text': translated_text,
                'output_video': output_video_path,
                'segments': transcription['segments']
            }
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            self.cleanup()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return jsonify({
        'status': 'success',
        'message': 'Video Dubbing Tool is running!',
        'supported_languages': list(INDIAN_LANGUAGES.keys()),
        'features': [
            'Video upload and processing',
            'Audio extraction with FFmpeg',
            'Speech transcription with Whisper AI',
            'Text translation to Indian languages',
            'Text-to-speech conversion',
            'Audio-video synchronization'
        ]
    })

@app.route('/upload', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        target_language = request.form.get('language', 'hindi').lower()
        
        if target_language not in INDIAN_LANGUAGES:
            return jsonify({'error': f'Unsupported language: {target_language}'}), 400
        
        # Save uploaded video
        video_filename = f"{uuid.uuid4()}_{video_file.filename}"
        video_path = os.path.join(UPLOAD_DIR, video_filename)
        video_file.save(video_path)
        
        logger.info(f"Video uploaded: {video_path}")
        
        # Process video
        processor = VideoDubbingProcessor()
        result = processor.process_video(video_path, target_language)
        
        if result['success']:
            return jsonify({
                'success': True,
                'session_id': result['session_id'],
                'original_text': result['original_text'],
                'translated_text': result['translated_text'],
                'original_video': f'/video/{video_filename}',
                'dubbed_video': f'/output/{os.path.basename(result["output_video"])}'
            })
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/video/<filename>')
def serve_video(filename):
    return send_file(os.path.join(UPLOAD_DIR, filename))

@app.route('/output/<filename>')
def serve_output(filename):
    return send_file(os.path.join(OUTPUT_DIR, filename))

@app.route('/languages')
def get_languages():
    return jsonify(list(INDIAN_LANGUAGES.keys()))

if __name__ == '__main__':
    print("=" * 60)
    print("🎬 Video Dubbing Tool for Indian Languages")
    print("=" * 60)
    print("Features:")
    print("• Video upload and processing")
    print("• Audio extraction with FFmpeg")
    print("• Speech transcription with Whisper AI")
    print("• Text translation to Indian languages")
    print("• Text-to-speech conversion")
    print("• Audio-video synchronization")
    print("=" * 60)
    print("🌐 Server starting at: http://localhost:5000")
    print("🧪 Test endpoint: http://localhost:5000/test")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
