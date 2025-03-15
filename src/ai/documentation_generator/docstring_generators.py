#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docstring generation module for the documentation generator.

This module provides functionality to generate docstrings for different code elements
(classes, methods, functions) in various programming languages.
"""

import re
import ast
import logging
from typing import Dict, Any, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

def generate_class_docstring(code: str, class_name: str, language: str) -> Optional[str]:
    """
    Generate a docstring for a class.
    
    Args:
        code (str): The source code containing the class.
        class_name (str): The name of the class.
        language (str): The programming language.
        
    Returns:
        Optional[str]: The generated docstring, or None if generation failed.
    """
    try:
        # For Python, use AST parsing
        if language == 'python':
            try:
                tree = ast.parse(code)
                class_node = None
                
                # Find the class node
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == class_name:
                        class_node = node
                        break
                        
                if not class_node:
                    logger.warning(f"Class {class_name} not found in code")
                    return None
                    
                # Extract class information
                bases = []
                for base in class_node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                
                # Create a basic docstring
                docstring = f'"""\n{class_name}.\n\n'
                docstring += f"A class that represents a {class_name.replace('_', ' ').lower()}.\n"
                
                # Add inheritance information if there are base classes
                if bases:
                    docstring += "\nInherits from:\n"
                    for base in bases:
                        docstring += f"    {base}\n"
                
                docstring += '"""'
                return docstring
            except Exception as e:
                logger.error(f"Error parsing Python class: {e}")
                # Fall back to a simple docstring
                return f'"""\n{class_name}.\n\nA class that represents a {class_name.replace("_", " ").lower()}.\n"""'
        else:
            # For other languages, create a basic docstring based on language
            if language in ['javascript', 'typescript']:
                return f"/**\n * {class_name} class.\n *\n * A class that represents a {class_name.replace('_', ' ').lower()}.\n */\n"
            elif language == 'cpp':
                return f"/**\n * {class_name} class.\n *\n * A class that represents a {class_name.replace('_', ' ').lower()}.\n */\n"
            elif language == 'java':
                return f"/**\n * {class_name} class.\n *\n * A class that represents a {class_name.replace('_', ' ').lower()}.\n */\n"
            else:
                # Default to Python-style docstring
                return f'"""\n{class_name}.\n\nA class that represents a {class_name.replace("_", " ").lower()}.\n"""'
    except Exception as e:
        logger.error(f"Error generating class docstring: {e}", exc_info=True)
        return None

def generate_method_docstring(code: str, class_name: str, method_name: str, language: str) -> Optional[str]:
    """
    Generate a docstring for a class method.
    
    Args:
        code (str): The source code containing the class and method.
        class_name (str): The name of the class.
        method_name (str): The name of the method.
        language (str): The programming language.
        
    Returns:
        Optional[str]: The generated docstring, or None if generation failed.
    """
    try:
        # For Python, use AST parsing
        if language == 'python':
            try:
                tree = ast.parse(code)
                method_node = None
                
                # Find the class node and then the method node
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == class_name:
                        for child in node.body:
                            if isinstance(child, ast.FunctionDef) and child.name == method_name:
                                method_node = child
                                break
                        break
                        
                if not method_node:
                    logger.warning(f"Method {class_name}.{method_name} not found in code")
                    return None
                    
                # Extract method signature
                args = []
                returns = None
                
                # Process arguments
                for arg in method_node.args.args:
                    arg_name = arg.arg
                    arg_type = None
                    
                    # Skip 'self' parameter
                    if arg_name == 'self':
                        continue
                        
                    # Check for type annotation
                    if arg.annotation:
                        if isinstance(arg.annotation, ast.Name):
                            arg_type = arg.annotation.id
                        elif isinstance(arg.annotation, ast.Subscript):
                            if isinstance(arg.annotation.value, ast.Name):
                                arg_type = arg.annotation.value.id
                                
                    args.append((arg_name, arg_type))
                    
                # Check for return type annotation
                if method_node.returns:
                    if isinstance(method_node.returns, ast.Name):
                        returns = method_node.returns.id
                    elif isinstance(method_node.returns, ast.Subscript):
                        if isinstance(method_node.returns.value, ast.Name):
                            returns = method_node.returns.value.id
                
                # Create a basic docstring
                docstring = f'"""\n{method_name.replace("_", " ").title()}.\n\n'
                
                # Add args section if there are arguments
                if args:
                    docstring += "Args:\n"
                    for arg_name, arg_type in args:
                        arg_desc = f"    {arg_name}"
                        if arg_type:
                            arg_desc += f" ({arg_type})"
                        arg_desc += ": Description of parameter."
                        docstring += arg_desc + "\n"
                        
                # Add returns section if there's a return value
                if returns:
                    docstring += "\nReturns:\n"
                    docstring += f"    {returns}: Description of return value.\n"
                
                docstring += '"""'
                return docstring
            except Exception as e:
                logger.error(f"Error parsing Python method: {e}")
                # Fall back to a simple docstring
                return f'"""\n{method_name.replace("_", " ").title()}.\n\nDescription of the method.\n"""'
        else:
            # For other languages, create a basic docstring based on language
            if language in ['javascript', 'typescript']:
                return f"/**\n * {method_name.replace('_', ' ').title()}.\n *\n * @returns {{any}} Description of return value.\n */\n"
            elif language == 'cpp':
                return f"/**\n * {method_name.replace('_', ' ').title()}.\n *\n * @return Description of return value.\n */\n"
            elif language == 'java':
                return f"/**\n * {method_name.replace('_', ' ').title()}.\n *\n * @return Description of return value.\n */\n"
            else:
                # Default to Python-style docstring
                return f'"""\n{method_name.replace("_", " ").title()}.\n\nDescription of the method.\n"""'
    except Exception as e:
        logger.error(f"Error generating method docstring: {e}", exc_info=True)
        return None

