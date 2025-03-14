#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the ConfigManager class.

This module contains unit tests for the ConfigManager class.
"""

import os
import tempfile
import unittest
import yaml
from pathlib import Path

import sys
import os
# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    """Test cases for the ConfigManager class."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.test_dir.name, "test_config.yaml")
        self.user_config_path = os.path.join(self.test_dir.name, "test_config.local.yaml")
        
        # Create a test configuration
        self.test_config = {
            "application": {
                "name": "TestApp",
                "version": "1.0.0"
            },
            "ui": {
                "theme": "dark",
                "font": {
                    "family": "Consolas",
                    "size": 12
                }
            },
            "recent_files": [
                "/path/to/file1.py",
                "/path/to/file2.py"
            ]
        }
        
        # Write the test configuration to the file
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.test_config, f)
        
        # Create the ConfigManager instance
        self.config_manager = ConfigManager(self.config_path)
        
        # Override the USER_CONFIG_PATH
        self.config_manager.USER_CONFIG_PATH = self.user_config_path
        
    def tearDown(self):
        """Clean up the test environment."""
        self.test_dir.cleanup()
        
    def test_load_config(self):
        """Test loading configuration from file."""
        config = self.config_manager.load_config()
        
        # Check that the configuration was loaded correctly
        self.assertEqual(config["application"]["name"], "TestApp")
        self.assertEqual(config["application"]["version"], "1.0.0")
        self.assertEqual(config["ui"]["theme"], "dark")
        self.assertEqual(config["ui"]["font"]["family"], "Consolas")
        self.assertEqual(config["ui"]["font"]["size"], 12)
        self.assertEqual(len(config["recent_files"]), 2)
        
    def test_get_setting(self):
        """Test getting a setting from the configuration."""
        self.config_manager.load_config()
        
        # Test getting existing settings
        self.assertEqual(self.config_manager.get_setting("application.name"), "TestApp")
        self.assertEqual(self.config_manager.get_setting("ui.theme"), "dark")
        self.assertEqual(self.config_manager.get_setting("ui.font.family"), "Consolas")
        
        # Test getting non-existent settings
        self.assertIsNone(self.config_manager.get_setting("non_existent"))
        self.assertEqual(self.config_manager.get_setting("non_existent", "default"), "default")
        
    def test_set_setting(self):
        """Test setting a setting in the configuration."""
        self.config_manager.load_config()
        
        # Test setting existing settings
        self.config_manager.set_setting("application.name", "NewApp")
        self.assertEqual(self.config_manager.get_setting("application.name"), "NewApp")
        
        # Test setting new settings
        self.config_manager.set_setting("new_setting", "value")
        self.assertEqual(self.config_manager.get_setting("new_setting"), "value")
        
        # Test setting nested settings
        self.config_manager.set_setting("new_section.nested", "nested_value")
        self.assertEqual(self.config_manager.get_setting("new_section.nested"), "nested_value")
        
    def test_save_config(self):
        """Test saving configuration to file."""
        self.config_manager.load_config()
        
        # Modify the configuration
        self.config_manager.set_setting("application.name", "NewApp")
        self.config_manager.set_setting("new_setting", "value")
        
        # Save the configuration
        self.config_manager.save_config(user_config_only=False)
        
        # Load the configuration again
        new_config_manager = ConfigManager(self.config_path)
        new_config = new_config_manager.load_config()
        
        # Check that the changes were saved
        self.assertEqual(new_config["application"]["name"], "NewApp")
        self.assertEqual(new_config["new_setting"], "value")
        
    def test_add_recent_file(self):
        """Test adding a file to the recent files list."""
        self.config_manager.load_config()
        
        # Add a new file
        self.config_manager.add_recent_file("/path/to/file3.py")
        
        # Check that the file was added to the beginning of the list
        recent_files = self.config_manager.get_setting("recent_files")
        self.assertEqual(len(recent_files), 3)
        self.assertEqual(recent_files[0], "/path/to/file3.py")
        
        # Add an existing file
        self.config_manager.add_recent_file("/path/to/file2.py")
        
        # Check that the file was moved to the beginning of the list
        recent_files = self.config_manager.get_setting("recent_files")
        self.assertEqual(len(recent_files), 3)
        self.assertEqual(recent_files[0], "/path/to/file2.py")
        
    def test_merge_configs(self):
        """Test merging configurations."""
        # Create a user configuration
        user_config = {
            "application": {
                "name": "UserApp"
            },
            "ui": {
                "theme": "light",
                "font": {
                    "size": 14
                }
            },
            "user_setting": "user_value"
        }
        
        # Write the user configuration to the file
        with open(self.user_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(user_config, f)
        
        # Load the configuration
        config = self.config_manager.load_config()
        
        # Check that the user configuration was merged correctly
        self.assertEqual(config["application"]["name"], "UserApp")  # Overridden
        self.assertEqual(config["application"]["version"], "1.0.0")  # Not overridden
        self.assertEqual(config["ui"]["theme"], "light")  # Overridden
        self.assertEqual(config["ui"]["font"]["family"], "Consolas")  # Not overridden
        self.assertEqual(config["ui"]["font"]["size"], 14)  # Overridden
        self.assertEqual(config["user_setting"], "user_value")  # Added
        
if __name__ == "__main__":
    unittest.main()
