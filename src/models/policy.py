from datetime import datetime
from src.models import db

class PolicyBrief(db.Model):
    """Model for storing policy briefs"""
    
    __tablename__ = 'policy_briefs'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    executive_summary = db.Column(db.Text)
    key_findings = db.Column(db.JSON)
    recommendations = db.Column(db.JSON)
    target_audience = db.Column(db.String(50))
    resource_requirements = db.Column(db.JSON)
    impact_assessment = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
