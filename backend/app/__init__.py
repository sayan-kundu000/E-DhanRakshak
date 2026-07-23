import os
import time
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, g, request, jsonify

from config import config_by_name
from app.extensions import db, bcrypt, jwt, cors, ma, limiter, celery_app

def configure_logging(app):
    """Sets up Python console and rotating file log output handlers."""
    app.logger.handlers.clear()
    
    log_format = "[%(asctime)s] %(levelname)s in %(module)s (%(threadName)s): %(message)s"
    formatter = logging.Formatter(log_format)
    
    # Stream (stdout) logging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    app.logger.addHandler(console_handler)
    
    # Enable file logging in development and production
    if not app.testing:
        log_dir = os.path.join(app.root_path, "..", "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "app.log"),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
    app.logger.setLevel(logging.INFO)


def configure_celery(app):
    """Integrates Celery with Flask application contexts."""
    celery_app.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        task_ignore_result=True
    )
    
    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
                
    celery_app.Task = ContextTask


def register_middleware(app):
    """Hooks global HTTP filters and request/response interceptors."""
    
    @app.before_request
    def start_timer():
        g.start_time = time.time()
        
    @app.after_request
    def add_security_headers_and_log(response):
        # Apply standard secure HTTP headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Track time elapsed
        if hasattr(g, "start_time"):
            duration = time.time() - g.start_time
            app.logger.info(
                f"Path: {request.path} | Method: {request.method} | "
                f"Status: {response.status_code} | Timing: {duration:.4f}s | "
                f"IP: {request.remote_addr}"
            )
        return response


def create_app(config_name="development"):
    """Application Factory creating, configuring, and returning the Flask app."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_by_name[config_name])
    
    # If in Production, validate secrets are present
    if config_name == "production":
        from config import ProductionConfig
        ProductionConfig.validate_secrets()
        
    # Configure logs
    configure_logging(app)
    from app.utils.logging_config import configure_domain_logging
    configure_domain_logging(app)
    
    # Load all models for db.create_all() detection
    from app import models
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)
    
    # Configure CORS mapping
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    
    # Configure Rate Limiter backend dynamically
    if config_name != "testing":
        limiter.init_app(app)
        limiter.storage_uri = app.config["RATELIMIT_STORAGE_URI"]
        
    # Configure Celery Broker connection parameters
    configure_celery(app)
    
    # Setup upload directory
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])
        
    # Register core global middleware hooks
    register_middleware(app)
    
    # Register exception handlers
    from app.middleware.error_handler import register_error_handlers
    register_error_handlers(app)
    
    # Register controller blueprints
    from app.controllers.health_controller import health_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.incident_controller import incident_bp
    from app.controllers.notification_controller import notification_bp
    from app.controllers.setting_controller import setting_bp
    from app.controllers.file_controller import file_bp
    from app.controllers.report_controller import report_bp
    from app.controllers.search_controller import search_bp
    from app.controllers.analytics_controller import analytics_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(incident_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(setting_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(analytics_bp)
    
    return app
