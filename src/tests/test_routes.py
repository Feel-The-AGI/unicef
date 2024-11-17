import pytest
import json
from datetime import datetime
from src.models import User, Analysis, Report, PolicyBrief, db

@pytest.fixture
def auth_headers(client, user):
    """Get authentication headers"""
    response = client.post('/api/auth/login', json={
        'email': user.email,
        'password': 'password123'
    })
    assert response.status_code == 200
    token = response.json['data']['token']
    return {
        'Authorization': f'Bearer {token}',
        'X-Request-ID': 'test-request-id'
    }

class TestAuthRoutes:
    def test_register(self, client):
        """Test user registration"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'organization': 'Test Org'
        })
        
        assert response.status_code == 201
        assert response.json['status'] == 'success'
        assert 'user_id' in response.json['data']
        
    def test_login(self, client, user):
        """Test user login"""
        response = client.post('/api/auth/login', json={
            'email': user.email,
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert 'token' in response.json['data']

class TestDataRoutes:
    def test_list_sources(self, client, auth_headers, data_sources):
        """Test listing data sources"""
        response = client.get('/api/sources', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert isinstance(response.json['data'], list)
        assert len(response.json['data']) == len(data_sources)
        
    def test_fetch_source_data(self, client, auth_headers):
        """Test fetching data from a source"""
        response = client.get(
            '/api/sources/UNICEF/data?topics=health,education&region=GHA',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert isinstance(response.json['data'], dict)

class TestAnalysisRoutes:
    def test_create_analysis(self, client, auth_headers, monkeypatch):
        """Test creating new analysis"""
        # Mock the Gemini API response
        mock_analysis_result = {
            "key_findings": ["Test finding 1", "Test finding 2"],
            "trends": ["Test trend 1"],
            "correlations": ["Test correlation 1"],
            "gaps": ["Test gap 1"],
            "recommendations": ["Test recommendation 1"]
        }

        # Mock the analyze_data method
        async def mock_analyze_data(*args, **kwargs):
            return mock_analysis_result

        from src.services.gemini_service import GeminiService
        monkeypatch.setattr(GeminiService, "analyze_data", mock_analyze_data)

        response = client.post('/api/analysis',
            json={
                'sources': ['UNICEF', 'WHO'],
                'topics': ['health', 'education'],
                'region': 'GHA'
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        assert response.json['status'] == 'success'
        assert 'analysis_id' in response.json['data']
        
    def test_get_analysis(self, client, auth_headers, analysis):
        """Test retrieving analysis"""
        response = client.get(
            f'/api/analysis/{analysis.id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert response.json['data']['id'] == analysis.id

class TestReportRoutes:
    def test_generate_report(self, client, auth_headers, analysis):
        """Test generating new report"""
        response = client.post('/api/reports',
            json={
                'analysis_id': analysis.id,
                'type': 'summary',
                'format': 'json'
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        assert response.json['status'] == 'success'
        assert 'report_id' in response.json['data']
        
    def test_get_report(self, client, auth_headers, report):
        """Test retrieving report"""
        response = client.get(
            f'/api/reports/{report.id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert response.json['data']['id'] == report.id

class TestPolicyBriefRoutes:
    def test_generate_brief(self, client, auth_headers, report):
        """Test generating policy brief"""
        response = client.post('/api/briefs',
            json={
                'report_id': report.id,
                'target_audience': 'policymakers'
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        assert response.json['status'] == 'success'
        assert 'brief_id' in response.json['data']
        
    def test_get_brief(self, client, auth_headers, policy_brief):
        """Test retrieving policy brief"""
        response = client.get(
            f'/api/briefs/{policy_brief.id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        assert response.json['data']['id'] == policy_brief.id

class TestErrorHandling:
    def test_invalid_parameters(self, client, auth_headers):
        """Test error handling for invalid parameters"""
        response = client.post('/api/analysis',
            json={
                'invalid': 'parameters'
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert response.json['status'] == 'error'
        assert 'code' in response.json['error']
        
    def test_not_found(self, client, auth_headers):
        """Test error handling for non-existent resources"""
        response = client.get('/api/analysis/99999', headers=auth_headers)
        
        assert response.status_code == 404
        assert response.json['status'] == 'error'
        assert response.json['error']['code'] == 'ANALYSIS_NOT_FOUND'
        
    def test_unauthorized(self, client):
        """Test error handling for unauthorized access"""
        response = client.get('/api/analysis/1')
        
        assert response.status_code == 401
        assert response.json['status'] == 'error'
        assert response.json['error']['code'] == 'UNAUTHORIZED'
