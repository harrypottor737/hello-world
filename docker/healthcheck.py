#!/usr/bin/env python3
"""
Health check script for Docker container
Tests if the video dubbing application is running and responsive
"""

import sys
import requests
import time

def health_check():
    """Check if the application is healthy"""
    try:
        # Test the main endpoint
        response = requests.get('http://localhost:5001/test', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print("✅ Application is healthy")
                return True
        
        print(f"❌ Application returned status {response.status_code}")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to application")
        return False
    except requests.exceptions.Timeout:
        print("❌ Application response timeout")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    if health_check():
        sys.exit(0)
    else:
        sys.exit(1)