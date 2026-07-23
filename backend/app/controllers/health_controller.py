import os
from flask import Blueprint, jsonify, current_app
from sqlalchemy import text
import redis

from app.extensions import db

health_bp = Blueprint("health", __name__, url_prefix="/api/v1/health")

@health_bp.route("", methods=["GET"])
def simple_health_check():
    """Simple ping-pong health check route for container monitors."""
    return jsonify({
        "success": True,
        "message": "E-Rakshak API server is running."
    }), 200


@health_bp.route("/details", methods=["GET"])
def detailed_health_check():
    """Validates connectivity to PostgreSQL, Redis, and checks storage writeable flags."""
    health_status = {
        "database": "unknown",
        "redis": "unknown",
        "storage": "unknown",
        "system": "healthy"
    }
    
    # 1. Test PostgreSQL database connection
    try:
        db.session.execute(text("SELECT 1"))
        health_status["database"] = "healthy"
    except Exception as e:
        current_app.logger.error(f"Health check PostgreSQL connection failure: {str(e)}")
        health_status["database"] = "unhealthy"
        health_status["system"] = "unhealthy"
        
    # 2. Test Redis connection
    try:
        redis_client = redis.from_url(current_app.config["REDIS_URL"], socket_timeout=2)
        redis_client.ping()
        health_status["redis"] = "healthy"
    except Exception as e:
        current_app.logger.error(f"Health check Redis broker connection failure: {str(e)}")
        health_status["redis"] = "unhealthy"
        health_status["system"] = "unhealthy"
        
    # 3. Test uploads folder storage
    try:
        upload_path = current_app.config["UPLOAD_FOLDER"]
        # Try writing a temporary dummy file to confirm write access
        test_file = os.path.join(upload_path, ".write_test")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        health_status["storage"] = "healthy"
    except Exception as e:
        current_app.logger.error(f"Health check uploads directory write failure: {str(e)}")
        health_status["storage"] = "unhealthy"
        health_status["system"] = "unhealthy"

    # Return status and appropriate code
    status_code = 200 if health_status["system"] == "healthy" else 503
    return jsonify({
        "success": health_status["system"] == "healthy",
        "data": health_status,
        "message": "Detailed health check completed."
    }), status_code
