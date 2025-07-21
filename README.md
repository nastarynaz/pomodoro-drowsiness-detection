# Drowsiness Detection Web Application

A modern Flask web application for real-time drowsiness detection with a beautiful blue-themed UI.

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
   Navigate to `[http://localhost:5000](http://127.0.0.1:5000/)`

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
