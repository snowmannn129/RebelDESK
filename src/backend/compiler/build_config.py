#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build configuration system for the compiler module.

This module provides functionality for managing build configurations for
different programming languages.
"""

import os
import logging
import json
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class BuildConfigManager:
    """
    Manages build configurations for different programming languages.
    
    This class provides functionality for creating, editing, and deleting
    build configurations for different programming languages.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the BuildConfigManager.
        
        Args:
            config_path (str, optional): Path to the build configuration file.
                If None, uses the default path.
        """
        self.config_path = config_path or self._get_default_config_path()
        self.configs: Dict[str, List[Dict[str, Any]]] = {}
        
        # Load configurations
        self.load_configs()
        
        # Create default configurations if none exist
        if not self.configs:
            self._create_default_configs()
    
    def _get_default_config_path(self) -> str:
        """
        Get the default path for the build configuration file.
        
        Returns:
            str: The default path.
        """
        # Use the user's home directory
        home_dir = str(Path.home())
        
        # Create the .rebeldesk directory if it doesn't exist
        config_dir = os.path.join(home_dir, '.rebeldesk')
        os.makedirs(config_dir, exist_ok=True)
        
        # Return the path to the build configuration file
        return os.path.join(config_dir, 'build_configs.json')
    
    def _create_default_configs(self) -> None:
        """Create default build configurations for supported languages."""
        # Python configurations
        python_configs = [
            {
                'name': 'Default',
                'args': ['-u'],  # Unbuffered output
                'description': 'Default Python configuration',
            },
            {
                'name': 'Debug',
                'args': ['-u', '-m', 'pdb'],  # Run with debugger
                'description': 'Run Python with debugger',
            },
            {
                'name': 'Profile',
                'args': ['-u', '-m', 'cProfile', '-s', 'cumtime'],  # Run with profiler
                'description': 'Run Python with profiler',
            },
        ]
        
        # JavaScript configurations
        javascript_configs = [
            {
                'name': 'Default',
                'args': [],
                'description': 'Default Node.js configuration',
            },
            {
                'name': 'Debug',
                'args': ['--inspect-brk'],  # Run with debugger
                'description': 'Run Node.js with debugger',
            },
            {
                'name': 'Strict',
                'args': ['--use-strict'],  # Run in strict mode
                'description': 'Run Node.js in strict mode',
            },
        ]
        
        # C++ configurations
        cpp_configs = [
            {
                'name': 'Debug',
                'args': ['-g', '-O0', '-Wall', '-Wextra'] if platform.system() != 'Windows' else ['/Od', '/Zi', '/W4'],
                'description': 'Debug build with no optimization',
            },
            {
                'name': 'Release',
                'args': ['-O3'] if platform.system() != 'Windows' else ['/O2'],
                'description': 'Release build with optimization',
            },
            {
                'name': 'Standard C++17',
                'args': ['-std=c++17'] if platform.system() != 'Windows' else ['/std:c++17'],
                'description': 'Build with C++17 standard',
            },
            {
                'name': 'Standard C++20',
                'args': ['-std=c++20'] if platform.system() != 'Windows' else ['/std:c++20'],
                'description': 'Build with C++20 standard',
            },
        ]
        
        # Java configurations
        java_configs = [
            {
                'name': 'Default',
                'args': [],
                'description': 'Default Java configuration',
            },
            {
                'name': 'Debug',
                'args': ['-g', '-Xlint:all'],
                'description': 'Debug build with all warnings enabled',
            },
            {
                'name': 'Release',
                'args': ['-Xlint:none'],
                'description': 'Release build with no warnings',
            },
        ]
        
        # Add configurations to the dictionary
        self.configs = {
            'python': python_configs,
            'javascript': javascript_configs,
            'cpp': cpp_configs,
            'java': java_configs,
        }
        
        # Save configurations
        self.save_configs()
    
    def load_configs(self) -> None:
        """Load build configurations from the configuration file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.configs = json.load(f)
                logger.info(f"Loaded build configurations from {self.config_path}")
            else:
                logger.info(f"Build configuration file {self.config_path} not found, using defaults")
                self.configs = {}
        except Exception as e:
            logger.error(f"Error loading build configurations: {str(e)}", exc_info=True)
            self.configs = {}
    
    def save_configs(self) -> bool:
        """
        Save build configurations to the configuration file.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.configs, f, indent=4)
            logger.info(f"Saved build configurations to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving build configurations: {str(e)}", exc_info=True)
            return False
    
    def get_languages(self) -> List[str]:
        """
        Get a list of languages with build configurations.
        
        Returns:
            list: List of language names.
        """
        return list(self.configs.keys())
    
    def get_configs(self, language: str) -> List[Dict[str, Any]]:
        """
        Get build configurations for a language.
        
        Args:
            language (str): The programming language.
            
        Returns:
            list: List of build configurations.
        """
        return self.configs.get(language, [])
    
    def get_config(self, language: str, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific build configuration.
        
        Args:
            language (str): The programming language.
            name (str): The name of the configuration.
            
        Returns:
            dict: The build configuration, or None if not found.
        """
        configs = self.get_configs(language)
        for config in configs:
            if config.get('name') == name:
                return config
        return None
    
    def add_config(self, language: str, name: str, args: List[str],
                  description: str = "") -> bool:
        """
        Add a new build configuration.
        
        Args:
            language (str): The programming language.
            name (str): The name of the configuration.
            args (list): The compiler arguments.
            description (str, optional): A description of the configuration.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # Check if a configuration with this name already exists
        if self.get_config(language, name) is not None:
            logger.warning(f"Build configuration {name} already exists for {language}")
            return False
        
        # Create new configuration
        new_config = {
            'name': name,
            'args': args,
            'description': description,
        }
        
        # Add to configurations
        if language not in self.configs:
            self.configs[language] = []
        self.configs[language].append(new_config)
        
        # Save configurations
        result = self.save_configs()
        
        logger.info(f"Added build configuration {name} for {language}")
        return result
    
    def update_config(self, language: str, name: str, args: Optional[List[str]] = None,
                     description: Optional[str] = None) -> bool:
        """
        Update an existing build configuration.
        
        Args:
            language (str): The programming language.
            name (str): The name of the configuration.
            args (list, optional): The new compiler arguments.
            description (str, optional): The new description.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # Get the configuration
        config = self.get_config(language, name)
        if config is None:
            logger.warning(f"Build configuration {name} not found for {language}")
            return False
        
        # Update the configuration
        if args is not None:
            config['args'] = args
        if description is not None:
            config['description'] = description
        
        # Save configurations
        result = self.save_configs()
        
        logger.info(f"Updated build configuration {name} for {language}")
        return result
    
    def delete_config(self, language: str, name: str) -> bool:
        """
        Delete a build configuration.
        
        Args:
            language (str): The programming language.
            name (str): The name of the configuration.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # Check if the language exists
        if language not in self.configs:
            logger.warning(f"Language {language} not found")
            return False
        
        # Find the configuration
        configs = self.configs[language]
        for i, config in enumerate(configs):
            if config.get('name') == name:
                # Remove the configuration
                configs.pop(i)
                
                # Save configurations
                result = self.save_configs()
                
                logger.info(f"Deleted build configuration {name} for {language}")
                return result
        
        logger.warning(f"Build configuration {name} not found for {language}")
        return False
    
    def rename_config(self, language: str, old_name: str, new_name: str) -> bool:
        """
        Rename a build configuration.
        
        Args:
            language (str): The programming language.
            old_name (str): The current name of the configuration.
            new_name (str): The new name for the configuration.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # Check if a configuration with the new name already exists
        if self.get_config(language, new_name) is not None:
            logger.warning(f"Build configuration {new_name} already exists for {language}")
            return False
        
        # Get the configuration
        config = self.get_config(language, old_name)
        if config is None:
            logger.warning(f"Build configuration {old_name} not found for {language}")
            return False
        
        # Update the name
        config['name'] = new_name
        
        # Save configurations
        result = self.save_configs()
        
        logger.info(f"Renamed build configuration {old_name} to {new_name} for {language}")
        return result
    
    def duplicate_config(self, language: str, name: str, new_name: str) -> bool:
        """
        Duplicate a build configuration.
        
        Args:
            language (str): The programming language.
            name (str): The name of the configuration to duplicate.
            new_name (str): The name for the new configuration.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # Check if a configuration with the new name already exists
        if self.get_config(language, new_name) is not None:
            logger.warning(f"Build configuration {new_name} already exists for {language}")
            return False
        
        # Get the configuration
        config = self.get_config(language, name)
        if config is None:
            logger.warning(f"Build configuration {name} not found for {language}")
            return False
        
        # Create a new configuration with the same settings
        new_config = {
            'name': new_name,
            'args': config.get('args', []).copy(),
            'description': f"Copy of {config.get('description', '')}",
        }
        
        # Add to configurations
        if language not in self.configs:
            self.configs[language] = []
        self.configs[language].append(new_config)
        
        # Save configurations
        result = self.save_configs()
        
        logger.info(f"Duplicated build configuration {name} to {new_name} for {language}")
        return result
    
    def import_configs(self, config_path: str) -> bool:
        """
        Import build configurations from a file.
        
        Args:
            config_path (str): Path to the configuration file.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Load configurations from the file
            with open(config_path, 'r') as f:
                imported_configs = json.load(f)
            
            # Merge with existing configurations
            for language, configs in imported_configs.items():
                if language not in self.configs:
                    self.configs[language] = []
                
                # Add new configurations
                for config in configs:
                    name = config.get('name')
                    if self.get_config(language, name) is None:
                        self.configs[language].append(config)
            
            # Save configurations
            result = self.save_configs()
            
            logger.info(f"Imported build configurations from {config_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error importing build configurations: {str(e)}", exc_info=True)
            return False
    
    def export_configs(self, config_path: str) -> bool:
        """
        Export build configurations to a file.
        
        Args:
            config_path (str): Path to the configuration file.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Save configurations to the file
            with open(config_path, 'w') as f:
                json.dump(self.configs, f, indent=4)
            
            logger.info(f"Exported build configurations to {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting build configurations: {str(e)}", exc_info=True)
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset build configurations to defaults.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        # Create default configurations
        self.configs = {}
        self._create_default_configs()
        
        logger.info("Reset build configurations to defaults")
        return True
