from flask import Flask
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint
from .crud import crud_blueprint
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Load configurations and logging settings
    load_configurations(app)
    configure_logging()

    # Import and register blueprints, if any
    app.register_blueprint(webhook_blueprint)
    app.register_blueprint(crud_blueprint)
   

    return app
