console.log("telemedicineApp loaded");

// Define the component function
function telemedicineApp() {
    console.log("telemedicineApp function called");
    return {
        videoEnabled: true, 
        audioEnabled: true,
        screenSharing: false,
        connectionStatus: 'connected',
        sidePanelOpen: true,
        activeTab: 'chat',
        chatMessage: '',
        sessionNotes: '',
        sessionTimer: '00:00',
        sessionStart: new Date(),
        uploadedFiles: [],
        
        init() {
            console.log("telemedicineApp init called");
            try {
                // Force the panel to be openCC for debugging
                this.sidePanelOpen = true;
                this.activeTab = 'chat';
                console.log("Initial state - sidePanelOpen:", this.sidePanelOpen, "activeTab:", this.activeTab);
                
                this.initializeMedia();
                this.startSessionTimer();
                this.fetchFiles();
                console.log("telemedicineApp init completed successfully");
                
                // Double-check the panel state after a short delay
                setTimeout(() => {
                    console.log("Panel state after init:", this.sidePanelOpen);
                }, 100);
            } catch (error) {
                console.error("Error in init:", error);
            }
        },
        
        async uploadFile() {
            console.log("uploadFile called");
            try {
                const input = document.getElementById('fileInput');
                if (!input.files.length) return;
                
                const formData = new FormData();
                formData.append('file', input.files[0]);
                
                const res = await fetch('/upload', { method: 'POST', body: formData });
                if (res.ok) {
                    this.fetchFiles();
                    input.value = '';
                    alert('File uploaded successfully!');
                } else {
                    alert('Upload failed. Please try again.');
                }
            } catch (error) {
                console.error('Upload error:', error);
                alert('Upload failed. Please try again.');
            }
        },
        
        async fetchFiles() {
            try {
                const res = await fetch('/uploads');
                if (res.ok) {
                    const data = await res.json();
                    this.uploadedFiles = data.files;
                    console.log("Fetched files:", this.uploadedFiles);
                }
            } catch (error) {
                console.error('Fetch files error:', error);
            }
        },
        
        async initializeMedia() {
            try {
                console.log("Initializing media...");
                const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                const localVideo = document.getElementById('localVideo');
                if (localVideo) {
                    localVideo.srcObject = stream;
                    console.log("Local video stream set");
                }
                this.simulateRemoteVideo();
                this.connectionStatus = 'connected';
            } catch (error) {
                console.error("Media initialization error:", error);
                this.connectionStatus = 'error';
                // Don't show alert for media errors in development
                console.log("Media access denied - this is normal in development");
            }
        },
        
        simulateRemoteVideo() {
            const remoteVideo = document.getElementById('remoteVideo');
            if (remoteVideo) {
                remoteVideo.style.backgroundColor = '#1f2937';
                console.log("Remote video simulated");
            }
        },
        
        toggleVideo() {
            console.log("toggleVideo called, current state:", this.videoEnabled);
            this.videoEnabled = !this.videoEnabled;
            const localVideo = document.getElementById('localVideo');
            if (localVideo && localVideo.srcObject) {
                localVideo.srcObject.getVideoTracks().forEach(track => { 
                    track.enabled = this.videoEnabled; 
                    console.log("Video track enabled:", this.videoEnabled);
                });
            }
        },
        
        toggleAudio() {
            console.log("toggleAudio called, current state:", this.audioEnabled);
            this.audioEnabled = !this.audioEnabled;
            const localVideo = document.getElementById('localVideo');
            if (localVideo && localVideo.srcObject) {
                localVideo.srcObject.getAudioTracks().forEach(track => { 
                    track.enabled = this.audioEnabled; 
                    console.log("Audio track enabled:", this.audioEnabled);
                });
            }
        },
        
        async toggleScreenShare() {
            console.log("toggleScreenShare called, current state:", this.screenSharing);
            if (!this.screenSharing) {
                try {
                    const stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
                    const localVideo = document.getElementById('localVideo');
                    if (localVideo) localVideo.srcObject = stream;
                    this.screenSharing = true;
                    stream.getVideoTracks()[0].addEventListener('ended', () => {
                        this.screenSharing = false;
                        this.initializeMedia();
                    });
                } catch (error) {
                    console.error("Screen share error:", error);
                    alert('Unable to share screen');
                }
            } else {
                this.screenSharing = false;
                this.initializeMedia();
            }
        },
        
        sendMessage() {
            console.log("sendMessage called with:", this.chatMessage);
            if (this.chatMessage.trim()) {
                // In real app, send via WebSocket
                this.chatMessage = '';
                alert('Message sent');
            }
        },
        
        openChat() {
            console.log("openChat called");
            this.sidePanelOpen = true;
            this.activeTab = 'chat';
        },
        
        startSessionTimer() {
            console.log("startSessionTimer called");
            setInterval(() => {
                const now = new Date();
                const elapsed = now - this.sessionStart;
                const minutes = Math.floor(elapsed / 60000);
                const seconds = Math.floor((elapsed % 60000) / 1000);
                this.sessionTimer = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }, 1000);
        },
        
        endCall() {
            if (confirm('Are you sure you want to end this call?')) {
                const localVideo = document.getElementById('localVideo');
                if (localVideo && localVideo.srcObject) {
                    localVideo.srcObject.getTracks().forEach(track => track.stop());
                }
                window.location.href = '/';
            }
        }
    }
}

// Make it globally available
window.telemedicineApp = telemedicineApp;

// Register with Alpine when it's ready
document.addEventListener('alpine:init', () => {
    console.log("Alpine init event fired");
    Alpine.data('telemedicineApp', telemedicineApp);
});

// Also try immediate registration
if (window.Alpine) {
    console.log("Alpine already available, registering immediately");
    Alpine.data('telemedicineApp', telemedicineApp);
}

// Fallback: if Alpine is not available, try to register when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM loaded, checking for Alpine");
    if (window.Alpine) {
        console.log("Alpine found on DOM ready, registering");
        Alpine.data('telemedicineApp', telemedicineApp);
    }
});

// Additional fallback - try to register after a short delay
setTimeout(() => {
    if (window.Alpine && !window.Alpine.data('telemedicineApp')) {
        console.log("Registering telemedicineApp after timeout");
        Alpine.data('telemedicineApp', telemedicineApp);
    }
}, 1000); 