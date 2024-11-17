from typing import Dict, Optional

def validate_source_params(params: Dict) -> Optional[str]:
    """Validate data source parameters"""
    if not params:
        return "No parameters provided"
        
    if 'topics' in params and not isinstance(params['topics'], (list, str)):
        return "Topics must be a list or comma-separated string"
        
    if 'region' in params and not isinstance(params['region'], str):
        return "Region must be a string"
        
    return None

def validate_analysis_params(params: Dict) -> Optional[str]:
    """Validate analysis parameters"""
    if not params:
        return "No parameters provided"
        
    required = ['sources', 'topics']
    missing = [field for field in required if field not in params]
    if missing:
        return f"Missing required fields: {', '.join(missing)}"
        
    if not isinstance(params['sources'], list):
        return "Sources must be a list"
        
    if not isinstance(params['topics'], list):
        return "Topics must be a list"
        
    return None

def validate_report_params(params: Dict) -> Optional[str]:
    """Validate report parameters"""
    if not params:
        return "No parameters provided"
        
    if 'analysis_id' not in params:
        return "Analysis ID is required"
        
    valid_types = ['summary', 'policy_brief', 'full_report']
    if 'type' in params and params['type'] not in valid_types:
        return f"Invalid report type. Must be one of: {', '.join(valid_types)}"
        
    valid_formats = ['pdf', 'json', 'html']
    if 'format' in params and params['format'] not in valid_formats:
        return f"Invalid format. Must be one of: {', '.join(valid_formats)}"
        
    return None

def validate_policy_brief_params(params: Dict) -> Optional[str]:
    """Validate policy brief parameters"""
    if not params:
        return "No parameters provided"
        
    if 'report_id' not in params:
        return "Report ID is required"
        
    valid_audiences = ['policymakers', 'stakeholders', 'public', 'technical']
    if 'target_audience' in params and params['target_audience'] not in valid_audiences:
        return f"Invalid target audience. Must be one of: {', '.join(valid_audiences)}"
        
    return None
