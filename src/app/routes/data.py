from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from src.services.data_service import DataService
from src.utils.validators import validate_source_params
from datetime import datetime
import uuid

bp = Blueprint('data', __name__, url_prefix='/api/sources')

data_service = DataService()

@bp.before_request
def before_request():
    """Ensure request has required headers"""
    if 'X-Request-ID' not in request.headers:
        request.environ['HTTP_X_REQUEST_ID'] = str(uuid.uuid4())

def create_response(status="success", data=None, message=None, error=None):
    """Create standardized response"""
    response = {
        "status": status,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "version": current_app.config['API_VERSION'],
            "request_id": request.headers.get('X-Request-ID')
        }
    }
    
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    if error:
        response["error"] = error
        
    return jsonify(response)

@bp.route('/<source_id>/data', methods=['GET'])
@login_required
def fetch_source_data(source_id):
    """Fetch data from specific source"""
    try:
        params = request.args.to_dict()
        validation_error = validate_source_params(params)
        if validation_error:
            return create_response(
                status="error",
                error={
                    "code": "INVALID_PARAMETERS",
                    "message": validation_error
                }
            ), 400
            
        # Fetch data
        data = data_service.get_data(
            sources=[source_id],
            topics=params.get('topics', '').split(','),
            region=params.get('region', 'GHA'),
            start_date=params.get('start_date'),
            end_date=params.get('end_date'),
            indicators=params.get('indicators', '').split(',') if params.get('indicators') else None
        )
        
        return create_response(
            data=data,
            message=f"Successfully fetched data from {source_id}"
        ), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching data from {source_id}: {str(e)}")
        return create_response(
            status="error",
            error={
                "code": "DATA_FETCH_ERROR",
                "message": "Failed to fetch source data",
                "details": str(e)
            }
        ), 500

@bp.route('', methods=['GET'])
@login_required
def list_sources():
    """List all available data sources"""
    try:
        sources = data_service.get_available_sources()
        return create_response(
            data=sources,
            message="Successfully retrieved data sources"
        ), 200
    except Exception as e:
        current_app.logger.error(f"Error listing sources: {str(e)}")
        return create_response(
            status="error",
            error={
                "code": "SOURCE_LIST_ERROR",
                "message": "Failed to retrieve data sources",
                "details": str(e)
            }
        ), 500
