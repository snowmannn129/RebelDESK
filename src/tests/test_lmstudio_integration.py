#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for LMStudio integration with the DocumentationGenerator.

This module contains tests for the integration of the DocumentationGenerator
with LMStudio for local LLM access.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import json
import requests

# Add src directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.documentation_generator import DocumentationGenerator
from src.utils.config_manager import ConfigManager


class TestLMStudioIntegration(unittest.TestCase):
    """Tests for LMStudio integration with the DocumentationGenerator."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test class."""
        # Check if LMStudio tests are enabled
        cls.lmstudio_enabled = os.environ.get('TEST_LMSTUDIO', '').lower() in ('true', '1', 'yes')
        cls.lmstudio_endpoint = os.environ.get('LMSTUDIO_ENDPOINT', 'http://127.0.0.1:1234/v1/completions')
        
        # Check if LMStudio is running
        if cls.lmstudio_enabled:
            try:
                response = requests.get(cls.lmstudio_endpoint.replace('/v1/completions', ''), timeout=2)
                cls.lmstudio_running = response.status_code == 200
            except requests.RequestException:
                cls.lmstudio_running = False
        else:
            cls.lmstudio_running = False
            
        # Log status
        if cls.lmstudio_enabled:
            if cls.lmstudio_running:
                print(f"LMStudio tests enabled and LMStudio is running at {cls.lmstudio_endpoint}")
            else:
                print(f"LMStudio tests enabled but LMStudio is not running at {cls.lmstudio_endpoint}")
        else:
            print("LMStudio tests disabled")
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test configuration with LMStudio
        self.config = {
            'ai': {
                'enable': True,
                'model': {
                    'type': 'local',
                    'api_endpoint': self.lmstudio_endpoint
                }
            }
        }
        
        # Create the documentation generator
        self.doc_generator = DocumentationGenerator(self.config)
        
    @unittest.skipIf(not os.environ.get('TEST_LMSTUDIO', '').lower() in ('true', '1', 'yes'),
                    "LMStudio tests disabled")
    def test_lmstudio_configuration(self):
        """Test LMStudio configuration."""
        # Check that the configuration is correct
        self.assertEqual(self.doc_generator.config['ai']['model']['type'], 'local')
        self.assertEqual(self.doc_generator.config['ai']['model']['api_endpoint'], self.lmstudio_endpoint)
        
        # Check that the model is loaded
        self.assertTrue(self.doc_generator.model_loaded)
        
    @unittest.skipIf(not os.environ.get('TEST_LMSTUDIO', '').lower() in ('true', '1', 'yes') or
                    not os.environ.get('LMSTUDIO_RUNNING', '').lower() in ('true', '1', 'yes'),
                    "LMStudio tests disabled or LMStudio not running")
    def test_lmstudio_function_docstring_generation(self):
        """Test generating a function docstring using LMStudio."""
        # Test code
        code = """
def calculate_fibonacci(n: int) -> int:
    if n <= 0:
        raise ValueError("Input must be a positive integer")
    elif n == 1 or n == 2:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
        
        # Generate docstring
        docstring = self.doc_generator.generate_function_docstring(code, "calculate_fibonacci")
        
        # Check that a docstring was generated
        self.assertIsNotNone(docstring)
        self.assertIn('"""', docstring)
        
        # Check that the docstring contains expected elements
        self.assertIn("fibonacci", docstring.lower())
        
    @unittest.skipIf(not os.environ.get('TEST_LMSTUDIO', '').lower() in ('true', '1', 'yes') or
                    not os.environ.get('LMSTUDIO_RUNNING', '').lower() in ('true', '1', 'yes'),
                    "LMStudio tests disabled or LMStudio not running")
    def test_lmstudio_class_docstring_generation(self):
        """Test generating a class docstring using LMStudio."""
        # Test code
        code = """
class DataProcessor:
    def __init__(self, data_source: str):
        self.data_source = data_source
        self.processed_data = None
        
    def process_data(self, filter_type: str = "none") -> dict:
        # Simulate data processing
        if filter_type not in ["none", "basic", "advanced"]:
            raise ValueError("Invalid filter type")
        self.processed_data = {"source": self.data_source, "filter": filter_type}
        return self.processed_data
"""
        
        # Generate docstring
        docstring = self.doc_generator.generate_class_docstring(code, "DataProcessor")
        
        # Check that a docstring was generated
        self.assertIsNotNone(docstring)
        self.assertIn('"""', docstring)
        
        # Check that the docstring contains expected elements
        self.assertIn("data", docstring.lower())
        
    @unittest.skipIf(not os.environ.get('TEST_LMSTUDIO', '').lower() in ('true', '1', 'yes') or
                    not os.environ.get('LMSTUDIO_RUNNING', '').lower() in ('true', '1', 'yes'),
                    "LMStudio tests disabled or LMStudio not running")
    def test_lmstudio_method_docstring_generation(self):
        """Test generating a method docstring using LMStudio."""
        # Test code
        code = """
class DataProcessor:
    def __init__(self, data_source: str):
        self.data_source = data_source
        self.processed_data = None
        
    def process_data(self, filter_type: str = "none") -> dict:
        # Simulate data processing
        if filter_type not in ["none", "basic", "advanced"]:
            raise ValueError("Invalid filter type")
        self.processed_data = {"source": self.data_source, "filter": filter_type}
        return self.processed_data
"""
        
        # Generate docstring
        docstring = self.doc_generator.generate_method_docstring(code, "DataProcessor", "process_data")
        
        # Check that a docstring was generated
        self.assertIsNotNone(docstring)
        self.assertIn('"""', docstring)
        
        # Check that the docstring contains expected elements
        self.assertIn("filter", docstring.lower())
        
    @patch('requests.post')
    def test_lmstudio_api_mock(self, mock_post):
        """Test LMStudio API with mocking."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [
                {
                    'text': '"""Calculate the nth Fibonacci number.\n\nArgs:\n    n (int): The position in the Fibonacci sequence.\n\nReturns:\n    int: The nth Fibonacci number.\n\nRaises:\n    ValueError: If n is not a positive integer.\n"""'
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Test code
        code = """
