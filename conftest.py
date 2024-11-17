import os
import sys
import pytest
from datetime import datetime
from src.app.main import create_app
from src.models import db, User, Analysis, Report, PolicyBrief, DataSource

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Add at the top of the file
pytest_plugins = ["pytest_asyncio"]

@pytest.fixture
def app():
    """Create application for testing"""
    os.environ['TESTING'] = 'True'
    os.environ['SQLITE_DATABASE_URI'] = 'sqlite:///:memory:'
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-key',
        'LOGIN_DISABLED': True  # Disable login requirement for some tests
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def user(app):
    """Create test user"""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            organization="Test Org"
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        
        # Query the user back using Session.get()
        user = db.session.get(User, user.id)
        return user

@pytest.fixture
def analysis(app, user):
    """Create test analysis"""
    with app.app_context():
        # Query user using Session.get()
        user = db.session.get(User, user.id)
        
        analysis = Analysis(
            user_id=user.id,
            sources=["UNICEF", "WHO"],
            topics=["health", "education"],
            region="GHA",
            date_range_start=datetime.fromisoformat("2023-01-01"),
            date_range_end=datetime.fromisoformat("2024-01-01"),
            status="completed",
            analysis_results={
                "key_findings": ["Finding 1", "Finding 2"],
                "trends": ["Trend 1", "Trend 2"]
            }
        )
        db.session.add(analysis)
        db.session.commit()
        
        # Query back using Session.get()
        analysis = db.session.get(Analysis, analysis.id)
        return analysis

@pytest.fixture
def report(app, user, analysis):
    """Create test report"""
    with app.app_context():
        # Query dependencies using Session.get()
        user = db.session.get(User, user.id)
        analysis = db.session.get(Analysis, analysis.id)
        
        report = Report(
            user_id=user.id,
            analysis_id=analysis.id,
            type="summary",
            format="json",
            content={
                "summary": ["Summary point 1", "Summary point 2"],
                "details": {"section1": "Content 1"}
            },
            report_metadata={
                "generated_at": datetime.utcnow().isoformat()
            }
        )
        db.session.add(report)
        db.session.commit()
        
        # Query back using Session.get()
        report = db.session.get(Report, report.id)
        return report

@pytest.fixture
def policy_brief(app, report):
    """Create test policy brief"""
    with app.app_context():
        # Query report using Session.get()
        report = db.session.get(Report, report.id)
        
        brief = PolicyBrief(
            report_id=report.id,
            executive_summary="Test summary",
            key_findings=["Finding 1", "Finding 2"],
            recommendations=[
                {
                    "action": "Action 1",
                    "rationale": "Rationale 1"
                }
            ],
            target_audience="policymakers",
            resource_requirements={
                "financial": "100000 USD",
                "human": "5 staff members"
            },
            impact_assessment={
                "short_term": ["Impact 1"],
                "long_term": ["Impact 2"]
            }
        )
        db.session.add(brief)
        db.session.commit()
        
        # Query back using Session.get()
        brief = db.session.get(PolicyBrief, brief.id)
        return brief

@pytest.fixture
def data_sources(app):
    """Create test data sources"""
    with app.app_context():
        sources = [
            DataSource(
                name='UNICEF Data API',
                type='UNICEF',
                url='https://data.unicef.org/api/v2',
                status='active',
                source_metadata={
                    'supported_indicators': ['health', 'education']
                }
            ),
            DataSource(
                name='WHO Global Health Observatory',
                type='WHO',
                url='https://ghoapi.azureedge.net/api',
                status='active',
                source_metadata={
                    'supported_indicators': ['health', 'mortality']
                }
            )
        ]
        
        for source in sources:
            db.session.add(source)
        db.session.commit()
        return sources 

@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response for testing"""
    return {
        "key_findings": ["Test finding 1", "Test finding 2"],
        "trends": ["Test trend 1"],
        "correlations": ["Test correlation 1"],
        "gaps": ["Test gap 1"],
        "recommendations": ["Test recommendation 1"]
    }

@pytest.fixture
def mock_policy_response():
    """Mock policy brief response for testing"""
    return {
        "executive_summary": "Test summary",
        "key_findings": ["Test finding 1"],
        "recommendations": [{"action": "Test action", "rationale": "Test rationale"}],
        "resource_requirements": {"financial": "Test requirement"},
        "impact_assessment": {"short_term": ["Test impact"]}
    }

@pytest.fixture
def mock_gemini_service(monkeypatch):
    """Mock GeminiService for testing"""
    mock_analysis_result = {
        "key_findings": ["Test finding 1", "Test finding 2"],
        "trends": ["Test trend 1"],
        "correlations": ["Test correlation 1"],
        "gaps": ["Test gap 1"],
        "recommendations": ["Test recommendation 1"]
    }

    mock_policy_result = {
        "executive_summary": "Test summary",
        "key_findings": ["Test finding 1"],
        "recommendations": [{"action": "Test action", "rationale": "Test rationale"}],
        "resource_requirements": {"financial": "Test requirement"},
        "impact_assessment": {"short_term": ["Test impact"]}
    }

    class MockGeminiService:
        async def analyze_data(self, data):
            return mock_analysis_result

        async def generate_policy_brief(self, analysis):
            return mock_policy_result

        async def process_complete_pipeline(self, data):
            return {
                "analysis": mock_analysis_result,
                "policy_brief": mock_policy_result
            }

    # Mock the chain classes instead of the service
    from src.chains import analysis_chain, policy_chain

    class MockAnalysisChain:
        async def analyze(self, data):
            return mock_analysis_result

        def get_prompt(self):
            return "Test prompt"

        def update_prompt(self, new_prompt):
            pass

    class MockPolicyChain:
        async def generate(self, analysis):
            return mock_policy_result

        def get_prompt(self):
            return "Test prompt"

        def update_prompt(self, new_prompt):
            pass

    monkeypatch.setattr(analysis_chain, "AnalysisChain", MockAnalysisChain)
    monkeypatch.setattr(policy_chain, "PolicyChain", MockPolicyChain)

    return MockGeminiService()

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()