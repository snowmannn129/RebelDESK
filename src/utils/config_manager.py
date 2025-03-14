#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Manager for RebelDESK.

This module handles loading, saving, and managing application configuration settings.
"""

import os
import logging
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration settings."""
    
    DEFAULT_CONFIG_PATH = "config.yaml"
    USER_CONFIG_PATH = "config.local.yaml"
    
    def __init__(self, config_path=None):
        """
        Initialize the ConfigManager.
        
        Args:
            config_path (str, optional): Path to the configuration file.
                If None, uses the default config path.
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = {}
        
    def load_config(self):
        """
        Load configuration from file.
        
        Returns:
            dict: The loaded configuration.
        """
        try:
            # Load default configuration
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                    logger.info(f"Loaded configuration from {self.config_path}")
            else:
                logger.warning(f"Configuration file {self.config_path} not found. Using default settings.")
                self.config = {}
            
            # Load user configuration and merge with default
            if os.path.exists(self.USER_CONFIG_PATH):
                with open(self.USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                    logger.info(f"Loaded user configuration from {self.USER_CONFIG_PATH}")
                    self._merge_configs(self.config, user_config)
            
            return self.config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}", exc_info=True)
            return {}
    
    def save_config(self, config=None, user_config_only=True):
        """
        Save configuration to file.
        
        Args:
            config (dict, optional): Configuration to save. If None, saves the current config.
            user_config_only (bool): If True, saves to user config file, otherwise to default.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if config is not None:
            self.config = config
            
        try:
            save_path = self.USER_CONFIG_PATH if user_config_only else self.config_path
            
            # Create directory if it doesn't exist
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)
                
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False)
                logger.info(f"Saved configuration to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}", exc_info=True)
            return False
    
    def get_setting(self, key_path, default=None):
        """
        Get a setting from the configuration using a dot-separated path.
        
        Args:
            key_path (str): Dot-separated path to the setting (e.g., 'ui.theme').
            default: Value to return if the setting is not found.
            
        Returns:
            The setting value or default if not found.
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
    
    def set_setting(self, key_path, value):
        """
        Set a setting in the configuration using a dot-separated path.
        
        Args:
            key_path (str): Dot-separated path to the setting (e.g., 'ui.theme').
            value: Value to set.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the nested dictionary
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            elif not isinstance(config[key], dict):
                config[key] = {}
            config = config[key]
            
        # Set the value
        config[keys[-1]] = value
        return True
    
    def add_recent_file(self, file_path):
        """
        Add a file to the recent files list.
        
        Args:
            file_path (str): Path to the file.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            if 'recent_files' not in self.config:
                self.config['recent_files'] = []
                
            # Convert to absolute path
            abs_path = str(Path(file_path).resolve())
            
            # Remove if already in list
            if abs_path in self.config['recent_files']:
                self.config['recent_files'].remove(abs_path)
                
            # Add to beginning of list
            self.config['recent_files'].insert(0, abs_path)
            
            # Limit list size
            max_recent = self.get_setting('editor.max_recent_files', 10)
            self.config['recent_files'] = self.config['recent_files'][:max_recent]
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding recent file: {e}", exc_info=True)
            return False
    
    def _merge_configs(self, base_config, override_config):
        """
        Recursively merge override_config into base_config.
        
        Args:
            base_config (dict): Base configuration to merge into.
            override_config (dict): Configuration to merge from.
        """
        for key, value in override_config.items():
            if (
                key in base_config and 
                isinstance(base_config[key], dict) and 
                isinstance(value, dict)
            ):
                self._merge_configs(base_config[key], value)
            else:
                base_config[key] = value
