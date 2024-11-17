import requests
from typing import Dict, List, Optional
from datetime import datetime
import logging
from flask import current_app
from src.models import DataSource, db

class WHODataTool:
    """WHO Data API Tool for fetching health data"""
    
    BASE_URL = "https://ghoapi.azureedge.net/api"
    ENDPOINTS = {
        "child_mortality": "/indicator/CHILDMORT",
        "immunization": "/indicator/IMMUNIZATION",
        "nutrition": "/indicator/NUTRITION",
        "maternal_health": "/indicator/MATERNALHEALTH",
        "disease_prevention": "/indicator/DISEASE"
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._init_data_source()
    
    def _init_data_source(self):
        """Initialize or fetch WHO data source from database"""
        source = DataSource.query.filter_by(type='WHO').first()
        if not source:
            source = DataSource(
                name='WHO Global Health Observatory',
                type='WHO',
                url=self.BASE_URL,
                status='active',
                metadata={
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
            "child_mortality": [
                "under_five_mortality_rate",
                "infant_mortality_rate",
                "neonatal_mortality_rate"
            ],
            "immunization": [
                "dtp3_coverage",
                "measles_coverage",
                "polio_coverage",
                "bcg_coverage"
            ],
            "nutrition": [
                "stunting_prevalence",
                "wasting_prevalence",
                "underweight_prevalence",
                "exclusive_breastfeeding"
            ],
            "maternal_health": [
                "maternal_mortality_ratio",
                "skilled_birth_attendance",
                "antenatal_care_coverage"
            ],
            "disease_prevention": [
                "malaria_incidence",
                "tuberculosis_incidence",
                "hiv_prevalence"
            ]
        }

    def fetch_data(self, 
                  topics: List[str], 
                  region: str = "GHA",
                  start_date: Optional[str] = None,
                  end_date: Optional[str] = None,
                  indicators: Optional[List[str]] = None) -> Dict:
        """Fetch data from WHO API (mock data for development)"""
        return {
            "health": {
                "child_mortality": {
                    "2023": {
                        "rate": 48.3,
                        "confidence_interval": [45.2, 51.4]
                    },
                    "2024": {
                        "rate": 46.9,
                        "confidence_interval": [43.8, 50.0]
                    }
                },
                "immunization": {
                    "dtp3_coverage": {
                        "2023": 89.2,
                        "2024": 90.5
                    },
                    "measles_coverage": {
                        "2023": 86.7,
                        "2024": 88.1
                    }
                },
                "nutrition": {
                    "stunting_prevalence": {
                        "2023": 18.8,
                        "2024": 18.1
                    },
                    "wasting_prevalence": {
                        "2023": 6.8,
                        "2024": 6.5
                    }
                }
            },
            "metadata": {
                "country": "Ghana",
                "source": "WHO Mock Data",
                "last_updated": datetime.utcnow().isoformat()
            }
        }

    def validate_data(self, data: Dict) -> Dict:
        """Validate and clean fetched data"""
        validated_data = {}
        for topic, topic_data in data.items():
            if "error" in topic_data:
                continue
                
            # WHO-specific data structure validation
            if "value" in topic_data and "dimension" in topic_data:
                validated_data[topic] = self._validate_who_structure(topic_data)
            else:
                validated_data[topic] = {
                    k: v for k, v in topic_data.items()
                    if v is not None and self._validate_data_point(k, v)
                }
        
        return validated_data
    
    def _validate_who_structure(self, data: Dict) -> Dict:
        """Validate WHO's specific data structure"""
        try:
            return {
                "values": [v for v in data["value"] if v is not None],
                "dimensions": {
                    dim: values for dim, values in data["dimension"].items()
                    if all(self._validate_data_point(str(i), v) for i, v in enumerate(values))
                }
            }
        except Exception as e:
            self.logger.error(f"WHO data structure validation error: {str(e)}")
            return {}
    
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
