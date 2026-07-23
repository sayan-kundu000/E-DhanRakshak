import os
import logging
from logging.handlers import RotatingFileHandler

def configure_domain_logging(app):
    """Configures specific loggers for security, workflow, analytics, and api categories."""
    if app.testing:
        return  # Avoid creating log files during test runs

    log_dir = os.path.join(app.root_path, "..", "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_format = "[%(asctime)s] %(levelname)s in %(module)s (%(threadName)s): %(message)s"
    formatter = logging.Formatter(log_format)

    def _setup_logger(name, file_name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        
        handler = RotatingFileHandler(
            os.path.join(log_dir, file_name),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.propagate = False
        return logger

    # Initialize domain specific loggers
    _setup_logger("app.api", "api.log")
    _setup_logger("app.security", "security.log")
    _setup_logger("app.workflow", "workflow.log")
    _setup_logger("app.analytics", "analytics.log")
