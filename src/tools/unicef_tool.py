import requests
from typing import Dict, List, Optional
from datetime import datetime
import logging
from flask import current_app
from src.models import DataSource, db
import os

class UNICEFDataTool:
    """UNICEF Data API Tool for fetching children's welfare data"""
    
    BASE_URL = "https://data.unicef.org/api/v2"
    ENDPOINTS = {
        "health": "/health",
        "education": "/education",
        "protection": "/protection",
        "wash": "/wash",
        "nutrition": "/nutrition"
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._init_data_source()
    
    def _init_data_source(self):
        """Initialize or fetch UNICEF data source from database"""
        source = DataSource.query.filter_by(type='UNICEF').first()
        if not source:
            source = DataSource(
                name='UNICEF Data API',
                type='UNICEF',
                url=self.BASE_URL,
                status='active',
                source_metadata={
                    'endpoints': self.ENDPOINTS,
                    'supported_indicators': self._get_supported_indicators()
                }
            )
            db.session.add(source)
            db.session.commit()
        self.data_source = source

    def _get_supported_indicators(self) -> Dict[str, List[str]]:
        """Get supported indicators for each endpoint"""
        return {
            "health": [
                "infant_mortality_rate",
                "under5_mortality_rate",
                "immunization_coverage",
                "maternal_health"
            ],
            "education": [
                "primary_enrollment",
                "secondary_enrollment",
                "completion_rate",
                "gender_parity"
            ],
            "protection": [
                "child_labor",
                "child_marriage",
                "birth_registration",
                "violence_against_children"
            ],
            "wash": [
                "water_access",
                "sanitation_access",
                "hygiene_practices",
                "school_wash"
            ],
            "nutrition": [
                "stunting",
                "wasting",
                "underweight",
                "breastfeeding"
            ]
        }

    def fetch_data(self, 
                  topics: List[str], 
                  region: str = "GHA",
                  start_date: Optional[str] = None,
                  end_date: Optional[str] = None,
                  indicators: Optional[List[str]] = None) -> Dict:
        """Fetch data from UNICEF API (mock data for development)"""
        # Return mock data since we don't have API access
        return {
            "health": {
                "infant_mortality_rate": {
                    "2023": 35.2,
                    "2024": 34.1
                },
                "under5_mortality_rate": {
                    "2023": 46.8,
                    "2024": 45.2
                },
                "immunization_coverage": {
                    "2023": 85.7,
                    "2024": 87.3
                }
            },
            "education": {
                "primary_enrollment": {
                    "2023": 92.3,
                    "2024": 93.1
                },
                "secondary_enrollment": {
                    "2023": 73.4,
                    "2024": 74.8
                },
                "completion_rate": {
                    "2023": 78.5,
                    "2024": 79.2
                },
                "gender_parity": {
                    "2023": 0.98,
                    "2024": 0.99
                }
            },
            "metadata": {
                "country": "Ghana",
                "region": region,
                "time_period": f"{start_date} to {end_date}",
                "data_source": "UNICEF Mock Data"
            }
        }

    def validate_data(self, data: Dict) -> Dict:
        """Validate and clean fetched data"""
        validated_data = {}
        for topic, topic_data in data.items():
            if "error" in topic_data:
                continue
                
            # Remove null values and validate data types
            validated_data[topic] = {
                k: v for k, v in topic_data.items()
                if v is not None and self._validate_data_point(k, v)
            }
        
        return validated_data
    
    def _validate_data_point(self, key: str, value: any) -> bool:
        """Validate individual data points"""
        try:
            if isinstance(value, (int, float)):
                return True
            elif isinstance(value, str):
                return bool(value.strip())
            elif isinstance(value, dict):
                return all(self._validate_data_point(k, v) for k, v in value.items())
            elif isinstance(value, list):
                return all(self._validate_data_point(str(i), v) for i, v in enumerate(value))
            return False
        except Exception as e:
            self.logger.error(f"Validation error for {key}: {str(e)}")
            return False
