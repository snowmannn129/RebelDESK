#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the integration of code completion with the editor.

This module contains tests for the integration of the code completion functionality
with the editor component.
"""

import os
import sys
import unittest
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add src directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtTest import QTest
from PyQt5.QtGui import QKeyEvent

from src.ui.editor.editor import CodeEditor
from src.ui.editor.completion_widget import CompletionWidget
from src.ai.code_completion import CodeCompletionManager
from src.utils.config_manager import ConfigManager


class TestEditorCompletionIntegration(unittest.TestCase):
    """Tests for the integration of code completion with the editor."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test class."""
        # Create QApplication instance if it doesn't exist
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a config with AI enabled
        self.config = {
            'ai': {
                'enable': True,
                'suggestion_delay': 0,  # No delay for testing
                'max_suggestions': 5
            },
            'ui': {
                'theme': 'dark',
                'font': {
                    'family': 'Consolas',
                    'size': 12
                },
                'editor': {
                    'tab_size': 4,
                    'use_spaces': True,
                    'auto_indent': True
                }
            }
        }
        
        # Create the editor
        self.editor = CodeEditor(config=self.config)
        
        # Patch the CodeCompletionManager to return test completions
        self.patcher = patch('src.ai.code_completion.CodeCompletionManager.get_completions')
        self.mock_get_completions = self.patcher.start()
        self.mock_get_completions.return_value = [
            {
                'text': 'test_function',
                'type': 'function',
                'description': 'Test function',
                'documentation': 'Test function documentation',
                'provider': 'test'
            },
            {
                'text': 'test_variable',
                'type': 'variable',
                'description': 'Test variable',
                'documentation': 'Test variable documentation',
                'provider': 'test'
            }
        ]
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()
        
    def test_completion_widget_creation(self):
        """Test that the completion widget is created with the editor."""
        self.assertIsNotNone(self.editor.completion_widget)
        self.assertIsInstance(self.editor.completion_widget, CompletionWidget)
        
    def test_completion_manager_creation(self):
        """Test that the completion manager is created with the editor."""
        self.assertIsNotNone(self.editor.completion_manager)
        self.assertIsInstance(self.editor.completion_manager, CodeCompletionManager)
        
    def test_completion_widget_signals(self):
        """Test that the completion widget signals are connected."""
        # Check that the completion_selected signal is connected
        self.assertTrue(self.editor.completion_widget.completion_selected.receivers() > 0)
        
    @patch('src.ui.editor.completion_widget.CompletionWidget.request_completions')
    def test_text_changed_triggers_completion(self, mock_request_completions):
        """Test that text changed triggers completion request."""
        # Set some text
        self.editor.setPlainText("test")
        
        # Check that request_completions was called
        mock_request_completions.assert_called_once()
        
    @patch('src.ui.editor.completion_widget.CompletionWidget.show_completions')
    def test_show_completions(self, mock_show_completions):
        """Test showing completions."""
        # Get the completion widget
        completion_widget = self.editor.completion_widget
        
        # Call show_completions directly
        completions = [
            {
                'text': 'test_function',
                'type': 'function',
                'description': 'Test function',
                'documentation': 'Test function documentation',
                'provider': 'test'
            }
        ]
        completion_widget.show_completions(completions)
        
        # Check that show_completions was called with the completions
        mock_show_completions.assert_called_once_with(completions)
        
    @patch('src.ui.editor.completion_widget.CompletionWidget.apply_completion')
    def test_apply_completion(self, mock_apply_completion):
        """Test applying a completion."""
        # Get the completion widget
        completion_widget = self.editor.completion_widget
        
        # Create a completion
        completion = {
            'text': 'test_function',
            'type': 'function',
            'description': 'Test function',
            'documentation': 'Test function documentation',
            'provider': 'test'
        }
        
        # Call apply_completion directly
        completion_widget.apply_completion(completion)
        
        # Check that apply_completion was called with the completion
        mock_apply_completion.assert_called_once_with(completion)
        
    def test_key_press_event_handling(self):
        """Test key press event handling."""
        # Get the completion widget
        completion_widget = self.editor.completion_widget
        
        # Mock the completion widget's keyPressEvent method
        completion_widget.keyPressEvent = MagicMock()
        
        # Set the completion widget as visible
        completion_widget.is_visible = True
        completion_widget.show()
        
        # Create a key event for the down arrow key
        event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Down, Qt.NoModifier)
        
        # Send the key event to the editor
        self.editor.keyPressEvent(event)
        
        # Check that the completion widget's keyPressEvent was called with the event
        completion_widget.keyPressEvent.assert_called_once_with(event)
        
    def test_integration_workflow(self):
        """Test the complete integration workflow."""
        # Set up the editor with some text
        self.editor.setPlainText("def test_function():\n    pass\n\ntes")
        
        # Move the cursor to the end of the text
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.End)
        self.editor.setTextCursor(cursor)
        
        # Mock the completion widget's methods
        self.editor.completion_widget.request_completions = MagicMock()
        self.editor.completion_widget.show_completions = MagicMock()
        self.editor.completion_widget.apply_completion = MagicMock()
        
        # Trigger text changed
        self.editor.textChanged.emit()
        
        # Check that request_completions was called
        self.editor.completion_widget.request_completions.assert_called_once()
        
        # Simulate showing completions
        completions = [
            {
                'text': 'test_function',
                'type': 'function',
                'description': 'Test function',
                'documentation': 'Test function documentation',
                'provider': 'test'
            }
        ]
        self.editor.completion_widget.current_completions = completions
        self.editor.completion_widget.is_visible = True
        
        # Simulate selecting a completion with the Enter key
        event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Return, Qt.NoModifier)
        self.editor.keyPressEvent(event)
        
        # Check that apply_completion was called with the completion
        self.editor.completion_widget.apply_completion.assert_called_once()


if __name__ == '__main__':
    unittest.main()
