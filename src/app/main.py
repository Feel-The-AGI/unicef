from flask import Flask
from .config import Config
from src.models import db
from src.utils.env_setup import init_environment
from flask_login import LoginManager

def create_app():
    # Initialize environment
    init_environment()
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        from src.models import User
        return db.session.get(User, int(user_id))
    
    # Register blueprints
    from src.app.routes import auth, data, analysis, reports, policy
    app.register_blueprint(auth.bp)
    app.register_blueprint(data.bp)
    app.register_blueprint(analysis.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(policy.bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
