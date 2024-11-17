from datetime import datetime
from src.models import db

class Report(db.Model):
    """Model for storing generated reports"""
    
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    type = db.Column(db.String(20))  # summary, policy_brief, full_report
    format = db.Column(db.String(10))  # pdf, json, html
    status = db.Column(db.String(20), default='pending')  # pending, generating, completed, failed
    content = db.Column(db.JSON)
    report_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Define relationships
    policy_brief = db.relationship('PolicyBrief', backref='report', lazy=True, uselist=False)
