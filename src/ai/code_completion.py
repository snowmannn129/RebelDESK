#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Code Completion for RebelDESK.

This module provides AI-powered code completion and suggestions.
"""

import os
import logging
import threading
import time
from typing import List, Dict, Any, Optional, Tuple, Callable
from pathlib import Path

import jedi
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import numpy as np

logger = logging.getLogger(__name__)

class CompletionProvider:
    """Base class for code completion providers."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the completion provider.
        
        Args:
            config (Dict[str, Any], optional): Configuration settings.
        """
        self.config = config or {}
        
    def get_completions(self, code: str, cursor_position: int, 
                        file_path: Optional[str] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get code completions for the given code and cursor position.
        
        Args:
            code (str): The code to get completions for.
            cursor_position (int): The cursor position in the code.
            file_path (str, optional): The path to the file being edited.
            language (str, optional): The programming language.
            
        Returns:
            List[Dict[str, Any]]: A list of completion suggestions.
        """
        raise NotImplementedError("Subclasses must implement get_completions")


class JediCompletionProvider(CompletionProvider):
    """Code completion provider using Jedi."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Jedi completion provider.
        
        Args:
            config (Dict[str, Any], optional): Configuration settings.
        """
        super().__init__(config)
        
    def get_completions(self, code: str, cursor_position: int, 
                        file_path: Optional[str] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get code completions using Jedi.
        
        Args:
            code (str): The code to get completions for.
            cursor_position (int): The cursor position in the code.
            file_path (str, optional): The path to the file being edited.
            language (str, optional): The programming language.
            
        Returns:
            List[Dict[str, Any]]: A list of completion suggestions.
        """
        if language and language.lower() != 'python':
            # Jedi only supports Python
            return []
            
        try:
            # Calculate line and column from cursor position
            lines = code[:cursor_position].split('\n')
            line = len(lines)
            column = len(lines[-1]) if lines else 0
            
            # Create Jedi script
            script = jedi.Script(code=code, path=file_path)
            
            # Get completions
            completions = script.complete(line, column)
            
            # Convert to standard format
            result = []
            for completion in completions:
                result.append({
                    'text': completion.name,
                    'type': completion.type,
                    'description': completion.description,
                    'documentation': completion.docstring(),
                    'provider': 'jedi'
                })
                
            return result
            
        except Exception as e:
            logger.error(f"Error getting Jedi completions: {e}", exc_info=True)
            return []


class TransformerCompletionProvider(CompletionProvider):
    """Code completion provider using Transformer models."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Transformer completion provider.
        
        Args:
            config (Dict[str, Any], optional): Configuration settings.
        """
        super().__init__(config)
        self.model = None
        self.tokenizer = None
        self.model_loaded = False
        self.loading_lock = threading.Lock()
        self.loading_thread = None
        
        # Start loading the model in a background thread
        self._load_model_async()
        
    def _load_model_async(self):
        """Load the model in a background thread."""
        if self.loading_thread is not None and self.loading_thread.is_alive():
            # Already loading
            return
            
        self.loading_thread = threading.Thread(target=self._load_model)
        self.loading_thread.daemon = True
        self.loading_thread.start()
        
    def _load_model(self):
        """Load the Transformer model and tokenizer."""
        with self.loading_lock:
            if self.model_loaded:
                return
                
            try:
                # Get model configuration
                model_type = self.config.get('ai', {}).get('model', {}).get('type', 'local')
                
                if model_type == 'local':
                    # Load local model
                    model_path = self.config.get('ai', {}).get('model', {}).get('local_path', '')
                    
                    if not model_path or not os.path.exists(model_path):
                        # Use a small default model if no path is specified
                        model_name = "codellama/CodeLlama-7b-hf"
                        logger.info(f"No local model path specified, using {model_name}")
                    else:
                        model_name = model_path
                        
                    # Load model and tokenizer
                    logger.info(f"Loading model from {model_name}")
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                    
                    # Load model with reduced precision to save memory
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        torch_dtype=torch.float16,
                        device_map="auto",
                        low_cpu_mem_usage=True
                    )
                    
                elif model_type == 'api':
                    # API-based model will be implemented in a future version
                    logger.warning("API-based models not yet implemented")
                    return
                    
                self.model_loaded = True
                logger.info("Model loaded successfully")
                
            except Exception as e:
                logger.error(f"Error loading model: {e}", exc_info=True)
                
    def is_model_loaded(self) -> bool:
        """
        Check if the model is loaded.
        
        Returns:
            bool: True if the model is loaded, False otherwise.
        """
        return self.model_loaded
        
    def get_completions(self, code: str, cursor_position: int, 
                        file_path: Optional[str] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get code completions using the Transformer model.
        
        Args:
            code (str): The code to get completions for.
            cursor_position (int): The cursor position in the code.
            file_path (str, optional): The path to the file being edited.
            language (str, optional): The programming language.
            
        Returns:
            List[Dict[str, Any]]: A list of completion suggestions.
        """
        if not self.is_model_loaded():
            # Model not loaded yet
            return []
            
        try:
            # Get context before cursor
            context = code[:cursor_position]
            
            # Get context lines
            context_lines = self.config.get('ai', {}).get('context_lines', 10)
            lines = context.split('\n')
            if len(lines) > context_lines:
                # Use only the last N lines for context
                context = '\n'.join(lines[-context_lines:])
                
            # Tokenize input
            inputs = self.tokenizer(context, return_tensors="pt").to(self.model.device)
            
            # Generate completions
            max_new_tokens = 50
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    num_return_sequences=3,
                    temperature=0.7,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
            # Decode completions
            completions = []
            for output in outputs:
                # Get only the newly generated tokens
                generated_tokens = output[inputs['input_ids'].shape[1]:]
                completion_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
                
                # Split at first newline to get just the current line completion
                if '\n' in completion_text:
                    completion_text = completion_text.split('\n')[0]
                    
                # Add to results if not empty
                if completion_text.strip():
                    completions.append({
                        'text': completion_text,
                        'type': 'suggestion',
                        'description': 'AI-generated code suggestion',
                        'documentation': '',
                        'provider': 'transformer'
                    })
                    
            return completions
            
        except Exception as e:
            logger.error(f"Error getting Transformer completions: {e}", exc_info=True)
            return []


class CodeCompletionManager:
    """Manages code completion providers and suggestions."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the code completion manager.
        
        Args:
            config (Dict[str, Any], optional): Configuration settings.
        """
        self.config = config or {}
        self.providers = []
        self.enabled = self.config.get('ai', {}).get('enable', True)
        self.suggestion_delay = self.config.get('ai', {}).get('suggestion_delay', 300) / 1000  # Convert to seconds
        self.max_suggestions = self.config.get('ai', {}).get('max_suggestions', 5)
        
        # Initialize providers
        self._initialize_providers()
        
        # Suggestion state
        self.last_request_time = 0
        self.last_code = ""
        self.last_cursor_position = 0
        self.suggestion_timer = None
        
    def _initialize_providers(self):
        """Initialize the completion providers."""
        # Add Jedi provider for Python
        self.providers.append(JediCompletionProvider(self.config))
        
        # Add Transformer provider if AI is enabled
        if self.enabled:
            self.providers.append(TransformerCompletionProvider(self.config))
            
    def get_completions(self, code: str, cursor_position: int, 
                        file_path: Optional[str] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get code completions from all providers.
        
        Args:
            code (str): The code to get completions for.
            cursor_position (int): The cursor position in the code.
            file_path (str, optional): The path to the file being edited.
            language (str, optional): The programming language.
            
        Returns:
            List[Dict[str, Any]]: A list of completion suggestions.
        """
        if not self.enabled:
            return []
            
        all_completions = []
        
        # Get completions from all providers
        for provider in self.providers:
            completions = provider.get_completions(code, cursor_position, file_path, language)
            all_completions.extend(completions)
            
        # Limit to max suggestions
        all_completions = all_completions[:self.max_suggestions]
        
        return all_completions
        
    def request_completions_async(self, code: str, cursor_position: int, 
                                 file_path: Optional[str] = None, language: Optional[str] = None,
                                 callback: Callable[[List[Dict[str, Any]]], None] = None):
        """
        Request completions asynchronously with debouncing.
        
        Args:
            code (str): The code to get completions for.
            cursor_position (int): The cursor position in the code.
            file_path (str, optional): The path to the file being edited.
            language (str, optional): The programming language.
            callback (Callable, optional): Function to call with completions.
        """
        if not self.enabled or not callback:
            return
            
        # Update state
        self.last_code = code
        self.last_cursor_position = cursor_position
        self.last_request_time = time.time()
        
        # Cancel existing timer
        if self.suggestion_timer:
            self.suggestion_timer.cancel()
            
        # Create new timer
        self.suggestion_timer = threading.Timer(
            self.suggestion_delay,
            self._get_completions_async,
            args=[code, cursor_position, file_path, language, callback, self.last_request_time]
        )
        self.suggestion_timer.daemon = True
        self.suggestion_timer.start()
        
    def _get_completions_async(self, code: str, cursor_position: int, 
                              file_path: Optional[str] = None, language: Optional[str] = None,
                              callback: Callable[[List[Dict[str, Any]]], None] = None,
                              request_time: float = 0):
        """
        Get completions in a background thread.
        
        Args:
            code (str): The code to get completions for.
            cursor_position (int): The cursor position in the code.
            file_path (str, optional): The path to the file being edited.
            language (str, optional): The programming language.
            callback (Callable, optional): Function to call with completions.
            request_time (float): The time when the request was made.
        """
        # Check if this is still the most recent request
        if request_time < self.last_request_time:
            return
            
        # Get completions
        completions = self.get_completions(code, cursor_position, file_path, language)
        
        # Call callback with completions
        if callback and completions:
            callback(completions)
            
    def set_enabled(self, enabled: bool):
        """
        Enable or disable code completion.
        
        Args:
            enabled (bool): Whether to enable code completion.
        """
        self.enabled = enabled
        
    def update_config(self, config: Dict[str, Any]):
        """
        Update the configuration.
        
        Args:
            config (Dict[str, Any]): The new configuration.
        """
        self.config = config
        self.enabled = self.config.get('ai', {}).get('enable', True)
        self.suggestion_delay = self.config.get('ai', {}).get('suggestion_delay', 300) / 1000
        self.max_suggestions = self.config.get('ai', {}).get('max_suggestions', 5)
        
        # Reinitialize providers
        self.providers = []
        self._initialize_providers()


class CompletionWidget:
    """Widget for displaying code completion suggestions."""
    
    def __init__(self, editor, completion_manager: CodeCompletionManager):
        """
        Initialize the completion widget.
        
        Args:
            editor: The editor widget.
            completion_manager (CodeCompletionManager): The completion manager.
        """
        self.editor = editor
        self.completion_manager = completion_manager
        self.current_completions = []
        
        # Connect to editor signals
        self._connect_signals()
        
    def _connect_signals(self):
        """Connect to editor signals."""
        # This would be implemented in a future step to connect to the editor's
        # text changed and cursor position changed signals
        pass
        
    def request_completions(self):
        """Request completions for the current cursor position."""
        if not self.completion_manager.enabled:
            return
            
        # Get current code and cursor position
        code = self.editor.toPlainText()
        cursor = self.editor.textCursor()
        cursor_position = cursor.position()
        
        # Get file path and language
        file_path = self.editor.current_file if hasattr(self.editor, 'current_file') else None
        language = self.editor.language if hasattr(self.editor, 'language') else None
        
        # Request completions
        self.completion_manager.request_completions_async(
            code, cursor_position, file_path, language,
            self._show_completions
        )
        
    def _show_completions(self, completions: List[Dict[str, Any]]):
        """
        Show completions in the editor.
        
        Args:
            completions (List[Dict[str, Any]]): The completions to show.
        """
        # This would be implemented in a future step to display the completions
        # in a popup or inline in the editor
        self.current_completions = completions
        
        # For now, just log the completions
        logger.debug(f"Got {len(completions)} completions")
        for completion in completions:
            logger.debug(f"  {completion['text']} ({completion['provider']})")
            
    def apply_completion(self, index: int):
        """
        Apply the selected completion.
        
        Args:
            index (int): The index of the completion to apply.
        """
        if not self.current_completions or index >= len(self.current_completions):
            return
            
        # Get the completion
        completion = self.current_completions[index]
        
        # Insert the completion text
        # This would be implemented in a future step to insert the completion
        # text at the current cursor position
        logger.debug(f"Applying completion: {completion['text']}")
