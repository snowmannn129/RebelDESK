"""
Tests for the error detection provider.
"""

import pytest
from unittest.mock import patch, MagicMock

from rebeldesk.ai.error_detection import ErrorDetectionProvider

class TestErrorDetectionProvider:
    """Tests for the error detection provider."""
    
    @patch("rebeldesk.ai.error_detection.LocalAIClient")
    def test_get_errors(self, mock_client_class):
        """Test that we can get errors from the error detection provider."""
        # Mock the LocalAIClient
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock the is_server_running method
        mock_client.is_server_running.return_value = True
        
        # Mock the get_completion method
        mock_client.get_completion.return_value = """
Line 2: Missing colon after 'if' statement
Line 5: Undefined variable 'result'
"""
        
        # Create the error detection provider
        provider = ErrorDetectionProvider()
        
        # Test code with errors
        code = """def calculate_sum(a, b):
    if a > 0 and b > 0
        return a + b
    else:
        return result
"""
        
        # Get errors
        errors = provider.get_errors(code)
        
        # Check that we got the expected errors
        assert len(errors) == 2
        assert errors[0]["line"] == 2
        assert "Missing colon" in errors[0]["message"]
        assert errors[0]["severity"] == "error"
        assert errors[1]["line"] == 5
        assert "Undefined variable" in errors[1]["message"]
        assert errors[1]["severity"] == "error"
        
        # Verify that the mock was called with the correct arguments
        mock_client.get_completion.assert_called_once()
        args, kwargs = mock_client.get_completion.call_args
        assert kwargs["prompt"].startswith(code)
        assert "List all errors" in kwargs["prompt"]
    
    @patch("rebeldesk.ai.error_detection.LocalAIClient")
    def test_get_fixes(self, mock_client_class):
        """Test that we can get fixes from the error detection provider."""
        # Mock the LocalAIClient
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock the is_server_running method
        mock_client.is_server_running.return_value = True
        
        # Mock the get_completion method
        mock_client.get_completion.return_value = "    if a > 0 and b > 0:"
        
        # Create the error detection provider
        provider = ErrorDetectionProvider()
        
        # Test code with errors
        code = """def calculate_sum(a, b):
    if a > 0 and b > 0
        return a + b
    else:
        return result
"""
        
        # Create an error
        error = {
            "line": 2,
            "message": "Missing colon after 'if' statement",
            "severity": "error",
            "range": {
                "start": 24,
                "end": 25
            }
        }
        
        # Get fixes
        fixes = provider.get_fixes(code, error)
        
        # Check that we got the expected fix
        assert len(fixes) == 1
        assert "Fix: Missing colon" in fixes[0]["title"]
        assert len(fixes[0]["edits"]) == 1
        assert fixes[0]["edits"][0]["newText"] == "    if a > 0 and b > 0:"
        
        # Verify that the mock was called with the correct arguments
        mock_client.get_completion.assert_called_once()
        args, kwargs = mock_client.get_completion.call_args
        assert "Code with error" in kwargs["prompt"]
        assert "Error on line 2" in kwargs["prompt"]
        assert "Missing colon" in kwargs["prompt"]
    
    @patch("rebeldesk.ai.error_detection.LocalAIClient")
    def test_server_not_running(self, mock_client_class):
        """Test that we handle the case where the server is not running."""
        # Mock the LocalAIClient
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock the is_server_running method
        mock_client.is_server_running.return_value = False
        
        # Create the error detection provider
        provider = ErrorDetectionProvider()
        
        # Test code with errors
        code = """def calculate_sum(a, b):
    if a > 0 and b > 0
        return a + b
    else:
        return result
"""
        
        # Get errors
        errors = provider.get_errors(code)
        
        # Check that we got no errors
        assert len(errors) == 0
        
        # Create an error
        error = {
            "line": 2,
            "message": "Missing colon after 'if' statement",
            "severity": "error",
            "range": {
                "start": 24,
                "end": 25
            }
        }
        
        # Get fixes
        fixes = provider.get_fixes(code, error)
        
        # Check that we got no fixes
        assert len(fixes) == 0
    
    def test_find_position_for_line(self):
        """Test that we can find the position for a line."""
        # Create the error detection provider
        provider = ErrorDetectionProvider()
        
        # Test code
        code = """def calculate_sum(a, b):
    if a > 0 and b > 0:
        return a + b
    else:
        return 0
"""
        
        # Check that we get the correct positions
        assert provider._find_position_for_line(code, 1) == 0
        assert provider._find_position_for_line(code, 2) == 24
        assert provider._find_position_for_line(code, 3) == 50
        assert provider._find_position_for_line(code, 4) == 70
        assert provider._find_position_for_line(code, 5) == 84
