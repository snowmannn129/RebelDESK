"""
RebelDESK AI components for code assistance and automation.
"""

from .local_ai_client import LocalAIClient
from .code_completion import CodeCompletionProvider
from .error_detection import ErrorDetectionProvider
from .natural_language_code_generation import NaturalLanguageCodeGenerator

__all__ = [
    "LocalAIClient",
    "CodeCompletionProvider",
    "ErrorDetectionProvider",
    "NaturalLanguageCodeGenerator"
]
