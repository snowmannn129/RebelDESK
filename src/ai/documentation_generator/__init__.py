#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Documentation Generator for RebelDESK.

This module provides functionality to generate documentation for code elements
such as functions, classes, and methods. Supports multiple programming languages
including Python, JavaScript, TypeScript, C++, and Java.
"""

import logging
from typing import Dict, Any, Optional

from .language_detector import detect_language
from .docstring_extractors import (
    extract_docstring_from_text,
    clean_docstring
)
from .docstring_generators import (
    generate_class_docstring,
    generate_method_docstring,
    generate_function_docstring
)

logger = logging.getLogger(__name__)

class DocumentationGenerator:
    """Generates documentation for code elements in multiple programming languages."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the documentation generator.
        
        Args:
            config (Dict[str, Any], optional): Configuration settings.
        """
        self.config = config or {}
        self.model = None
        self.tokenizer = None
        self.model_loaded = False
        
        # Initialize model if AI is enabled
        if self.config.get('ai', {}).get('enable', True):
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the AI model for documentation generation."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            # Get model configuration
            model_type = self.config.get('ai', {}).get('model', {}).get('type', 'local')
            api_endpoint = self.config.get('ai', {}).get('model', {}).get('api_endpoint', '')
            
            # Check if we're using a local model with API endpoint (LMStudio)
            if model_type == 'local' and api_endpoint:
                # Using LMStudio or similar API for local model
                self.model_loaded = True
                logger.info(f"Using local model via API endpoint: {api_endpoint}")
                return
            
            if model_type == 'local':
                # Load local model
                model_path = self.config.get('ai', {}).get('model', {}).get('local_path', '')
                
                if not model_path:
                    # Use a default model if no path is specified
                    model_name = "codellama/CodeLlama-7b-hf"
                    logger.info(f"No local model path specified, using {model_name}")
                else:
                    model_name = model_path
                    
                # Load tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                
                # Load model with reduced precision to save memory
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    low_cpu_mem_usage=True
                )
                
                self.model_loaded = True
                logger.info("Local model loaded successfully for documentation generation")
                
            elif model_type == 'api':
                # API-based model doesn't need to load anything locally
                self.model_loaded = True
                logger.info("API-based model configured for documentation generation")
                
        except Exception as e:
            logger.error(f"Error initializing documentation model: {e}", exc_info=True)
    
    def generate_class_docstring(self, code: str, class_name: str, language: Optional[str] = None) -> Optional[str]:
        """
        Generate a docstring for a class.
        
        Args:
            code (str): The source code containing the class.
            class_name (str): The name of the class.
            language (str, optional): The programming language.
            
        Returns:
            Optional[str]: The generated docstring, or None if generation failed.
        """
        # Detect language if not provided
        detected_language = detect_language(code, language=language)
        return generate_class_docstring(code, class_name, detected_language)
    
    def generate_method_docstring(self, code: str, class_name: str, method_name: str, language: Optional[str] = None) -> Optional[str]:
        """
        Generate a docstring for a class method.
        
        Args:
            code (str): The source code containing the class and method.
            class_name (str): The name of the class.
            method_name (str): The name of the method.
            language (str, optional): The programming language.
            
        Returns:
            Optional[str]: The generated docstring, or None if generation failed.
        """
        # Detect language if not provided
        detected_language = detect_language(code, language=language)
        return generate_method_docstring(code, class_name, method_name, detected_language)
    
    def generate_function_docstring(self, code: str, function_name: str, language: Optional[str] = None) -> Optional[str]:
        """
        Generate a docstring for a function.
        
        Args:
            code (str): The source code containing the function.
            function_name (str): The name of the function.
            language (str, optional): The programming language.
            
        Returns:
            Optional[str]: The generated docstring, or None if generation failed.
        """
        # Detect language if not provided
        detected_language = detect_language(code, language=language)
        return generate_function_docstring(code, function_name, detected_language)
    
    def extract_docstring_from_text(self, generated_text: str, language: str = 'python') -> str:
        """
        Extract a docstring from generated text.
        
        Args:
            generated_text (str): The text generated by the AI model.
            language (str, optional): The programming language.
            
        Returns:
            str: The extracted docstring.
        """
        return extract_docstring_from_text(generated_text, language)
    
    def clean_docstring(self, docstring: str, language: str = 'python') -> str:
        """
        Clean up a generated docstring.
        
        Args:
            docstring (str): The docstring to clean.
            language (str, optional): The programming language.
            
        Returns:
            str: The cleaned docstring.
        """
        return clean_docstring(docstring, language)
