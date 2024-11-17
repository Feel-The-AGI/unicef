from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from src.services.gemini_service import GeminiService
from src.models import PolicyBrief, Report, Analysis, db
from src.utils.validators import validate_policy_brief_params
from datetime import datetime
import uuid

bp = Blueprint('policy', __name__, url_prefix='/api/briefs')

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
    """Ensure request has required headers"""
    if not request.headers.get('X-Request-ID'):
        request.headers['X-Request-ID'] = str(uuid.uuid4())

@bp.route('', methods=['POST'])
@login_required
async def generate_policy_brief():
    """Generate new policy brief"""
    try:
        data = request.get_json()
        validation_error = validate_policy_brief_params(data)
        if validation_error:
            return create_response(
                status="error",
                error={
                    "code": "INVALID_PARAMETERS",
                    "message": validation_error
                }
            ), 400
            
        # Get report
        report = db.session.get(Report, data['report_id'])
        if not report:
            return create_response(
                status="error",
                error={
                    "code": "REPORT_NOT_FOUND",
                    "message": "Report not found"
                }
            ), 404
            
        # Check report ownership
        if report.user_id != current_user.id:
            return create_response(
                status="error",
                error={
                    "code": "UNAUTHORIZED",
                    "message": "Not authorized to access this report"
                }
            ), 403
            
        # Check if policy brief already exists
        if PolicyBrief.query.filter_by(report_id=report.id).first():
            return create_response(
                status="error",
                error={
                    "code": "BRIEF_EXISTS",
                    "message": "Policy brief already exists for this report"
                }
            ), 409
            
        # Get analysis results
        analysis = db.session.get(Analysis, report.analysis_id)
        if not analysis:
            return create_response(
                status="error",
                error={
                    "code": "ANALYSIS_NOT_FOUND",
                    "message": "Analysis not found"
                }
            ), 404
            
        # Generate policy brief using Gemini
        brief_content = await gemini_service.generate_policy_brief(analysis.analysis_results)
        
        # Create policy brief record
        policy_brief = PolicyBrief(
            report_id=report.id,
            executive_summary=brief_content['executive_summary'],
            key_findings=brief_content['key_findings'],
            recommendations=brief_content['recommendations'],
            target_audience=data.get('target_audience', 'policymakers'),
            resource_requirements=brief_content['resource_requirements'],
            impact_assessment=brief_content['impact_assessment']
        )
        
        db.session.add(policy_brief)
        db.session.commit()
        
        return create_response(
            data={
                'brief_id': policy_brief.id,
                'content': brief_content
            },
            message="Policy brief generated successfully"
        ), 201
        
    except Exception as e:
        current_app.logger.error(f"Policy brief generation error: {str(e)}")
        return create_response(
            status="error",
            error={
                "code": "GENERATION_ERROR",
                "message": "Failed to generate policy brief",
                "details": str(e)
            }
        ), 500

@bp.route('/<int:brief_id>', methods=['GET'])
@login_required
def get_policy_brief(brief_id):
    """Get specific policy brief"""
    try:
        brief = db.session.get(PolicyBrief, brief_id)
        if not brief:
            return create_response(
                status="error",
                error={
                    "code": "BRIEF_NOT_FOUND",
                    "message": f"Policy brief {brief_id} not found"
                }
            ), 404
            
        # Check ownership through report
        report = db.session.get(Report, brief.report_id)
        if report.user_id != current_user.id:
            return create_response(
                status="error",
                error={
                    "code": "UNAUTHORIZED",
                    "message": "Not authorized to access this policy brief"
                }
            ), 403
            
        return create_response(
            data={
                'id': brief.id,
                'report_id': brief.report_id,
                'executive_summary': brief.executive_summary,
                'key_findings': brief.key_findings,
                'recommendations': brief.recommendations,
                'target_audience': brief.target_audience,
                'resource_requirements': brief.resource_requirements,
                'impact_assessment': brief.impact_assessment,
                'created_at': brief.created_at.isoformat(),
                'updated_at': brief.updated_at.isoformat() if brief.updated_at else None
            },
            message="Policy brief retrieved successfully"
        ), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving policy brief {brief_id}: {str(e)}")
        return create_response(
            status="error",
            error={
                "code": "RETRIEVAL_ERROR",
                "message": "Failed to retrieve policy brief",
                "details": str(e)
            }
        ), 500

