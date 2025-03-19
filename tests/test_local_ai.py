"""
Tests for the local AI integration.
"""

import pytest
import requests
import json
import os
from unittest.mock import patch, MagicMock

# This test will be skipped if the local AI server is not running
def is_local_ai_server_running():
    """Check if the local AI server is running."""
    try:
        response = requests.get("http://127.0.0.1:1234/health", timeout=2)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False

# Skip the test if the local AI server is not running
pytestmark = pytest.mark.skipif(
    not is_local_ai_server_running(),
    reason="Local AI server is not running"
)

class TestLocalAI:
    """Tests for the local AI integration."""
    
    def test_local_ai_connection(self):
        """Test that we can connect to the local AI server."""
        response = requests.get("http://127.0.0.1:1234/health", timeout=2)
        assert response.status_code == 200
    
    def test_local_ai_completion(self):
        """Test that we can get completions from the local AI server."""
        # This is a simple test to check if the API is working
        # In a real implementation, we would use a proper client library
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "prompt": "def fibonacci(n):",
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        response = requests.post(
            "http://127.0.0.1:1234/v1/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=10
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "choices" in result
        assert len(result["choices"]) > 0
        assert "text" in result["choices"][0]
        assert len(result["choices"][0]["text"]) > 0
    
    @patch("requests.post")
    def test_local_ai_integration_with_mock(self, mock_post):
        """Test the local AI integration with a mock."""
        # Mock the response from the local AI server
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "text": """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
"""
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Create a simple client function to test
        def get_completion(prompt, max_tokens=100, temperature=0.7):
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(
                "http://127.0.0.1:1234/v1/completions",
                headers=headers,
                data=json.dumps(data),
                timeout=10
            )
            
            if response.status_code != 200:
                raise Exception(f"Error: {response.status_code}")
            
            result = response.json()
            return result["choices"][0]["text"]
        
        # Test the client function
        completion = get_completion("def fibonacci(n):")
        assert "return fibonacci(n-1) + fibonacci(n-2)" in completion
        
        # Verify that the mock was called with the correct arguments
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "http://127.0.0.1:1234/v1/completions"
        assert kwargs["headers"] == {"Content-Type": "application/json"}
        assert json.loads(kwargs["data"]) == {
            "prompt": "def fibonacci(n):",
            "max_tokens": 100,
            "temperature": 0.7
        }
