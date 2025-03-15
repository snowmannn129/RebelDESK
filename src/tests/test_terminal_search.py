#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the terminal search functionality.

This module contains unit tests for the terminal search functionality.
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
from PyQt5.QtCore import Qt, QProcess, QByteArray

# Import the terminal search classes
from src.backend.terminal.terminal_search import TerminalSearchBar, TerminalSearchHighlighter
from src.backend.terminal.terminal import TerminalWidget, Terminal

# Check if running in CI environment
CI_ENVIRONMENT = os.environ.get('CI', 'false').lower() == 'true' or os.environ.get('GITHUB_ACTIONS', 'false').lower() == 'true'

# Skip UI tests in CI environment
pytestmark = pytest.mark.skipif(CI_ENVIRONMENT, reason="UI tests are skipped in CI environment")

class TestTerminalSearchBar(unittest.TestCase):
    """Test cases for the TerminalSearchBar class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for all tests."""
        # Create a QApplication instance
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """Set up the test environment before each test."""
        self.search_bar = TerminalSearchBar()
        
    def test_initialization(self):
        """Test that the widget initializes correctly."""
        self.assertIsNotNone(self.search_bar)
        self.assertFalse(self.search_bar.isVisible())
        
    def test_show_search_bar(self):
        """Test showing the search bar."""
        self.search_bar.show_search_bar()
        self.assertTrue(self.search_bar.isVisible())
        
    def test_hide_search_bar(self):
        """Test hiding the search bar."""
        self.search_bar.show()
        self.search_bar.hide_search_bar()
        self.assertFalse(self.search_bar.isVisible())
        
    def test_search_requested_signal(self):
        """Test the search_requested signal."""
        # Set up a mock signal handler
        self.search_bar.search_requested = MagicMock()
        
        # Set the search text
        self.search_bar.search_input.setText("test")
        
        # Trigger the search
        self.search_bar.on_search()
        
        # Verify the signal was emitted
        self.search_bar.search_requested.emit.assert_called_once_with("test", False, False)
        
    def test_close_requested_signal(self):
        """Test the close_requested signal."""
        # Set up a mock signal handler
        self.search_bar.close_requested = MagicMock()
        
        # Trigger the close
        self.search_bar.on_close()
        
        # Verify the signal was emitted
        self.search_bar.close_requested.emit.assert_called_once()
        
    def test_case_sensitive_checkbox(self):
        """Test the case sensitive checkbox."""
        # Set up a mock signal handler
        self.search_bar.search_requested = MagicMock()
        
        # Set the search text
        self.search_bar.search_input.setText("test")
        
        # Check the case sensitive checkbox
        self.search_bar.case_sensitive_check.setChecked(True)
        
        # Trigger the search
        self.search_bar.on_search()
        
        # Verify the signal was emitted with case_sensitive=True
        self.search_bar.search_requested.emit.assert_called_with("test", True, False)
        
    def test_whole_word_checkbox(self):
        """Test the whole word checkbox."""
        # Set up a mock signal handler
        self.search_bar.search_requested = MagicMock()
        
        # Set the search text
        self.search_bar.search_input.setText("test")
        
        # Check the whole word checkbox
        self.search_bar.whole_word_check.setChecked(True)
        
        # Trigger the search
        self.search_bar.on_search()
        
        # Verify the signal was emitted with whole_word=True
        self.search_bar.search_requested.emit.assert_called_with("test", False, True)


