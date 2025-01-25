import time
from flask import Blueprint, current_app, request, jsonify
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import os
from dotenv import load_dotenv
load_dotenv()
main_bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main_bp.route('/api/v1/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
        
    file = request.files['image']
    threshold = float(request.form.get('threshold', 0.5))
    
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    try:
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        service = current_app.anti_spoof_service
        is_real, score, result_img, time_taken = service.predict(image, threshold)

        if not is_real:
            filename = os.path.join(os.getenv("SPOOF_DIR"), f"{int(time.time())}.jpeg")
            cv2.imwrite(filename, result_img)
            
        return jsonify({
            "is_real": is_real,
            "score": float(score),
            "threshold": float(threshold),
            "time_taken": time_taken,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500