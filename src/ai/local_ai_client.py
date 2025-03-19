"""
Client for interacting with a local AI server.

This module provides a client for interacting with a local AI server
that implements the OpenAI API-compatible interface.
"""

import json
import logging
import requests
from typing import Dict, List, Optional, Union, Any

logger = logging.getLogger(__name__)

class LocalAIClient:
    """
    Client for interacting with a local AI server.
    
    This client is designed to work with local AI servers that implement
    the OpenAI API-compatible interface, such as LM Studio, llama.cpp server,
    or other local inference servers.
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:1234"):
        """
        Initialize the LocalAIClient.
        
        Args:
            base_url: The base URL of the local AI server.
        """
        self.base_url = base_url
        self.completions_url = f"{base_url}/v1/completions"
        self.chat_completions_url = f"{base_url}/v1/chat/completions"
        self.embeddings_url = f"{base_url}/v1/embeddings"
        self.models_url = f"{base_url}/v1/models"
        self.health_url = f"{base_url}/health"
        
        # Default headers for API requests
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def is_server_running(self) -> bool:
        """
        Check if the local AI server is running.
        
        Returns:
            bool: True if the server is running, False otherwise.
        """
        try:
            response = requests.get(self.health_url, timeout=2)
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            return False
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Get the list of available models from the server.
        
        Returns:
            List[Dict[str, Any]]: A list of model information dictionaries.
        
        Raises:
            Exception: If the server returns an error.
        """
        try:
            response = requests.get(self.models_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Error getting models: {response.status_code}")
                raise Exception(f"Error: {response.status_code}")
            
            result = response.json()
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            raise
    
    def get_completion(
        self,
        prompt: str,
        model: str = "deepseek-r1-distill-llama-8b",
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 1.0,
        n: int = 1,
        stop: Optional[Union[str, List[str]]] = None,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
    ) -> str:
        """
        Get a completion from the local AI server.
        
        Args:
            prompt: The prompt to generate a completion for.
            model: The model to use for the completion.
            max_tokens: The maximum number of tokens to generate.
            temperature: The temperature to use for sampling.
            top_p: The top-p value to use for sampling.
            n: The number of completions to generate.
            stop: A string or list of strings to stop generation at.
            presence_penalty: The presence penalty to use.
            frequency_penalty: The frequency penalty to use.
        
        Returns:
            str: The generated completion.
        
        Raises:
            Exception: If the server returns an error.
        """
        data = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "n": n,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
        }
        
        if stop is not None:
            data["stop"] = stop
        
        try:
            response = requests.post(
                self.completions_url,
                headers=self.headers,
                data=json.dumps(data),
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Error getting completion: {response.status_code}")
                raise Exception(f"Error: {response.status_code}")
            
            result = response.json()
            
            if "choices" not in result or len(result["choices"]) == 0:
                logger.error(f"No choices in completion response: {result}")
                raise Exception("No choices in completion response")
            
            return result["choices"][0]["text"]
        except Exception as e:
            logger.error(f"Error getting completion: {e}")
            raise
    
    def get_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek-r1-distill-llama-8b",
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 1.0,
        n: int = 1,
        stop: Optional[Union[str, List[str]]] = None,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
    ) -> str:
        """
        Get a chat completion from the local AI server.
        
        Args:
            messages: A list of message dictionaries with 'role' and 'content' keys.
            model: The model to use for the completion.
            max_tokens: The maximum number of tokens to generate.
            temperature: The temperature to use for sampling.
            top_p: The top-p value to use for sampling.
            n: The number of completions to generate.
            stop: A string or list of strings to stop generation at.
            presence_penalty: The presence penalty to use.
            frequency_penalty: The frequency penalty to use.
        
        Returns:
            str: The generated completion.
        
        Raises:
            Exception: If the server returns an error.
        """
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "n": n,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
        }
        
        if stop is not None:
            data["stop"] = stop
        
        try:
            response = requests.post(
                self.chat_completions_url,
                headers=self.headers,
                data=json.dumps(data),
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Error getting chat completion: {response.status_code}")
                raise Exception(f"Error: {response.status_code}")
            
            result = response.json()
            
            if "choices" not in result or len(result["choices"]) == 0:
                logger.error(f"No choices in chat completion response: {result}")
                raise Exception("No choices in chat completion response")
            
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error getting chat completion: {e}")
            raise
    
    def get_embeddings(
        self,
        texts: List[str],
        model: str = "deepseek-r1-distill-llama-8b",
    ) -> List[List[float]]:
        """
        Get embeddings for a list of texts from the local AI server.
        
        Args:
            texts: A list of texts to get embeddings for.
            model: The model to use for the embeddings.
        
        Returns:
            List[List[float]]: A list of embedding vectors.
        
        Raises:
            Exception: If the server returns an error.
        """
        data = {
            "model": model,
            "input": texts,
        }
        
        try:
            response = requests.post(
                self.embeddings_url,
                headers=self.headers,
                data=json.dumps(data),
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Error getting embeddings: {response.status_code}")
                raise Exception(f"Error: {response.status_code}")
            
            result = response.json()
            
            if "data" not in result or len(result["data"]) == 0:
                logger.error(f"No data in embeddings response: {result}")
                raise Exception("No data in embeddings response")
            
            return [item["embedding"] for item in result["data"]]
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            raise
