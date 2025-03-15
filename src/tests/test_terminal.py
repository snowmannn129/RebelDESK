#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the Terminal class.

This module contains unit tests for the Terminal class.
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

# Import the Terminal class
from src.backend.terminal.terminal import Terminal, TerminalWidget, CommandInput, TerminalSession

# Check if running in CI environment
CI_ENVIRONMENT = os.environ.get('CI', 'false').lower() == 'true' or os.environ.get('GITHUB_ACTIONS', 'false').lower() == 'true'

# Skip UI tests in CI environment
pytestmark = pytest.mark.skipif(CI_ENVIRONMENT, reason="UI tests are skipped in CI environment")

class TestTerminalWidget(unittest.TestCase):
    """Test cases for the TerminalWidget class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for all tests."""
        # Create a QApplication instance
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """Set up the test environment before each test."""
        self.widget = TerminalWidget()
        
    def test_initialization(self):
        """Test that the widget initializes correctly."""
        self.assertIsNotNone(self.widget)
        self.assertTrue(self.widget.isReadOnly())
        self.assertEqual(self.widget.lineWrapMode(), TerminalWidget.NoWrap)
        self.assertTrue(self.widget.acceptRichText())
        
    def test_append_output(self):
        """Test appending output to the terminal."""
        # Test with plain text
        self.widget.append_output("Test output")
        self.assertEqual(self.widget.toPlainText(), "Test output")
        
        # Test with colored text
        self.widget.clear()
        self.widget.append_output("Colored output", Qt.red)
        self.assertEqual(self.widget.toPlainText(), "Colored output")
        
    def test_append_html(self):
        """Test appending HTML to the terminal."""
        self.widget.append_html("<b>Bold text</b>")
        self.assertEqual(self.widget.toPlainText(), "Bold text")
        
    def test_process_ansi_escape_codes(self):
        """Test processing ANSI escape codes."""
        # Test with reset code
        html = self.widget.process_ansi_escape_codes("\033[0mReset text")
        self.assertEqual(html, "</span>Reset text")
        
        # Test with color code
        html = self.widget.process_ansi_escape_codes("\033[31mRed text")
        self.assertTrue("color: #cd0000" in html)
        self.assertTrue("Red text" in html)
        
        # Test with multiple codes
        html = self.widget.process_ansi_escape_codes("\033[31mRed\033[32mGreen")
        self.assertTrue("color: #cd0000" in html)
        self.assertTrue("color: #00cd00" in html)
        self.assertTrue("Red" in html)
        self.assertTrue("Green" in html)
        
    def test_display_prompt(self):
        """Test displaying the command prompt."""
        self.widget.display_prompt()
        self.assertEqual(self.widget.toPlainText(), "\n> ")
        
        # Test with custom prompt
        self.widget.clear()
        self.widget.set_prompt("$ ")
        self.widget.display_prompt()
        self.assertEqual(self.widget.toPlainText(), "\n$ ")
        
    def test_clear_terminal(self):
        """Test clearing the terminal."""
        self.widget.append_output("Test output")
        self.widget.clear_terminal()
        self.assertEqual(self.widget.toPlainText(), "\n> ")


class TestCommandInput(unittest.TestCase):
    """Test cases for the CommandInput class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for all tests."""
        # Create a QApplication instance
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """Set up the test environment before each test."""
        self.input = CommandInput()
        
    def test_initialization(self):
        """Test that the widget initializes correctly."""
        self.assertIsNotNone(self.input)
        self.assertEqual(self.input.placeholderText(), "Enter command...")
        self.assertEqual(len(self.input.command_history), 0)
        
    def test_on_return_pressed(self):
        """Test handling return key press."""
        # Set up a mock signal handler
        self.input.command_entered = MagicMock()
        
        # Test with empty command
        self.input.setText("")
        self.input.on_return_pressed()
        self.input.command_entered.emit.assert_not_called()
        
        # Test with valid command
        self.input.setText("test command")
        self.input.on_return_pressed()
        self.input.command_entered.emit.assert_called_once_with("test command")
        self.assertEqual(self.input.text(), "")
        self.assertEqual(len(self.input.command_history), 1)
        self.assertEqual(self.input.command_history[0], "test command")
        
    def test_key_press_event(self):
        """Test handling key press events."""
        # Add some commands to history
        self.input.command_history = ["command1", "command2", "command3"]
        self.input.history_index = 3
        
        # Test Up key
        event = MagicMock()
        event.key.return_value = Qt.Key_Up
        self.input.keyPressEvent(event)
        self.assertEqual(self.input.history_index, 2)
        self.assertEqual(self.input.text(), "command3")
        
        # Test Down key
        event = MagicMock()
        event.key.return_value = Qt.Key_Down
        self.input.keyPressEvent(event)
        self.assertEqual(self.input.history_index, 3)
        self.assertEqual(self.input.text(), "")


