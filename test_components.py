#!/usr/bin/env python3

"""
Component Test Script for Video Dubbing Tool
Tests individual components to ensure they work correctly
"""

import os
import sys
import subprocess
import tempfile

def test_ffmpeg():
    """Test if FFmpeg is installed and working"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg is installed and working")
            version = result.stdout.split('\n')[0]
            print(f"   {version}")
            return True
        else:
            print("❌ FFmpeg test failed")
            return False
    except Exception as e:
        print(f"❌ FFmpeg not found: {e}")
        return False

def test_whisper():
    """Test if Whisper can be imported and loaded"""
    try:
        import whisper
        print("✅ Whisper imported successfully")
        
        # Test model loading (this might take a while on first run)
        print("   Loading base model (this may take a moment)...")
        model = whisper.load_model("base")
        print("✅ Whisper base model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        return False

def test_translation():
    """Test translation functionality"""
    try:
        from deep_translator import GoogleTranslator
        
        translator = GoogleTranslator(source='auto', target='hi')
        result = translator.translate("Hello, this is a test.")
        
        if result and len(result) > 0:
            print("✅ Translation service working")
            print(f"   Test translation: '{result}'")
            return True
        else:
            print("❌ Translation returned empty result")
            return False
    except Exception as e:
        print(f"❌ Translation test failed: {e}")
        return False

def test_tts():
    """Test text-to-speech functionality"""
    try:
        from gtts import gTTS
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_path = temp_file.name
        
        tts = gTTS(text="Hello, this is a test.", lang='en', slow=False)
        tts.save(temp_path)
        
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            print("✅ Text-to-Speech working")
            print(f"   Test audio file created: {os.path.getsize(temp_path)} bytes")
            os.unlink(temp_path)  # Clean up
            return True
        else:
            print("❌ Text-to-Speech failed to create audio file")
            return False
    except Exception as e:
        print(f"❌ Text-to-Speech test failed: {e}")
        return False

def test_flask():
    """Test Flask and web components"""
    try:
        from flask import Flask
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        print("✅ Flask and CORS imported successfully")
        return True
    except Exception as e:
        print(f"❌ Flask test failed: {e}")
        return False

def test_directories():
    """Test if required directories exist"""
    directories = ['/workspace/uploads', '/workspace/outputs', '/workspace/temp']
    all_good = True
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            print(f"❌ Directory missing: {directory}")
            all_good = False
    
    return all_good

def main():
    print("🧪 Video Dubbing Tool - Component Tests")
    print("=" * 50)
    
    tests = [
        ("Directories", test_directories),
        ("FFmpeg", test_ffmpeg),
        ("Flask", test_flask),
        ("Translation", test_translation),
        ("Text-to-Speech", test_tts),
        ("Whisper AI", test_whisper),  # This one last as it's slow
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The video dubbing tool should work correctly.")
    else:
        print("⚠️  Some tests failed. Please check the installation and dependencies.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())