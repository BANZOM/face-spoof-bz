import time
import logging
from flask import Blueprint, current_app, request, jsonify
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import os
from dotenv import load_dotenv
load_dotenv()
main_bp = Blueprint('main', __name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main_bp.route('/api/v1/predict', methods=['POST'])
def predict():
    logging.info("Received prediction request")
    if 'image' not in request.files:
        logging.error("No image provided in the request")
        return jsonify({"error": "No image provided"}), 400
        
    file = request.files['image']
    threshold = float(request.form.get('threshold', 0.5))
    
    if file.filename == '':
        logging.error("Empty filename provided")
        return jsonify({"error": "Empty filename"}), 400
        
    if not allowed_file(file.filename):
        logging.error(f"Invalid file type: {file.filename}")
        return jsonify({"error": "Invalid file type"}), 400

    try:
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        service = current_app.anti_spoof_service
        is_real, score, result_img, time_taken = service.predict(image, threshold)

        if not is_real:
            filename = os.path.join(os.getenv("SPOOF_DIR", "spoofs"), f"{int(time.time())}.jpeg")
            cv2.imwrite(filename, result_img)
            logging.info(f"Spoof detected. Image saved to {filename}")
            
        logging.info(f"Prediction result: is_real={is_real}, score={score}, threshold={threshold}, time_taken={time_taken}")
        return jsonify({
            "is_real": is_real,
            "score": float(score),
            "threshold": float(threshold),
            "time_taken": time_taken,
        }), 200

    except Exception as e:
        logging.error(f"Error during prediction: {str(e)}")
        return jsonify({"error": str(e)}), 500