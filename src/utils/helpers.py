from datetime import datetime
from typing import Dict, Any
import json

def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO format"""
    return dt.isoformat() if dt else None

def sanitize_json(data: Dict) -> Dict:
    """Ensure all values in a dict are JSON serializable"""
    def sanitize_value(v: Any) -> Any:
        if isinstance(v, datetime):
            return format_datetime(v)
        elif isinstance(v, dict):
            return sanitize_json(v)
        elif isinstance(v, list):
            return [sanitize_value(x) for x in v]
        return v
    
    return {k: sanitize_value(v) for k, v in data.items()}

def create_error_response(code: str, message: str, details: Any = None) -> Dict:
    """Create standardized error response"""
    error = {
        "code": code,
        "message": message
    }
    if details:
        error["details"] = details
    return error

def parse_date_range(start: str, end: str = None) -> Dict:
    """Parse and validate date range"""
    try:
        start_date = datetime.fromisoformat(start)
        end_date = datetime.fromisoformat(end) if end else datetime.now()
        
        if start_date > end_date:
            raise ValueError("Start date must be before end date")
            
        return {
            "start": start_date,
            "end": end_date
        }
    except Exception as e:
        raise ValueError(f"Invalid date format: {str(e)}")
