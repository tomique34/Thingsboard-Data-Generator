import os
from flask import Flask, session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Dummy CSRF protection class that does nothing
class DummyCSRF:
    def __init__(self):
        pass
    
    def exempt(self, view):
        # This is a no-op decorator
        return view
    
    def init_app(self, app):
        pass

# Create a dummy csrf object for backward compatibility
csrf = DummyCSRF()

def create_app():
    app = Flask(__name__)
    
    # Configure application
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-me')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # DISABLE CSRF for this development app
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Thingsboard configuration
    app.config['TB_HOST'] = os.getenv('TB_HOST', 'http://localhost')
    app.config['TB_PORT'] = os.getenv('TB_PORT', '8080')
    app.config['TB_USERNAME'] = os.getenv('TB_USERNAME', 'tenant@thingsboard.org')
    app.config['TB_PASSWORD'] = os.getenv('TB_PASSWORD', 'tenant')
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app
