#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal implementation for RebelDESK.

This module provides a terminal emulator widget for the RebelDESK IDE.
"""

import os
import sys
import logging
import platform
import shlex
from pathlib import Path
from typing import List, Dict, Optional, Callable

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QHBoxLayout,
    QPushButton, QToolBar, QAction, QMenu, QComboBox, QSplitter,
    QSizePolicy, QDialog
)
from PyQt5.QtCore import (
    Qt, QProcess, pyqtSignal, pyqtSlot, QTimer, QSize, QByteArray
)
from PyQt5.QtGui import (
    QTextCursor, QColor, QFont, QKeySequence, QIcon, QTextCharFormat
)

from src.backend.terminal.terminal_customization import TerminalCustomizationDialog
from src.backend.terminal.terminal_search import TerminalSearchBar, TerminalSearchHighlighter

logger = logging.getLogger(__name__)

class TerminalWidget(QTextEdit):
    """Widget for displaying terminal output."""
    
    command_entered = pyqtSignal(str)
    
    def __init__(self, parent=None, config=None):
        """
        Initialize the terminal widget.
        
        Args:
            parent (QWidget, optional): The parent widget.
            config (dict, optional): Configuration settings.
        """
        super().__init__(parent)
        
        self.config = config or {}
        
        # Set up the widget
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setAcceptRichText(True)
        
        # Set up the font from config
        font_family = self.config.get('ui', {}).get('font', {}).get('family', "Consolas, 'Courier New', monospace")
        font_size = self.config.get('ui', {}).get('font', {}).get('size', 12)
        
        # Parse font family (may contain multiple fonts)
        font_families = [f.strip().strip("'\"") for f in font_family.split(',')]
        font = QFont(font_families[0])  # Use the first font in the list
        font.setPointSize(font_size)
        self.setFont(font)
        
        # Set up colors based on theme
        theme = self.config.get('ui', {}).get('theme', 'dark')
        if theme == 'dark':
            bg_color = "#1e1e1e"
            fg_color = "#f0f0f0"
        else:  # light theme
            bg_color = "#f5f5f5"
            fg_color = "#000000"
            
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg_color};
                color: {fg_color};
                border: none;
            }}
        """)
        
        # ANSI color codes
        self.ansi_colors = {
            30: QColor(0, 0, 0),        # Black
            31: QColor(205, 0, 0),      # Red
            32: QColor(0, 205, 0),      # Green
            33: QColor(205, 205, 0),    # Yellow
            34: QColor(0, 0, 238),      # Blue
            35: QColor(205, 0, 205),    # Magenta
            36: QColor(0, 205, 205),    # Cyan
            37: QColor(229, 229, 229),  # White
            90: QColor(127, 127, 127),  # Bright Black
            91: QColor(255, 0, 0),      # Bright Red
            92: QColor(0, 255, 0),      # Bright Green
            93: QColor(255, 255, 0),    # Bright Yellow
            94: QColor(92, 92, 255),    # Bright Blue
            95: QColor(255, 0, 255),    # Bright Magenta
            96: QColor(0, 255, 255),    # Bright Cyan
            97: QColor(255, 255, 255)   # Bright White
        }
        
        # Command history
        self.command_history = []
        self.history_index = 0
        
        # Current prompt
        self.current_prompt = "> "
        
    def append_output(self, text: str, color: QColor = None):
        """
        Append text to the terminal output.
        
        Args:
            text (str): The text to append.
            color (QColor, optional): The color of the text.
        """
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        if color:
            format = QTextCharFormat()
            format.setForeground(color)
            cursor.setCharFormat(format)
            
        cursor.insertText(text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        
    def append_html(self, html: str):
        """
        Append HTML to the terminal output.
        
        Args:
            html (str): The HTML to append.
        """
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(html)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        
    def process_ansi_escape_codes(self, text: str) -> str:
        """
        Process ANSI escape codes in the text.
        
        Args:
            text (str): The text to process.
            
        Returns:
            str: The processed text as HTML.
        """
        # This is a simplified implementation that handles only color codes
        # A full implementation would handle more escape codes
        
        result = ""
        i = 0
        while i < len(text):
            if text[i] == '\033' and i + 1 < len(text) and text[i + 1] == '[':
                # Found an escape sequence
                end = text.find('m', i)
                if end != -1:
                    # Extract the escape code
                    code_str = text[i + 2:end]
                    codes = [int(c) for c in code_str.split(';') if c]
                    
                    # Process the codes
                    if not codes or codes[0] == 0:
                        # Reset
                        result += '</span>'
                    else:
                        # Apply color
                        for code in codes:
                            if code in self.ansi_colors:
                                color = self.ansi_colors[code]
                                result += f'<span style="color: {color.name()}">'
                    
                    i = end + 1
                    continue
            
            # Regular character
            if text[i] == '<':
                result += '&lt;'
            elif text[i] == '>':
                result += '&gt;'
            elif text[i] == '&':
                result += '&amp;'
            else:
                result += text[i]
            
            i += 1
            
        return result
        
    def display_prompt(self):
        """Display the command prompt."""
        self.append_output("\n" + self.current_prompt)
        
    def clear_terminal(self):
        """Clear the terminal output."""
        self.clear()
        self.display_prompt()
        
    def set_prompt(self, prompt: str):
        """
        Set the command prompt.
        
        Args:
            prompt (str): The new prompt.
        """
        self.current_prompt = prompt
        
    def keyPressEvent(self, event):
        """
        Handle key press events.
        
        Args:
            event (QKeyEvent): The key event.
        """
        # Let the parent handle most key events
        super().keyPressEvent(event)


class CommandInput(QLineEdit):
    """Widget for entering terminal commands."""
    
    command_entered = pyqtSignal(str)
    
    def __init__(self, parent=None, config=None):
        """
        Initialize the command input widget.
        
        Args:
            parent (QWidget, optional): The parent widget.
            config (dict, optional): Configuration settings.
        """
        super().__init__(parent)
        
        self.config = config or {}
        
        # Set up the widget
        self.setPlaceholderText("Enter command...")
        
        # Set up the font from config
        font_family = self.config.get('ui', {}).get('font', {}).get('family', "Consolas, 'Courier New', monospace")
        font_size = self.config.get('ui', {}).get('font', {}).get('size', 12)
        
        # Parse font family (may contain multiple fonts)
        font_families = [f.strip().strip("'\"") for f in font_family.split(',')]
        font = QFont(font_families[0])  # Use the first font in the list
        font.setPointSize(font_size)
        self.setFont(font)
        
        # Set up colors based on theme
        theme = self.config.get('ui', {}).get('theme', 'dark')
        if theme == 'dark':
            bg_color = "#1e1e1e"
            fg_color = "#f0f0f0"
            border_color = "#3c3c3c"
        else:  # light theme
            bg_color = "#f5f5f5"
            fg_color = "#000000"
            border_color = "#cccccc"
            
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg_color};
                color: {fg_color};
                border: none;
                border-top: 1px solid {border_color};
                padding: 5px;
            }}
        """)
        
        # Command history
        self.command_history = []
        self.history_index = 0
        
        # Connect signals
        self.returnPressed.connect(self.on_return_pressed)
        
    def on_return_pressed(self):
        """Handle return key press."""
        command = self.text().strip()
        if command:
            # Add to history
            self.command_history.append(command)
            self.history_index = len(self.command_history)
            
            # Emit signal
            self.command_entered.emit(command)
            
            # Clear input
            self.clear()
            
    def keyPressEvent(self, event):
        """
        Handle key press events.
        
        Args:
            event (QKeyEvent): The key event.
        """
        if event.key() == Qt.Key_Up:
            # Navigate command history up
            if self.command_history and self.history_index > 0:
                self.history_index -= 1
                self.setText(self.command_history[self.history_index])
                self.setCursorPosition(len(self.text()))
        elif event.key() == Qt.Key_Down:
            # Navigate command history down
            if self.command_history and self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.setText(self.command_history[self.history_index])
                self.setCursorPosition(len(self.text()))
            elif self.history_index == len(self.command_history) - 1:
                self.history_index = len(self.command_history)
                self.clear()
        else:
            # Let the parent handle other key events
            super().keyPressEvent(event)


class TerminalSession:
    """Represents a terminal session with a process."""
    
    def __init__(self, name: str, working_dir: str = None):
        """
        Initialize the terminal session.
        
        Args:
            name (str): The name of the session.
            working_dir (str, optional): The working directory for the session.
        """
        self.name = name
        self.working_dir = working_dir or os.getcwd()
        self.process = QProcess()
        self.process.setWorkingDirectory(self.working_dir)
        
        # Set up environment
        from PyQt5.QtCore import QProcessEnvironment
        env = QProcessEnvironment.systemEnvironment()
        self.process.setProcessEnvironment(env)
        
        # Command history
        self.command_history = []
        
    def start_shell(self):
        """Start the shell process."""
        if platform.system() == "Windows":
            self.process.start("cmd.exe")
        else:
            self.process.start("/bin/bash")
            
    def execute_command(self, command: str):
        """
        Execute a command in the terminal.
        
        Args:
            command (str): The command to execute.
        """
        # Add to history
        self.command_history.append(command)
        
        # Write to process
        self.process.write(f"{command}\n".encode())
        
    def terminate(self):
        """Terminate the process."""
        self.process.terminate()
        
    def kill(self):
        """Kill the process."""
        self.process.kill()


class Terminal(QWidget):
    """Terminal widget for RebelDESK."""
    
    def __init__(self, parent=None, config=None):
        """
        Initialize the terminal widget.
        
        Args:
            parent (QWidget, optional): The parent widget.
            config (dict, optional): Configuration settings.
        """
        super().__init__(parent)
        
        self.config = config or {}
        self.sessions = {}
        self.current_session = None
        self.split_terminals = []  # List to track split terminal widgets
        
        self._setup_ui()
        self._create_actions()
        self._connect_signals()
        
        # Create default session
        self.create_session("Default")
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setMovable(False)
        
        # Set toolbar style based on theme
        theme = self.config.get('ui', {}).get('theme', 'dark')
        if theme == 'dark':
            bg_color = "#2d2d2d"
            fg_color = "#f0f0f0"
            border_color = "#3c3c3c"
        else:  # light theme
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            border_color = "#cccccc"
            
        self.toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {bg_color};
                color: {fg_color};
                border: none;
                border-bottom: 1px solid {border_color};
                spacing: 5px;
                padding: 2px;
            }}
            
            QToolButton {{
                background-color: transparent;
                color: {fg_color};
                border: none;
                border-radius: 3px;
                padding: 3px;
            }}
            
            QToolButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
            
            QToolButton:pressed {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
            
            QComboBox {{
                background-color: {bg_color};
                color: {fg_color};
                border: 1px solid {border_color};
                border-radius: 3px;
                padding: 2px 5px;
                min-width: 150px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
        """)
        
        self.layout.addWidget(self.toolbar)
        
        # Session selector
        self.session_selector = QComboBox()
        self.toolbar.addWidget(self.session_selector)
        
        # Add spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)
        
        # Terminal container (for split terminals)
        self.terminal_container = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.terminal_container, 1)
        
        # Main terminal widget
        self.main_terminal = QWidget()
        self.main_terminal_layout = QVBoxLayout(self.main_terminal)
        self.main_terminal_layout.setContentsMargins(0, 0, 0, 0)
        self.main_terminal_layout.setSpacing(0)
        
        # Terminal output
        self.terminal_output = TerminalWidget(self, self.config)
        self.main_terminal_layout.addWidget(self.terminal_output, 1)
        
        # Search bar
        self.search_bar = TerminalSearchBar(self, self.config)
        self.main_terminal_layout.addWidget(self.search_bar)
        self.search_bar.hide()  # Hide by default
        
        # Connect search bar signals
        self.search_bar.search_requested.connect(self.on_search_requested)
        self.search_bar.close_requested.connect(self.on_search_close)
        
        # Command input
        self.command_input = CommandInput(self, self.config)
        self.main_terminal_layout.addWidget(self.command_input)
        
        # Add the main terminal to the container
        self.terminal_container.addWidget(self.main_terminal)
        
        # Create search highlighter
        self.search_highlighter = TerminalSearchHighlighter(self.terminal_output)
        
    def _create_actions(self):
        """Create actions for the toolbar."""
        # New session action
        self.new_session_action = QAction("New Session", self)
        self.new_session_action.setToolTip("Create a new terminal session")
        self.toolbar.addAction(self.new_session_action)
        
        # Close session action
        self.close_session_action = QAction("Close Session", self)
        self.close_session_action.setToolTip("Close the current terminal session")
        self.toolbar.addAction(self.close_session_action)
        
        # Clear terminal action
        self.clear_terminal_action = QAction("Clear", self)
        self.clear_terminal_action.setToolTip("Clear the terminal output")
        self.toolbar.addAction(self.clear_terminal_action)
        
        # Split terminal horizontally action
        self.split_h_action = QAction("Split Horizontally", self)
        self.split_h_action.setToolTip("Split the terminal horizontally")
        self.toolbar.addAction(self.split_h_action)
        
        # Split terminal vertically action
        self.split_v_action = QAction("Split Vertically", self)
        self.split_v_action.setToolTip("Split the terminal vertically")
        self.toolbar.addAction(self.split_v_action)
        
        # Close split terminal action
        self.close_split_action = QAction("Close Split", self)
        self.close_split_action.setToolTip("Close the current split terminal")
        self.close_split_action.setEnabled(False)  # Disabled until a split is created
        self.toolbar.addAction(self.close_split_action)
        
        # Add separator
        self.toolbar.addSeparator()
        
        # Search action
        self.search_action = QAction("Search", self)
        self.search_action.setToolTip("Search in terminal output")
        self.search_action.setShortcut(QKeySequence("Ctrl+F"))
        self.toolbar.addAction(self.search_action)
        
        # Customize terminal action
        self.customize_action = QAction("Customize", self)
        self.customize_action.setToolTip("Customize terminal appearance and behavior")
        self.toolbar.addAction(self.customize_action)
        
    def _connect_signals(self):
        """Connect signals to slots."""
        # Command input
        self.command_input.command_entered.connect(self.execute_command)
        
        # Actions
        self.new_session_action.triggered.connect(self.on_new_session)
        self.close_session_action.triggered.connect(self.on_close_session)
        self.clear_terminal_action.triggered.connect(self.terminal_output.clear_terminal)
        self.split_h_action.triggered.connect(lambda: self.split_terminal(Qt.Horizontal))
        self.split_v_action.triggered.connect(lambda: self.split_terminal(Qt.Vertical))
        self.close_split_action.triggered.connect(self.close_current_split)
        self.search_action.triggered.connect(self.on_search)
        self.customize_action.triggered.connect(self.on_customize)
        
        # Session selector
        self.session_selector.currentTextChanged.connect(self.switch_session)
        
    def create_session(self, name: str, working_dir: str = None):
        """
        Create a new terminal session.
        
        Args:
            name (str): The name of the session.
            working_dir (str, optional): The working directory for the session.
            
        Returns:
            str: The name of the created session.
        """
        # Generate a unique name if needed
        if name in self.sessions:
            i = 1
            while f"{name} ({i})" in self.sessions:
                i += 1
            name = f"{name} ({i})"
            
        # Create the session
        session = TerminalSession(name, working_dir)
        self.sessions[name] = session
        
        # Add to selector
        self.session_selector.addItem(name)
        
        # Switch to the new session
        self.session_selector.setCurrentText(name)
        
        # Start the shell
        session.start_shell()
        
        # Connect process signals
        session.process.readyReadStandardOutput.connect(
            lambda: self.on_process_output(session.process.readAllStandardOutput())
        )
        session.process.readyReadStandardError.connect(
            lambda: self.on_process_error(session.process.readAllStandardError())
        )
        session.process.finished.connect(
            lambda: self.on_process_finished(name)
        )
        
        # Display welcome message
        self.terminal_output.clear()
        self.terminal_output.append_output(f"Terminal session '{name}' started.\n")
        self.terminal_output.append_output(f"Working directory: {session.working_dir}\n")
        self.terminal_output.display_prompt()
        
        return name
        
    def switch_session(self, name: str):
        """
        Switch to a different terminal session.
        
        Args:
            name (str): The name of the session to switch to.
        """
        if name in self.sessions:
            self.current_session = name
            
    def on_new_session(self):
        """Handle new session action."""
        self.create_session("Terminal")
        
    def on_close_session(self):
        """Handle close session action."""
        if self.current_session:
            # Get the session
            session = self.sessions.get(self.current_session)
            if session:
                # Terminate the process
                session.terminate()
                
                # Remove from selector
                index = self.session_selector.findText(self.current_session)
                if index >= 0:
                    self.session_selector.removeItem(index)
                    
                # Remove from sessions
                del self.sessions[self.current_session]
                
                # Switch to another session if available
                if self.sessions:
                    self.current_session = next(iter(self.sessions.keys()))
                    self.session_selector.setCurrentText(self.current_session)
                else:
                    self.current_session = None
                    
    def execute_command(self, command: str):
        """
        Execute a command in the current terminal session.
        
        Args:
            command (str): The command to execute.
        """
        if self.current_session:
            # Get the session
            session = self.sessions.get(self.current_session)
            if session:
                # Display the command
                self.terminal_output.append_output(command + "\n")
                
                # Execute the command
                session.execute_command(command)
                
    def on_process_output(self, output: QByteArray):
        """
        Handle process standard output.
        
        Args:
            output (QByteArray): The output data.
        """
        text = output.data().decode('utf-8', errors='replace')
        
        # Process ANSI escape codes
        html = self.terminal_output.process_ansi_escape_codes(text)
        
        # Append to terminal
        self.terminal_output.append_html(html)
        
    def on_process_error(self, output: QByteArray):
        """
        Handle process standard error.
        
        Args:
            output (QByteArray): The error data.
        """
        text = output.data().decode('utf-8', errors='replace')
        
        # Process ANSI escape codes
        html = self.terminal_output.process_ansi_escape_codes(text)
        
        # Append to terminal with error color
        self.terminal_output.append_html(f'<span style="color: #ff5555">{html}</span>')
        
    def on_process_finished(self, session_name: str):
        """
        Handle process finished event.
        
        Args:
            session_name (str): The name of the session.
        """
        try:
            # Display message
            self.terminal_output.append_output(f"\nProcess finished for session '{session_name}'.\n")
            
            # Remove from sessions
            if session_name in self.sessions:
                # Remove from selector
                index = self.session_selector.findText(session_name)
                if index >= 0:
                    self.session_selector.removeItem(index)
                    
                # Remove from sessions
                del self.sessions[session_name]
                
                # Switch to another session if available
                if self.sessions:
                    self.current_session = next(iter(self.sessions.keys()))
                    self.session_selector.setCurrentText(self.current_session)
                else:
                    self.current_session = None
        except RuntimeError:
            # Widget might have been deleted
            logger.debug(f"Terminal widget deleted before process finished for session '{session_name}'")
                
    def run_command(self, command: str, working_dir: str = None):
        """
        Run a command in a new terminal session.
        
        Args:
            command (str): The command to run.
            working_dir (str, optional): The working directory for the command.
            
        Returns:
            str: The name of the created session.
        """
        # Create a new session
        session_name = self.create_session(f"Command: {command[:20]}...", working_dir)
        
        # Execute the command
        self.execute_command(command)
        
        return session_name
        
    def split_terminal(self, orientation):
        """
        Split the terminal in the specified orientation.
        
        Args:
            orientation (Qt.Orientation): The orientation to split (Qt.Horizontal or Qt.Vertical).
        """
        # Create a new terminal widget
        new_terminal = QWidget()
        new_terminal_layout = QVBoxLayout(new_terminal)
        new_terminal_layout.setContentsMargins(0, 0, 0, 0)
        new_terminal_layout.setSpacing(0)
        
        # Create terminal output and command input
        terminal_output = TerminalWidget(self, self.config)
        command_input = CommandInput(self, self.config)
        
        # Connect command input signal
        command_input.command_entered.connect(
            lambda cmd: self.execute_command_in_split(cmd, terminal_output)
        )
        
        # Add widgets to layout
        new_terminal_layout.addWidget(terminal_output, 1)
        new_terminal_layout.addWidget(command_input)
        
        # If we're changing the orientation of the splitter
        if (orientation == Qt.Horizontal and self.terminal_container.orientation() == Qt.Vertical) or \
           (orientation == Qt.Vertical and self.terminal_container.orientation() == Qt.Horizontal):
            # Create a new splitter with the desired orientation
            new_splitter = QSplitter(orientation)
            
            # Get the current widget (first widget in the container)
            current_widget = self.terminal_container.widget(0)
            
            # Remove the current widget from the container
            current_widget.setParent(None)
            
            # Add the current widget and the new terminal to the new splitter
            new_splitter.addWidget(current_widget)
            new_splitter.addWidget(new_terminal)
            
            # Add the new splitter to the container
            self.terminal_container.addWidget(new_splitter)
        else:
            # Set the orientation of the container
            self.terminal_container.setOrientation(orientation)
            
            # Add the new terminal to the container
            self.terminal_container.addWidget(new_terminal)
        
        # Store the new terminal in the list
        self.split_terminals.append({
            'widget': new_terminal,
            'output': terminal_output,
            'input': command_input,
            'session': None  # No session yet
        })
        
        # Create a new session for the split terminal
        session_name = self.create_session(f"Split {len(self.split_terminals)}")
        split_terminal = self.split_terminals[-1]
        split_terminal['session'] = session_name
        
        # Display welcome message
        terminal_output.clear()
        terminal_output.append_output(f"Terminal session '{session_name}' started.\n")
        terminal_output.append_output(f"Working directory: {os.getcwd()}\n")
        terminal_output.display_prompt()
        
        # Enable the close split action
        self.close_split_action.setEnabled(True)
        
        logger.info(f"Created split terminal with session '{session_name}'")
        
    def execute_command_in_split(self, command, terminal_output):
        """
        Execute a command in a split terminal.
        
        Args:
            command (str): The command to execute.
            terminal_output (TerminalWidget): The terminal output widget.
        """
        # Find the split terminal with the given output widget
        for split in self.split_terminals:
            if split['output'] == terminal_output:
                # Display the command
                terminal_output.append_output(command + "\n")
                
                # Execute the command in the session
                session = self.sessions.get(split['session'])
                if session:
                    session.execute_command(command)
                break
                
    def close_current_split(self):
        """Close the current split terminal."""
        # Get the current widget
        current_widget = self.terminal_container.currentWidget()
        
        # Find the split terminal with the current widget
        for i, split in enumerate(self.split_terminals):
            if split['widget'] == current_widget:
                # Close the session
                session_name = split['session']
                if session_name in self.sessions:
                    self.sessions[session_name].terminate()
                    del self.sessions[session_name]
                
                # Remove the widget
                current_widget.setParent(None)
                current_widget.deleteLater()
                
                # Remove from the list
                self.split_terminals.pop(i)
                
                # If there are no more split terminals, disable the close split action
                if not self.split_terminals:
                    self.close_split_action.setEnabled(False)
                
                logger.info(f"Closed split terminal with session '{session_name}'")
                break
        
    def on_customize(self):
        """Handle customize action."""
        # Create the customization dialog
        dialog = TerminalCustomizationDialog(self.config, self)
        
        # Connect the settings changed signal
        dialog.settings_changed.connect(self.apply_settings)
        
        # Show the dialog
        dialog.exec_()
        
    def apply_settings(self, config):
        """
        Apply settings from the customization dialog.
        
        Args:
            config (dict): The configuration settings.
        """
        # Update the config
        self.config.update(config)
        
        # Apply theme
        theme = config.get('ui', {}).get('theme', 'dark')
        self.apply_theme(theme)
        
        # Apply font
        font_family = config.get('ui', {}).get('font', {}).get('family', "Consolas")
        font_size = config.get('ui', {}).get('font', {}).get('size', 12)
        self.apply_font(font_family, font_size)
        
        # Apply ANSI colors
        ansi_colors = config.get('ui', {}).get('ansi_colors', {})
        self.apply_ansi_colors(ansi_colors)
        
        # Apply cursor settings
        cursor_style = config.get('ui', {}).get('cursor', {}).get('style', 'block')
        cursor_blink = config.get('ui', {}).get('cursor', {}).get('blink', True)
        self.apply_cursor_settings(cursor_style, cursor_blink)
        
        # Apply scrollback settings
        scrollback = config.get('ui', {}).get('scrollback', 1000)
        scroll_output = config.get('ui', {}).get('scroll_on_output', True)
        scroll_keystroke = config.get('ui', {}).get('scroll_on_keystroke', True)
        self.apply_scrollback_settings(scrollback, scroll_output, scroll_keystroke)
        
        # Apply input settings
        tab_size = config.get('ui', {}).get('tab_size', 4)
        auto_wrap = config.get('ui', {}).get('auto_wrap', False)
        self.apply_input_settings(tab_size, auto_wrap)
        
        # Apply shell settings
        shell_path = config.get('shell', {}).get('path', '')
        shell_args = config.get('shell', {}).get('args', '')
        env_vars = config.get('shell', {}).get('env', {})
        self.apply_shell_settings(shell_path, shell_args, env_vars)
        
        # Apply performance settings
        update_interval = config.get('performance', {}).get('update_interval', 100)
        buffer_size = config.get('performance', {}).get('buffer_size', 10)
        self.apply_performance_settings(update_interval, buffer_size)
        
        logger.info("Applied terminal customization settings")
        
    def apply_theme(self, theme):
        """
        Apply the theme to the terminal.
        
        Args:
            theme (str): The theme to apply ('dark', 'light', or 'custom').
        """
        # Get colors from config
        colors = self.config.get('ui', {}).get('colors', {})
        bg_color = colors.get('background', "#1e1e1e" if theme == 'dark' else "#f5f5f5")
        fg_color = colors.get('foreground', "#f0f0f0" if theme == 'dark' else "#000000")
        border_color = "#3c3c3c" if theme == 'dark' else "#cccccc"
        
        # Update terminal output widget
        self.terminal_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg_color};
                color: {fg_color};
                border: none;
            }}
        """)
        
        # Update command input widget
        self.command_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg_color};
                color: {fg_color};
                border: none;
                border-top: 1px solid {border_color};
                padding: 5px;
            }}
        """)
        
        # Update toolbar
        self.toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {bg_color};
                color: {fg_color};
                border: none;
                border-bottom: 1px solid {border_color};
                spacing: 5px;
                padding: 2px;
            }}
            
            QToolButton {{
                background-color: transparent;
                color: {fg_color};
                border: none;
                border-radius: 3px;
                padding: 3px;
            }}
            
            QToolButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
            
            QToolButton:pressed {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
            
            QComboBox {{
                background-color: {bg_color};
                color: {fg_color};
                border: 1px solid {border_color};
                border-radius: 3px;
                padding: 2px 5px;
                min-width: 150px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
        """)
        
        # Update split terminals
        for split in self.split_terminals:
            split['output'].setStyleSheet(f"""
                QTextEdit {{
                    background-color: {bg_color};
                    color: {fg_color};
                    border: none;
                }}
            """)
            
            split['input'].setStyleSheet(f"""
                QLineEdit {{
                    background-color: {bg_color};
                    color: {fg_color};
                    border: none;
                    border-top: 1px solid {border_color};
                    padding: 5px;
                }}
            """)
        
        logger.info(f"Applied {theme} theme to terminal")
        
    def apply_font(self, font_family, font_size):
        """
        Apply font settings to the terminal.
        
        Args:
            font_family (str): The font family.
            font_size (int): The font size.
        """
        # Create the font
        font = QFont(font_family)
        font.setPointSize(font_size)
        
        # Apply to terminal output
        self.terminal_output.setFont(font)
        
        # Apply to command input
        self.command_input.setFont(font)
        
        # Apply to split terminals
        for split in self.split_terminals:
            split['output'].setFont(font)
            split['input'].setFont(font)
            
        logger.info(f"Applied font {font_family} {font_size}pt to terminal")
        
    def apply_ansi_colors(self, ansi_colors):
        """
        Apply ANSI color settings to the terminal.
        
        Args:
            ansi_colors (dict): The ANSI color settings.
        """
        # Update the ANSI colors in the terminal output
        for i in range(8):
            color_key = f'color{i}'
            if color_key in ansi_colors:
                color = QColor(ansi_colors[color_key])
                self.terminal_output.ansi_colors[30 + i] = color  # Basic colors
                self.terminal_output.ansi_colors[90 + i] = color.lighter(150)  # Bright colors
                
        # Update split terminals
        for split in self.split_terminals:
            for i in range(8):
                color_key = f'color{i}'
                if color_key in ansi_colors:
                    color = QColor(ansi_colors[color_key])
                    split['output'].ansi_colors[30 + i] = color  # Basic colors
                    split['output'].ansi_colors[90 + i] = color.lighter(150)  # Bright colors
                    
        logger.info("Applied ANSI color settings to terminal")
        
    def apply_cursor_settings(self, cursor_style, cursor_blink):
        """
        Apply cursor settings to the terminal.
        
        Args:
            cursor_style (str): The cursor style ('block', 'underline', or 'ibeam').
            cursor_blink (bool): Whether the cursor should blink.
        """
        # TODO: Implement cursor style and blink settings
        # This would require custom implementation in the TerminalWidget class
        logger.info(f"Applied cursor settings: style={cursor_style}, blink={cursor_blink}")
        
    def apply_scrollback_settings(self, scrollback, scroll_output, scroll_keystroke):
        """
        Apply scrollback settings to the terminal.
        
        Args:
            scrollback (int): The number of lines to keep in the scrollback buffer.
            scroll_output (bool): Whether to scroll on output.
            scroll_keystroke (bool): Whether to scroll on keystroke.
        """
        # TODO: Implement scrollback settings
        # This would require custom implementation in the TerminalWidget class
        logger.info(f"Applied scrollback settings: lines={scrollback}, scroll_output={scroll_output}, scroll_keystroke={scroll_keystroke}")
        
    def apply_input_settings(self, tab_size, auto_wrap):
        """
        Apply input settings to the terminal.
        
        Args:
            tab_size (int): The tab size.
            auto_wrap (bool): Whether to auto-wrap text.
        """
        # Set tab size
        # TODO: Implement tab size setting
        
        # Set auto-wrap
        if auto_wrap:
            self.terminal_output.setLineWrapMode(QTextEdit.WidgetWidth)
        else:
            self.terminal_output.setLineWrapMode(QTextEdit.NoWrap)
            
        # Apply to split terminals
        for split in self.split_terminals:
            if auto_wrap:
                split['output'].setLineWrapMode(QTextEdit.WidgetWidth)
            else:
                split['output'].setLineWrapMode(QTextEdit.NoWrap)
                
        logger.info(f"Applied input settings: tab_size={tab_size}, auto_wrap={auto_wrap}")
        
    def apply_shell_settings(self, shell_path, shell_args, env_vars):
        """
        Apply shell settings to the terminal.
        
        Args:
            shell_path (str): The shell path.
            shell_args (str): The shell arguments.
            env_vars (dict): The environment variables.
        """
        # Store the settings for new sessions
        self.config['shell'] = {
            'path': shell_path,
            'args': shell_args,
            'env': env_vars
        }
        
        logger.info("Applied shell settings")
        
    def apply_performance_settings(self, update_interval, buffer_size):
        """
        Apply performance settings to the terminal.
        
        Args:
            update_interval (int): The update interval in milliseconds.
            buffer_size (int): The buffer size in MB.
        """
        # Store the settings
        self.config['performance'] = {
            'update_interval': update_interval,
            'buffer_size': buffer_size
        }
        
        logger.info(f"Applied performance settings: update_interval={update_interval}ms, buffer_size={buffer_size}MB")
        
    def on_search(self):
        """Handle search action."""
        # Show the search bar
        self.search_bar.show()
        self.search_bar.search_input.setFocus()
        
    def on_search_requested(self, text, case_sensitive, whole_word):
        """
        Handle search request from the search bar.
        
        Args:
            text (str): The text to search for.
            case_sensitive (bool): Whether the search is case sensitive.
            whole_word (bool): Whether to match whole words only.
        """
        # Perform the search
        found = self.search_highlighter.search(text, case_sensitive, whole_word)
        
        # If not found, show a message
        if not found:
            self.terminal_output.append_output(f"\nNo matches found for '{text}'.\n")
            
    def on_search_close(self):
        """Handle search close request."""
        # Clear the search highlights
        self.search_highlighter.clear_highlights()
        
    def set_theme(self, theme):
        """
        Set the theme for the terminal.
        
        Args:
            theme (str): The theme to apply ('dark' or 'light').
        """
        # Update config
        self.config['ui']['theme'] = theme
        
        # Apply theme
        self.apply_theme(theme)
    
    def run_file(self, file_path: str):
        """
        Run a file in a new terminal session.
        
        Args:
            file_path (str): The path to the file to run.
            
        Returns:
            str: The name of the created session.
        """
        # Determine the command based on file extension
        file_path = Path(file_path)
        ext = file_path.suffix.lower()
        
        command = None
        if ext == '.py':
            command = f"python {file_path}"
        elif ext == '.js':
            command = f"node {file_path}"
        elif ext in ['.sh', '.bash']:
            command = f"bash {file_path}"
        elif ext == '.bat':
            command = str(file_path)
        elif ext == '.ps1':
            command = f"powershell -File {file_path}"
        elif ext in ['.cpp', '.cc', '.cxx']:
            # This is a simplified approach; real implementation would use a build system
            output_path = file_path.with_suffix('.exe' if platform.system() == 'Windows' else '')
            command = f"g++ {file_path} -o {output_path} && {output_path}"
        else:
            # Unknown file type
            return None
            
        # Run the command
        return self.run_command(command, str(file_path.parent))
