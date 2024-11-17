from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableSequence
from typing import Dict
import os

class PolicyChain:
    """LangChain implementation for policy brief generation"""
    
    def __init__(self):
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-pro",
                temperature=0.3,
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
            
            self.policy_prompt = ChatPromptTemplate.from_messages([
                HumanMessage(content="""Create a policy brief based on this analysis. Format the output as JSON with these sections:
                - executive_summary: Brief overview of the situation
                - key_findings: List of detailed findings
                - recommendations: List of actions with rationale and implementation steps
                - resource_requirements: Financial and human resource needs
                - impact_assessment: Expected short-term and long-term impacts
                
                Analysis to process: {analysis}""")
            ])
            
            # Create policy chain
            self.chain = self.policy_prompt | self.llm | JsonOutputParser()
            
        except Exception as e:
            raise Exception(f"Failed to initialize policy chain: {str(e)}")
    
    async def generate(self, analysis: Dict) -> Dict:
        """Run policy generation chain on analysis results"""
        try:
            result = await self.chain.ainvoke({"analysis": analysis})
            return result
        except Exception as e:
            raise Exception(f"Policy chain failed: {str(e)}")
    
    def get_prompt(self) -> str:
        """Get the current prompt template"""
        return self.policy_prompt.messages[0].content
    
    def update_prompt(self, new_prompt: str) -> None:
        """Update the policy prompt template"""
        self.policy_prompt = ChatPromptTemplate.from_messages([
            HumanMessage(content=new_prompt)
        ])
        self.chain = self.policy_prompt | self.llm | JsonOutputParser()
