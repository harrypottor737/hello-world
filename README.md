# 🎬 Video Dubbing Tool for Indian Languages

A comprehensive AI-powered video dubbing tool that converts videos to different Indian languages using advanced speech processing and machine learning technologies.

## 🌟 Features

- **Video Upload & Processing**: Support for multiple video formats (MP4, AVI, MOV, MKV)
- **Audio Extraction**: High-quality audio extraction using FFmpeg
- **Speech Transcription**: AI-powered speech-to-text using OpenAI Whisper
- **Language Translation**: Text translation to 10+ Indian languages
- **Text-to-Speech**: Natural-sounding voice generation using Google TTS
- **Audio-Video Sync**: Seamless synchronization of dubbed audio with original video
- **Modern UI**: Beautiful, responsive web interface with real-time progress tracking

## 🗣️ Supported Languages

- Hindi (हिंदी)
- Kannada (ಕನ್ನಡ)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Malayalam (മലയാളം)
- Marathi (मराठी)
- Gujarati (ગુજરાતી)
- Punjabi (ਪੰਜਾਬੀ)
- Bengali (বাংলা)
- Urdu (اردو)

## 🚀 How It Works

1. **Upload Video**: Select your video file and target language
2. **Audio Extraction**: FFmpeg separates audio from video
3. **Speech Recognition**: Whisper AI transcribes the original audio
4. **Translation**: Text is translated to the selected Indian language
5. **Voice Generation**: AI creates natural-sounding dubbed audio
6. **Synchronization**: New audio is synced with the original video
7. **Download**: Get your dubbed video with high-quality output

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for video processing)
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd video-dubbing-tool
   ```

2. **Install FFmpeg**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update && sudo apt-get install -y ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

3. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Usage

### Start the Application

```bash
source venv/bin/activate  # Activate virtual environment
python app_working.py     # Start the server
```

The application will be available at: `http://localhost:5000`

### Using the Web Interface

1. Open your browser and navigate to `http://localhost:5000`
2. Select a video file (max 100MB recommended)
3. Choose your target Indian language
4. Click "Start Dubbing" and wait for processing
5. View both original and dubbed videos side by side
6. Download the final dubbed video

### API Endpoints

- `GET /` - Main web interface
- `GET /test` - API status and features
- `GET /languages` - List of supported languages
- `POST /upload` - Upload and process video
- `GET /video/<filename>` - Serve original video
- `GET /output/<filename>` - Serve dubbed video

## 📁 Project Structure

```
video-dubbing-tool/
├── app_working.py          # Main application
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Web interface
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       └── app.js         # Frontend JavaScript
├── uploads/               # Uploaded videos
├── outputs/               # Processed videos
├── temp/                  # Temporary files
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables

You can configure the application using environment variables:

- `UPLOAD_DIR`: Directory for uploaded files (default: ./uploads)
- `OUTPUT_DIR`: Directory for processed files (default: ./outputs)
- `TEMP_DIR`: Directory for temporary files (default: ./temp)

### Whisper Model

The application uses the "base" Whisper model by default. You can modify this in `app_working.py`:

```python
model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
```

## 🎨 Technical Stack

- **Backend**: Flask (Python web framework)
- **AI/ML**: OpenAI Whisper (speech recognition)
- **Translation**: Deep Translator (Google Translate API)
- **TTS**: Google Text-to-Speech (gTTS)
- **Video Processing**: FFmpeg
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap UI)
- **File Handling**: Python standard libraries

## 📊 Performance

- **Processing Time**: 2-5 minutes for a 1-minute video (depends on system specs)
- **File Size Limit**: 100MB recommended (configurable)
- **Supported Formats**: MP4, AVI, MOV, MKV
- **Output Quality**: High-quality MP4 with AAC audio

## 🔒 Security Considerations

- File uploads are validated for type and size
- Temporary files are automatically cleaned up
- Session-based processing with unique identifiers
- CORS enabled for cross-origin requests

## 🐛 Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Ensure FFmpeg is installed and in PATH
   - Test with: `ffmpeg -version`

2. **Out of memory errors**
   - Use smaller video files
   - Consider using "tiny" Whisper model for lower memory usage

3. **Language not supported**
   - Check if the language is in INDIAN_LANGUAGES dictionary
   - Some languages may fallback to Hindi for TTS

4. **Slow processing**
   - Processing time depends on video length and system specs
   - Consider using GPU acceleration for Whisper if available

## 🚀 Future Enhancements

- [ ] Voice cloning for more natural dubbing
- [ ] Batch processing for multiple videos
- [ ] Advanced audio synchronization algorithms
- [ ] More Indian languages support
- [ ] GPU acceleration for faster processing
- [ ] Real-time dubbing capabilities
- [ ] Integration with cloud storage services

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI Whisper for speech recognition
- Google Translate for language translation
- FFmpeg for video processing
- Flask community for the web framework
- All contributors to the open-source libraries used

---

**Note**: This tool is designed for educational and research purposes. Please ensure you have the right to process and modify any video content you use with this tool.