import pytest
from datetime import datetime
from src.models import User, Analysis, Report, PolicyBrief, db

@pytest.fixture
def test_data():
    """Test data for all models"""
    return {
        'user': {
            'username': "testuser",
            'email': "test@example.com",
            'organization': "Test Org",
            'password': "password123"
        },
        'analysis': {
            'sources': ["UNICEF", "WHO"],
            'topics': ["health", "education"],
            'region': "GHA",
            'status': "completed",
            'analysis_results': {
                "key_findings": ["Finding 1", "Finding 2"],
                "trends": ["Trend 1", "Trend 2"]
            }
        },
        'report': {
            'type': "summary",
            'format': "json",
            'content': {
                "summary": ["Summary point 1", "Summary point 2"],
                "details": {"section1": "Content 1"}
            }
        },
        'policy_brief': {
            'executive_summary': "Test summary",
            'key_findings': ["Finding 1", "Finding 2"],
            'recommendations': [
                {
                    "action": "Action 1",
                    "rationale": "Rationale 1"
                }
            ],
            'target_audience': "policymakers",
            'resource_requirements': {
                "financial": "100000 USD",
                "human": "5 staff members"
            },
            'impact_assessment': {
                "short_term": ["Impact 1"],
                "long_term": ["Impact 2"]
            }
        }
    }

class TestUser:
    def test_create_user(self, app, test_data):
        """Test user creation"""
        with app.app_context():
            user = User(
                username=test_data['user']['username'],
                email=test_data['user']['email'],
                organization=test_data['user']['organization']
            )
            user.set_password(test_data['user']['password'])
            
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.check_password(test_data['user']['password'])
            assert not user.check_password("wrongpass")
            
    def test_user_relationships(self, app, user, test_data):
        """Test user relationships"""
        with app.app_context():
            # Get fresh user instance from database
            user = db.session.get(User, user.id)
            
            # Create analysis
            analysis = Analysis(
                user_id=user.id,
                **test_data['analysis']
            )
            db.session.add(analysis)
            db.session.commit()
            
            # Create report
            report = Report(
                user_id=user.id,
                analysis_id=analysis.id,
                **test_data['report']
            )
            db.session.add(report)
            db.session.commit()
            
            # Get fresh user instance again to see new relationships
            user = db.session.get(User, user.id)
            
            # Test relationships
            assert len(user.analyses) == 1
            assert len(user.reports) == 1
            assert user.analyses[0].id == analysis.id
            assert user.reports[0].id == report.id

class TestAnalysis:
    def test_create_analysis(self, app, user, test_data):
        """Test analysis creation"""
        with app.app_context():
            analysis = Analysis(
                user_id=user.id,
                **test_data['analysis']
            )
            
            db.session.add(analysis)
            db.session.commit()
            
            assert analysis.id is not None
            assert analysis.status == "completed"
            assert analysis.user_id == user.id
            
    def test_analysis_relationships(self, app, user, test_data):
        """Test analysis relationships"""
        with app.app_context():
            # Create analysis
            analysis = Analysis(
                user_id=user.id,
                **test_data['analysis']
            )
            db.session.add(analysis)
            db.session.commit()
            
            # Create report
            report = Report(
                user_id=user.id,
                analysis_id=analysis.id,
                **test_data['report']
            )
            db.session.add(report)
            db.session.commit()
            
            # Test relationships
            assert len(analysis.reports) == 1
            assert analysis.reports[0].id == report.id
            assert analysis.user.id == user.id

class TestReport:
    def test_create_report(self, app, user, analysis, test_data):
        """Test report creation"""
        with app.app_context():
            report = Report(
                user_id=user.id,
                analysis_id=analysis.id,
                **test_data['report']
            )
            
            db.session.add(report)
            db.session.commit()
            
            assert report.id is not None
            assert report.type == "summary"
            assert report.user_id == user.id
            assert report.analysis_id == analysis.id
            
    def test_report_relationships(self, app, user, analysis, test_data):
        """Test report relationships"""
        with app.app_context():
            # Create report
            report = Report(
                user_id=user.id,
                analysis_id=analysis.id,
                **test_data['report']
            )
            db.session.add(report)
            db.session.commit()
            
            # Create policy brief
            brief = PolicyBrief(
                report_id=report.id,
                **test_data['policy_brief']
            )
            db.session.add(brief)
            db.session.commit()
            
            # Test relationships
            assert report.policy_brief.id == brief.id
            assert report.user.id == user.id
            assert report.analysis.id == analysis.id

class TestPolicyBrief:
    def test_create_policy_brief(self, app, user, analysis, test_data):
        """Test policy brief creation"""
        with app.app_context():
            # Create report first
            report = Report(
                user_id=user.id,
                analysis_id=analysis.id,
                **test_data['report']
            )
            db.session.add(report)
            db.session.commit()
            
            # Create policy brief
            brief = PolicyBrief(
                report_id=report.id,
                **test_data['policy_brief']
            )
            db.session.add(brief)
            db.session.commit()
            
            assert brief.id is not None
            assert brief.report_id == report.id
            assert brief.target_audience == "policymakers"
            
    def test_policy_brief_relationships(self, app, user, analysis, test_data):
        """Test policy brief relationships"""
        with app.app_context():
            # Create report
            report = Report(
                user_id=user.id,
                analysis_id=analysis.id,
                **test_data['report']
            )
            db.session.add(report)
            db.session.commit()
            
            # Create policy brief
            brief = PolicyBrief(
                report_id=report.id,
                **test_data['policy_brief']
            )
            db.session.add(brief)
            db.session.commit()
            
            # Test relationships
            assert brief.report.id == report.id
