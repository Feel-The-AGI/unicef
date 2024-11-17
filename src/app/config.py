import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLITE_DATABASE_URI', 'sqlite:///unicef_api.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # API Versioning
    API_VERSION = '1.0'
    
    # Testing
    TESTING = os.getenv('TESTING', 'False').lower() == 'true'
