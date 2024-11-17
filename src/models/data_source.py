from datetime import datetime
from src.models import db

class DataSource(db.Model):
    """Model for tracking data sources and their metadata"""
    
    __tablename__ = 'data_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # UNICEF, WHO, WORLDBANK
    url = db.Column(db.String(500))
    status = db.Column(db.String(20), default='active')  # active, inactive, error
    last_fetch = db.Column(db.DateTime)
    source_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