def generate_function_docstring(code: str, function_name: str, language: str) -> Optional[str]:
    """
    Generate a docstring for a function.
    
    Args:
        code (str): The source code containing the function.
        function_name (str): The name of the function.
        language (str): The programming language.
        
    Returns:
        Optional[str]: The generated docstring, or None if generation failed.
    """
    try:
        # For Python, use AST parsing
        if language == 'python':
            try:
                tree = ast.parse(code)
                function_node = None
                
                # Find the function node
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == function_name:
                        function_node = node
                        break
                        
                if not function_node:
                    logger.warning(f"Function {function_name} not found in code")
                    return None
                    
                # Extract function signature
                args = []
                returns = None
                
                # Process arguments
                for arg in function_node.args.args:
                    arg_name = arg.arg
                    arg_type = None
                    
                    # Check for type annotation
                    if arg.annotation:
                        if isinstance(arg.annotation, ast.Name):
                            arg_type = arg.annotation.id
                        elif isinstance(arg.annotation, ast.Subscript):
                            if isinstance(arg.annotation.value, ast.Name):
                                arg_type = arg.annotation.value.id
                                
                    args.append((arg_name, arg_type))
                    
                # Check for return type annotation
                if function_node.returns:
                    if isinstance(function_node.returns, ast.Name):
                        returns = function_node.returns.id
                    elif isinstance(function_node.returns, ast.Subscript):
                        if isinstance(function_node.returns.value, ast.Name):
                            returns = function_node.returns.value.id
                
                # Create a basic docstring
                docstring = f'"""\n{function_name.replace("_", " ").title()}.\n\n'
                
                # Add args section if there are arguments
                if args:
                    docstring += "Args:\n"
                    for arg_name, arg_type in args:
                        arg_desc = f"    {arg_name}"
                        if arg_type:
                            arg_desc += f" ({arg_type})"
                        arg_desc += ": Description of parameter."
                        docstring += arg_desc + "\n"
                        
                # Add returns section if there's a return value
                if returns:
                    docstring += "\nReturns:\n"
                    docstring += f"    {returns}: Description of return value.\n"
                
                docstring += '"""'
                return docstring
            except Exception as e:
                logger.error(f"Error parsing Python function: {e}")
                # Fall back to a simple docstring
                return f'"""\n{function_name.replace("_", " ").title()}.\n\nDescription of the function.\n"""'
        else:
            # For other languages, create a basic docstring based on language
            if language in ['javascript', 'typescript']:
                return f"/**\n * {function_name.replace('_', ' ').title()}.\n *\n * @returns {{any}} Description of return value.\n */\n"
            elif language == 'cpp':
                return f"/**\n * {function_name.replace('_', ' ').title()}.\n *\n * @return Description of return value.\n */\n"
            elif language == 'java':
                return f"/**\n * {function_name.replace('_', ' ').title()}.\n *\n * @return Description of return value.\n */\n"
            else:
                # Default to Python-style docstring
                return f'"""\n{function_name.replace("_", " ").title()}.\n\nDescription of the function.\n"""'
    except Exception as e:
        logger.error(f"Error generating function docstring: {e}", exc_info=True)
        return None
