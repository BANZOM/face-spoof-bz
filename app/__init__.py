import logging
from flask import Flask
from .config import config

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    
    from services.anti_spoof_service import AntiSpoofService
    app.anti_spoof_service = AntiSpoofService(
        model_dir=app.config['MODEL_DIR'],
        device_id=app.config['DEVICE_ID']
    )
    with app.app_context():
        from .routes import main_bp
        app.register_blueprint(main_bp)
    
    return app