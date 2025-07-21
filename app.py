
from flask import Flask, render_template, request, jsonify, Response
import cv2
import base64
import numpy as np
from io import BytesIO
from PIL import Image
import threading
import time
import tensorflow as tf

app = Flask(__name__)

class DrowsinessDetector:

    def __init__(self):
        self.is_detecting = False
        self.current_frame = None
        self.drowsiness_status = "Alert"
        self.confidence_score = 0.0
        self.drowsy_counter = 0
        self.DROWSY_COUNTER_THRESHOLD = 20
        self.IMG_SIZE = 64
        self.FONT = cv2.FONT_HERSHEY_SIMPLEX
        try:
            self.yawn_model = tf.keras.models.load_model("drowiness_new6.model_y.keras")
            self.eye_model = tf.keras.models.load_model("drowiness_new6.model_e.keras")
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        except Exception as e:
            print(f"Error loading models or cascade files: {e}")
            print("Please make sure the .keras model files and OpenCV's XML files are accessible.")
            self.yawn_model = None
            self.eye_model = None
            self.face_cascade = None
            self.eye_cascade = None

    def process_frame(self, frame):
        processed_frame = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        is_currently_drowsy = False
        drowsy_confidences = []

        if self.face_cascade is None or self.eye_cascade is None or self.yawn_model is None or self.eye_model is None:
            cv2.putText(processed_frame, "Model/Cascade not loaded", (50, 50), self.FONT, 1, (0, 0, 255), 2)
            return processed_frame, False, 0.0

        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color_face = processed_frame[y:y + h, x:x + w]

            # --- Yawn Detection ---
            try:
                face_for_yawn = cv2.resize(roi_color_face, (self.IMG_SIZE, self.IMG_SIZE))
                face_for_yawn = face_for_yawn / 255.0
                face_for_yawn = np.reshape(face_for_yawn, (1, self.IMG_SIZE, self.IMG_SIZE, 3))
                yawn_prob = self.yawn_model.predict(face_for_yawn, verbose=0)[0][0]
                yawn_label = "Yawn" if yawn_prob > 0.5 else "No Yawn"
                is_yawning = (yawn_label == "Yawn")
                drowsy_confidences.append(yawn_prob)
                cv2.putText(processed_frame, yawn_label, (x, y - 10), self.FONT, 0.7, (0, 0, 255), 2)
                if is_yawning:
                    is_currently_drowsy = True
            except Exception as e:
                cv2.putText(processed_frame, f"YawnErr", (x, y - 10), self.FONT, 0.7, (0, 0, 255), 2)

            # --- Eye Detection ---
            eyes_detected = False
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            filtered_eyes = []
            for (ex, ey, ew, eh) in eyes:
                # Only accept eyes in upper 40% of face and with aspect ratio between 0.7 and 1.8
                if ey > int(h * 0.4):
                    continue  # skip eyes detected below upper 40% (likely nose)
                aspect_ratio = ew / float(eh)
                if aspect_ratio < 0.7 or aspect_ratio > 1.8:
                    continue  # skip if not eye-like
                filtered_eyes.append((ex, ey, ew, eh))
            for (ex, ey, ew, eh) in filtered_eyes:
                eyes_detected = True
                cv2.rectangle(roi_color_face, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                eye_roi = roi_color_face[ey:ey + eh, ex:ex + ew]
                try:
                    eye_for_model = cv2.resize(eye_roi, (self.IMG_SIZE, self.IMG_SIZE))
                    eye_for_model = eye_for_model / 255.0
                    eye_for_model = np.reshape(eye_for_model, (1, self.IMG_SIZE, self.IMG_SIZE, 3))
                    eye_prob = self.eye_model.predict(eye_for_model, verbose=0)[0][0]
                    eye_label = "Open" if eye_prob > 0.5 else "Closed"
                    drowsy_confidences.append(1-eye_prob if eye_label=="Closed" else eye_prob)
                    if eye_label == "Closed":
                        is_currently_drowsy = True
                    cv2.putText(processed_frame, eye_label, (x + ex, y + ey - 5), self.FONT, 0.5, (0, 255, 255), 2)
                except Exception as e:
                    cv2.putText(processed_frame, f"EyeErr", (x + ex, y + ey - 5), self.FONT, 0.5, (0, 255, 255), 2)

            if not eyes_detected:
                is_currently_drowsy = True
                cv2.putText(processed_frame, "No Eyes Detected", (x, y + h + 20), self.FONT, 0.7, (0, 0, 255), 2)

        # --- Drowsiness Logic with Counter ---
        if is_currently_drowsy:
            self.drowsy_counter += 1
        else:
            self.drowsy_counter = 0

        is_drowsy = self.drowsy_counter > self.DROWSY_COUNTER_THRESHOLD

        # Confidence: average of drowsy_confidences if available, else 0.0
        confidence = float(np.mean(drowsy_confidences)) if drowsy_confidences else 0.0

        if is_drowsy:
            cv2.putText(processed_frame, "ALERT: DROWSINESS DETECTED!", (50, 50), self.FONT, 1, (0, 0, 255), 3)

        return processed_frame, is_drowsy, confidence
    
    def detect_from_webcam(self, camera_index=0):
        """
        🔹 WEBCAM INTEGRATION POINT 🔹
        This method handles webcam capture and calls your detection code.
        You may need to modify camera settings or add preprocessing here.
        camera_index: int, default 0 (MacBook built-in usually 0)
        """
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"Error: Could not open camera with index {camera_index}.")
            return
        while self.is_detecting:
            ret, frame = cap.read()
            if not ret:
                break
            processed_frame, is_drowsy, confidence = self.process_frame(frame)
            self.drowsiness_status = "Drowsy" if is_drowsy else "Alert"
            self.confidence_score = confidence
            self.current_frame = processed_frame
            time.sleep(0.1)
        cap.release()

