from datetime import datetime
from src.models import db

class Analysis(db.Model):
    """Model for storing analysis results"""
    
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    topics = db.Column(db.JSON, nullable=True)
    analysis_results = db.Column(db.JSON, nullable=True)
    error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    sources = db.Column(db.JSON, nullable=True)
    region = db.Column(db.String(100), nullable=True)
    date_range_start = db.Column(db.DateTime, nullable=True)
    date_range_end = db.Column(db.DateTime, nullable=True)
    raw_data = db.Column(db.JSON, nullable=True)
    
    # Define relationships
    reports = db.relationship('Report', backref='analysis', lazy=True, cascade="all, delete-orphan")
