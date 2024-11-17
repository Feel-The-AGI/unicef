from typing import Dict
from src.chains.analysis_chain import AnalysisChain
from src.chains.policy_chain import PolicyChain
import os

class GeminiService:
    """Service for handling LLM operations with Gemini Pro"""
    
    def __init__(self):
        self.analysis_chain = AnalysisChain()
        self.policy_chain = PolicyChain()
        
        # Add error handling for Gemini API initialization
        if not os.getenv('GOOGLE_API_KEY'):
            raise EnvironmentError("GOOGLE_API_KEY environment variable is required")
    
    async def analyze_data(self, data: Dict) -> Dict:
        """
        Analyze children's welfare data
        
        Args:
            data: Dictionary containing data from various sources
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            analysis_result = await self.analysis_chain.analyze(data)
            return analysis_result
        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")
    
    async def generate_policy_brief(self, analysis: Dict) -> Dict:
        """
        Generate policy brief from analysis
        
        Args:
            analysis: Dictionary containing analysis results
            
        Returns:
            Dictionary containing policy brief
        """
        try:
            brief_result = await self.policy_chain.generate(analysis)
            return brief_result
        except Exception as e:
            raise Exception(f"Policy brief generation failed: {str(e)}")
    
    async def process_complete_pipeline(self, data: Dict) -> Dict:
        """
        Run complete analysis and policy brief generation pipeline
        
        Args:
            data: Raw data from various sources
            
        Returns:
            Dictionary containing both analysis and policy brief
        """
        try:
            analysis_result = await self.analyze_data(data)
            brief_result = await self.generate_policy_brief(analysis_result)
            return {
                "analysis": analysis_result,
                "policy_brief": brief_result
            }
        except Exception as e:
            raise Exception(f"Pipeline processing failed: {str(e)}")
