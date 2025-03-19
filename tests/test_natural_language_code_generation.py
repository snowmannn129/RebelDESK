"""
Tests for the natural language code generation module.
"""

import pytest
import json
from unittest.mock import patch, MagicMock

from src.ai.natural_language_code_generation import NaturalLanguageCodeGenerator

# Skip the test if the local AI server is not running
def is_local_ai_server_running():
    """Check if the local AI server is running."""
    try:
        import requests
        response = requests.get("http://127.0.0.1:1234/health", timeout=2)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout, ImportError):
        return False

pytestmark = pytest.mark.skipif(
    not is_local_ai_server_running(),
    reason="Local AI server is not running"
)

class TestNaturalLanguageCodeGenerator:
    """Tests for the natural language code generation module."""
    
    def test_initialization(self):
        """Test that the generator initializes correctly."""
        generator = NaturalLanguageCodeGenerator()
        assert generator.model_name == "deepseek-r1-distill-llama-8b"
        assert generator.max_tokens == 500
        assert generator.temperature == 0.2
        assert generator.top_p == 0.95
        assert generator.default_language == "python"
    
    def test_initialization_with_config(self):
        """Test that the generator initializes correctly with a custom config."""
        config = {
            "base_url": "http://localhost:8080",
            "model_name": "test-model",
            "max_tokens": 1000,
            "temperature": 0.5,
            "top_p": 0.8,
            "default_language": "javascript"
        }
        generator = NaturalLanguageCodeGenerator(config)
        assert generator.model_name == "test-model"
        assert generator.max_tokens == 1000
        assert generator.temperature == 0.5
        assert generator.top_p == 0.8
        assert generator.default_language == "javascript"
    
    @patch("src.ai.local_ai_client.LocalAIClient.is_server_running")
    def test_is_available(self, mock_is_server_running):
        """Test that is_available returns the correct value."""
        mock_is_server_running.return_value = True
        generator = NaturalLanguageCodeGenerator()
        assert generator.is_available() is True
        
        mock_is_server_running.return_value = False
        assert generator.is_available() is False
        
        mock_is_server_running.side_effect = Exception("Test exception")
        assert generator.is_available() is False
    
    @patch("src.ai.local_ai_client.LocalAIClient.get_completion")
    @patch("src.ai.local_ai_client.LocalAIClient.is_server_running")
    def test_generate_code(self, mock_is_server_running, mock_get_completion):
        """Test that generate_code returns the correct value."""
        mock_is_server_running.return_value = True
        mock_get_completion.return_value = """```python
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
```"""
        
        generator = NaturalLanguageCodeGenerator()
        result = generator.generate_code("Create a function to calculate the nth Fibonacci number")
        
        assert result["success"] is True
        assert "fibonacci" in result["code"]
        assert result["language"] == "python"
        
        # Test with a different language
        result = generator.generate_code(
            "Create a function to calculate the nth Fibonacci number",
            language="javascript"
        )
        
        assert result["success"] is True
        assert "fibonacci" in result["code"]
        assert result["language"] == "javascript"
        
        # Test with context
        context = """def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n-1)
"""
        
        result = generator.generate_code(
            "Create a function to calculate the nth Fibonacci number",
            context=context
        )
        
        assert result["success"] is True
        assert "fibonacci" in result["code"]
        assert result["language"] == "python"
        
        # Test when server is not available
        mock_is_server_running.return_value = False
        result = generator.generate_code("Create a function to calculate the nth Fibonacci number")
        
        assert result["success"] is False
        assert result["error"] == "Natural language code generator is not available"
        assert result["code"] == ""
        assert result["language"] == "python"
        
        # Test when an exception occurs
        mock_is_server_running.return_value = True
        mock_get_completion.side_effect = Exception("Test exception")
        result = generator.generate_code("Create a function to calculate the nth Fibonacci number")
        
        assert result["success"] is False
        assert result["error"] == "Test exception"
        assert result["code"] == ""
        assert result["language"] == "python"
    
    @patch("src.ai.local_ai_client.LocalAIClient.get_completion")
    @patch("src.ai.local_ai_client.LocalAIClient.is_server_running")
    def test_generate_code_with_explanation(self, mock_is_server_running, mock_get_completion):
        """Test that generate_code_with_explanation returns the correct value."""
        mock_is_server_running.return_value = True
        mock_get_completion.return_value = """```python
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
```

## Explanation
This function calculates the nth Fibonacci number using recursion.
- If n is less than or equal to 0, it returns 0.
- If n is 1, it returns 1.
- Otherwise, it returns the sum of the (n-1)th and (n-2)th Fibonacci numbers.
"""
        
        generator = NaturalLanguageCodeGenerator()
        result = generator.generate_code_with_explanation("Create a function to calculate the nth Fibonacci number")
        
        assert result["success"] is True
        assert "fibonacci" in result["code"]
        assert "recursion" in result["explanation"]
        assert result["language"] == "python"
        
        # Test when server is not available
        mock_is_server_running.return_value = False
        result = generator.generate_code_with_explanation("Create a function to calculate the nth Fibonacci number")
        
        assert result["success"] is False
        assert result["error"] == "Natural language code generator is not available"
        assert result["code"] == ""
        assert result["explanation"] == ""
        assert result["language"] == "python"
        
        # Test when an exception occurs
        mock_is_server_running.return_value = True
        mock_get_completion.side_effect = Exception("Test exception")
        result = generator.generate_code_with_explanation("Create a function to calculate the nth Fibonacci number")
        
        assert result["success"] is False
        assert result["error"] == "Test exception"
        assert result["code"] == ""
        assert result["explanation"] == ""
        assert result["language"] == "python"
    
    @patch("src.ai.local_ai_client.LocalAIClient.get_completion")
    @patch("src.ai.local_ai_client.LocalAIClient.is_server_running")
    def test_improve_code(self, mock_is_server_running, mock_get_completion):
        """Test that improve_code returns the correct value."""
        mock_is_server_running.return_value = True
        mock_get_completion.return_value = """```python
def fibonacci(n):
    # Calculate the nth Fibonacci number
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
```"""
        
        generator = NaturalLanguageCodeGenerator()
        code = """def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
"""
        
        result = generator.improve_code(code, "Add a docstring")
        
        assert result["success"] is True
        assert "fibonacci" in result["code"]
        assert '# Calculate the nth Fibonacci number' in result["code"]
        assert result["language"] == "python"
        
        # Test when server is not available
        mock_is_server_running.return_value = False
        result = generator.improve_code(code, "Add a docstring")
        
        assert result["success"] is False
        assert result["error"] == "Natural language code generator is not available"
        assert result["code"] == code
        assert result["language"] == "python"
        
        # Test when an exception occurs
        mock_is_server_running.return_value = True
        mock_get_completion.side_effect = Exception("Test exception")
        result = generator.improve_code(code, "Add a docstring")
        
        assert result["success"] is False
        assert result["error"] == "Test exception"
        assert result["code"] == code
        assert result["language"] == "python"
    
    def test_clean_generated_code(self):
        """Test that _clean_generated_code returns the correct value."""
        generator = NaturalLanguageCodeGenerator()
        
        # Test with markdown code block
        generated_code = """```python
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
```"""
        
        cleaned_code = generator._clean_generated_code(generated_code, "python")
        assert "```" not in cleaned_code
        assert "def fibonacci(n):" in cleaned_code
        
        # Test without markdown code block
        generated_code = """def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)"""
        
        cleaned_code = generator._clean_generated_code(generated_code, "python")
        assert cleaned_code == generated_code
    
    def test_parse_code_and_explanation(self):
        """Test that _parse_code_and_explanation returns the correct value."""
        generator = NaturalLanguageCodeGenerator()
        
        # Test with markdown code block and explanation
        response = """```python
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
```

## Explanation
This function calculates the nth Fibonacci number using recursion.
- If n is less than or equal to 0, it returns 0.
- If n is 1, it returns 1.
- Otherwise, it returns the sum of the (n-1)th and (n-2)th Fibonacci numbers.
"""
        
        code, explanation = generator._parse_code_and_explanation(response, "python")
        assert "def fibonacci(n):" in code
        assert "recursion" in explanation
        
        # Test with markdown code block but no explanation
        response = """```python
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
```"""
        
        code, explanation = generator._parse_code_and_explanation(response, "python")
        assert "def fibonacci(n):" in code
        assert explanation == ""
        
        # Test with no markdown code block but with explanation header
        response = """def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

## Explanation
This function calculates the nth Fibonacci number using recursion."""
        
        code, explanation = generator._parse_code_and_explanation(response, "python")
        assert "def fibonacci(n):" in code
        assert "recursion" in explanation
        
        # Test with no markdown code block and no explanation header
        response = """def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)"""
        
        code, explanation = generator._parse_code_and_explanation(response, "python")
        assert "def fibonacci(n):" in code
        assert explanation == ""
    
    def test_infer_language(self):
        """Test that _infer_language returns the correct value."""
        generator = NaturalLanguageCodeGenerator()
        
        # Test Python
        code = """def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
"""
        
        language = generator._infer_language(code)
        assert language == "python"
        
        # Test JavaScript
        code = """function fibonacci(n) {
    if (n <= 0) {
        return 0;
    } else if (n === 1) {
        return 1;
    } else {
        return fibonacci(n-1) + fibonacci(n-2);
    }
}
"""
        
        language = generator._infer_language(code)
        assert language == "javascript"
        
        # Test Java
        code = """public class Fibonacci extends Object {
    public static int fibonacci(int n) {
        if (n <= 0) {
            return 0;
        } else if (n == 1) {
            return 1;
        } else {
            return fibonacci(n-1) + fibonacci(n-2);
        }
    }
}
"""
        
        language = generator._infer_language(code)
        assert language == "java"
        
        # Test C++
        code = """#include <iostream>

int fibonacci(int n) {
    if (n <= 0) {
        return 0;
    } else if (n == 1) {
        return 1;
    } else {
        return fibonacci(n-1) + fibonacci(n-2);
    }
}

int main() {
    std::cout << fibonacci(10) << std::endl;
    return 0;
}
"""
        
        language = generator._infer_language(code)
        assert language == "c++"
        
        # Test Rust
        code = """fn fibonacci(n: u32) -> u32 {
    if n <= 0 {
        return 0;
    } else if n == 1 {
        return 1;
    } else {
        return fibonacci(n-1) + fibonacci(n-2);
    }
}
"""
        
        language = generator._infer_language(code)
        assert language == "rust"
        
        # Test Go
        code = """package main

import "fmt"

func fibonacci(n int) int {
    if n <= 0 {
        return 0
    } else if n == 1 {
        return 1
    } else {
        return fibonacci(n-1) + fibonacci(n-2)
    }
}

func main() {
    fmt.Println(fibonacci(10))
}
"""
        
        language = generator._infer_language(code)
        assert language == "go"
        
        # Test unknown language
        code = """fibonacci = function(n)
    if n <= 0 then
        return 0
    elseif n == 1 then
        return 1
    else
        return fibonacci(n-1) + fibonacci(n-2)
    end
end
"""
        
        language = generator._infer_language(code)
        assert language == "python"  # Default language
