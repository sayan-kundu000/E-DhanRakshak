import os
from app import create_app
from app.extensions import celery_app

# Create Flask application to configure and bind celery settings
flask_app = create_app(os.environ.get("FLASK_ENV", "development"))
