import pytest
from src.chains.analysis_chain import AnalysisChain
from src.chains.policy_chain import PolicyChain

class TestAnalysisChain:
    @pytest.mark.asyncio
    async def test_analyze_data(self, mock_gemini_service):
        """Test data analysis"""
        chain = AnalysisChain()
        data = {
            'unicef': {'health': {'value': 123}},
            'who': {'education': {'value': 456}}
        }
        
        result = await chain.analyze(data)
        assert isinstance(result, dict)
        assert 'key_findings' in result
        assert 'recommendations' in result
    
    def test_prompt_management(self):
        """Test prompt template management"""
        chain = AnalysisChain()
        original_prompt = chain.analysis_prompt.messages[0].content
        
        # Update prompt
        new_prompt = "New analysis prompt for {data}"
        chain.update_prompt(new_prompt)
        
        updated_prompt = chain.analysis_prompt.messages[0].content
        assert updated_prompt != original_prompt
        assert new_prompt == updated_prompt

class TestPolicyChain:
    @pytest.mark.asyncio
    async def test_generate_brief(self, mock_gemini_service):
        """Test policy brief generation"""
        chain = PolicyChain()
        analysis = {
            'key_findings': ['Finding 1'],
            'recommendations': ['Recommendation 1']
        }
        
        result = await chain.generate(analysis)
        assert isinstance(result, dict)
        assert 'executive_summary' in result
        assert 'recommendations' in result
    
    def test_prompt_management(self):
        """Test prompt template management"""
        chain = PolicyChain()
        original_prompt = chain.policy_prompt.messages[0].content
        
        # Update prompt
        new_prompt = "New policy brief prompt for {analysis}"
        chain.update_prompt(new_prompt)
        
        updated_prompt = chain.policy_prompt.messages[0].content
        assert updated_prompt != original_prompt
        assert new_prompt == updated_prompt
