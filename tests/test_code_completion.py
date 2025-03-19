"""
Tests for the code completion provider.
"""

import pytest
from unittest.mock import patch, MagicMock

from rebeldesk.ai.code_completion import CodeCompletionProvider

class TestCodeCompletionProvider:
    """Tests for the code completion provider."""
    
    @patch("rebeldesk.ai.code_completion.LocalAIClient")
    def test_get_completions(self, mock_client_class):
        """Test that we can get completions from the code completion provider."""
        # Mock the LocalAIClient
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock the is_server_running method
        mock_client.is_server_running.return_value = True
        
        # Mock the get_models method
        mock_client.get_models.return_value = [
            {"id": "deepseek-r1-distill-llama-8b"}
        ]
        
        # Mock the get_completion method
        mock_client.get_completion.return_value = """
    return a + b
"""
        
        # Create the code completion provider
        provider = CodeCompletionProvider()
        
        # Test code for completion
        code = """def add(a, b):
    # Add two numbers
"""
        
        # Get completions
        completions = provider.get_completions(code, len(code))
        
        # Check that we got the expected completion
        assert len(completions) == 1
        assert completions[0]["text"].strip() == "return a + b"
        assert completions[0]["range"]["start"] == len(code)
        assert completions[0]["range"]["end"] == len(code)
        
        # Verify that the mock was called with the correct arguments
        mock_client.get_completion.assert_called_once()
        args, kwargs = mock_client.get_completion.call_args
        assert kwargs["prompt"] == code
        assert kwargs["model"] == "deepseek-r1-distill-llama-8b"
    
    @patch("rebeldesk.ai.code_completion.LocalAIClient")
    def test_get_signature_help(self, mock_client_class):
        """Test that we can get signature help from the code completion provider."""
        # Mock the LocalAIClient
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock the is_server_running method
        mock_client.is_server_running.return_value = True
        
        # Mock the get_models method
        mock_client.get_models.return_value = [
            {"id": "deepseek-r1-distill-llama-8b"}
        ]
        
        # Mock the get_completion method
        mock_client.get_completion.return_value = """
add(a: int, b: int) -> int
Parameters:
- a: The first number to add
- b: The second number to add
Returns:
- The sum of a and b
"""
        
        # Create the code completion provider
        provider = CodeCompletionProvider()
        
        # Test code for signature help
        code = """def add(a, b):
    return a + b

result = add("""
        
        # Get signature help
        signature_help = provider.get_signature_help(code, len(code))
        
        # Check that we got the expected signature help
        assert signature_help is not None
        assert len(signature_help["signatures"]) == 1
        assert "add(a: int, b: int) -> int" in signature_help["signatures"][0]["label"]
        assert "Parameters" in signature_help["signatures"][0]["documentation"]
        
        # Verify that the mock was called with the correct arguments
        mock_client.get_completion.assert_called_once()
        args, kwargs = mock_client.get_completion.call_args
        assert kwargs["prompt"].startswith(code)
        assert "What are the parameters" in kwargs["prompt"]
    
    @patch("rebeldesk.ai.code_completion.LocalAIClient")
    def test_get_hover_info(self, mock_client_class):
        """Test that we can get hover information from the code completion provider."""
        # Mock the LocalAIClient
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock the is_server_running method
        mock_client.is_server_running.return_value = True
        
        # Mock the get_models method
        mock_client.get_models.return_value = [
            {"id": "deepseek-r1-distill-llama-8b"}
        ]
        
        # Mock the get_completion method
        mock_client.get_completion.return_value = """
add is a function that takes two parameters, a and b, and returns their sum.
"""
        
        # Create the code completion provider
        provider = CodeCompletionProvider()
        
        # Test code for hover info
        code = """def add(a, b):
    return a + b

result = add(1, 2)
"""
        
        # Position of "add" in the last line
        position = code.rfind("add") + 3
        
        # Get hover info
        hover_info = provider.get_hover_info(code, position)
        
        # Check that we got the expected hover info
        assert hover_info is not None
        assert "add is a function" in hover_info["contents"]
        assert hover_info["range"]["start"] == position - 3
        assert hover_info["range"]["end"] == position
        
        # Verify that the mock was called with the correct arguments
        mock_client.get_completion.assert_called_once()
        args, kwargs = mock_client.get_completion.call_args
        assert kwargs["prompt"].startswith(code)
        assert "Explain what 'add' is" in kwargs["prompt"]
    
    @patch("rebeldesk.ai.code_completion.LocalAIClient")
    def test_server_not_running(self, mock_client_class):
        """Test that we handle the case where the server is not running."""
        # Mock the LocalAIClient
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock the is_server_running method
        mock_client.is_server_running.return_value = False
        
        # Create the code completion provider
        provider = CodeCompletionProvider()
        
        # Test code
        code = """def add(a, b):
    # Add two numbers
"""
        
        # Get completions
        completions = provider.get_completions(code, len(code))
        
        # Check that we got no completions
        assert len(completions) == 0
        
        # Get signature help
        signature_help = provider.get_signature_help(code, len(code))
        
        # Check that we got no signature help
        assert signature_help is None
        
        # Get hover info
        hover_info = provider.get_hover_info(code, len(code))
        
        # Check that we got no hover info
        assert hover_info is None
    
    @patch("rebeldesk.ai.code_completion.LocalAIClient")
    def test_model_not_available(self, mock_client_class):
        """Test that we handle the case where the model is not available."""
        # Mock the LocalAIClient
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock the is_server_running method
        mock_client.is_server_running.return_value = True
        
        # Mock the get_models method
        mock_client.get_models.return_value = [
            {"id": "different-model"}
        ]
        
        # Create the code completion provider
        provider = CodeCompletionProvider()
        
        # Test code
        code = """def add(a, b):
    # Add two numbers
"""
        
        # Get completions
        completions = provider.get_completions(code, len(code))
        
        # Check that we got no completions
        assert len(completions) == 0
