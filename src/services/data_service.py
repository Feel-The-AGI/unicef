from typing import List, Dict, Optional
from datetime import datetime
from flask import current_app
from src.tools.unicef_tool import UNICEFDataTool
from src.tools.who_tool import WHODataTool
from src.tools.worldbank_tool import WorldBankTool
from src.models import DataSource, db

class DataService:
    """Service for managing data fetching from multiple sources"""
    
    def __init__(self):
        self._unicef_tool = None
        self._who_tool = None
        self._worldbank_tool = None
    
    @property
    def unicef_tool(self):
        if self._unicef_tool is None:
            self._unicef_tool = UNICEFDataTool()
        return self._unicef_tool
    
    @property
    def who_tool(self):
        if self._who_tool is None:
            self._who_tool = WHODataTool()
        return self._who_tool
    
    @property
    def worldbank_tool(self):
        if self._worldbank_tool is None:
            self._worldbank_tool = WorldBankTool()
        return self._worldbank_tool
    
    def get_data(self,
                sources: List[str],
                topics: List[str],
                region: str = "GHA",
                **kwargs) -> Dict:
        """
        Get data from multiple sources for specified topics
        
        Args:
            sources: List of data sources to use (UNICEF, WHO, WORLDBANK)
            topics: List of topics to fetch
            region: Country/region code
            **kwargs: Additional parameters for data fetching
        """
        # Fetch fresh data from each source
        data = {}
        source_tools = {
            'UNICEF': self.unicef_tool,
            'WHO': self.who_tool,
            'WORLDBANK': self.worldbank_tool
        }
        
        for source in sources:
            if source not in source_tools:
                continue
                
            try:
                source_data = source_tools[source].fetch_data(
                    topics=topics,
                    region=region,
                    **kwargs
                )
                validated_data = source_tools[source].validate_data(source_data)
                data[source.lower()] = validated_data
                
            except Exception as e:
                data[source.lower()] = {"error": str(e)}
        
        return data
    
    def get_available_sources(self) -> List[Dict]:
        """Get list of available data sources and their status"""
        sources = DataSource.query.all()
        return [{
            'id': source.id,
            'name': source.name,
            'type': source.type,
            'status': source.status,
            'last_fetch': source.last_fetch.isoformat() if source.last_fetch else None,
            'metadata': source.source_metadata
        } for source in sources]
    
    def get_source_metadata(self, source_type: str) -> Dict:
        """Get metadata for a specific data source"""
        source = DataSource.query.filter_by(type=source_type).first()
        if not source:
            return {}
            
        return {
            'name': source.name,
            'type': source.type,
            'status': source.status,
            'last_fetch': source.last_fetch.isoformat() if source.last_fetch else None,
            'metadata': source.source_metadata
        }
    
    def refresh_data_sources(self) -> Dict[str, str]:
        """Refresh all data sources and return their status"""
        sources = DataSource.query.all()
        status = {}
        
        source_tools = {
            'UNICEF': self.unicef_tool,
            'WHO': self.who_tool,
            'WORLDBANK': self.worldbank_tool
        }
        
        for source in sources:
            try:
                if source.type in source_tools:
                    # Fetch sample data to verify source is working
                    data = source_tools[source.type].fetch_data(
                        topics=list(source_tools[source.type].ENDPOINTS.keys())[:1],
                        region="GHA"
                    )
                    source.status = 'active' if data else 'error'
                    source.last_fetch = datetime.utcnow()
                    status[source.name] = source.status
                    
            except Exception as e:
                source.status = 'error'
                source.metadata = {
                    **source.metadata,
                    'last_error': str(e),
                    'last_error_time': datetime.utcnow().isoformat()
                }
                status[source.name] = f"error: {str(e)}"
        
        db.session.commit()
        return status
    
    def get_source_indicators(self, source_type: str) -> Dict[str, List[str]]:
        """Get available indicators for a specific data source"""
        source_tools = {
            'UNICEF': self.unicef_tool,
            'WHO': self.who_tool,
            'WORLDBANK': self.worldbank_tool
        }
        
        if source_type not in source_tools:
            return {}
            
        return source_tools[source_type]._get_supported_indicators()
    
    def clear_cache(self, pattern: Optional[str] = None) -> int:
        """
        Clear cache entries matching pattern
        
        Args:
            pattern: Redis key pattern to match (e.g., "data:GHA:*")
        Returns:
            Number of keys deleted
        """
        if pattern:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
        else:
            return self.redis_client.flushdb()
        return 0
