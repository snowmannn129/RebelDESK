#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the DocumentationGenerator with LMStudio.

This script tests the DocumentationGenerator with the deepseek-r1-distill-llama-8b model
running in LMStudio at http://127.0.0.1:1234.
"""

import os
import sys
import yaml
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add src directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent))

from src.ai.documentation_generator import DocumentationGenerator

def main():
    """Test the DocumentationGenerator with LMStudio."""
    # Create a configuration directly
    config = {
        'ai': {
            'enable': True,
            'model': {
                'type': 'local',
                'api_endpoint': 'http://127.0.0.1:1234/v1/completions',
                'local_path': '',
                'api_key_env': ''
            }
        }
    }
    
    print("Using configuration:")
    print(yaml.dump(config, default_flow_style=False))
    
    # Create DocumentationGenerator
    doc_generator = DocumentationGenerator(config)
    
    # Sample function to document
    sample_code = """
def calculate_fibonacci(n: int) -> int:
    \"\"\"\"\"\"
    if n <= 0:
        raise ValueError("Input must be a positive integer")
    elif n == 1 or n == 2:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
    
    print("\nGenerating docstring for sample function...")
    docstring = doc_generator.generate_function_docstring(sample_code, "calculate_fibonacci")
    
    print("\nGenerated docstring:")
    print(docstring)
    
    # Sample class to document
    sample_class_code = """
class DataProcessor:
    \"\"\"\"\"\"
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
    
    print("\nGenerating docstring for sample class...")
    class_docstring = doc_generator.generate_class_docstring(sample_class_code, "DataProcessor")
    
    print("\nGenerated class docstring:")
    print(class_docstring)
    
    print("\nGenerating docstring for sample method...")
    method_docstring = doc_generator.generate_method_docstring(sample_class_code, "DataProcessor", "process_data")
    
    print("\nGenerated method docstring:")
    print(method_docstring)

if __name__ == "__main__":
    main()
