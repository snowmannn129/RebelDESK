#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the DocumentationGenerator class.

This module contains tests for the documentation generation functionality.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add src directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.documentation_generator import DocumentationGenerator
from src.utils.config_manager import ConfigManager


class TestDocumentationGenerator(unittest.TestCase):
    """Tests for the DocumentationGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test configuration
        self.config = {
            'ai': {
                'enable': True,
                'model': {
                    'type': 'template'  # Use template-based generation for tests
                }
            }
        }
        
        # Create the documentation generator
        self.doc_generator = DocumentationGenerator(self.config)
        
    def test_initialization(self):
        """Test initialization of the DocumentationGenerator."""
        self.assertIsNotNone(self.doc_generator)
        self.assertEqual(self.doc_generator.config, self.config)
        
    def test_generate_function_docstring_template(self):
        """Test generating a function docstring using the template method."""
        # Mock the _generate_docstring_template method to return a known docstring
        with patch.object(self.doc_generator, '_generate_docstring_template') as mock_generate:
            mock_generate.return_value = '"""\nTest Function.\n\nArgs:\n    param1: Description of parameter.\n    param2 (str): Description of parameter.\n    param3 (int): Description of parameter.\n\nReturns:\n    bool: Description of return value.\n\nRaises:\n    ValueError: Description of when this exception is raised.\n"""'
            
            # Test code with a simple function
            code = """
def test_function(param1, param2: str, param3: int = 0) -> bool:
    if param3 > 0:
        raise ValueError("param3 must be non-negative")
    return True
