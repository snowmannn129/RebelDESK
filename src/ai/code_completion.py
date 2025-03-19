"""
Code completion provider using local AI models.

This module provides a code completion provider that uses local AI models
to generate code completions.
"""

import logging
import threading
from typing import List, Dict, Any, Optional

from .local_ai_client import LocalAIClient

logger = logging.getLogger(__name__)

class CodeCompletionProvider:
    """
    Code completion provider using local AI models.
    
    This class provides code completions using a local AI model.
    It handles loading the model, generating completions, and
    managing the completion context.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the code completion provider.
        
        Args:
            config: Configuration dictionary for the provider.
        """
        self.config = config or {}
        self.model_loaded = False
        self.loading_lock = threading.Lock()
        self.client = LocalAIClient(
            base_url=self.config.get("base_url", "http://127.0.0.1:1234")
        )
        
        # Default model settings
        self.model_name = self.config.get("model_name", "deepseek-r1-distill-llama-8b")
        self.max_tokens = self.config.get("max_tokens", 100)
        self.temperature = self.config.get("temperature", 0.2)  # Lower temperature for code
        self.top_p = self.config.get("top_p", 0.95)
        
        # Completion context
        self.context_window = self.config.get("context_window", 2048)
        
        # Try to load the model
        self._check_model_availability()
    
    def _check_model_availability(self) -> bool:
        """
        Check if the model is available.
        
        Returns:
            bool: True if the model is available, False otherwise.
        """
        try:
            if not self.client.is_server_running():
                logger.warning("Local AI server is not running")
                return False
            
            # Try to get the list of models
            models = self.client.get_models()
            
            # Check if our model is available
            model_available = any(model.get("id") == self.model_name for model in models)
            
            if not model_available:
                logger.warning(f"Model {self.model_name} is not available")
                return False
            
            self.model_loaded = True
            return True
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
    
    def get_completions(self, code: str, position: int) -> List[Dict[str, Any]]:
        """
        Get code completions for the given code at the given position.
        
        Args:
            code: The code to get completions for.
            position: The position in the code to get completions at.
        
        Returns:
            List[Dict[str, Any]]: A list of completion dictionaries.
        """
        if not self.model_loaded and not self._check_model_availability():
            logger.warning("Model not loaded, cannot get completions")
            return []
        
        try:
            # Extract the code before the cursor
            prefix = code[:position]
            
            # Limit the prefix to the context window
            if len(prefix) > self.context_window:
                prefix = prefix[-self.context_window:]
            
            # Generate a completion
            completion = self.client.get_completion(
                prompt=prefix,
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p
            )
            
            # Return the completion as a list of dictionaries
            return [
                {
                    "text": completion,
                    "range": {
                        "start": position,
                        "end": position
                    }
                }
            ]
        except Exception as e:
            logger.error(f"Error getting completions: {e}")
            return []
    
    def get_signature_help(self, code: str, position: int) -> Optional[Dict[str, Any]]:
        """
        Get signature help for the given code at the given position.
        
        Args:
            code: The code to get signature help for.
            position: The position in the code to get signature help at.
        
        Returns:
            Optional[Dict[str, Any]]: A signature help dictionary, or None if not available.
        """
        if not self.model_loaded and not self._check_model_availability():
            logger.warning("Model not loaded, cannot get signature help")
            return None
        
        try:
            # Extract the code before the cursor
            prefix = code[:position]
            
            # Limit the prefix to the context window
            if len(prefix) > self.context_window:
                prefix = prefix[-self.context_window:]
            
            # Add a prompt to get signature help
            prompt = f"{prefix}\n# What are the parameters for the function being called above?"
            
            # Generate a completion
            completion = self.client.get_completion(
                prompt=prompt,
                model=self.model_name,
                max_tokens=100,
                temperature=0.1,  # Lower temperature for more deterministic results
                top_p=0.95
            )
            
            # Parse the completion to extract signature information
            # This is a simple implementation and could be improved
            lines = completion.strip().split("\n")
            if not lines:
                return None
            
            # Return the signature help
            return {
                "signatures": [
                    {
                        "label": lines[0],
                        "documentation": "\n".join(lines[1:]),
                        "parameters": []
                    }
                ],
                "activeSignature": 0,
                "activeParameter": 0
            }
        except Exception as e:
            logger.error(f"Error getting signature help: {e}")
            return None
    
    def get_hover_info(self, code: str, position: int) -> Optional[Dict[str, Any]]:
        """
        Get hover information for the given code at the given position.
        
        Args:
            code: The code to get hover information for.
            position: The position in the code to get hover information at.
        
        Returns:
            Optional[Dict[str, Any]]: A hover information dictionary, or None if not available.
        """
        if not self.model_loaded and not self._check_model_availability():
            logger.warning("Model not loaded, cannot get hover information")
            return None
        
        try:
            # Extract the code before and after the cursor to get context
            prefix = code[:position]
            suffix = code[position:]
            
            # Try to extract the current word
            import re
            word_match = re.search(r'[A-Za-z0-9_]+$', prefix)
            if not word_match:
                return None
            
            word = word_match.group(0)
            
            # Limit the code to the context window
            context = prefix[-self.context_window:] + suffix[:100]
            
            # Add a prompt to get hover information
            prompt = f"{context}\n# Explain what '{word}' is in the code above:"
            
            # Generate a completion
            completion = self.client.get_completion(
                prompt=prompt,
                model=self.model_name,
                max_tokens=200,
                temperature=0.1,  # Lower temperature for more deterministic results
                top_p=0.95
            )
            
            # Return the hover information
            return {
                "contents": completion.strip(),
                "range": {
                    "start": position - len(word),
                    "end": position
                }
            }
        except Exception as e:
            logger.error(f"Error getting hover information: {e}")
            return None
