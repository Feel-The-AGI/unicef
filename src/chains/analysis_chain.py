from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableSequence
from typing import Dict
import os
import asyncio

class AnalysisChain:
    """LangChain implementation for data analysis"""
    
    def __init__(self):
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-pro",
                temperature=0.3,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                timeout=30
            )
            
            self.analysis_prompt = ChatPromptTemplate.from_messages([
                HumanMessage(content="""You are an expert in analyzing children's welfare data for UNICEF in Ghana.
                Analyze this data focusing on:
                - Education access and quality trends
                - Child health indicators and gaps
                - Regional disparities and inequalities
                - Resource allocation needs
                - Areas requiring immediate intervention
                
                Provide analysis in JSON format with these sections:
                - key_findings: List of main findings about education, health, and welfare
                - trends: Identified trends in the data
                - correlations: Important relationships between different metrics
                - gaps: Missing or incomplete data points
                - recommendations: Specific, actionable recommendations for Ghana
                
                Data to analyze: {data}""")
            ])
            
            # Create analysis chain
            self.chain = self.analysis_prompt | self.llm | JsonOutputParser()
            
        except Exception as e:
            raise Exception(f"Failed to initialize analysis chain: {str(e)}")
    
    async def analyze(self, data: Dict) -> Dict:
        """Run analysis chain on data"""
        try:
            result = await asyncio.wait_for(
                self.chain.ainvoke({"data": data}),
                timeout=30
            )
            return result
        except asyncio.TimeoutError:
            raise Exception("Analysis timed out after 30 seconds")
        except Exception as e:
            raise Exception(f"Analysis chain failed: {str(e)}")
    
    def get_prompt(self) -> str:
        """Get the current prompt template"""
        return self.analysis_prompt.messages[0].content
    
    def update_prompt(self, new_prompt: str) -> None:
        """Update the analysis prompt template"""
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            HumanMessage(content=new_prompt)
        ])
        self.chain = self.analysis_prompt | self.llm | JsonOutputParser()
