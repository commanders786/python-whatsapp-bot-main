from flask import Flask
from app.config import load_configurations, configure_logging
from app.services.filter_service import main as filter_main
from app.services.product_service import fetch_and_categorize_products
from app.utils.sse import register_sse_endpoint
from .views import webhook_blueprint
from .crud import crud_blueprint
from .auth import auth_bp
from flask_cors import CORS




def create_app():
    app = Flask(__name__)
    # CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://emart-ui.vercel.app"]}})
    CORS(app, resources={r"/*": {"origins": "*"}})


    # Load configurations and logging settings
    load_configurations(app)
    configure_logging()
    register_sse_endpoint(app)  
    # Import and register blueprints, if any
    app.register_blueprint(webhook_blueprint)
    app.register_blueprint(crud_blueprint)
    app.register_blueprint(auth_bp) 
    fetch_and_categorize_products()
    filter_main()
    
    

    

    return app
