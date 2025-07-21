# real code 

import cv2
import numpy as np
import tensorflow as tf

# --- Constants ---
IMG_SIZE = 64
FONT = cv2.FONT_HERSHEY_SIMPLEX
DROWSY_COUNTER_THRESHOLD = 20 # Number of consecutive frames to trigger alarm

# --- Load Models and Cascades ---
try:
    # Load the trained models for yawn and eye state detection
    yawn_model = tf.keras.models.load_model("drowiness_new6.model_y.keras")
    eye_model = tf.keras.models.load_model("drowiness_new6.model_e.keras")

    # Load Haar Cascade classifiers for face and eye detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
except Exception as e:
    print(f"Error loading models or cascade files: {e}")
    print("Please make sure the .keras model files and OpenCV's XML files are accessible.")
    exit()

# --- Initialize Webcam ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# --- Drowsiness Tracking Variables ---
drowsy_counter = 0
is_drowsy = False

# --- Main Loop ---
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to grayscale for cascade classifiers
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    is_currently_drowsy = False

    for (x, y, w, h) in faces:
        # Draw a rectangle around the detected face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        # Get face Region of Interest (ROI) for both color and gray images
        roi_gray = gray[y:y + h, x:x + w]
        roi_color_face = frame[y:y + h, x:x + w]

        # --- Yawn Detection ---
        try:
            # Preprocess face ROI for the yawn model
            face_for_yawn = cv2.resize(roi_color_face, (IMG_SIZE, IMG_SIZE))
            face_for_yawn = face_for_yawn / 255.0
            face_for_yawn = np.reshape(face_for_yawn, (1, IMG_SIZE, IMG_SIZE, 3))
            
            # Predict yawn
            yawn_prob = yawn_model.predict(face_for_yawn, verbose=0)[0][0]
            yawn_label = "Yawn" if yawn_prob > 0.5 else "No Yawn"
            is_yawning = (yawn_label == "Yawn")
            
            # Display yawn status
            cv2.putText(frame, yawn_label, (x, y - 10), FONT, 0.7, (0, 0, 255), 2)
            if is_yawning:
                is_currently_drowsy = True

        except Exception as e:
            print(f"Could not process face for yawn detection: {e}")

        # --- Eye Detection ---
        eyes_detected = False
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex, ey, ew, eh) in eyes:
            eyes_detected = True
            # Draw rectangle around eyes
            cv2.rectangle(roi_color_face, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
            
            # Preprocess eye ROI for the eye model
            eye_roi = roi_color_face[ey:ey + eh, ex:ex + ew]
            eye_for_model = cv2.resize(eye_roi, (IMG_SIZE, IMG_SIZE))
            eye_for_model = eye_for_model / 255.0
            eye_for_model = np.reshape(eye_for_model, (1, IMG_SIZE, IMG_SIZE, 3))

            # Predict eye state
            eye_prob = eye_model.predict(eye_for_model, verbose=0)[0][0]
            eye_label = "Open" if eye_prob > 0.5 else "Closed"
            
            # If any eye is closed, mark as drowsy for this frame
            if eye_label == "Closed":
                is_currently_drowsy = True

            # Display eye status
            cv2.putText(frame, eye_label, (x + ex, y + ey - 5), FONT, 0.5, (0, 255, 255), 2)

        # If no eyes are detected, it might be because they are closed.
        if not eyes_detected:
            is_currently_drowsy = True
            cv2.putText(frame, "No Eyes Detected", (x, y + h + 20), FONT, 0.7, (0, 0, 255), 2)

    # --- Drowsiness Logic with Counter ---
    if is_currently_drowsy:
        drowsy_counter += 1
    else:
        drowsy_counter = 0
        is_drowsy = False

    if drowsy_counter > DROWSY_COUNTER_THRESHOLD:
        is_drowsy = True

    if is_drowsy:
        cv2.putText(frame, "ALERT: DROWSINESS DETECTED!", (50, 50), FONT, 1, (0, 0, 255), 3)

    # Display the final frame
    cv2.imshow("Drowsiness Detection", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()