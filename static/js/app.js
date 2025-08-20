// Video Dubbing Tool JavaScript

class VideoDubbingApp {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.currentSessionId = null;
        this.dubbedVideoUrl = null;
    }

    initializeElements() {
        this.uploadForm = document.getElementById('uploadForm');
        this.submitBtn = document.getElementById('submitBtn');
        this.progressCard = document.getElementById('progressCard');
        this.progressBar = document.getElementById('progressBar');
        this.progressText = document.getElementById('progressText');
        this.statusText = document.getElementById('statusText');
        this.resultsCard = document.getElementById('resultsCard');
        this.errorCard = document.getElementById('errorCard');
        this.errorMessage = document.getElementById('errorMessage');
        this.originalVideo = document.getElementById('originalVideo');
        this.dubbedVideo = document.getElementById('dubbedVideo');
        this.originalText = document.getElementById('originalText');
        this.translatedText = document.getElementById('translatedText');
        this.downloadBtn = document.getElementById('downloadBtn');
    }

    bindEvents() {
        this.uploadForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.downloadBtn.addEventListener('click', () => this.downloadVideo());
    }

    async handleSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(this.uploadForm);
        const videoFile = formData.get('video');
        const language = formData.get('language');

        if (!videoFile || !language) {
            this.showError('Please select a video file and target language.');
            return;
        }

        // Validate file size (limit to 100MB)
        if (videoFile.size > 100 * 1024 * 1024) {
            this.showError('File size too large. Please select a video smaller than 100MB.');
            return;
        }

        // Validate file type
        if (!videoFile.type.startsWith('video/')) {
            this.showError('Please select a valid video file.');
            return;
        }

        this.startProcessing();
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.showResults(result);
            } else {
                this.showError(result.error || 'An error occurred during processing.');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showError('Network error. Please check your connection and try again.');
        }
    }

    startProcessing() {
        this.hideAllCards();
        this.progressCard.style.display = 'block';
        this.submitBtn.disabled = true;
        this.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';

        // Simulate progress steps
        this.simulateProgress();
    }

    simulateProgress() {
        const steps = [
            { progress: 10, text: 'Uploading video...', status: 'Uploading and validating video file' },
            { progress: 25, text: 'Extracting audio...', status: 'Separating audio track from video using FFmpeg' },
            { progress: 45, text: 'Transcribing audio...', status: 'Converting speech to text using AI' },
            { progress: 65, text: 'Translating text...', status: 'Translating to target language' },
            { progress: 80, text: 'Generating speech...', status: 'Creating dubbed audio with text-to-speech' },
            { progress: 95, text: 'Syncing audio...', status: 'Synchronizing dubbed audio with video' },
            { progress: 100, text: 'Complete!', status: 'Dubbing process completed successfully' }
        ];

        let currentStep = 0;
        const interval = setInterval(() => {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                this.updateProgress(step.progress, step.text, step.status);
                currentStep++;
            } else {
                clearInterval(interval);
            }
        }, 2000);
    }

    updateProgress(percentage, text, status) {
        this.progressBar.style.width = `${percentage}%`;
        this.progressText.textContent = text;
        this.statusText.textContent = status;
    }

    showResults(result) {
        this.hideAllCards();
        this.resultsCard.style.display = 'block';
        
        // Set video sources
        this.originalVideo.src = result.original_video;
        this.dubbedVideo.src = result.dubbed_video;
        this.dubbedVideoUrl = result.dubbed_video;
        
        // Set text content
        this.originalText.textContent = result.original_text;
        this.translatedText.textContent = result.translated_text;
        
        // Store session ID
        this.currentSessionId = result.session_id;
        
        // Reset form
        this.resetFormState();
    }

    showError(message) {
        this.hideAllCards();
        this.errorCard.style.display = 'block';
        this.errorMessage.textContent = message;
        this.resetFormState();
    }

    hideAllCards() {
        this.progressCard.style.display = 'none';
        this.resultsCard.style.display = 'none';
        this.errorCard.style.display = 'none';
    }

    resetFormState() {
        this.submitBtn.disabled = false;
        this.submitBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Start Dubbing';
    }

    downloadVideo() {
        if (this.dubbedVideoUrl) {
            const link = document.createElement('a');
            link.href = this.dubbedVideoUrl;
            link.download = `dubbed_video_${this.currentSessionId}.mp4`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
}

// Utility Functions
function resetForm() {
    location.reload();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// File input handler
document.addEventListener('DOMContentLoaded', function() {
    const app = new VideoDubbingApp();
    
    // Add file input change handler
    const videoInput = document.getElementById('videoFile');
    if (videoInput) {
        videoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const fileSize = formatFileSize(file.size);
                const fileName = file.name;
                
                // Update UI to show selected file
                const fileInfo = document.createElement('div');
                fileInfo.className = 'alert alert-info mt-2';
                fileInfo.innerHTML = `
                    <i class="fas fa-file-video me-2"></i>
                    <strong>${fileName}</strong> (${fileSize})
                `;
                
                // Remove previous file info
                const existingInfo = videoInput.parentNode.querySelector('.alert');
                if (existingInfo) {
                    existingInfo.remove();
                }
                
                videoInput.parentNode.appendChild(fileInfo);
            }
        });
    }
    
    // Add drag and drop functionality
    const uploadCard = document.querySelector('.card');
    if (uploadCard) {
        uploadCard.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadCard.classList.add('border-primary');
        });
        
        uploadCard.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadCard.classList.remove('border-primary');
        });
        
        uploadCard.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadCard.classList.remove('border-primary');
            
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type.startsWith('video/')) {
                videoInput.files = files;
                videoInput.dispatchEvent(new Event('change'));
            }
        });
    }
});

// Add some animations
document.addEventListener('DOMContentLoaded', function() {
    // Animate cards on load
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 200);
    });
    
    // Add hover effects to feature icons
    const featureIcons = document.querySelectorAll('.feature-icon i');
    featureIcons.forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.2) rotate(5deg)';
            this.style.transition = 'all 0.3s ease';
        });
        
        icon.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) rotate(0deg)';
        });
    });
});