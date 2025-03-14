#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the MainWindow class.

This module contains unit tests for the MainWindow class.
"""

import sys
import os
import unittest
import pytest
from unittest.mock import MagicMock, patch

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import PyQt5 modules
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Import the MainWindow class
from src.ui.main_window import MainWindow

# Check if running in CI environment
CI_ENVIRONMENT = os.environ.get('CI', 'false').lower() == 'true' or os.environ.get('GITHUB_ACTIONS', 'false').lower() == 'true'

# Skip UI tests in CI environment
pytestmark = pytest.mark.skipif(CI_ENVIRONMENT, reason="UI tests are skipped in CI environment")

class TestMainWindow(unittest.TestCase):
    """Test cases for the MainWindow class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for all tests."""
        # Create a QApplication instance
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """Set up the test environment before each test."""
        # Create a mock configuration
        self.config = {
            "application": {
                "name": "TestApp",
                "version": "1.0.0"
            },
            "ui": {
                "theme": "dark",
                "font": {
                    "family": "Consolas",
                    "size": 12
                },
                "window": {
                    "default_width": 800,
                    "default_height": 600,
                    "start_maximized": False
                }
            },
            "editor": {
                "auto_save": True,
                "auto_save_interval": 60,
                "backup_files": True,
                "max_recent_files": 10,
                "default_language": "python"
            },
            "recent_files": []
        }
        
        # Create the MainWindow instance
        self.window = MainWindow(self.config)
    
    def tearDown(self):
        """Clean up the test environment after each test."""
        self.window.close()
    
    def test_window_initialization(self):
        """Test that the window initializes correctly."""
        # Check window title
        self.assertEqual(self.window.windowTitle(), "RebelDESK")
        
        # Check window size
        self.assertEqual(self.window.width(), 800)
        self.assertEqual(self.window.height(), 600)
        
        # Check that the editor tabs widget exists
        self.assertIsNotNone(self.window.editor_tabs)
        
        # Check that the status bar exists
        self.assertIsNotNone(self.window.statusBar())
        
        # Check that the menus exist
        self.assertIsNotNone(self.window.file_menu)
        self.assertIsNotNone(self.window.edit_menu)
        self.assertIsNotNone(self.window.view_menu)
        self.assertIsNotNone(self.window.settings_menu)
        self.assertIsNotNone(self.window.run_menu)
        self.assertIsNotNone(self.window.help_menu)
        
        # Check that the toolbars exist
        self.assertIsNotNone(self.window.file_toolbar)
        self.assertIsNotNone(self.window.edit_toolbar)
        self.assertIsNotNone(self.window.run_toolbar)
    
    def test_actions_initialization(self):
        """Test that the actions are initialized correctly."""
        # Check file actions
        self.assertIsNotNone(self.window.new_action)
        self.assertIsNotNone(self.window.open_action)
        self.assertIsNotNone(self.window.save_action)
        self.assertIsNotNone(self.window.save_as_action)
        self.assertIsNotNone(self.window.close_tab_action)
        self.assertIsNotNone(self.window.exit_action)
        
        # Check edit actions
        self.assertIsNotNone(self.window.undo_action)
        self.assertIsNotNone(self.window.redo_action)
        self.assertIsNotNone(self.window.cut_action)
        self.assertIsNotNone(self.window.copy_action)
        self.assertIsNotNone(self.window.paste_action)
        self.assertIsNotNone(self.window.select_all_action)
        self.assertIsNotNone(self.window.find_action)
        self.assertIsNotNone(self.window.replace_action)
        
        # Check view actions
        self.assertIsNotNone(self.window.toggle_terminal_action)
        
        # Check settings actions
        self.assertIsNotNone(self.window.settings_action)
        
        # Check run actions
        self.assertIsNotNone(self.window.run_action)
    
    @patch('src.ui.main_window.QFileDialog')
    def test_new_file_action(self, mock_file_dialog):
        """Test the new file action."""
        # Trigger the new file action
        with patch.object(self.window, 'new_file') as mock_new_file:
            self.window.new_action.trigger()
            mock_new_file.assert_called_once()
    
    @patch('src.ui.main_window.QFileDialog')
    def test_open_file_action(self, mock_file_dialog):
        """Test the open file action."""
        # Trigger the open file action
        with patch.object(self.window, 'open_file') as mock_open_file:
            self.window.open_action.trigger()
            mock_open_file.assert_called_once()
    
    @patch('src.ui.main_window.QFileDialog')
    def test_save_file_action(self, mock_file_dialog):
        """Test the save file action."""
        # Trigger the save file action
        with patch.object(self.window, 'save_file') as mock_save_file:
            self.window.save_action.trigger()
            mock_save_file.assert_called_once()
    
    @patch('src.ui.main_window.QFileDialog')
    def test_save_file_as_action(self, mock_file_dialog):
        """Test the save file as action."""
        # Trigger the save file as action
        with patch.object(self.window, 'save_file_as') as mock_save_file_as:
            self.window.save_as_action.trigger()
            mock_save_file_as.assert_called_once()
    
    def test_close_tab_action(self):
        """Test the close tab action."""
        # Trigger the close tab action
        with patch.object(self.window, 'close_current_tab') as mock_close_current_tab:
            self.window.close_tab_action.trigger()
            mock_close_current_tab.assert_called_once()
    
    def test_exit_action(self):
        """Test the exit action."""
        # Trigger the exit action
        with patch.object(self.window, 'close') as mock_close:
            self.window.exit_action.trigger()
            mock_close.assert_called_once()
    
    @patch('src.ui.main_window.SettingsPanel')
    def test_settings_action(self, mock_settings_panel):
        """Test the settings action."""
        # Mock the settings panel
        mock_settings_instance = MagicMock()
        mock_settings_instance.exec_.return_value = True
        mock_settings_panel.return_value = mock_settings_instance
        
        # Mock the config manager
        mock_config = {'ui': {'theme': 'light'}}
        self.window.config_manager.load_config = MagicMock(return_value=mock_config)
        
        # Trigger the settings action
        with patch.object(self.window, 'open_settings') as mock_open_settings:
            self.window.settings_action.trigger()
            mock_open_settings.assert_called_once()
    
    @patch('src.ui.main_window.SettingsPanel')
    def test_open_settings(self, mock_settings_panel):
        """Test the open_settings method."""
        # Mock the settings panel
        mock_settings_instance = MagicMock()
        mock_settings_instance.exec_.return_value = True
        mock_settings_panel.return_value = mock_settings_instance
        
        # Mock the config manager
        mock_config = {'ui': {'theme': 'light'}}
        self.window.config_manager.load_config = MagicMock(return_value=mock_config)
        
        # Call the open_settings method
        self.window.open_settings()
        
        # Check that the settings panel was created with the correct arguments
        mock_settings_panel.assert_called_once_with(self.window, self.window.config_manager)
        
        # Check that exec_ was called on the settings panel
        mock_settings_instance.exec_.assert_called_once()
        
        # Check that load_config was called on the config manager
        self.window.config_manager.load_config.assert_called_once()
        
        # Check that the config was updated
        self.assertEqual(self.window.config, mock_config)

if __name__ == "__main__":
    unittest.main()
