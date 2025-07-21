// Drowsiness Detection Web App JavaScript

class DrowsinessApp {
  constructor() {
    this.isDetecting = false;
    this.sessionStartTime = null;
    this.drowsinessCount = 0;
    this.confidenceSum = 0;
    this.confidenceReadings = 0;
    this.statusCheckInterval = null;

    this.initializeElements();
    this.attachEventListeners();
    this.updateSessionTime();
  }

  initializeElements() {
    // Buttons
    this.startBtn = document.getElementById("startBtn");
    this.stopBtn = document.getElementById("stopBtn");
    this.uploadBtn = document.getElementById("uploadBtn");
    this.imageUpload = document.getElementById("imageUpload");
    this.closeAlert = document.getElementById("closeAlert");

    // Display elements
    this.videoFeed = document.getElementById("videoFeed");
    this.placeholder = document.getElementById("placeholder");
    this.uploadPreview = document.getElementById("uploadPreview");
    this.uploadedImage = document.getElementById("uploadedImage");

    // Status elements
    this.statusCircle = document.getElementById("statusCircle");
    this.statusText = document.getElementById("statusText");
    this.detectionStatus = document.getElementById("detectionStatus");
    this.confidenceLevel = document.getElementById("confidenceLevel");
    this.currentState = document.getElementById("currentState");

    // Stats elements
    this.sessionTime = document.getElementById("sessionTime");
    this.drowsinessCountEl = document.getElementById("drowsinessCount");
    this.avgConfidence = document.getElementById("avgConfidence");

    // Modal
    this.alertModal = document.getElementById("alertModal");
  }

  attachEventListeners() {
    this.startBtn.addEventListener("click", () => this.startDetection());
    this.stopBtn.addEventListener("click", () => this.stopDetection());
    this.uploadBtn.addEventListener("click", () => this.imageUpload.click());
    this.imageUpload.addEventListener("change", (e) =>
      this.handleImageUpload(e)
    );
    this.closeAlert.addEventListener("click", () => this.closeAlertModal());

    // Close modal when clicking outside
    this.alertModal.addEventListener("click", (e) => {
      if (e.target === this.alertModal) {
        this.closeAlertModal();
      }
    });
  }

