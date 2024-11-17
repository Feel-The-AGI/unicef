import pytest
from src.utils.validators import (
    validate_source_params,
    validate_analysis_params,
    validate_report_params,
    validate_policy_brief_params
)

class TestValidators:
    def test_source_params_validation(self):
        """Test data source parameter validation"""
        # Test valid parameters
        valid_params = {
            'topics': ['health', 'education'],
            'region': 'GHA'
        }
        assert validate_source_params(valid_params) is None
        
        # Test invalid parameters
        invalid_params = {
            'topics': 123,  # Should be list or string
            'region': ['GHA']  # Should be string
        }
        assert validate_source_params(invalid_params) is not None
        
        # Test empty parameters
        assert validate_source_params({}) == "No parameters provided"
    
    def test_analysis_params_validation(self):
        """Test analysis parameter validation"""
        # Test valid parameters
        valid_params = {
            'sources': ['UNICEF', 'WHO'],
            'topics': ['health', 'education'],
            'region': 'GHA'
        }
        assert validate_analysis_params(valid_params) is None
        
        # Test missing required fields
        missing_params = {
            'sources': ['UNICEF']
        }
        assert validate_analysis_params(missing_params) == "Missing required fields: topics"
        
        # Test invalid types
        invalid_params = {
            'sources': 'UNICEF',  # Should be list
            'topics': ['health']
        }
        assert validate_analysis_params(invalid_params) == "Sources must be a list"
    
    def test_report_params_validation(self):
        """Test report parameter validation"""
        # Test valid parameters
        valid_params = {
            'analysis_id': 1,
            'type': 'summary',
            'format': 'json'
        }
        assert validate_report_params(valid_params) is None
        
        # Test missing analysis_id
        missing_params = {
            'type': 'summary'
        }
        assert validate_report_params(missing_params) == "Analysis ID is required"
        
        # Test invalid report type
        invalid_type = {
            'analysis_id': 1,
            'type': 'invalid_type'
        }
        assert "Invalid report type" in validate_report_params(invalid_type)
    
    def test_policy_brief_params_validation(self):
        """Test policy brief parameter validation"""
        # Test valid parameters
        valid_params = {
            'report_id': 1,
            'target_audience': 'policymakers'
        }
        assert validate_policy_brief_params(valid_params) is None
        
        # Test missing report_id
        missing_params = {
            'target_audience': 'policymakers'
        }
        assert validate_policy_brief_params(missing_params) == "Report ID is required"
        
        # Test invalid target audience
        invalid_audience = {
            'report_id': 1,
            'target_audience': 'invalid_audience'
        }
        assert "Invalid target audience" in validate_policy_brief_params(invalid_audience) 