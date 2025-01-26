import time
import logging
from flask import Blueprint, current_app, request, jsonify
import cv2
import numpy as np
import os
import logging
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

    current_app.logger.info(f"Received request at /api/v1/predict from {request.remote_addr}")
    
    if 'image' not in request.files:
        current_app.logger.error("No image provided in request")
        return jsonify({"error": "No image provided"}), 400
        
    file = request.files['image']
    threshold = float(request.form.get('threshold', 0.5))
    
    current_app.logger.debug(f"Processing file: {file.filename}, threshold: {threshold}")

    if file.filename == '':
        current_app.logger.warning("Received empty filename")
        return jsonify({"error": "Empty filename"}), 400
        
    if not allowed_file(file.filename):
        current_app.logger.warning(f"Invalid file type attempted: {file.filename}")
        return jsonify({"error": "Invalid file type"}), 400

    try:
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        current_app.logger.info(f"Image processing started ({image.shape[1]}x{image.shape[0]})")
        
        service = current_app.anti_spoof_service
        is_real, score, result_img, time_taken = service.predict(image, threshold)

        current_app.logger.info(
            f"Prediction result - Real: {is_real}, Score: {score:.2f}, "
            f"Threshold: {threshold}, Time: {time_taken}s"
        )

        if not is_real:
            filename = os.path.join(os.getenv("SPOOF_DIR", "spoofs"), f"{int(time.time())}.jpeg")
            cv2.imwrite(filename, result_img)
            current_app.logger.warning(f"Spoof detected! Image saved to {filename}")

        return jsonify({
            "is_real": is_real,
            "score": float(score),
            "threshold": float(threshold),
            "time_taken": time_taken,
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500