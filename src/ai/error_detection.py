"""
Error detection provider using local AI models.

This module provides an error detection provider that uses local AI models
to detect errors in code and suggest fixes.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple

from .local_ai_client import LocalAIClient

logger = logging.getLogger(__name__)

class ErrorDetectionProvider:
    """
    Error detection provider using local AI models.
    
    This class provides error detection using a local AI model.
    It can detect errors in code and suggest fixes.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the error detection provider.
        
        Args:
            config: Configuration dictionary for the provider.
        """
        self.config = config or {}
        self.client = LocalAIClient(
            base_url=self.config.get("base_url", "http://127.0.0.1:1234")
        )
        
        # Default model settings
        self.model_name = self.config.get("model_name", "deepseek-r1-distill-llama-8b")
        self.max_tokens = self.config.get("max_tokens", 200)
        self.temperature = self.config.get("temperature", 0.1)  # Lower temperature for more deterministic results
        
        # Completion context
        self.context_window = self.config.get("context_window", 2048)
    
    def get_errors(self, code: str) -> List[Dict[str, Any]]:
        """
        Get errors in the given code.
        
        Args:
            code: The code to check for errors.
        
        Returns:
            List[Dict[str, Any]]: A list of error dictionaries.
        """
        if not self.client.is_server_running():
            logger.warning("Local AI server is not running")
            return []
        
        try:
            # Limit the code to the context window
            if len(code) > self.context_window:
                logger.warning(f"Code is too long ({len(code)} > {self.context_window}), truncating")
                code = code[-self.context_window:]
            
            # Add a prompt to get error detection
            prompt = f"{code}\n\n# List all errors in the above code, one per line, in the format 'Line X: Error description'"
            
            # Generate a completion
            completion = self.client.get_completion(
                prompt=prompt,
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Parse the completion to extract error information
            errors = []
            
            # Use a regex to extract line numbers and error descriptions
            error_pattern = r"Line\s+(\d+):\s+(.*)"
            for line in completion.strip().split("\n"):
                match = re.match(error_pattern, line)
                if match:
                    line_number = int(match.group(1))
                    error_description = match.group(2)
                    
                    # Find the position in the code
                    position = self._find_position_for_line(code, line_number)
                    
                    errors.append({
                        "line": line_number,
                        "message": error_description,
                        "severity": "error",
                        "range": {
                            "start": position,
                            "end": position + 1  # Just highlight one character
                        }
                    })
            
            return errors
        except Exception as e:
            logger.error(f"Error detecting errors: {e}")
            return []
    
    def get_fixes(self, code: str, error: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get fixes for the given error in the given code.
        
        Args:
            code: The code containing the error.
            error: The error dictionary.
        
        Returns:
            List[Dict[str, Any]]: A list of fix dictionaries.
        """
        if not self.client.is_server_running():
            logger.warning("Local AI server is not running")
            return []
        
        try:
            # Extract the line number and error message
            line_number = error.get("line")
            error_message = error.get("message")
            
            if line_number is None or error_message is None:
                logger.warning("Invalid error dictionary")
                return []
            
            # Extract the line of code with the error
            lines = code.split("\n")
            if line_number < 1 or line_number > len(lines):
                logger.warning(f"Invalid line number: {line_number}")
                return []
            
            error_line = lines[line_number - 1]
            
            # Get some context around the error
            context_start = max(0, line_number - 3)
            context_end = min(len(lines), line_number + 2)
            context = "\n".join(lines[context_start:context_end])
            
            # Add a prompt to get fix suggestions
            prompt = f"Code with error:\n{context}\n\nError on line {line_number}: {error_message}\n\nFixed code (provide only the corrected line):"
            
            # Generate a completion
            completion = self.client.get_completion(
                prompt=prompt,
                model=self.model_name,
                max_tokens=100,
                temperature=self.temperature
            )
            
            # Parse the completion to extract the fixed line
            fixed_line = completion.strip()
            
            # Return the fix
            return [
                {
                    "title": f"Fix: {error_message}",
                    "edits": [
                        {
                            "range": {
                                "start": self._find_position_for_line(code, line_number),
                                "end": self._find_position_for_line(code, line_number) + len(error_line)
                            },
                            "newText": fixed_line
                        }
                    ]
                }
            ]
        except Exception as e:
            logger.error(f"Error getting fixes: {e}")
            return []
    
    def _find_position_for_line(self, code: str, line_number: int) -> int:
        """
        Find the position in the code for the given line number.
        
        Args:
            code: The code to search in.
            line_number: The line number to find.
        
        Returns:
            int: The position in the code.
        """
        lines = code.split("\n")
        position = 0
        
        for i in range(min(line_number - 1, len(lines))):
            position += len(lines[i]) + 1  # +1 for the newline character
        
        return position
