import pytest
from src.services.data_service import DataService
from src.models import DataSource, db

class TestDataService:
    def test_get_data(self, app, data_sources):
        """Test fetching data from multiple sources"""
        with app.app_context():
            service = DataService()
            data = service.get_data(
                sources=['UNICEF', 'WHO'],
                topics=['health', 'education'],
                region='GHA'
            )
            
            assert isinstance(data, dict)
            assert 'unicef' in data
            assert 'who' in data
            
    def test_get_available_sources(self, app, data_sources):
        """Test listing available data sources"""
        with app.app_context():
            service = DataService()
            sources = service.get_available_sources()
            
            assert len(sources) == len(data_sources)
            assert all('id' in source for source in sources)
            assert all('status' in source for source in sources)
    
    def test_refresh_data_sources(self, app, data_sources):
        """Test refreshing data sources"""
        with app.app_context():
            service = DataService()
            status = service.refresh_data_sources()
            
            assert isinstance(status, dict)
            assert all(source.name in status for source in data_sources)
    
    def test_source_metadata(self, app, data_sources):
        """Test getting source metadata"""
        with app.app_context():
            service = DataService()
            metadata = service.get_source_metadata('UNICEF')
            
            assert metadata['type'] == 'UNICEF'
            assert 'supported_indicators' in metadata['metadata'] 