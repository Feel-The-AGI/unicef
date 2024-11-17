import requests
from typing import Dict, List, Optional
from datetime import datetime
import logging
from flask import current_app
from src.models import DataSource, db

class WorldBankTool:
    """World Bank Data API Tool for fetching development indicators"""
    
    BASE_URL = "https://api.worldbank.org/v2"
    ENDPOINTS = {
        "education": "/country/{country}/indicator/SE.PRM.ENRR",  # Primary enrollment
        "health": "/country/{country}/indicator/SH.STA.MMRT",    # Maternal mortality
        "poverty": "/country/{country}/indicator/SI.POV.NAHC",   # Poverty headcount
        "sanitation": "/country/{country}/indicator/SH.STA.BASS.ZS",  # Basic sanitation
        "nutrition": "/country/{country}/indicator/SH.STA.STNT.ZS"    # Stunting
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._init_data_source()
    
    def _init_data_source(self):
        """Initialize or fetch World Bank data source from database"""
        source = DataSource.query.filter_by(type='WORLDBANK').first()
        if not source:
            source = DataSource(
                name='World Bank Development Indicators',
                type='WORLDBANK',
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
            "education": [
                "primary_enrollment_rate",
                "secondary_enrollment_rate",
                "completion_rate",
                "literacy_rate"
            ],
            "health": [
                "maternal_mortality",
                "child_mortality",
                "healthcare_access",
                "health_expenditure"
            ],
            "poverty": [
                "poverty_headcount",
                "poverty_gap",
                "gini_index",
                "income_share"
            ],
            "sanitation": [
                "basic_sanitation",
                "improved_water_source",
                "handwashing_facilities",
                "open_defecation"
            ],
            "nutrition": [
                "stunting_prevalence",
                "wasting_prevalence",
                "obesity_prevalence",
                "food_insecurity"
            ]
        }

    def fetch_data(self, 
                  topics: List[str], 
                  region: str = "GHA",
                  start_date: Optional[str] = None,
                  end_date: Optional[str] = None,
                  indicators: Optional[List[str]] = None) -> Dict:
        """
        Fetch data from World Bank API for specified topics and region
        
        Args:
            topics: List of topics to fetch
            region: Country code (default: GHA for Ghana)
            start_date: Start date for data range (YYYY)
            end_date: End date for data range (YYYY)
            indicators: Specific indicators to fetch
        """
        if not self.data_source.status == 'active':
            raise Exception("World Bank data source is currently inactive")

        data = {}
        for topic in topics:
            if topic not in self.ENDPOINTS:
                self.logger.warning(f"Unsupported topic: {topic}")
                continue
                
            try:
                endpoint = self.ENDPOINTS[topic].format(country=region)
                url = f"{self.BASE_URL}{endpoint}"
                params = {
                    "format": "json",
                    "per_page": 1000,
                    "date": f"{start_date or '2023'}:{end_date or '2024'}",
                    "source": indicators[0] if indicators else None
                }
                
                response = requests.get(
                    url,
                    params={k: v for k, v in params.items() if v is not None},
                    timeout=30
                )
                response.raise_for_status()
                
                # World Bank API returns a list where [0] is metadata and [1] is data
                response_data = response.json()
                if isinstance(response_data, list) and len(response_data) > 1:
                    data[topic] = response_data[1]
                else:
                    data[topic] = response_data
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error fetching {topic} data from World Bank: {str(e)}")
                data[topic] = {"error": str(e)}
        
        # Update last fetch timestamp
        self.data_source.last_fetch = datetime.utcnow()
        self.data_source.metadata.update({"last_fetch_status": "success" if data else "partial"})
        db.session.commit()
        
        return data

    def validate_data(self, data: Dict) -> Dict:
        """Validate and clean fetched data"""
        validated_data = {}
        for topic, topic_data in data.items():
            if "error" in topic_data:
                continue
                
            if isinstance(topic_data, list):
                # World Bank specific data structure
                validated_data[topic] = [
                    item for item in topic_data
                    if self._validate_worldbank_item(item)
                ]
            else:
                validated_data[topic] = {
                    k: v for k, v in topic_data.items()
                    if v is not None and self._validate_data_point(k, v)
                }
        
        return validated_data
    
    def _validate_worldbank_item(self, item: Dict) -> bool:
        """Validate World Bank data item structure"""
        required_fields = ['indicator', 'country', 'value', 'date']
        try:
            return all(
                field in item and item[field] is not None
                for field in required_fields
            )
        except Exception as e:
            self.logger.error(f"World Bank item validation error: {str(e)}")
            return False
    
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
