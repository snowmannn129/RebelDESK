#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the DocumentationGenerator with LMStudio.

This script tests the DocumentationGenerator with a local LLM model running in LMStudio.
"""

import os
import sys
import yaml
from pathlib import Path

# Add src directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config_manager import ConfigManager
from src.ai.documentation_generator import DocumentationGenerator

def main():
    """Test the DocumentationGenerator with LMStudio."""
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Also load directly from file for comparison
    print("\nLoading config directly from file for comparison:")
    try:
        with open("config.yaml", 'r', encoding='utf-8') as f:
            direct_config = yaml.safe_load(f) or {}
            print("Direct config AI section:")
            print(yaml.dump(direct_config.get('ai', {}), default_flow_style=False))
    except Exception as e:
        print(f"Error loading direct config: {e}")
    
    print("Configuration loaded:")
    print(f"  AI enabled: {config.get('ai', {}).get('enable', False)}")
    print(f"  Model type: {config.get('ai', {}).get('model', {}).get('type', 'unknown')}")
    print(f"  API endpoint: {config.get('ai', {}).get('model', {}).get('api_endpoint', 'none')}")
    
    # Print full AI configuration for debugging
    print("\nFull AI configuration:")
    print(yaml.dump(config.get('ai', {}), default_flow_style=False))
    
    # Determine which model is being used
    model_type = config.get('ai', {}).get('model', {}).get('type', 'unknown')
    if model_type == 'local':
        api_endpoint = config.get('ai', {}).get('model', {}).get('api_endpoint', '')
        if api_endpoint:
            print(f"  Using local model via API endpoint: {api_endpoint}")
            print("  This is likely using LMStudio with deepseek-r1-distill-llama-8b")
        else:
            model_path = config.get('ai', {}).get('model', {}).get('local_path', '')
            if model_path:
                print(f"  Using local model from path: {model_path}")
            else:
                print("  Using default CodeLlama-7b-hf model")
    elif model_type == 'api':
        print("  Using remote API model")
    
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
