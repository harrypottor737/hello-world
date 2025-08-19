import os
import tempfile
import uuid
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import whisper
from deep_translator import GoogleTranslator
from gtts import gTTS
import moviepy.editor as mp
from pydub import AudioSegment
import subprocess
import logging
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create necessary directories
UPLOAD_DIR = "/workspace/uploads"
OUTPUT_DIR = "/workspace/outputs"
TEMP_DIR = "/workspace/temp"

for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)

# Initialize Whisper model
whisper_model = whisper.load_model("base")

# GoogleTranslator will be initialized per request

# Supported Indian languages mapping
INDIAN_LANGUAGES = {
    'hindi': 'hi',
    'kannada': 'kn',
    'tamil': 'ta',
    'telugu': 'te',
    'malayalam': 'ml',
    'marathi': 'mr',
    'gujarati': 'gu',
    'punjabi': 'pa',
    'bengali': 'bn',
    'odia': 'or',
    'assamese': 'as',
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
            logger.info("Starting transcription...")
            result = whisper_model.transcribe(audio_path)
            
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
            if target_language not in INDIAN_LANGUAGES:
                raise ValueError(f"Unsupported language: {target_language}")
            
            lang_code = INDIAN_LANGUAGES[target_language]
            logger.info(f"Translating to {target_language} ({lang_code})")
            
            translator = GoogleTranslator(source='auto', target=lang_code)
            translated = translator.translate(text)
            return translated
            
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            raise
    
    def generate_speech(self, text, language, output_path):
        """Generate speech from text using gTTS"""
        try:
            lang_code = INDIAN_LANGUAGES[language]
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(output_path)
            logger.info(f"Speech generated: {output_path}")
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            raise
    
    def sync_audio_video(self, video_path, audio_path, output_path):
        """Sync translated audio with video"""
        try:
            logger.info("Starting audio-video synchronization...")
            
            # Load video and audio
            video = mp.VideoFileClip(video_path)
            audio = mp.AudioFileClip(audio_path)
            
            # Adjust audio duration to match video
            if audio.duration != video.duration:
                # Speed up or slow down audio to match video duration
                speed_factor = audio.duration / video.duration
                audio = audio.fx(mp.afx.speedx, speed_factor)
            
            # Combine video with new audio
            final_video = video.set_audio(audio)
            
            # Write the result
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=f"{output_path}_temp_audio.m4a",
                remove_temp=True
            )
            
            # Clean up
            video.close()
            audio.close()
            final_video.close()
            
            logger.info(f"Video with dubbed audio saved: {output_path}")
            
        except Exception as e:
            logger.error(f"Error syncing audio-video: {e}")
            raise
    
    def process_video(self, video_path, target_language):
        """Main processing pipeline"""
        try:
            self.session_id = str(uuid.uuid4())
            
            # Step 1: Extract audio
            audio_path = self.extract_audio(video_path)
            
            # Step 2: Transcribe audio
            transcription = self.transcribe_audio(audio_path)
            
            # Step 3: Translate text
            translated_text = self.translate_text(
                transcription['full_text'], 
                target_language
            )
            
            # Step 4: Generate speech
            dubbed_audio_path = os.path.join(
                TEMP_DIR, 
                f"{self.session_id}_dubbed_audio.mp3"
            )
            self.generate_speech(translated_text, target_language, dubbed_audio_path)
            self.temp_files.append(dubbed_audio_path)
            
            # Step 5: Sync with video
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
    app.run(debug=True, host='0.0.0.0', port=5000)