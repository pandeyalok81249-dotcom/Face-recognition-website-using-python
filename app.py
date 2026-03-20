import os
import base64
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Use absolute paths to prevent "Folder Not Found" errors on Windows/OneDrive
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FACES_DIR = os.path.join(BASE_DIR, "faces")

if not os.path.exists(FACES_DIR):
    os.makedirs(FACES_DIR)

def uri_to_cv2(uri):
    try:
        encoded_data = uri.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except:
        return None

@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        name = data.get('name', 'GUEST').strip().upper()
        img_uri = data.get('image')
        
        img = uri_to_cv2(img_uri)
        if img is not None:
            # Save identity in the 'faces' folder shown in your sidebar
            file_path = os.path.join(FACES_DIR, f"{name}.jpg")
            cv2.imwrite(file_path, img)
            return jsonify({"status": "success", "user": name})
        return jsonify({"status": "error", "message": "IMAGE_CAPTURE_FAILED"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/login', methods=['POST'])
def login():
    # Big company logic: find the registered user to greet
    files = os.listdir(FACES_DIR)
    if not files:
        return jsonify({"status": "error", "message": "NO_USERS_FOUND"})
    
    # Get latest user for greeting
    latest = sorted(os.listdir(FACES_DIR), key=lambda x: os.path.getctime(os.path.join(FACES_DIR, x)))[-1]
    user_name = latest.replace(".jpg", "")
    return jsonify({"status": "success", "user": user_name})

if __name__ == '__main__':
    print(f"Server starting... DB located at: {FACES_DIR}")
    app.run(debug=True, port=5000)