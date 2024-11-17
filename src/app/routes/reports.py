from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from src.services.gemini_service import GeminiService
from src.models import Report, Analysis, db
from src.utils.validators import validate_report_params
from datetime import datetime
import uuid

bp = Blueprint('reports', __name__, url_prefix='/api/reports')

gemini_service = GeminiService()

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

@bp.before_request
def before_request():
    """Ensure request has required headers and check rate limits"""
    if not request.headers.get('X-Request-ID'):
        request.headers['X-Request-ID'] = str(uuid.uuid4())
    
    # Check concurrent report generation limit
    active_reports = Report.query.filter_by(
        user_id=current_user.id,
        status='generating'
    ).count()
    
    if active_reports >= 5:  # From DEV.md rate limits
        return create_response(
            status="error",
            error={
                "code": "CONCURRENT_LIMIT_EXCEEDED",
                "message": "Maximum concurrent report generations limit reached"
            }
        ), 429

@bp.route('', methods=['POST'])
@login_required
async def generate_report():
    """Generate new report"""
    try:
        data = request.get_json()
        validation_error = validate_report_params(data)
        if validation_error:
            return create_response(
                status="error",
                error={
                    "code": "INVALID_PARAMETERS",
                    "message": validation_error
                }
            ), 400
            
        # Get analysis
        analysis = db.session.get(Analysis, data['analysis_id'])
        if not analysis:
            return create_response(
                status="error",
                error={
                    "code": "ANALYSIS_NOT_FOUND",
                    "message": "Analysis not found"
                }
            ), 404
            
        # Check analysis ownership
        if analysis.user_id != current_user.id:
            return create_response(
                status="error",
                error={
                    "code": "UNAUTHORIZED",
                    "message": "Not authorized to access this analysis"
                }
            ), 403
            
        # Create report record
        report = Report(
            analysis_id=analysis.id,
            user_id=current_user.id,
            type=data.get('type', 'summary'),
            format=data.get('format', 'json'),
            status='generating',
            report_metadata={
                'requested_at': datetime.utcnow().isoformat(),
                'report_type': data.get('type', 'summary'),
                'format': data.get('format', 'json')
            }
        )
        db.session.add(report)
        db.session.commit()
        
        # Generate report content based on type
        if report.type == 'policy_brief':
            content = await gemini_service.generate_policy_brief(analysis.analysis_results)
        else:
            content = {
                'summary': analysis.analysis_results.get('key_findings', []),
                'details': analysis.analysis_results,
                'metadata': {
                    'analysis_id': analysis.id,
                    'generated_at': datetime.utcnow().isoformat(),
                    'data_sources': analysis.sources,
                    'topics': analysis.topics
                }
            }
        
        # Update report with content
        report.content = content
        report.status = 'completed'
        report.updated_at = datetime.utcnow()
        db.session.commit()
        
        return create_response(
            data={
                'report_id': report.id,
                'status': report.status,
                'content': report.content
            },
            message="Report generated successfully"
        ), 201
        
    except Exception as e:
        current_app.logger.error(f"Report generation error: {str(e)}")
        if 'report' in locals():
            report.status = 'failed'
            report.report_metadata['error'] = str(e)
            report.updated_at = datetime.utcnow()
            db.session.commit()
            
        return create_response(
            status="error",
            error={
                "code": "REPORT_GENERATION_ERROR",
                "message": "Failed to generate report",
                "details": str(e)
            }
        ), 500

