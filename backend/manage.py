import os
from app import create_app

# Fetch execution environment name or default to development
config_name = os.environ.get("FLASK_ENV", "development")
app = create_app(config_name)

if __name__ == "__main__":
    # Pull dynamic ports (e.g. for Render compliance) or bind to local port 5000
    bind_port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=bind_port)