@bp.route('/<int:brief_id>', methods=['PUT'])
@login_required
def update_policy_brief(brief_id):
    """Update policy brief"""
    try:
        brief = db.session.get(PolicyBrief, brief_id)
        if not brief:
            return create_response(
                status="error",
                error={
                    "code": "BRIEF_NOT_FOUND",
                    "message": f"Policy brief {brief_id} not found"
                }
            ), 404
            
        # Check ownership through report
        report = db.session.get(Report, brief.report_id)
        if report.user_id != current_user.id:
            return create_response(
                status="error",
                error={
                    "code": "UNAUTHORIZED",
                    "message": "Not authorized to update this policy brief"
                }
            ), 403
            
        data = request.get_json()
        validation_error = validate_policy_brief_params(data)
        if validation_error:
            return create_response(
                status="error",
                error={
                    "code": "INVALID_PARAMETERS",
                    "message": validation_error
                }
            ), 400
            
        # Update allowed fields
        brief.target_audience = data.get('target_audience', brief.target_audience)
        if 'resource_requirements' in data:
            brief.resource_requirements.update(data['resource_requirements'])
        if 'impact_assessment' in data:
            brief.impact_assessment.update(data['impact_assessment'])
            
        brief.updated_at = datetime.utcnow()
        db.session.commit()
        
        return create_response(
            data={
                'id': brief.id,
                'target_audience': brief.target_audience,
                'resource_requirements': brief.resource_requirements,
                'impact_assessment': brief.impact_assessment
            },
            message="Policy brief updated successfully"
        ), 200
        
    except Exception as e:
        current_app.logger.error(f"Error updating policy brief {brief_id}: {str(e)}")
        return create_response(
            status="error",
            error={
                "code": "UPDATE_ERROR",
                "message": "Failed to update policy brief",
                "details": str(e)
            }
        ), 500

@bp.route('/report/<int:report_id>', methods=['GET'])
@login_required
def get_report_brief(report_id):
    """Get policy brief for specific report"""
    try:
        # Check report ownership
        report = db.session.get(Report, report_id)
        if not report:
            return create_response(
                status="error",
                error={
                    "code": "REPORT_NOT_FOUND",
                    "message": "Report not found"
                }
            ), 404
            
        if report.user_id != current_user.id:
            return create_response(
                status="error",
                error={
                    "code": "UNAUTHORIZED",
                    "message": "Not authorized to access this report's brief"
                }
            ), 403
            
        brief = PolicyBrief.query.filter_by(report_id=report_id).first()
        if not brief:
            return create_response(
                status="error",
                error={
                    "code": "BRIEF_NOT_FOUND",
                    "message": "No policy brief found for this report"
                }
            ), 404
            
        return create_response(
            data={
                'id': brief.id,
                'report_id': brief.report_id,
                'executive_summary': brief.executive_summary,
                'key_findings': brief.key_findings,
                'recommendations': brief.recommendations,
                'target_audience': brief.target_audience,
                'resource_requirements': brief.resource_requirements,
                'impact_assessment': brief.impact_assessment,
                'created_at': brief.created_at.isoformat(),
                'updated_at': brief.updated_at.isoformat() if brief.updated_at else None
            },
            message="Policy brief retrieved successfully"
        ), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving policy brief for report {report_id}: {str(e)}")
        return create_response(
            status="error",
            error={
                "code": "RETRIEVAL_ERROR",
                "message": "Failed to retrieve policy brief",
                "details": str(e)
            }
        ), 500
