# HealthTech4Africa - UNICEF AI Research Tools Project

## Table of Contents
- [Project Overview](#project-overview)
- [Setup Instructions](#setup-instructions)
- [Architecture](#architecture)
- [Core Components](#core-components)
- [API Specification](#api-specification)
- [Database Models](#database-models)
- [Technical Details](#technical-details)
- [Development Guidelines](#development-guidelines)

## Project Overview
AI-powered research tool that processes and analyzes children's welfare data from multiple sources to generate evidence-based policy briefs. Built with Flask, LangChain 0.3.x, and Google's Gemini Pro.

## Setup Instructions

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install langchain==0.3.7 
pip install langchain-google-genai
pip install flask
pip install python-dotenv
pip install requests
```

### Environment Variables
Create `.env` file:
```env
GOOGLE_API_KEY=your-gemini-api-key
SQLITE_DATABASE_URI=sqlite:///unicef_api.db
```

## Architecture

### Project Structure
```
src/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── main.py           # Main application entry
│   └── routes/
│       ├── __init__.py
│       ├── auth.py       # Authentication routes
│       ├── data.py       # Data source routes
│       ├── analysis.py   # Analysis routes
│       └── reports.py    # Report generation routes
├── models/
│   ├── __init__.py
│   ├── user.py          # User model
│   ├── data_source.py   # Data source model
│   ├── analysis.py      # Analysis model
│   ├── report.py        # Report model
│   └── policy.py        # Policy brief model
├── services/
│   ├── __init__.py
│   ├── gemini_service.py    # Gemini LLM service
│   ├── data_service.py      # Data fetching service
├── chains/
│   ├── __init__.py
│   ├── analysis_chain.py    # Data analysis chain
│   └── policy_chain.py      # Policy generation chain
├── tools/
│   ├── __init__.py
│   ├── unicef_tool.py      # UNICEF data tool
│   ├── who_tool.py         # WHO data tool
│   └── worldbank_tool.py   # World Bank data tool
├── utils/
│   ├── __init__.py
│   ├── validators.py       # Input validation
│   └── helpers.py         # Helper functions
└── tests/
    ├── __init__.py
    ├── test_routes.py
    ├── test_models.py
    └── test_chains.py
```

## Core Components

### Data Sources
1. UNICEF Data API (Priority Source)
   - Endpoint: https://data.unicef.org/resources/api/
   - Data Points: 
     - Child health indicators
     - Education statistics
     - Nutrition data
     - Child protection metrics

2. Ghana-Specific Sources
   - Ghana Open Data Initiative (GODI)
   - Ghana Health Service data
   - DHS Program data for Ghana

3. Supporting Sources
   - World Bank API
   - WHO API
   - UNESCO Statistics
   - UN Data API

### LangChain + Gemini Implementation
```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableSequence

# Initialize Gemini Pro
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=0.3,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Data Analysis Prompt
analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert in analyzing children's welfare data for UNICEF.
    Focus on these key areas:
    - Education access and quality
    - Child health indicators
    - Nutrition status
    - Child protection measures
    - WASH (Water, Sanitation, and Hygiene)
    
    Generate insights that can inform policy decisions."""),
    ("user", "Analyze this children's welfare data: {data}")
])

# Policy Brief Prompt
brief_prompt = ChatPromptTemplate.from_messages([
    ("system", """Create a policy brief that:
    1. Simplifies complex information for stakeholders
    2. Presents key messages for decision-making
    3. Focuses on mobilizing resources for children
    4. Aligns with UNICEF's focus areas
    
    Format:
    - Executive Summary
    - Key Findings
    - Evidence-based Recommendations
    - Resource Mobilization Strategy"""),
    ("user", "Create a policy brief based on this analysis: {analysis}")
])

# Create Pipeline
analysis_chain = analysis_prompt | llm | JsonOutputParser()
brief_chain = brief_prompt | llm

pipeline = RunnableSequence([
    analysis_chain,
    brief_chain
])
```

### Data Fetcher Implementation
```python
from langchain.tools import Tool
from langchain_core.tools import ToolException

class UNICEFDataTool:
    def fetch_data(self, params):
        endpoints = {
            "health": "https://data.unicef.org/api/v2/health",
            "education": "https://data.unicef.org/api/v2/education",
            "protection": "https://data.unicef.org/api/v2/protection",
            "wash": "https://data.unicef.org/api/v2/wash"
        }
        
        data = {}
        for topic, endpoint in endpoints.items():
            response = requests.get(
                endpoint,
                params={
                    "country": "GHA",  # Ghana
                    "year": "2023-2024",
                    **params
                }
            )
            data[topic] = response.json()
            
        return data

unicef_tool = Tool(
    name="unicef_data",
    description="Fetch children's welfare data from UNICEF",
    func=UNICEFDataTool().fetch_data
)
```

## API Specification

### Authentication Routes
- POST `/api/auth/register` - Register new user
- POST `/api/auth/login` - Login existing user
- GET `/api/auth/user` - Get current user details

### Data Source Routes
- GET `/api/sources` - List all available data sources
- GET `/api/sources/{source_id}` - Get specific source details
- GET `/api/sources/{source_id}/data` - Fetch data from specific source
- POST `/api/sources/fetch` - Trigger data fetch from multiple sources

### Analysis Routes
- POST `/api/analysis` - Start new analysis
- GET `/api/analysis/{analysis_id}` - Get analysis results
- GET `/api/analysis/user/{user_id}` - Get user's analyses
- DELETE `/api/analysis/{analysis_id}` - Delete analysis

### Report Routes
- POST `/api/reports` - Generate new report
- GET `/api/reports/{report_id}` - Get report
- GET `/api/reports/user/{user_id}` - Get user's reports
- PUT `/api/reports/{report_id}` - Update report
- DELETE `/api/reports/{report_id}` - Delete report

### Policy Brief Routes
- POST `/api/briefs` - Generate policy brief
- GET `/api/briefs/{brief_id}` - Get policy brief
- PUT `/api/briefs/{brief_id}` - Update policy brief

## Database Models

### User Model
```python
class User:
    id: Integer
    username: str
    email: str
    password_hash: str
    organization: str
    role: str
    created_at: datetime
    last_login: datetime
```

### DataSource Model
```python
class DataSource:
    id: Integer
    name: str
    type: str  # UNICEF, WHO, WorldBank, etc.
    url: str
    api_key: str
    status: str  # active, inactive
    last_fetch: datetime
    metadata: dict
```

### Analysis Model
```python
class Analysis:
    id: Integer
    user_id: Integer
    sources: List[str]
    topics: List[str]
    region: str
    date_range: {
        start: datetime,
        end: datetime
    }
    raw_data: dict
    analysis_results: dict
    status: str  # pending, completed, failed
    created_at: datetime
    updated_at: datetime
```

### Report Model
```python
class Report:
    id: Integer
    analysis_id: Integer
    user_id: Integer
    type: str  # policy_brief, summary, full_report
    content: dict
    format: str  # pdf, json, html
    created_at: datetime
    metadata: dict
```

### PolicyBrief Model
```python
class PolicyBrief:
    id: Integer
    report_id: Integer
    executive_summary: str
    key_findings: List[str]
    recommendations: List[str]
    target_audience: str
    resource_requirements: dict
    impact_assessment: dict
```

## Technical Details

### Response Format
All API responses follow this structure:
```json
{
    "status": "success|error",
    "data": {
        // Response data
    },
    "message": "Description message",
    "metadata": {
        "timestamp": "ISO datetime",
        "version": "API version",
        "request_id": "UUID"
    }
}
```

### Error Responses
```json
{
    "status": "error",
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description",
        "details": {}
    },
    "metadata": {
        "timestamp": "ISO datetime",
        "request_id": "UUID"
    }
}
```

### Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 500: Server Error

## Development Guidelines

### Rate Limits
- 100 requests/minute for authenticated users
- 1000 requests/day per API key
- 50 concurrent analyses per user
- 5 concurrent report generations per user

### Development Timeline
1. Setup & Configuration (5 mins)
   - Environment setup
   - Dependencies installation
   - API keys configuration

2. Core Implementation (15 mins)
   - Data fetcher setup
   - LangChain pipeline implementation
   - API endpoint creation

3. Testing & Refinement (10 mins)
   - Endpoint testing
   - Data processing verification
   - Output format validation

### Notes
- Focus on Ghana-specific data sources first
- Ensure proper error handling for API timeouts
- Cache frequently accessed data
- Monitor Gemini API usage
- Follow UNICEF data privacy guidelines

### Requirements
```
flask==3.0.0
langchain==0.3.7
langchain-google-genai==0.0.3
python-dotenv==1.0.0
requests==2.31.0
```