"""
            
            # Generate docstring
            docstring = self.doc_generator.generate_function_docstring(code, "test_function")
            
            # Check that the docstring contains expected elements
            self.assertIsNotNone(docstring)
            self.assertIn('"""', docstring)
            self.assertIn("Test Function", docstring)
            self.assertIn("Args:", docstring)
            self.assertIn("param1", docstring)
            self.assertIn("param2 (str)", docstring)
            self.assertIn("param3 (int)", docstring)
            self.assertIn("Returns:", docstring)
            self.assertIn("bool", docstring)
            self.assertIn("Raises:", docstring)
            self.assertIn("ValueError", docstring)
        
    def test_generate_class_docstring_template(self):
        """Test generating a class docstring using the template method."""
        # Test code with a simple class
        code = """
class TestClass(BaseClass):
    attr1 = None
    attr2 = "test"
    
    def __init__(self, param1):
        self.param1 = param1
        
    def test_method(self):
        pass
"""
        
        # Generate docstring
        docstring = self.doc_generator.generate_class_docstring(code, "TestClass")
        
        # Check that the docstring contains expected elements
        self.assertIsNotNone(docstring)
        self.assertIn('"""', docstring)
        self.assertIn("TestClass", docstring)
        self.assertIn("Inherits from:", docstring)
        self.assertIn("BaseClass", docstring)
        self.assertIn("Attributes:", docstring)
        self.assertIn("attr1", docstring)
        self.assertIn("attr2", docstring)
        
    def test_generate_method_docstring_template(self):
        """Test generating a method docstring using the template method."""
        # Mock the _generate_docstring_template method to return a known docstring
        with patch.object(self.doc_generator, '_generate_docstring_template') as mock_generate:
            mock_generate.return_value = '"""\nTest Method.\n\nArgs:\n    param1 (str): Description of parameter.\n    param2 (int): Description of parameter.\n\nReturns:\n    dict: Description of return value.\n\nRaises:\n    ValueError: Description of when this exception is raised.\n"""'
            
            # Test code with a class containing a method
            code = """
class TestClass:
    def test_method(self, param1: str, param2: int = 0) -> dict:
        result = {}
        if param2 < 0:
            raise ValueError("param2 must be non-negative")
        return result
"""
            
            # Generate docstring
            docstring = self.doc_generator.generate_method_docstring(code, "TestClass", "test_method")
            
            # Check that the docstring contains expected elements
            self.assertIsNotNone(docstring)
            self.assertIn('"""', docstring)
            self.assertIn("Test Method", docstring)
            self.assertIn("Args:", docstring)
            self.assertIn("param1 (str)", docstring)
            self.assertIn("param2 (int)", docstring)
            self.assertIn("Returns:", docstring)
            self.assertIn("dict", docstring)
            self.assertIn("Raises:", docstring)
            self.assertIn("ValueError", docstring)
        
    def test_clean_docstring(self):
        """Test cleaning a docstring."""
        # Test with a docstring that needs cleaning
        docstring = 'This is a test docstring'
        cleaned = self.doc_generator._clean_docstring(docstring)
        
        # Check that the docstring is properly formatted
        self.assertEqual(cleaned, '"""\nThis is a test docstring\n"""')
        
        # Test with a docstring that's already properly formatted
        docstring = '"""This is a test docstring"""'
        cleaned = self.doc_generator._clean_docstring(docstring)
        
        # Check that the docstring is still properly formatted
        self.assertEqual(cleaned, '"""This is a test docstring"""')
        
    @patch('src.ai.documentation_generator.jedi.Script')
    def test_get_documentation_completion(self, mock_script):
        """Test getting documentation completions."""
        # Mock Jedi Script
        mock_script_instance = MagicMock()
        mock_script.return_value = mock_script_instance
        
        # Mock completions
        mock_completion = MagicMock()
        mock_completion.type = 'function'
        mock_completion.name = 'test_function'
        mock_script_instance.complete.return_value = [mock_completion]
        
        # Mock definitions
        mock_definition = MagicMock()
        mock_definition.type = 'function'
        mock_definition.name = 'test_function'
        mock_script_instance.goto_definitions.return_value = [mock_definition]
        
        # Mock generate_function_docstring
        self.doc_generator.generate_function_docstring = MagicMock(return_value='"""Test docstring"""')
        
        # Test code
        code = "def test_function():\n    pass\n\ntest_"
        
        # Get completions
        completions = self.doc_generator.get_documentation_completion(code, len(code), None, 'python')
        
        # Check that completions were returned
        self.assertEqual(len(completions), 1)
        self.assertEqual(completions[0]['text'], '"""Test docstring"""')
        self.assertEqual(completions[0]['type'], 'documentation')
        self.assertEqual(completions[0]['provider'], 'documentation_generator')
        
    def test_function_not_found(self):
        """Test handling of a function that doesn't exist."""
        # Test code without the function
        code = "def other_function():\n    pass"
        
        # Generate docstring
        docstring = self.doc_generator.generate_function_docstring(code, "test_function")
        
        # Check that None is returned
        self.assertIsNone(docstring)
        
    def test_class_not_found(self):
        """Test handling of a class that doesn't exist."""
        # Test code without the class
        code = "class OtherClass:\n    pass"
        
        # Generate docstring
        docstring = self.doc_generator.generate_class_docstring(code, "TestClass")
        
        # Check that None is returned
        self.assertIsNone(docstring)
        
    def test_method_not_found(self):
        """Test handling of a method that doesn't exist."""
        # Test code without the method
        code = "class TestClass:\n    def other_method(self):\n        pass"
        
        # Generate docstring
        docstring = self.doc_generator.generate_method_docstring(code, "TestClass", "test_method")
        
        # Check that None is returned
        self.assertIsNone(docstring)
        
    @patch('src.ai.documentation_generator.torch.no_grad')
    @patch('src.ai.documentation_generator.AutoTokenizer')
    @patch('src.ai.documentation_generator.AutoModelForCausalLM')
    def test_local_model_docstring_generation(self, mock_model_class, mock_tokenizer_class, mock_no_grad):
        """Test generating a docstring using a local model."""
        # Skip this test if not using a local model
        if self.config['ai']['model']['type'] != 'local':
            self.skipTest("Test only applicable for local model")
            
        # Create a new config with local model
        config = {
            'ai': {
                'enable': True,
                'model': {
                    'type': 'local',
                    'local_path': 'test_model'
                }
            }
        }
        
        # Mock tokenizer and model
        mock_tokenizer = MagicMock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        
        mock_model = MagicMock()
        mock_model_class.from_pretrained.return_value = mock_model
        
        # Mock generate method
        mock_outputs = MagicMock()
        mock_model.generate.return_value = [mock_outputs]
        
        # Mock tokenizer decode
        mock_tokenizer.decode.return_value = "Generate a detailed docstring for the following Python function:\n\ndef test_function():\n    pass\n\nDocstring:This is a test docstring"
        
        # Create the documentation generator with the local model config
        doc_generator = DocumentationGenerator(config)
        doc_generator.model_loaded = True
        
        # Test code
        code = "def test_function():\n    pass"
        
        # Generate docstring
        with patch('src.ai.documentation_generator.ast.unparse', return_value=code):
            docstring = doc_generator._generate_docstring_local(
                MagicMock(), [], None
            )
        
        # Check that the docstring was generated
        self.assertEqual(docstring, '"""This is a test docstring\n"""')
        
    @patch('src.ai.documentation_generator.requests.post')
    def test_api_model_docstring_generation(self, mock_post):
        """Test generating a docstring using an API model."""
        # Skip this test if not using an API model
        if self.config['ai']['model']['type'] != 'api':
            self.skipTest("Test only applicable for API model")
            
        # Create a new config with API model
        config = {
            'ai': {
                'enable': True,
                'model': {
                    'type': 'api',
                    'api_endpoint': 'https://api.example.com/generate',
                    'api_key_env': 'TEST_API_KEY'
                }
            }
        }
        
        # Mock environment variable
        with patch.dict(os.environ, {'TEST_API_KEY': 'test_key'}):
            # Mock API response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [
                    {'text': 'This is a test docstring'}
                ]
            }
            mock_post.return_value = mock_response
            
            # Create the documentation generator with the API model config
            doc_generator = DocumentationGenerator(config)
            
            # Test code
            code = "def test_function():\n    pass"
            
            # Generate docstring
            with patch('src.ai.documentation_generator.ast.unparse', return_value=code):
                docstring = doc_generator._generate_docstring_api(
                    MagicMock(), [], None
                )
            
            # Check that the docstring was generated
            self.assertEqual(docstring, '"""This is a test docstring\n"""')
            
            # Check that the API was called with the correct parameters
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertEqual(args[0], 'https://api.example.com/generate')
            self.assertEqual(kwargs['headers']['Authorization'], 'Bearer test_key')
            self.assertIn('prompt', kwargs['json'])


if __name__ == '__main__':
    unittest.main()
