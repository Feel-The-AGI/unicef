import pytest
from src.services.gemini_service import GeminiService

class TestGeminiService:
    @pytest.mark.asyncio
    async def test_analyze_data(self, mock_gemini_service):
        """Test data analysis"""
        data = {
            'unicef': {'health': {'value': 123}},
            'who': {'education': {'value': 456}}
        }
        
        result = await mock_gemini_service.analyze_data(data)
        assert 'key_findings' in result
        assert 'recommendations' in result
    
    @pytest.mark.asyncio
    async def test_generate_policy_brief(self, mock_gemini_service):
        """Test policy brief generation"""
        analysis = {
            'key_findings': ['Finding 1'],
            'recommendations': ['Recommendation 1']
        }
        
        result = await mock_gemini_service.generate_policy_brief(analysis)
        assert 'executive_summary' in result
        assert 'recommendations' in result
    
    @pytest.mark.asyncio
    async def test_complete_pipeline(self, mock_gemini_service):
        """Test complete analysis pipeline"""
        data = {
            'unicef': {'health': {'value': 123}},
            'who': {'education': {'value': 456}}
        }
        
        result = await mock_gemini_service.process_complete_pipeline(data)
        assert 'analysis' in result
        assert 'policy_brief' in result 