# Global detector instance
detector = DrowsinessDetector()

@app.route('/')
def index():
    return render_template('index.html')


# Camera index selection via query param
@app.route('/start_detection', methods=['POST'])
def start_detection():
    """Start drowsiness detection"""
    camera_index = int(request.args.get('camera', 0))
    if not detector.is_detecting:
        detector.is_detecting = True
        detection_thread = threading.Thread(target=detector.detect_from_webcam, args=(camera_index,))
        detection_thread.daemon = True
        detection_thread.start()
        return jsonify({"status": "started", "message": f"Detection started on camera {camera_index}"})
    return jsonify({"status": "already_running", "message": "Detection already running"})

# Camera preview route
@app.route('/camera_preview')
def camera_preview():
    """Preview a single frame from a given camera index (for selection)"""
    camera_index = int(request.args.get('camera', 0))
    cap = cv2.VideoCapture(camera_index)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return jsonify({"error": f"Could not open camera {camera_index}"}), 400
    ret, buffer = cv2.imencode('.jpg', frame)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return jsonify({"preview_image": f"data:image/jpeg;base64,{img_base64}", "camera_index": camera_index})

@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    """Stop drowsiness detection"""
    detector.is_detecting = False
    detector.drowsiness_status = "Stopped"
    return jsonify({"status": "stopped", "message": "Detection stopped"})

@app.route('/get_status')
def get_status():
    """Get current detection status"""
    return jsonify({
        "is_detecting": detector.is_detecting,
        "status": detector.drowsiness_status,
        "confidence": round(detector.confidence_score, 2)
    })

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    def generate():
        while detector.is_detecting and detector.current_frame is not None:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', detector.current_frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.1)
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    """
    🔹 IMAGE UPLOAD PROCESSING POINT 🔹
    
    Handle uploaded images for drowsiness detection.
    You can add your image processing code here.
    """
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No image selected"}), 400
    
    try:
        # Read and process the uploaded image
        image = Image.open(file.stream)
        frame = np.array(image)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Process with your detection code
        processed_frame, is_drowsy, confidence = detector.process_frame(frame)
        
        # Encode processed image for return
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            "success": True,
            "processed_image": f"data:image/jpeg;base64,{img_base64}",
            "is_drowsy": is_drowsy,
            "confidence": round(confidence, 2),
            "status": "Drowsy" if is_drowsy else "Alert"
        })
        
    except Exception as e:
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