class TestTerminalSession(unittest.TestCase):
    """Test cases for the TerminalSession class."""
    
    def setUp(self):
        """Set up the test environment before each test."""
        self.session = TerminalSession("Test Session")
        
    def test_initialization(self):
        """Test that the session initializes correctly."""
        self.assertIsNotNone(self.session)
        self.assertEqual(self.session.name, "Test Session")
        self.assertEqual(self.session.working_dir, os.getcwd())
        self.assertEqual(len(self.session.command_history), 0)
        
    def test_execute_command(self):
        """Test executing a command."""
        # Mock the process
        self.session.process = MagicMock()
        
        # Execute a command
        self.session.execute_command("test command")
        
        # Verify the command was added to history
        self.assertEqual(len(self.session.command_history), 1)
        self.assertEqual(self.session.command_history[0], "test command")
        
        # Verify the command was written to the process
        self.session.process.write.assert_called_once_with(b"test command\n")
        
    def test_terminate(self):
        """Test terminating the process."""
        # Mock the process
        self.session.process = MagicMock()
        
        # Terminate the process
        self.session.terminate()
        
        # Verify the process was terminated
        self.session.process.terminate.assert_called_once()
        
    def test_kill(self):
        """Test killing the process."""
        # Mock the process
        self.session.process = MagicMock()
        
        # Kill the process
        self.session.kill()
        
        # Verify the process was killed
        self.session.process.kill.assert_called_once()


