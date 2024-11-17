import os
from dotenv import load_dotenv

def init_environment():
    """Initialize environment variables"""
    load_dotenv()
    
    required_vars = [
        'GOOGLE_API_KEY',
        'SQLITE_DATABASE_URI',
        'SECRET_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

    return {var: os.getenv(var) for var in required_vars} 