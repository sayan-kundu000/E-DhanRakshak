import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environmental variables from .env file if it exists
load_dotenv()

class Config:
    """Base Configuration class containing universal system settings."""
    DEBUG = False
    TESTING = False
    
    # Core Security Key
    SECRET_KEY = os.environ.get("SECRET_KEY", "default-insecure-secret-key-change-it-in-prod")
    
    # Database Settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", 
        "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(__file__)), "app.db")
    )
    
    # JWT Settings
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "default-insecure-jwt-key-change-it")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.environ.get("JWT_ACCESS_EXPIRES_MINS", 15)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get("JWT_REFRESH_EXPIRES_DAYS", 7)))
    JWT_ERROR_MESSAGE_KEY = "message"
    
    # Redis & Task Queue Config
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", REDIS_URL)
    
    # Rate Limiting Storage
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URL", REDIS_URL)
    
    # File Storage Settings
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER", 
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "uploads")
    )
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH_BYTES", 5 * 1024 * 1024))  # 5MB Default
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf", "doc", "docx"}
    
    # CORS Origins list
    cors_allowed = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
    CORS_ORIGINS = [origin.strip() for origin in cors_allowed.split(",")]


class DevelopmentConfig(Config):
    """Configuration options used for local development sessions."""
    DEBUG = True
    # Rate Limiting can be turned off in development if needed
    RATELIMIT_ENABLED = os.environ.get("RATELIMIT_ENABLED", "True").lower() == "true"


class TestingConfig(Config):
    """Configuration overrides loaded by pytest execution threads."""
    TESTING = True
    DEBUG = True
    # Override DB to use a temporary in-memory database configuration or test specific database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", 
        "sqlite:///:memory:"
    )
    RATELIMIT_ENABLED = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)  # Quick expiry for authentication tests
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=10)


class ProductionConfig(Config):
    """Production deployment parameters forcing security settings."""
    # Ensure debug is disabled
    DEBUG = False
    TESTING = False
    
    # Enforce strict production secret checks
    @classmethod
    def validate_secrets(cls):
        """Raises ValueError if default insecure secrets are left unconfigured in production."""
        if cls.SECRET_KEY == "default-insecure-secret-key-change-it-in-prod":
            raise ValueError("SECRET_KEY environment variable is missing in ProductionConfig!")
        if cls.JWT_SECRET_KEY == "default-insecure-jwt-key-change-it":
            raise ValueError("JWT_SECRET_KEY environment variable is missing in ProductionConfig!")
        if cls.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
            raise ValueError("ProductionConfig cannot be deployed using an SQLite database!")


# Map configuration classes
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}