class TestTerminal(unittest.TestCase):
    """Test cases for the Terminal class."""
    
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
        
    def test_initialization(self):
        """Test that the terminal initializes correctly."""
        self.assertIsNotNone(self.terminal)
        self.assertIsNotNone(self.terminal.terminal_output)
        self.assertIsNotNone(self.terminal.command_input)
        self.assertIsNotNone(self.terminal.session_selector)
        self.assertEqual(len(self.terminal.sessions), 1)
        self.assertEqual(self.terminal.current_session, "Default")
        self.assertEqual(len(self.terminal.split_terminals), 0)
        self.assertFalse(self.terminal.close_split_action.isEnabled())
        
    def test_create_session(self):
        """Test creating a terminal session."""
        # Create a new session
        session_name = self.terminal.create_session("Test Session")
        
        # Verify the session was created
        self.assertEqual(session_name, "Test Session")
        self.assertIn(session_name, self.terminal.sessions)
        self.assertEqual(self.terminal.current_session, session_name)
        
        # Verify the session selector was updated
        self.assertEqual(self.terminal.session_selector.count(), 2)
        self.assertEqual(self.terminal.session_selector.currentText(), session_name)
        
    def test_switch_session(self):
        """Test switching between terminal sessions."""
        # Create two sessions
        self.terminal.create_session("Session 1")
        self.terminal.create_session("Session 2")
        
        # Switch to the first session
        self.terminal.switch_session("Session 1")
        self.assertEqual(self.terminal.current_session, "Session 1")
        
        # Switch to the second session
        self.terminal.switch_session("Session 2")
        self.assertEqual(self.terminal.current_session, "Session 2")
        
    def test_execute_command(self):
        """Test executing a command."""
        # Mock the session
        session = self.terminal.sessions["Default"]
        session.execute_command = MagicMock()
        
        # Execute a command
        self.terminal.execute_command("test command")
        
        # Verify the command was executed
        session.execute_command.assert_called_once_with("test command")
        
    def test_on_process_output(self):
        """Test handling process output."""
        # Create a QByteArray with test output
        output = QByteArray(b"Test output")
        
        # Mock the terminal_output.append_html method
        self.terminal.terminal_output.append_html = MagicMock()
        
        # Process the output
        self.terminal.on_process_output(output)
        
        # Verify the output was processed
        self.terminal.terminal_output.append_html.assert_called_once()
        
    def test_on_process_error(self):
        """Test handling process error."""
        # Create a QByteArray with test error
        error = QByteArray(b"Test error")
        
        # Mock the terminal_output.append_html method
        self.terminal.terminal_output.append_html = MagicMock()
        
        # Process the error
        self.terminal.on_process_error(error)
        
        # Verify the error was processed
        self.terminal.terminal_output.append_html.assert_called_once()
        
    def test_run_command(self):
        """Test running a command in a new session."""
        # Mock the create_session and execute_command methods
        self.terminal.create_session = MagicMock(return_value="Command Session")
        self.terminal.execute_command = MagicMock()
        
        # Run a command
        session_name = self.terminal.run_command("test command")
        
        # Verify the session was created
        self.terminal.create_session.assert_called_once()
        self.assertEqual(session_name, "Command Session")
        
        # Verify the command was executed
        self.terminal.execute_command.assert_called_once_with("test command")
        
    def test_split_terminal_horizontal(self):
        """Test splitting the terminal horizontally."""
        # Mock the create_session method
        self.terminal.create_session = MagicMock(return_value="Split 1")
        
        # Split the terminal horizontally
        self.terminal.split_terminal(Qt.Horizontal)
        
        # Verify the split was created
        self.assertEqual(len(self.terminal.split_terminals), 1)
        self.assertEqual(self.terminal.split_terminals[0]['session'], "Split 1")
        self.assertTrue(self.terminal.close_split_action.isEnabled())
        
        # Verify the create_session method was called
        self.terminal.create_session.assert_called_once()
        
    def test_split_terminal_vertical(self):
        """Test splitting the terminal vertically."""
        # Mock the create_session method
        self.terminal.create_session = MagicMock(return_value="Split 1")
        
        # Split the terminal vertically
        self.terminal.split_terminal(Qt.Vertical)
        
        # Verify the split was created
        self.assertEqual(len(self.terminal.split_terminals), 1)
        self.assertEqual(self.terminal.split_terminals[0]['session'], "Split 1")
        self.assertTrue(self.terminal.close_split_action.isEnabled())
        
        # Verify the create_session method was called
        self.terminal.create_session.assert_called_once()
        
    def test_execute_command_in_split(self):
        """Test executing a command in a split terminal."""
        # Create a split terminal
        self.terminal.create_session = MagicMock(return_value="Split 1")
        self.terminal.split_terminal(Qt.Horizontal)
        
        # Mock the session
        split_session = MagicMock()
        self.terminal.sessions["Split 1"] = split_session
        
        # Mock the terminal output
        terminal_output = self.terminal.split_terminals[0]['output']
        terminal_output.append_output = MagicMock()
        
        # Execute a command in the split terminal
        self.terminal.execute_command_in_split("test command", terminal_output)
        
        # Verify the command was displayed
        terminal_output.append_output.assert_called_once_with("test command\n")
        
        # Verify the command was executed
        split_session.execute_command.assert_called_once_with("test command")
        
    def test_close_current_split(self):
        """Test closing a split terminal."""
        # Create a split terminal
        self.terminal.create_session = MagicMock(return_value="Split 1")
        self.terminal.split_terminal(Qt.Horizontal)
        
        # Mock the session
        split_session = MagicMock()
        self.terminal.sessions["Split 1"] = split_session
        
        # Mock the terminal container
        self.terminal.terminal_container.currentWidget = MagicMock(
            return_value=self.terminal.split_terminals[0]['widget']
        )
        
        # Close the split terminal
        self.terminal.close_current_split()
        
        # Verify the session was terminated
        split_session.terminate.assert_called_once()
        
        # Verify the split was removed
        self.assertEqual(len(self.terminal.split_terminals), 0)
        self.assertFalse(self.terminal.close_split_action.isEnabled())
        
    def test_run_file(self):
        """Test running a file in a new session."""
        # Mock the run_command method
        self.terminal.run_command = MagicMock(return_value="File Session")
        
        # Run a Python file
        session_name = self.terminal.run_file("test.py")
        
        # Verify the command was run
        self.terminal.run_command.assert_called_once()
        self.assertEqual(session_name, "File Session")
        
        # Test with different file types
        self.terminal.run_command.reset_mock()
        self.terminal.run_file("test.js")
        self.terminal.run_command.assert_called_once()
        
        self.terminal.run_command.reset_mock()
        self.terminal.run_file("test.sh")
        self.terminal.run_command.assert_called_once()
        
        self.terminal.run_command.reset_mock()
        self.terminal.run_file("test.cpp")
        self.terminal.run_command.assert_called_once()
        
        # Test with unknown file type
        self.terminal.run_command.reset_mock()
        result = self.terminal.run_file("test.unknown")
        self.assertIsNone(result)
        self.terminal.run_command.assert_not_called()


if __name__ == "__main__":
    unittest.main()
