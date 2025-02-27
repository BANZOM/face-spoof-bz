import os
import time
import logging
import cv2
import numpy as np
import logging
from src.anti_spoof_predict import AntiSpoofPredict
from src.generate_patches import CropImage
from src.utility import parse_model_name

class AntiSpoofService:
    def __init__(self, model_dir, device_id):
        self.logger = logging.getLogger(__name__)
        self.model_dir = model_dir
        self.device_id = device_id
        self.model_test = AntiSpoofPredict(device_id)
        self.image_cropper = CropImage()
        self._load_models()
        self.logger.info(f"AntiSpoofService initialized with {len(self.models)} models")

    def _load_models(self):
        self.models = []
        try:
            for model_name in os.listdir(self.model_dir):
                h_input, w_input, model_type, scale = parse_model_name(model_name)
                self.models.append({
                    "name": model_name,
                    "h_input": h_input,
                    "w_input": w_input,
                    "scale": scale
                })
            self.logger.debug(f"Loaded {len(self.models)} models from {self.model_dir}")
        except Exception as e:
            self.logger.error(f"Failed to load models: {str(e)}", exc_info=True)
            raise

    def predict(self, image, threshold):
        self.logger.debug(f"Starting prediction with threshold {threshold}")
        start_time = time.time()
        
        try:
            image = cv2.resize(image, (int(image.shape[0] * 3/4), image.shape[0]))
            image_bbox = self.model_test.get_bbox(image)
            prediction = np.zeros((1, 3))

            self.logger.debug(f"Processing with {len(self.models)} models")
            for model in self.models:
                param = {
                    "org_img": image,
                    "bbox": image_bbox,
                    "scale": model["scale"],
                    "out_w": model["w_input"],
                    "out_h": model["h_input"],
                    "crop": model["scale"] is not None,
                }
                img = self.image_cropper.crop(**param)
                prediction += self.model_test.predict(img, os.path.join(self.model_dir, model["name"]))

            processing_time = time.time() - start_time
            label = np.argmax(prediction)
            confidence = prediction[0][label] / 2
            
            self.logger.debug(f"Raw prediction values: {prediction}")
            self.logger.info(f"Final confidence: {confidence:.2f}, Label: {'Real' if label == 1 else 'Fake'}")

            result_img = self._generate_result_image(image, image_bbox, label, confidence)
            is_real = bool(label == 1 and confidence > threshold)
            
            return is_real, confidence, result_img, "{:.2f}".format(processing_time)


        except Exception as e:
            self.logger.error(f"Prediction failed: {str(e)}", exc_info=True)
            raise

    def _generate_result_image(self, image, bbox, label, confidence):
        color = (255, 0, 0) if label == 1 else (0, 0, 255)
        text = "Real ({:.2f})" if label == 1 else "Fake ({:.2f})"
        text = text.format(confidence)
        
        img = image.copy()
        cv2.rectangle(img, 
            (bbox[0], bbox[1]),
            (bbox[0] + bbox[2], bbox[1] + bbox[3]),
            color, 2)
        cv2.putText(img, text,
            (bbox[0], bbox[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        self.logger.debug(f"Generated result image with {label} label")
        return img