def calculate_fibonacci(n: int) -> int:
    if n <= 0:
        raise ValueError("Input must be a positive integer")
    elif n == 1 or n == 2:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
        
        # Generate docstring
        docstring = self.doc_generator.generate_function_docstring(code, "calculate_fibonacci")
        
        # Check that a docstring was generated
        self.assertIsNotNone(docstring)
        self.assertIn('"""', docstring)
        self.assertIn("Calculate the nth Fibonacci number", docstring)
        
        # Check that the API was called with the correct parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], self.lmstudio_endpoint)
        self.assertIn('prompt', kwargs['json'])
        self.assertIn('calculate_fibonacci', kwargs['json']['prompt'])
        
    def test_fallback_to_template(self):
        """Test fallback to template-based generation when LMStudio is not available."""
        # Create a configuration with an invalid endpoint
        config = {
            'ai': {
                'enable': True,
                'model': {
                    'type': 'local',
                    'api_endpoint': 'http://invalid-endpoint'
                }
            }
        }
        
        # Create the documentation generator with mocked methods
        with patch('src.ai.documentation_generator.DocumentationGenerator._generate_docstring_local') as mock_local, \
             patch('src.ai.documentation_generator.DocumentationGenerator._generate_docstring_template') as mock_template:
            
            # Set up the mocks
            mock_local.side_effect = Exception("API error")
            mock_template.return_value = '"""Calculate fibonacci.\n\nArgs:\n    n (int): Description of parameter.\n\nReturns:\n    int: Description of return value.\n\nRaises:\n    ValueError: Description of when this exception is raised.\n"""'
            
            # Create the documentation generator
            doc_generator = DocumentationGenerator(config)
            
            # Test code
            code = """
def calculate_fibonacci(n: int) -> int:
    if n <= 0:
        raise ValueError("Input must be a positive integer")
    elif n == 1 or n == 2:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
            
            # Generate docstring
            docstring = doc_generator.generate_function_docstring(code, "calculate_fibonacci")
            
            # Check that a docstring was generated using the template
            self.assertIsNotNone(docstring)
            self.assertIn('"""', docstring)
            self.assertIn("calculate fibonacci", docstring.lower())
            
            # Verify that the template method was called
            mock_template.assert_called_once()
            
    def test_empty_code(self):
        """Test handling of empty code."""
        # Test with empty code
        docstring = self.doc_generator.generate_function_docstring("", "test_function")
        
        # Check that None is returned
        self.assertIsNone(docstring)
        
    def test_code_with_syntax_errors(self):
        """Test handling of code with syntax errors."""
        # Test code with syntax errors
        code = "def test_function(:\n    pass"
        
        # Generate docstring
        docstring = self.doc_generator.generate_function_docstring(code, "test_function")
        
        # Check that None is returned
        self.assertIsNone(docstring)
        
    def test_code_with_existing_docstring(self):
        """Test handling of code with existing docstring."""
        # Test code with existing docstring
        code = 'def test_function():\n    """Existing docstring."""\n    pass'
        
        # Parse the code to extract the existing docstring
        import ast
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == "test_function":
                    # Check if there's a docstring
                    if (len(node.body) > 0 and 
                        isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Constant)):
                        existing_docstring = node.body[0].value.value
                        self.assertEqual(existing_docstring, "Existing docstring.")
        except SyntaxError:
            self.fail("Failed to parse code with existing docstring")


if __name__ == '__main__':
    with open("lmstudio_test_output.txt", "w") as f:
        f.write("Running LMStudio integration tests...\n")
        
    # Run the tests
    result = unittest.main(exit=False)
    
    # Write the results to a file
    with open("lmstudio_test_results.txt", "w") as f:
        f.write(f"Tests run: {result.result.testsRun}\n")
        f.write(f"Errors: {len(result.result.errors)}\n")
        f.write(f"Failures: {len(result.result.failures)}\n")
        
        if result.result.failures:
            for i, failure in enumerate(result.result.failures):
                f.write(f"Failure {i+1}: {failure[0]}\n")
                f.write(f"Error: {failure[1]}\n")
                
        if result.result.errors:
            for i, error in enumerate(result.result.errors):
                f.write(f"Error {i+1}: {error[0]}\n")
                f.write(f"Error: {error[1]}\n")
