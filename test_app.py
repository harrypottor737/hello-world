#!/usr/bin/env python3

"""
Simple test version of the video dubbing app to verify basic functionality
"""

import os
import sys
import tempfile
import uuid
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Create necessary directories
UPLOAD_DIR = "/workspace/uploads"
OUTPUT_DIR = "/workspace/outputs"
TEMP_DIR = "/workspace/temp"

for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return jsonify({
        'status': 'success',
        'message': 'Video Dubbing Tool is running!',
        'supported_languages': list(INDIAN_LANGUAGES.keys())
    })

@app.route('/languages')
def get_languages():
    return jsonify(list(INDIAN_LANGUAGES.keys()))

@app.route('/upload', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        target_language = request.form.get('language', 'hindi').lower()
        
        if target_language not in INDIAN_LANGUAGES:
            return jsonify({'error': f'Unsupported language: {target_language}'}), 400
        
        # For now, just return a mock response
        session_id = str(uuid.uuid4())
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully! Full processing will be implemented.',
            'session_id': session_id,
            'original_text': 'This is a sample transcription of the uploaded video.',
            'translated_text': f'यह अपलोड किए गए वीडियो का एक नमूना ट्रांसक्रिप्शन है। (Sample translation to {target_language})',
            'target_language': target_language,
            'file_size': video_file.content_length if hasattr(video_file, 'content_length') else 'Unknown'
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Video Dubbing Tool Test Server...")
    print("Available at: http://localhost:5000")
    print("Test endpoint: http://localhost:5000/test")
    app.run(debug=True, host='0.0.0.0', port=5000)