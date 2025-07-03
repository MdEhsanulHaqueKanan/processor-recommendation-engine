# app/__init__.py
from flask import Flask
from config import Config

def create_app(config_class=Config):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Import and register the blueprint from the routes module
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app