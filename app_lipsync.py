#!/usr/bin/env python3

"""
Video Dubbing Tool with Enhanced Lip Synchronization
Improved version with segment-based timing and audio stretching for better lip sync
"""

import os
import tempfile
import uuid
import subprocess
import logging
import json
import numpy as np
from pathlib import Path

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Create necessary directories
UPLOAD_DIR = "/app/uploads"
OUTPUT_DIR = "/app/outputs"
TEMP_DIR = "/app/temp"

for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)

# Supported Indian languages mapping for gTTS
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
    'urdu': 'ur'
}

class LipSyncVideoDubbingProcessor:
    def __init__(self):
        self.session_id = None
        self.temp_files = []
        self.original_segments = []
        self.translated_segments = []
    
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
            
            # Use FFmpeg to extract audio with specific sample rate for better processing
            cmd = [
                'ffmpeg', '-i', video_path,
                '-ar', '16000',  # 16kHz sample rate for Whisper
                '-ac', '1',      # Mono channel
                '-q:a', '0',
                '-y',            # Overwrite output file
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
    
    def transcribe_audio_with_timing(self, audio_path):
        """Transcribe audio with precise word-level timing using Whisper"""
        try:
            import whisper
            
            logger.info("Loading Whisper model for detailed transcription...")
            model = whisper.load_model("base")
            
            logger.info("Starting detailed transcription with word timestamps...")
            result = model.transcribe(
                audio_path,
                word_timestamps=True,  # Enable word-level timestamps
                verbose=True
            )
            
            # Extract detailed segments with word-level timing
            detailed_segments = []
            for segment in result['segments']:
                segment_data = {
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip(),
                    'words': []
                }
                
                # Extract word-level timing if available
                if 'words' in segment:
                    for word in segment['words']:
                        segment_data['words'].append({
                            'word': word.get('word', '').strip(),
                            'start': word.get('start', segment['start']),
                            'end': word.get('end', segment['end'])
                        })
                
                detailed_segments.append(segment_data)
            
            self.original_segments = detailed_segments
            
            logger.info(f"Detailed transcription completed. Found {len(detailed_segments)} segments")
            return {
                'full_text': result['text'],
                'segments': detailed_segments
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    def translate_segments(self, segments, target_language):
        """Translate segments while preserving timing structure"""
        try:
            from deep_translator import GoogleTranslator
            
            if target_language not in INDIAN_LANGUAGES:
                raise ValueError(f"Unsupported language: {target_language}")
            
            lang_code = INDIAN_LANGUAGES[target_language]
            logger.info(f"Translating segments to {target_language} ({lang_code})")
            
            translator = GoogleTranslator(source='auto', target=lang_code)
            translated_segments = []
            
            for segment in segments:
                try:
                    translated_text = translator.translate(segment['text'])
                    translated_segment = {
                        'start': segment['start'],
                        'end': segment['end'],
                        'original_text': segment['text'],
                        'translated_text': translated_text,
                        'duration': segment['end'] - segment['start'],
                        'words': segment.get('words', [])
                    }
                    translated_segments.append(translated_segment)
                    
                except Exception as trans_error:
                    logger.warning(f"Translation failed for segment: {trans_error}")
                    # Keep original if translation fails
                    translated_segment = {
                        'start': segment['start'],
                        'end': segment['end'],
                        'original_text': segment['text'],
                        'translated_text': segment['text'],
                        'duration': segment['end'] - segment['start'],
                        'words': segment.get('words', [])
                    }
                    translated_segments.append(translated_segment)
            
            self.translated_segments = translated_segments
            return translated_segments
            
        except Exception as e:
            logger.error(f"Error translating segments: {e}")
            raise
    
    def generate_timed_speech_segments(self, segments, language, temp_dir):
        """Generate speech for each segment and adjust timing"""
        try:
            from gtts import gTTS
            import librosa
            import soundfile as sf
            from scipy import signal
            
            lang_code = INDIAN_LANGUAGES[language]
            segment_audio_files = []
            
            logger.info(f"Generating speech for {len(segments)} segments...")
            
            for i, segment in enumerate(segments):
                segment_audio_path = os.path.join(temp_dir, f"segment_{i:03d}.wav")
                
                try:
                    # Generate TTS for this segment
                    tts = gTTS(text=segment['translated_text'], lang=lang_code, slow=False)
                    temp_mp3_path = os.path.join(temp_dir, f"segment_{i:03d}.mp3")
                    tts.save(temp_mp3_path)
                    self.temp_files.append(temp_mp3_path)
                    
                    # Convert MP3 to WAV and load audio
                    subprocess.run([
                        'ffmpeg', '-i', temp_mp3_path, 
                        '-ar', '16000', '-ac', '1',
                        '-y', segment_audio_path
                    ], capture_output=True)
                    self.temp_files.append(segment_audio_path)
                    
                    # Load the generated audio
                    audio, sr = librosa.load(segment_audio_path, sr=16000)
                    original_duration = len(audio) / sr
                    target_duration = segment['duration']
                    
                    # Time-stretch audio to match original timing
                    if target_duration > 0 and original_duration > 0:
                        stretch_ratio = original_duration / target_duration
                        
                        # Apply time stretching if the difference is significant
                        if abs(stretch_ratio - 1.0) > 0.1:  # More than 10% difference
                            logger.info(f"Segment {i}: Stretching audio from {original_duration:.2f}s to {target_duration:.2f}s (ratio: {stretch_ratio:.2f})")
                            
                            # Use librosa for time stretching
                            stretched_audio = librosa.effects.time_stretch(audio, rate=stretch_ratio)
                            
                            # Ensure the audio is exactly the right length
                            target_samples = int(target_duration * sr)
                            if len(stretched_audio) > target_samples:
                                stretched_audio = stretched_audio[:target_samples]
                            elif len(stretched_audio) < target_samples:
                                # Pad with silence
                                padding = target_samples - len(stretched_audio)
                                stretched_audio = np.pad(stretched_audio, (0, padding), mode='constant')
                            
                            # Save the time-stretched audio
                            sf.write(segment_audio_path, stretched_audio, sr)
                    
                    segment_info = {
                        'file_path': segment_audio_path,
                        'start': segment['start'],
                        'end': segment['end'],
                        'duration': segment['duration'],
                        'original_text': segment['original_text'],
                        'translated_text': segment['translated_text']
                    }
                    segment_audio_files.append(segment_info)
                    
                except Exception as segment_error:
                    logger.warning(f"Failed to generate audio for segment {i}: {segment_error}")
                    # Create silence for failed segments
                    silence_duration = segment['duration']
                    silence_samples = int(silence_duration * 16000)
                    silence_audio = np.zeros(silence_samples)
                    sf.write(segment_audio_path, silence_audio, 16000)
                    self.temp_files.append(segment_audio_path)
                    
                    segment_info = {
                        'file_path': segment_audio_path,
                        'start': segment['start'],
                        'end': segment['end'],
                        'duration': segment['duration'],
                        'original_text': segment['original_text'],
                        'translated_text': '[Audio generation failed]'
                    }
                    segment_audio_files.append(segment_info)
            
            return segment_audio_files
            
        except Exception as e:
            logger.error(f"Error generating timed speech segments: {e}")
            raise
    
    def combine_audio_segments(self, segment_files, total_duration):
        """Combine individual audio segments into a single audio track"""
        try:
            import librosa
            import soundfile as sf
            
            logger.info("Combining audio segments...")
            
            # Create the full audio track
            sample_rate = 16000
            total_samples = int(total_duration * sample_rate)
            combined_audio = np.zeros(total_samples)
            
            for segment in segment_files:
                start_sample = int(segment['start'] * sample_rate)
                end_sample = int(segment['end'] * sample_rate)
                
                # Load segment audio
                segment_audio, _ = librosa.load(segment['file_path'], sr=sample_rate)
                
                # Ensure we don't exceed the bounds
                segment_length = min(len(segment_audio), end_sample - start_sample)
                if start_sample + segment_length <= len(combined_audio):
                    combined_audio[start_sample:start_sample + segment_length] = segment_audio[:segment_length]
            
            # Save combined audio
            combined_audio_path = os.path.join(TEMP_DIR, f"{self.session_id}_combined_dubbed.wav")
            sf.write(combined_audio_path, combined_audio, sample_rate)
            self.temp_files.append(combined_audio_path)
            
            logger.info(f"Combined audio saved: {combined_audio_path}")
            return combined_audio_path
            
        except Exception as e:
            logger.error(f"Error combining audio segments: {e}")
            raise
    
    def get_video_duration(self, video_path):
        """Get video duration using FFmpeg"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                info = json.loads(result.stdout)
                duration = float(info['format']['duration'])
                return duration
            else:
                raise Exception("Could not get video duration")
        except Exception as e:
            logger.error(f"Error getting video duration: {e}")
            return 60.0  # Default fallback
    
    def sync_audio_video_with_timing(self, video_path, audio_path, output_path):
        """Sync translated audio with video using precise timing"""
        try:
            logger.info("Starting precise audio-video synchronization...")
            
            # Use FFmpeg to replace audio with better sync options
            cmd = [
                'ffmpeg',
                '-i', video_path,     # Input video
                '-i', audio_path,     # Input audio
                '-c:v', 'copy',       # Copy video stream without re-encoding
                '-c:a', 'aac',        # Encode audio as AAC
                '-b:a', '128k',       # Audio bitrate
                '-ar', '44100',       # Output sample rate
                '-ac', '2',           # Stereo output
                '-map', '0:v:0',      # Map video from first input
                '-map', '1:a:0',      # Map audio from second input
                '-shortest',          # End when shortest stream ends
                '-avoid_negative_ts', 'make_zero',  # Handle timing issues
                '-fflags', '+genpts', # Generate presentation timestamps
                '-y',                 # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg sync error: {result.stderr}")
            
            logger.info(f"Video with lip-synced audio saved: {output_path}")
            
        except Exception as e:
            logger.error(f"Error syncing audio-video: {e}")
            raise
    
    def process_video_with_lipsync(self, video_path, target_language):
        """Main processing pipeline with enhanced lip synchronization"""
        try:
            self.session_id = str(uuid.uuid4())
            
            # Step 1: Extract audio
            logger.info("Step 1: Extracting audio...")
            audio_path = self.extract_audio(video_path)
            
            # Step 2: Get video duration for timing
            logger.info("Step 2: Analyzing video timing...")
            video_duration = self.get_video_duration(video_path)
            logger.info(f"Video duration: {video_duration:.2f} seconds")
            
            # Step 3: Transcribe with detailed timing
            logger.info("Step 3: Transcribing with word-level timing...")
            transcription = self.transcribe_audio_with_timing(audio_path)
            
            # Step 4: Translate segments preserving timing
            logger.info("Step 4: Translating segments...")
            translated_segments = self.translate_segments(
                transcription['segments'], 
                target_language
            )
            
            # Step 5: Generate timed speech segments
            logger.info("Step 5: Generating time-synchronized speech...")
            segment_temp_dir = os.path.join(TEMP_DIR, f"{self.session_id}_segments")
            os.makedirs(segment_temp_dir, exist_ok=True)
            
            segment_audio_files = self.generate_timed_speech_segments(
                translated_segments, 
                target_language, 
                segment_temp_dir
            )
            
            # Step 6: Combine segments into final audio
            logger.info("Step 6: Combining synchronized audio segments...")
            final_audio_path = self.combine_audio_segments(segment_audio_files, video_duration)
            
            # Step 7: Sync with video using precise timing
            logger.info("Step 7: Final video synchronization...")
            output_video_path = os.path.join(
                OUTPUT_DIR,
                f"{self.session_id}_lipsynced.mp4"
            )
            self.sync_audio_video_with_timing(video_path, final_audio_path, output_video_path)
            
            # Prepare full text versions
            full_original_text = " ".join([seg['original_text'] for seg in translated_segments])
            full_translated_text = " ".join([seg['translated_text'] for seg in translated_segments])
            
            return {
                'success': True,
                'session_id': self.session_id,
                'original_text': full_original_text,
                'translated_text': full_translated_text,
                'output_video': output_video_path,
                'segments': translated_segments,
                'timing_info': {
                    'total_segments': len(translated_segments),
                    'video_duration': video_duration,
                    'sync_method': 'segment_based_time_stretching'
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing video with lip sync: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            self.cleanup()

@app.route('/')
def index():
    return render_template('index_lipsync.html')

@app.route('/test')
def test():
    return jsonify({
        'status': 'success',
        'message': 'Enhanced Video Dubbing Tool with Lip Sync is running!',
        'supported_languages': list(INDIAN_LANGUAGES.keys()),
        'features': [
            'Video upload and processing',
            'Audio extraction with FFmpeg',
            'Word-level speech transcription with Whisper AI',
            'Segment-based text translation',
            'Time-synchronized speech generation',
            'Audio time-stretching for lip sync',
            'Precise audio-video synchronization'
        ],
        'enhancements': [
            'Word-level timestamp extraction',
            'Segment-based audio generation',
            'Audio time-stretching for duration matching',
            'Precise timing preservation',
            'Enhanced synchronization algorithms'
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
        
        # Process video with enhanced lip sync
        processor = LipSyncVideoDubbingProcessor()
        result = processor.process_video_with_lipsync(video_path, target_language)
        
        if result['success']:
            return jsonify({
                'success': True,
                'session_id': result['session_id'],
                'original_text': result['original_text'],
                'translated_text': result['translated_text'],
                'original_video': f'/video/{video_filename}',
                'dubbed_video': f'/output/{os.path.basename(result["output_video"])}',
                'timing_info': result['timing_info'],
                'lip_sync_enabled': True
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
    print("=" * 70)
    print("🎬 Enhanced Video Dubbing Tool with Lip Synchronization")
    print("=" * 70)
    print("New Features:")
    print("• Word-level timestamp extraction")
    print("• Segment-based audio generation")
    print("• Audio time-stretching for duration matching")
    print("• Precise timing preservation")
    print("• Enhanced synchronization algorithms")
    print("=" * 70)
    print("🌐 Server starting at: http://localhost:5000")
    print("🧪 Test endpoint: http://localhost:5000/test")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5001)  # Using port 5001 to avoid conflicts
