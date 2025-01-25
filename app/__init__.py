from flask import Flask
from .config import config
import logging
from logging.handlers import RotatingFileHandler

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    
    if not app.debug:
        file_handler = RotatingFileHandler(
            'app.log',
            maxBytes=1024 * 1024 * 10,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.INFO)

        app.logger.info('Application startup')

    from services.anti_spoof_service import AntiSpoofService
    app.anti_spoof_service = AntiSpoofService(
        model_dir=app.config['MODEL_DIR'],
        device_id=app.config['DEVICE_ID']
    )
    
    with app.app_context():
        from .routes import main_bp
        app.register_blueprint(main_bp)
    
    return app