class TestTerminalSearchHighlighter(unittest.TestCase):
    """Test cases for the TerminalSearchHighlighter class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for all tests."""
        # Create a QApplication instance
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """Set up the test environment before each test."""
        self.terminal_widget = TerminalWidget()
        self.highlighter = TerminalSearchHighlighter(self.terminal_widget)
        
    def test_initialization(self):
        """Test that the highlighter initializes correctly."""
        self.assertIsNotNone(self.highlighter)
        self.assertEqual(self.highlighter.search_text, "")
        self.assertEqual(self.highlighter.current_match, -1)
        self.assertEqual(len(self.highlighter.matches), 0)
        
    def test_search_no_matches(self):
        """Test searching with no matches."""
        # Add some text to the terminal
        self.terminal_widget.append_output("This is a test.")
        
        # Search for a non-existent string
        result = self.highlighter.search("nonexistent")
        
        # Verify the result
        self.assertFalse(result)
        self.assertEqual(len(self.highlighter.matches), 0)
        
    def test_search_with_matches(self):
        """Test searching with matches."""
        # Add some text to the terminal
        self.terminal_widget.append_output("This is a test. This is another test.")
        
        # Search for "test"
        result = self.highlighter.search("test")
        
        # Verify the result
        self.assertTrue(result)
        self.assertEqual(len(self.highlighter.matches), 2)
        self.assertEqual(self.highlighter.current_match, 0)
        
    def test_search_case_sensitive(self):
        """Test case sensitive searching."""
        # Add some text to the terminal
        self.terminal_widget.append_output("This is a Test. This is another test.")
        
        # Search for "Test" with case sensitivity
        result = self.highlighter.search("Test", case_sensitive=True)
        
        # Verify the result
        self.assertTrue(result)
        self.assertEqual(len(self.highlighter.matches), 1)
        
    def test_search_whole_word(self):
        """Test whole word searching."""
        # Add some text to the terminal
        self.terminal_widget.append_output("This is a test. This is testing.")
        
        # Search for "test" with whole word
        result = self.highlighter.search("test", whole_word=True)
        
        # Verify the result
        self.assertTrue(result)
        self.assertEqual(len(self.highlighter.matches), 1)
        
    def test_clear_highlights(self):
        """Test clearing highlights."""
        # Add some text to the terminal
        self.terminal_widget.append_output("This is a test.")
        
        # Search for "test"
        self.highlighter.search("test")
        
        # Clear the highlights
        self.highlighter.clear_highlights()
        
        # Verify the result
        self.assertEqual(self.highlighter.search_text, "")
        self.assertEqual(self.highlighter.current_match, -1)
        self.assertEqual(len(self.highlighter.matches), 0)


class TestTerminalSearch(unittest.TestCase):
    """Test cases for the terminal search functionality in the Terminal class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for all tests."""
        # Create a QApplication instance
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """Set up the test environment before each test."""
        # Mock the QProcess.start method to prevent actual process creation
        self.process_patcher = patch('PyQt5.QtCore.QProcess.start')
        self.mock_process_start = self.process_patcher.start()
        
        # Create the Terminal instance
        self.terminal = Terminal()
        
    def tearDown(self):
        """Clean up the test environment after each test."""
        self.process_patcher.stop()
        
    def test_search_bar_visibility(self):
        """Test the search bar visibility."""
        # Initially, the search bar should be hidden
        self.assertFalse(self.terminal.search_bar.isVisible())
        
        # Trigger the search action
        self.terminal.on_search()
        
        # The search bar should now be visible
        self.assertTrue(self.terminal.search_bar.isVisible())
        
    def test_search_requested(self):
        """Test the search_requested handler."""
        # Mock the search highlighter
        self.terminal.search_highlighter.search = MagicMock(return_value=True)
        
        # Trigger a search
        self.terminal.on_search_requested("test", False, False)
        
        # Verify the search was performed
        self.terminal.search_highlighter.search.assert_called_once_with("test", False, False)
        
    def test_search_requested_no_matches(self):
        """Test the search_requested handler with no matches."""
        # Mock the search highlighter
        self.terminal.search_highlighter.search = MagicMock(return_value=False)
        
        # Mock the terminal output
        self.terminal.terminal_output.append_output = MagicMock()
        
        # Trigger a search
        self.terminal.on_search_requested("test", False, False)
        
        # Verify the search was performed
        self.terminal.search_highlighter.search.assert_called_once_with("test", False, False)
        
        # Verify the message was displayed
        self.terminal.terminal_output.append_output.assert_called_once()
        
    def test_search_close(self):
        """Test the search_close handler."""
        # Mock the search highlighter
        self.terminal.search_highlighter.clear_highlights = MagicMock()
        
        # Trigger a search close
        self.terminal.on_search_close()
        
        # Verify the highlights were cleared
        self.terminal.search_highlighter.clear_highlights.assert_called_once()


if __name__ == "__main__":
    unittest.main()
