#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the modular DocumentationGenerator implementation.
"""

import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ai.documentation_generator import DocumentationGenerator
from src.ai.documentation_generator.language_detector import detect_language

class TestDocumentationGenerator(unittest.TestCase):
    """Test cases for the DocumentationGenerator class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.generator = DocumentationGenerator()
    
    def test_detect_language(self):
        """Test language detection functionality."""
        # Python code
        python_code = """
def hello_world():
    print("Hello, World!")
"""
        self.assertEqual(detect_language(python_code), 'python')
        
        # JavaScript code
        js_code = """
function helloWorld() {
    console.log("Hello, World!");
}
"""
        self.assertEqual(detect_language(js_code), 'javascript')
        
        # TypeScript code
        ts_code = """
function helloWorld(): string {
    return "Hello, World!";
}
"""
        self.assertEqual(detect_language(ts_code), 'typescript')
    
    def test_generate_class_docstring(self):
        """Test class docstring generation."""
        python_class = """
class TestClass:
    def __init__(self):
        self.value = 0
"""
        docstring = self.generator.generate_class_docstring(python_class, 'TestClass')
        self.assertIsNotNone(docstring)
        self.assertIn('TestClass', docstring)
    
    def test_generate_function_docstring(self):
        """Test function docstring generation."""
        python_function = """
def test_function(param1, param2: int) -> str:
    return f"{param1} {param2}"
"""
        docstring = self.generator.generate_function_docstring(python_function, 'test_function')
        self.assertIsNotNone(docstring)
        # Check for the title-cased, space-separated version of the function name
        self.assertIn('Test Function', docstring)
        self.assertIn('param1', docstring)
        self.assertIn('param2', docstring)
        self.assertIn('str', docstring)

if __name__ == '__main__':
    unittest.main()