  async startDetection() {
    try {
      this.showLoading(this.startBtn);

      const response = await fetch("/start_detection", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (data.status === "started" || data.status === "already_running") {
        this.isDetecting = true;
        this.sessionStartTime = new Date();
        this.startBtn.disabled = true;
        this.stopBtn.disabled = false;
        this.updateStatus("Running", "alert");

        // Start video feed
        this.startVideoFeed();

        // Start status checking
        this.startStatusChecking();

        this.showNotification("Detection started successfully!", "success");
      } else {
        this.showNotification("Failed to start detection", "error");
      }
    } catch (error) {
      console.error("Error starting detection:", error);
      this.showNotification("Error starting detection", "error");
    } finally {
      this.hideLoading(this.startBtn);
    }
  }

  async stopDetection() {
    try {
      this.showLoading(this.stopBtn);

      const response = await fetch("/stop_detection", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (data.status === "stopped") {
        this.isDetecting = false;
        this.sessionStartTime = null;
        this.startBtn.disabled = false;
        this.stopBtn.disabled = true;
        this.updateStatus("Stopped", "stopped");

        // Stop video feed
        this.stopVideoFeed();

        // Stop status checking
        this.stopStatusChecking();

        this.showNotification("Detection stopped", "info");
      }
    } catch (error) {
      console.error("Error stopping detection:", error);
      this.showNotification("Error stopping detection", "error");
    } finally {
      this.hideLoading(this.stopBtn);
    }
  }

  startVideoFeed() {
    this.placeholder.style.display = "none";
    this.uploadPreview.style.display = "none";
    this.videoFeed.style.display = "block";
    this.videoFeed.src = "/video_feed";
  }

  stopVideoFeed() {
    this.videoFeed.style.display = "none";
    this.uploadPreview.style.display = "none";
    this.placeholder.style.display = "flex";
    this.videoFeed.src = "";
  }

  startStatusChecking() {
    this.statusCheckInterval = setInterval(async () => {
      try {
        const response = await fetch("/get_status");
        const data = await response.json();

        this.updateDetectionInfo(data);

        // Check for drowsiness alert
        if (data.status === "Drowsy" && data.is_detecting) {
          this.handleDrowsinessAlert(data.confidence);
        }
      } catch (error) {
        console.error("Error checking status:", error);
      }
    }, 1000); // Check every second
  }

  stopStatusChecking() {
    if (this.statusCheckInterval) {
      clearInterval(this.statusCheckInterval);
      this.statusCheckInterval = null;
    }
  }

  updateDetectionInfo(data) {
    // Update status display
    this.detectionStatus.textContent = data.is_detecting
      ? "Running"
      : "Stopped";
    this.confidenceLevel.textContent = `${(data.confidence * 100).toFixed(1)}%`;
    this.currentState.textContent = data.status;

    // Update status indicator
    this.updateStatus(data.status, data.status.toLowerCase());

    // Update confidence tracking
    if (data.is_detecting && data.confidence > 0) {
      this.confidenceSum += data.confidence;
      this.confidenceReadings++;
      const avgConf = (this.confidenceSum / this.confidenceReadings) * 100;
      this.avgConfidence.textContent = `${avgConf.toFixed(1)}%`;
    }
  }

  updateStatus(text, state) {
    this.statusText.textContent = text;
    this.statusCircle.className = `status-circle ${state}`;
  }

  handleDrowsinessAlert(confidence) {
    this.drowsinessCount++;
    this.drowsinessCountEl.textContent = this.drowsinessCount;

    // Show alert modal
    this.showAlertModal();

    // Play alert sound (if you want to add this later)
    this.playAlertSound();

    // Add visual feedback
    document.body.style.background =
      "linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)";
    setTimeout(() => {
      document.body.style.background = "";
    }, 2000);
  }

  showAlertModal() {
    this.alertModal.style.display = "block";
  }

  closeAlertModal() {
    this.alertModal.style.display = "none";
  }

  playAlertSound() {
    // Create a simple beep sound
    const audioContext = new (window.AudioContext ||
      window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = 800;
    oscillator.type = "sine";

    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(
      0.01,
      audioContext.currentTime + 0.5
    );

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
  }

  async handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    try {
      this.showLoading(this.uploadBtn);

      const formData = new FormData();
      formData.append("image", file);

      const response = await fetch("/upload_image", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        // Display the processed image
        this.placeholder.style.display = "none";
        this.videoFeed.style.display = "none";
        this.uploadPreview.style.display = "flex";
        this.uploadedImage.src = data.processed_image;

        // Update status with results
        this.detectionStatus.textContent = "Image Analysis";
        this.confidenceLevel.textContent = `${(data.confidence * 100).toFixed(
          1
        )}%`;
        this.currentState.textContent = data.status;
        this.updateStatus(data.status, data.status.toLowerCase());

        if (data.is_drowsy) {
          this.handleDrowsinessAlert(data.confidence);
        }

        this.showNotification("Image processed successfully!", "success");
      } else {
        this.showNotification(data.error || "Error processing image", "error");
      }
    } catch (error) {
      console.error("Error uploading image:", error);
      this.showNotification("Error uploading image", "error");
    } finally {
      this.hideLoading(this.uploadBtn);
      // Clear the file input
      event.target.value = "";
    }
  }

  updateSessionTime() {
    setInterval(() => {
      if (this.sessionStartTime) {
        const now = new Date();
        const diff = now - this.sessionStartTime;
        const minutes = Math.floor(diff / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        this.sessionTime.textContent = `${minutes
          .toString()
          .padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
      } else {
        this.sessionTime.textContent = "00:00";
      }
    }, 1000);
  }

  showLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<div class="loading"></div>';
    button.disabled = true;
    button.originalText = originalText;
  }

  hideLoading(button) {
    if (button.originalText) {
      button.innerHTML = button.originalText;
      delete button.originalText;
    }
    // Don't automatically enable - let the detection state control this
  }

  showNotification(message, type = "info") {
    // Create notification element
    const notification = document.createElement("div");
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
            <div class="notification-content">
                <span>${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;

    // Add styles
    notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${
              type === "success"
                ? "var(--success)"
                : type === "error"
                ? "var(--danger)"
                : "var(--primary-blue)"
            };
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1001;
            animation: slideInRight 0.3s ease;
            max-width: 400px;
        `;

    // Add to document
    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.style.animation = "slideOutRight 0.3s ease";
        setTimeout(() => {
          if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
          }
        }, 300);
      }
    }, 5000);

    // Close button functionality
    const closeBtn = notification.querySelector(".notification-close");
    closeBtn.addEventListener("click", () => {
      notification.style.animation = "slideOutRight 0.3s ease";
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    });
  }
}

// Add notification animations to CSS
const notificationStyles = document.createElement("style");
notificationStyles.textContent = `
    .notification-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 15px;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        font-size: 1.2rem;
        cursor: pointer;
        padding: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(notificationStyles);

// Initialize the app when the DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.drowsinessApp = new DrowsinessApp();
});

// Handle page visibility changes
document.addEventListener("visibilitychange", () => {
  if (
    document.hidden &&
    window.drowsinessApp &&
    window.drowsinessApp.isDetecting
  ) {
    // Optionally pause detection when tab is not visible
    console.log("Tab hidden - detection continues in background");
  } else if (!document.hidden && window.drowsinessApp) {
    console.log("Tab visible - detection active");
  }
});
