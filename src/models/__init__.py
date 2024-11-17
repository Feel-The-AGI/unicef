from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models after db is defined
from src.models.user import User
from src.models.data_source import DataSource
from src.models.analysis import Analysis
from src.models.report import Report
from src.models.policy import PolicyBrief

# Register models with SQLAlchemy
__all__ = ['db', 'User', 'DataSource', 'Analysis', 'Report', 'PolicyBrief']