@bp.route('/<int:report_id>', methods=['GET'])
@login_required
def get_report(report_id):
    """Get specific report"""
    try:
        report = db.session.get(Report, report_id)
        if not report:
            return create_response(
                status="error",
                error={
                    "code": "REPORT_NOT_FOUND",
                    "message": f"Report {report_id} not found"
                }
            ), 404
            
        # Check ownership
        if report.user_id != current_user.id:
            return create_response(
                status="error",
                error={
                    "code": "UNAUTHORIZED",
                    "message": "Not authorized to access this report"
                }
            ), 403
            
        # Convert metadata to serializable format
        metadata = dict(report.report_metadata) if report.report_metadata else {}
            
        return create_response(
            data={
                'id': report.id,
                'analysis_id': report.analysis_id,
                'type': report.type,
                'format': report.format,
                'content': report.content,
                'status': report.status,
                'created_at': report.created_at.isoformat(),
                'updated_at': report.updated_at.isoformat() if report.updated_at else None,
                'metadata': metadata
            },
            message="Report retrieved successfully"
        ), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving report {report_id}: {str(e)}")
        return create_response(
            status="error",
            error={
                "code": "RETRIEVAL_ERROR",
                "message": "Failed to retrieve report",
                "details": str(e)
            }
        ), 500

@bp.route('/user/<int:user_id>', methods=['GET'])
@login_required
def get_user_reports(user_id):
    """Get user's reports"""
    try:
        # Check authorization
        if user_id != current_user.id:
            return create_response(
                status="error",
                error={
                    "code": "UNAUTHORIZED",
                    "message": "Not authorized to access these reports"
                }
            ), 403
            
        reports = Report.query.filter_by(user_id=user_id).all()
        
        return create_response(
            data=[{
                'id': report.id,
                'analysis_id': report.analysis_id,
                'type': report.type,
                'format': report.format,
                'status': report.status,
                'created_at': report.created_at.isoformat(),
                'updated_at': report.updated_at.isoformat() if report.updated_at else None
            } for report in reports],
            message=f"Retrieved {len(reports)} reports"
        ), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving reports for user {user_id}: {str(e)}")
        return create_response(
            status="error",
            error={
                "code": "RETRIEVAL_ERROR",
                "message": "Failed to retrieve reports",
                "details": str(e)
            }
        ), 500

@bp.route('/<int:report_id>', methods=['PUT'])
@login_required
def update_report(report_id):
    """Update report"""
    try:
        report = db.session.get(Report, report_id)
        if not report:
            return create_response(
                status="error",
                error={
                    "code": "REPORT_NOT_FOUND",
                    "message": f"Report {report_id} not found"
                }
            ), 404
            
        # Check ownership
        if report.user_id != current_user.id:
            return create_response(
                status="error",
                error={
                    "code": "UNAUTHORIZED",
                    "message": "Not authorized to update this report"
                }
            ), 403
            
        data = request.get_json()
        validation_error = validate_report_params(data)
        if validation_error:
            return create_response(
                status="error",
                error={
                    "code": "INVALID_PARAMETERS",
                    "message": validation_error
                }
            ), 400
            
        # Update allowed fields
        report.type = data.get('type', report.type)
        report.format = data.get('format', report.format)
        report.metadata.update(data.get('metadata', {}))
        report.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return create_response(
            data={
                'id': report.id,
                'type': report.type,
                'format': report.format,
                'metadata': report.metadata
            },
            message="Report updated successfully"
        ), 200
        
    except Exception as e:
        current_app.logger.error(f"Error updating report {report_id}: {str(e)}")
        return create_response(
            status="error",
            error={
                "code": "UPDATE_ERROR",
                "message": "Failed to update report",
                "details": str(e)
            }
        ), 500

@bp.route('/<int:report_id>', methods=['DELETE'])
@login_required
def delete_report(report_id):
    """Delete report"""
    try:
        report = db.session.get(Report, report_id)
        if not report:
            return create_response(
                status="error",
                error={
                    "code": "REPORT_NOT_FOUND",
                    "message": f"Report {report_id} not found"
                }
            ), 404
            
        # Check ownership
        if report.user_id != current_user.id:
            return create_response(
                status="error",
                error={
                    "code": "UNAUTHORIZED",
                    "message": "Not authorized to delete this report"
                }
            ), 403
            
        db.session.delete(report)
        db.session.commit()
        
        return create_response(
            message="Report deleted successfully"
        ), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting report {report_id}: {str(e)}")
        return create_response(
            status="error",
            error={
                "code": "DELETE_ERROR",
                "message": "Failed to delete report",
                "details": str(e)
            }
        ), 500
