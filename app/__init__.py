from flask import Flask
from app.config import load_configurations, configure_logging
from app.services.filter_service import main as filter_main
from app.services.product_service import fetch_and_categorize_products
from app.utils.sse import register_sse_endpoint
from .views import webhook_blueprint
from .crud import crud_blueprint
from .auth import auth_bp
from .insights import insights_blueprint
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
    app.register_blueprint(insights_blueprint) 
    
    # Lazy load heavy operations - move to background or first request
    # This prevents blocking the main thread during startup
    try:
        # Only load if not already loaded
        if not hasattr(app, 'products_loaded'):
            app.logger.info("Loading products in background...")
            fetch_and_categorize_products()
            app.products_loaded = True
            
        if not hasattr(app, 'filter_loaded'):
            app.logger.info("Loading filter service in background...")
            filter_main()
            app.filter_loaded = True
    except Exception as e:
        app.logger.error(f"Error during background loading: {e}")
        # Continue app startup even if background loading fails

    return app
