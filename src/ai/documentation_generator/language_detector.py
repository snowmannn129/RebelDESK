#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Language detection module for the documentation generator.

This module provides functionality to detect the programming language
of code snippets based on syntax patterns and file extensions.
"""

import re
import os
from typing import Optional

def detect_language(code: str, file_path: Optional[str] = None, language: Optional[str] = None) -> str:
    """
    Detect the programming language of the code.
    
    Args:
        code (str): The code to analyze.
        file_path (str, optional): The path to the file being edited.
        language (str, optional): The programming language if already known.
        
    Returns:
        str: The detected programming language.
    """
    if language:
        return language.lower()
        
    # Try to determine language from file extension
    if file_path:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.py':
            return 'python'
        elif ext in ['.js', '.jsx']:
            return 'javascript'
        elif ext in ['.ts', '.tsx']:
            return 'typescript'
        elif ext in ['.cpp', '.cc', '.cxx', '.c++', '.hpp', '.hh', '.hxx', '.h', '.h++']:
            return 'cpp'
        elif ext == '.java':
            return 'java'
    
    # Try to determine language from code content
    # Check for JavaScript/TypeScript first (more specific patterns)
    if re.search(r'function\s+\w+\s*\(.*?\)', code) or re.search(r'(const|let|var)\s+\w+\s*=', code):
        # Check for TypeScript-specific syntax
        if re.search(r':\s*(string|number|boolean|any)\b', code) or re.search(r'interface\s+\w+\s*\{', code):
            return 'typescript'
        else:
            return 'javascript'
    # Check for Java
    elif re.search(r'public\s+class\s+\w+', code) or re.search(r'import\s+java\.', code):
        return 'java'
    # Check for C++
    elif re.search(r'#include\s*<\w+>', code) or re.search(r'namespace\s+\w+\s*\{', code):
        return 'cpp'
    # Check for Python-specific syntax (last, as it's less distinctive)
    elif re.search(r'def\s+\w+\s*\(.*\)\s*:', code) or re.search(r'class\s+\w+\s*(\(.*\))?\s*:', code):
        return 'python'
    
    # Default to Python if language can't be determined
    return 'python'
