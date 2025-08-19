# 🎬 Video Dubbing Tool - Demo Instructions

## Quick Start Demo

### 1. Start the Application

```bash
# Navigate to the project directory
cd /workspace

# Activate virtual environment
source venv/bin/activate

# Start the server
python app_working.py
```

You should see output like:
```
============================================================
🎬 Video Dubbing Tool for Indian Languages
============================================================
Features:
• Video upload and processing
• Audio extraction with FFmpeg
• Speech transcription with Whisper AI
• Text translation to Indian languages
• Text-to-speech conversion
• Audio-video synchronization
============================================================
🌐 Server starting at: http://localhost:5000
🧪 Test endpoint: http://localhost:5000/test
============================================================
```

### 2. Test Basic Functionality

Open another terminal and test the API:

```bash
# Test if the server is running
curl http://localhost:5000/test

# Expected output:
{
  "features": [
    "Video upload and processing",
    "Audio extraction with FFmpeg",
    "Speech transcription with Whisper AI",
    "Text translation to Indian languages",
    "Text-to-speech conversion",
    "Audio-video synchronization"
  ],
  "message": "Video Dubbing Tool is running!",
  "status": "success",
  "supported_languages": [
    "hindi", "kannada", "tamil", "telugu", "malayalam",
    "marathi", "gujarati", "punjabi", "bengali", "urdu"
  ]
}
```

### 3. Access Web Interface

1. Open your web browser
2. Navigate to: `http://localhost:5000`
3. You should see the Video Dubbing Tool interface

### 4. Demo Workflow

#### Step 1: Prepare a Test Video
For the demo, you can use any short video file (MP4, AVI, MOV, MKV) with spoken content. Recommended:
- Duration: 10-30 seconds for quick testing
- Size: Under 50MB for faster processing
- Content: Clear speech in English

#### Step 2: Upload and Process
1. Click "Select Video File" and choose your test video
2. Select a target language (e.g., "Hindi")
3. Click "Start Dubbing"
4. Watch the progress indicators:
   - Uploading video...
   - Extracting audio...
   - Transcribing audio...
   - Translating text...
   - Generating speech...
   - Syncing audio...

#### Step 3: Review Results
Once processing is complete, you'll see:
- **Original Video**: Your uploaded video
- **Dubbed Video**: Video with new audio in the selected language
- **Original Text**: Transcribed text from the original audio
- **Translated Text**: Text translated to the target language
- **Download Button**: To save the dubbed video

## 🧪 Testing Different Languages

Try the dubbing process with different target languages:
- **Hindi** (हिंदी) - Most reliable
- **Tamil** (தமிழ்) - Good support
- **Bengali** (বাংলা) - Good support
- **Gujarati** (ગુજરાતી) - May fallback to Hindi
- **Kannada** (ಕನ್ನಡ) - May fallback to Hindi

## 📊 Expected Processing Times

| Video Length | Processing Time | Notes |
|--------------|----------------|-------|
| 10 seconds   | 30-60 seconds  | Quick test |
| 30 seconds   | 1-2 minutes    | Good for demo |
| 1 minute     | 2-5 minutes    | Full workflow |
| 5 minutes    | 10-20 minutes  | Longer processing |

*Times vary based on system specifications and video complexity*

## 🔍 What to Look For

### Successful Processing Indicators:
1. **Audio Extraction**: Check console logs for "Audio extracted to: ..."
2. **Transcription**: Original text appears accurately
3. **Translation**: Translated text is in the target language
4. **Speech Generation**: New audio file is created
5. **Video Sync**: Final video plays with new audio

### Quality Checks:
- **Transcription Accuracy**: How well the original speech was converted to text
- **Translation Quality**: How natural the translated text sounds
- **Audio Quality**: Clarity of the generated speech
- **Synchronization**: How well the new audio matches the video timing

## 🐛 Common Demo Issues and Solutions

### Issue: "FFmpeg not found"
**Solution**: Ensure FFmpeg is installed
```bash
sudo apt-get install ffmpeg  # Ubuntu/Debian
brew install ffmpeg          # macOS
```

### Issue: "Out of memory" during Whisper processing
**Solution**: Use smaller video files or restart the application

### Issue: Translation appears in English
**Solution**: Some languages may not be fully supported by gTTS and will fallback to Hindi

### Issue: Audio sync problems
**Solution**: This can happen with very long videos or complex audio. Try shorter clips.

## 📱 Mobile Testing

The web interface is responsive and can be tested on mobile devices:
1. Ensure your phone is on the same network
2. Access using your computer's IP address: `http://[YOUR_IP]:5000`
3. Upload smaller video files on mobile for better performance

## 🎯 Demo Script

Here's a suggested demo flow:

1. **Introduction** (30 seconds)
   - "This is an AI-powered video dubbing tool for Indian languages"
   - Show the main interface

2. **Upload Process** (1 minute)
   - Select a short test video
   - Choose Hindi as target language
   - Explain each step as it processes

3. **Results Review** (2 minutes)
   - Play original video
   - Show transcribed text
   - Show translated text
   - Play dubbed video
   - Compare the two videos

4. **Language Variety** (1 minute)
   - Show the supported languages list
   - Mention the technical stack (Whisper, Google Translate, gTTS)

5. **Technical Details** (1 minute)
   - Explain the workflow: Extract → Transcribe → Translate → Generate → Sync
   - Mention use cases: education, content creation, accessibility

## 🔧 Advanced Demo Features

For technical audiences, you can also demonstrate:

### API Usage
```bash
# Upload via API
curl -X POST -F "video=@test_video.mp4" -F "language=hindi" \
     http://localhost:5000/upload

# Get supported languages
curl http://localhost:5000/languages
```

### Console Output
Show the detailed processing logs in the terminal running the application.

### File Structure
Explain how files are organized in uploads/, outputs/, and temp/ directories.

---

**Pro Tip**: Keep a few short test videos ready in different languages to showcase the tool's versatility!