"""
Natural language code generation provider using local AI models.

This module provides a natural language code generation provider that uses local AI models
to generate code from natural language descriptions.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple

from .local_ai_client import LocalAIClient

logger = logging.getLogger(__name__)

class NaturalLanguageCodeGenerator:
    """
    Natural language code generation provider using local AI models.
    
    This class provides code generation from natural language descriptions using a local AI model.
    It handles parsing natural language descriptions and generating appropriate code in the
    target programming language.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the natural language code generator.
        
        Args:
            config: Configuration dictionary for the generator.
        """
        self.config = config or {}
        self.client = LocalAIClient(
            base_url=self.config.get("base_url", "http://127.0.0.1:1234")
        )
        
        # Default model settings
        self.model_name = self.config.get("model_name", "deepseek-r1-distill-llama-8b")
        self.max_tokens = self.config.get("max_tokens", 500)
        self.temperature = self.config.get("temperature", 0.2)  # Lower temperature for more deterministic results
        self.top_p = self.config.get("top_p", 0.95)
        
        # Context settings
        self.context_window = self.config.get("context_window", 2048)
        
        # Language-specific prompts
        self.language_prompts = {
            "python": "Write Python code that",
            "javascript": "Write JavaScript code that",
            "typescript": "Write TypeScript code that",
            "java": "Write Java code that",
            "c++": "Write C++ code that",
            "c#": "Write C# code that",
            "rust": "Write Rust code that",
            "go": "Write Go code that",
            "ruby": "Write Ruby code that",
            "php": "Write PHP code that",
            "swift": "Write Swift code that",
            "kotlin": "Write Kotlin code that",
            "lua": "Write Lua code that",
        }
        
        # Default language
        self.default_language = self.config.get("default_language", "python")
    
    def is_available(self) -> bool:
        """
        Check if the natural language code generator is available.
        
        Returns:
            bool: True if the generator is available, False otherwise.
        """
        try:
            return self.client.is_server_running()
        except Exception as e:
            logger.error(f"Error checking if natural language code generator is available: {e}")
            return False
    
    def generate_code(
        self, 
        description: str, 
        language: Optional[str] = None, 
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code from a natural language description.
        
        Args:
            description: The natural language description of the code to generate.
            language: The programming language to generate code in. If None, the default language will be used.
            context: Optional context code to help guide the generation.
            
        Returns:
            Dict[str, Any]: A dictionary containing the generated code and metadata.
        """
        if not self.is_available():
            logger.warning("Natural language code generator is not available")
            return {
                "success": False,
                "error": "Natural language code generator is not available",
                "code": "",
                "language": language or self.default_language
            }
        
        try:
            # Use the specified language or the default
            target_language = language or self.default_language
            
            # Get the language-specific prompt
            language_prompt = self.language_prompts.get(
                target_language.lower(), 
                f"Write {target_language} code that"
            )
            
            # Build the prompt
            prompt_parts = []
            
            # Add context if provided
            if context:
                # Limit context to the context window
                if len(context) > self.context_window // 2:
                    logger.warning(f"Context is too long ({len(context)} > {self.context_window // 2}), truncating")
                    context = context[-(self.context_window // 2):]
                
                prompt_parts.append(f"Given the following code context:\n\n```{target_language}\n{context}\n```\n\n")
            
            # Add the main prompt
            prompt_parts.append(f"{language_prompt} {description}")
            
            # Add instructions for output format
            prompt_parts.append("\nProvide only the code without explanations or markdown formatting.")
            
            # Combine the prompt parts
            prompt = "\n".join(prompt_parts)
            
            # Generate the code
            generated_code = self.client.get_completion(
                prompt=prompt,
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p
            )
            
            # Clean up the generated code
            cleaned_code = self._clean_generated_code(generated_code, target_language)
            
            return {
                "success": True,
                "code": cleaned_code,
                "language": target_language,
                "description": description
            }
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return {
                "success": False,
                "error": str(e),
                "code": "",
                "language": language or self.default_language
            }
    
    def generate_code_with_explanation(
        self, 
        description: str, 
        language: Optional[str] = None, 
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code from a natural language description with an explanation.
        
        Args:
            description: The natural language description of the code to generate.
            language: The programming language to generate code in. If None, the default language will be used.
            context: Optional context code to help guide the generation.
            
        Returns:
            Dict[str, Any]: A dictionary containing the generated code, explanation, and metadata.
        """
        if not self.is_available():
            logger.warning("Natural language code generator is not available")
            return {
                "success": False,
                "error": "Natural language code generator is not available",
                "code": "",
                "explanation": "",
                "language": language or self.default_language
            }
        
        try:
            # Use the specified language or the default
            target_language = language or self.default_language
            
            # Get the language-specific prompt
            language_prompt = self.language_prompts.get(
                target_language.lower(), 
                f"Write {target_language} code that"
            )
            
            # Build the prompt
            prompt_parts = []
            
            # Add context if provided
            if context:
                # Limit context to the context window
                if len(context) > self.context_window // 2:
                    logger.warning(f"Context is too long ({len(context)} > {self.context_window // 2}), truncating")
                    context = context[-(self.context_window // 2):]
                
                prompt_parts.append(f"Given the following code context:\n\n```{target_language}\n{context}\n```\n\n")
            
            # Add the main prompt
            prompt_parts.append(f"{language_prompt} {description}")
            
            # Add instructions for output format
            prompt_parts.append("\nProvide the code followed by a detailed explanation of how it works. Format your response as follows:")
            prompt_parts.append("\n```" + target_language + "\n[Your code here]\n```")
            prompt_parts.append("\n## Explanation\n[Your explanation here]")
            
            # Combine the prompt parts
            prompt = "\n".join(prompt_parts)
            
            # Generate the code with explanation
            response = self.client.get_completion(
                prompt=prompt,
                model=self.model_name,
                max_tokens=self.max_tokens * 2,  # Double the tokens for explanation
                temperature=self.temperature,
                top_p=self.top_p
            )
            
            # Parse the response to extract code and explanation
            code, explanation = self._parse_code_and_explanation(response, target_language)
            
            return {
                "success": True,
                "code": code,
                "explanation": explanation,
                "language": target_language,
                "description": description
            }
        except Exception as e:
            logger.error(f"Error generating code with explanation: {e}")
            return {
                "success": False,
                "error": str(e),
                "code": "",
                "explanation": "",
                "language": language or self.default_language
            }
    
    def improve_code(
        self, 
        code: str, 
        instructions: str, 
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Improve existing code based on instructions.
        
        Args:
            code: The existing code to improve.
            instructions: Instructions for how to improve the code.
            language: The programming language of the code. If None, it will be inferred.
            
        Returns:
            Dict[str, Any]: A dictionary containing the improved code and metadata.
        """
        if not self.is_available():
            logger.warning("Natural language code generator is not available")
            return {
                "success": False,
                "error": "Natural language code generator is not available",
                "code": code,
                "language": language or self._infer_language(code)
            }
        
        try:
            # Infer the language if not provided
            target_language = language or self._infer_language(code)
            
            # Limit code to the context window
            if len(code) > self.context_window // 2:
                logger.warning(f"Code is too long ({len(code)} > {self.context_window // 2}), truncating")
                code = code[-(self.context_window // 2):]
            
            # Build the prompt
            prompt = f"""Improve the following {target_language} code according to these instructions: {instructions}

```{target_language}
{code}
```

Provide only the improved code without explanations or markdown formatting.
"""
            
            # Generate the improved code
            improved_code = self.client.get_completion(
                prompt=prompt,
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p
            )
            
            # Clean up the improved code
            cleaned_code = self._clean_generated_code(improved_code, target_language)
            
            return {
                "success": True,
                "code": cleaned_code,
                "language": target_language,
                "instructions": instructions
            }
        except Exception as e:
            logger.error(f"Error improving code: {e}")
            return {
                "success": False,
                "error": str(e),
                "code": code,
                "language": language or self._infer_language(code)
            }
    
    def _clean_generated_code(self, generated_code: str, language: str) -> str:
        """
        Clean up generated code by removing markdown formatting and unnecessary text.
        
        Args:
            generated_code: The generated code to clean up.
            language: The programming language of the code.
            
        Returns:
            str: The cleaned up code.
        """
        # Remove markdown code blocks if present
        code_block_pattern = r"```(?:\w+)?\n([\s\S]*?)\n```"
        code_blocks = re.findall(code_block_pattern, generated_code)
        
        if code_blocks:
            # Use the first code block
            return code_blocks[0].strip()
        
        # If no code blocks found, just return the generated code
        return generated_code.strip()
    
    def _parse_code_and_explanation(self, response: str, language: str) -> Tuple[str, str]:
        """
        Parse the response to extract code and explanation.
        
        Args:
            response: The response from the AI model.
            language: The programming language of the code.
            
        Returns:
            Tuple[str, str]: The code and explanation.
        """
        # Try to extract code block
        code_block_pattern = r"```(?:\w+)?\n([\s\S]*?)\n```"
        code_blocks = re.findall(code_block_pattern, response)
        
        code = ""
        explanation = ""
        
        if code_blocks:
            # Use the first code block as the code
            code = code_blocks[0].strip()
            
            # Extract explanation (everything after the code block)
            explanation_pattern = r"```(?:\w+)?\n[\s\S]*?\n```\s*([\s\S]*)"
            explanation_match = re.search(explanation_pattern, response)
            
            if explanation_match:
                explanation = explanation_match.group(1).strip()
            
            # If no explanation found but there's text after the last code block
            if not explanation:
                last_code_block_end = response.rfind("```")
                if last_code_block_end != -1 and last_code_block_end + 3 < len(response):
                    explanation = response[last_code_block_end + 3:].strip()
        else:
            # If no code blocks found, try to split by "Explanation" or similar headers
            parts = re.split(r"(?i)##?\s*explanation|explanation:", response, 1)
            
            if len(parts) > 1:
                code = parts[0].strip()
                explanation = parts[1].strip()
            else:
                # If no clear separation, just use the whole response as code
                code = response.strip()
        
        return code, explanation
    
    def _infer_language(self, code: str) -> str:
        """
        Infer the programming language from the code.
        
        Args:
            code: The code to infer the language from.
            
        Returns:
            str: The inferred programming language.
        """
        # This is a simple heuristic and could be improved
        if "def " in code and ":" in code:
            return "python"
        elif "function " in code and "{" in code:
            return "javascript"
        elif "class " in code and "extends " in code:
            return "java"
        elif "#include" in code and "int main" in code:
            return "c++"
        elif "using namespace" in code:
            return "c++"
        elif "import React" in code:
            return "javascript"
        elif "fn " in code and " -> " in code:
            return "rust"
        elif "package main" in code and "func " in code:
            return "go"
        else:
            # Default to the default language
            return self.default_language
