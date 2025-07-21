# Drowsiness Detection Web Application

A modern Flask web application for real-time drowsiness detection with a beautiful blue-themed UI.

## 🔹 Where to Add Your Drowsiness Detection Code

### Main Detection Method: `process_frame()` in `app.py`

**Location**: Line 15 in `app.py`

This is the **primary method** where you should add your drowsiness detection algorithm:

```python
def process_frame(self, frame):
    """
    🔹 PUT YOUR DROWSINESS DETECTION CODE HERE 🔹

    This method receives a frame (numpy array) and should return:
    - processed_frame: The frame with detection overlays
    - is_drowsy: Boolean indicating if drowsiness is detected
    - confidence: Float between 0-1 indicating confidence level
    """

    # 1. Add your eye detection code here
    # Example: eyes = eye_cascade.detectMultiScale(gray)

    # 2. Add your blink detection code here
    # Example: ear = calculate_eye_aspect_ratio(landmarks)

    # 3. Add your drowsiness classification code here
    # Example: if ear < THRESHOLD: is_drowsy = True

    # 4. Draw detection overlays on the frame
    # Example: cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

    return processed_frame, is_drowsy, confidence
```

### Additional Integration Points:

1. **Webcam Settings** (Line 45): Modify camera initialization if needed
2. **Image Upload Processing** (Line 120): Add image-specific preprocessing
3. **Model Loading**: Add your model loading code in the `__init__` method (Line 10)

## 🚀 Quick Start

> **⚠️ Note:**
> If you are using Python 3.13, you may encounter errors installing Pillow or other dependencies. It is recommended to use Python 3.11 or 3.12 for best compatibility with this project.

1. **Install Dependencies**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the Application**:

   ```bash
   python app.py
   ```

3. **Open Your Browser**:
   Navigate to `http://localhost:5000`

## 📁 Project Structure

```
Drowsiness/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main web interface
├── static/
│   ├── css/
│   │   └── style.css     # Modern blue styling
│   └── js/
│       └── script.js     # Frontend JavaScript
└── README.md             # This file
```

## 🎯 Features

- **Real-time Webcam Detection**: Live video feed processing
- **Image Upload Analysis**: Upload and analyze static images
- **Modern Blue UI**: Beautiful, responsive interface
- **Detection Statistics**: Session tracking and metrics
- **Alert System**: Visual and audio drowsiness alerts
- **Confidence Scoring**: Real-time confidence levels

## 🔧 Code Integration Guide

### Step 1: Replace the Placeholder Detection

Find this section in `app.py` (around line 35):

```python
# Placeholder implementation - replace with your code
processed_frame = frame.copy()
# ... replace everything here with your detection logic
```

### Step 2: Add Your Model/Cascade Files

```python
def __init__(self):
    # Add your model loading here
    # self.face_cascade = cv2.CascadeClassifier('path/to/haarcascade_frontalface_default.xml')
    # self.eye_cascade = cv2.CascadeClassifier('path/to/haarcascade_eye.xml')
    # self.model = load_model('your_model.h5')  # if using deep learning

    self.is_detecting = False
    # ... rest of init
```

### Step 3: Implement Your Detection Logic

```python
def process_frame(self, frame):
    # Convert to grayscale if needed
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Your detection code here:
    # - Face detection
    # - Eye detection
    # - Feature extraction
    # - Drowsiness classification

    # Return results
    return processed_frame, is_drowsy, confidence_score
```

## 🎨 UI Features

- **Control Panel**: Start/stop detection, upload images
- **Live Video Feed**: Real-time camera stream with overlays
- **Status Panel**: Current detection state and confidence
- **Statistics Dashboard**: Session metrics and alert counts
- **Alert Modal**: Drowsiness warning notifications

## 📱 Responsive Design

The interface adapts to different screen sizes:

- Desktop: Full layout with side panels
- Tablet: Stacked layout
- Mobile: Single column, optimized buttons

## 🛠 Customization

### Colors and Themes

Edit `static/css/style.css` CSS variables:

```css
:root {
  --primary-blue: #2563eb;
  --secondary-blue: #3b82f6;
  /* ... modify colors here */
}
```

### Detection Parameters

Add configuration variables to the `DrowsinessDetector` class:

```python
def __init__(self):
    # Your detection parameters
    self.ear_threshold = 0.25
    self.consecutive_frames = 20
    # ... etc
```

## 🔍 Testing Your Integration

1. **Test with Static Image**: Use the upload feature first
2. **Test with Webcam**: Start real-time detection
3. **Verify Alerts**: Ensure drowsiness triggers work
4. **Check UI Updates**: Confirm status and confidence display correctly

## 📝 Notes

- The app uses threading for non-blocking webcam processing
- OpenCV handles video capture and image processing
- Flask serves the web interface and API endpoints
- JavaScript manages real-time UI updates and user interactions

Replace the placeholder code with your drowsiness detection algorithm and you'll have a fully functional web application!
