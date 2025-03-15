#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal search functionality for RebelDESK.

This module provides a search bar for the terminal widget.
"""

import logging
from typing import Callable, Optional

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QToolButton,
    QCheckBox, QLabel, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtGui import QIcon, QTextCursor, QTextDocument, QColor

logger = logging.getLogger(__name__)

class TerminalSearchBar(QWidget):
    """Search bar for the terminal widget."""
    
    search_requested = pyqtSignal(str, bool, bool)  # text, case_sensitive, whole_word
    close_requested = pyqtSignal()
    
    def __init__(self, parent=None, config=None):
        """
        Initialize the search bar.
        
        Args:
            parent (QWidget, optional): The parent widget.
            config (dict, optional): Configuration settings.
        """
        super().__init__(parent)
        
        self.config = config or {}
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Main layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        
        # Set up colors based on theme
        theme = self.config.get('ui', {}).get('theme', 'dark')
        if theme == 'dark':
            bg_color = "#2d2d2d"
            fg_color = "#f0f0f0"
            border_color = "#3c3c3c"
        else:  # light theme
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            border_color = "#cccccc"
            
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                color: {fg_color};
                border: none;
                border-top: 1px solid {border_color};
            }}
            
            QLineEdit {{
                background-color: {bg_color};
                color: {fg_color};
                border: 1px solid {border_color};
                border-radius: 3px;
                padding: 3px 5px;
                min-width: 200px;
            }}
            
            QPushButton, QToolButton {{
                background-color: transparent;
                color: {fg_color};
                border: 1px solid {border_color};
                border-radius: 3px;
                padding: 3px 5px;
                min-width: 80px;
            }}
            
            QPushButton:hover, QToolButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
            
            QPushButton:pressed, QToolButton:pressed {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
            
            QCheckBox {{
                spacing: 5px;
            }}
            
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
                border: 1px solid {border_color};
                border-radius: 3px;
            }}
            
            QCheckBox::indicator:checked {{
                background-color: #3c7fb1;
            }}
        """)
        
        # Search label
        self.search_label = QLabel("Search:")
        self.layout.addWidget(self.search_label)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search text...")
        self.layout.addWidget(self.search_input)
        
        # Case sensitive checkbox
        self.case_sensitive_check = QCheckBox("Case Sensitive")
        self.layout.addWidget(self.case_sensitive_check)
        
        # Whole word checkbox
        self.whole_word_check = QCheckBox("Whole Word")
        self.layout.addWidget(self.whole_word_check)
        
        # Previous button
        self.prev_button = QPushButton("Previous")
        self.layout.addWidget(self.prev_button)
        
        # Next button
        self.next_button = QPushButton("Next")
        self.layout.addWidget(self.next_button)
        
        # Close button
        self.close_button = QToolButton()
        self.close_button.setText("×")
        self.close_button.setToolTip("Close Search")
        self.close_button.setFixedSize(20, 20)
        self.layout.addWidget(self.close_button)
        
        # Add stretch to push everything to the left
        self.layout.addStretch()
        
        # Hide by default
        self.hide()
        
    def _connect_signals(self):
        """Connect signals to slots."""
        # Search input
        self.search_input.returnPressed.connect(self.on_search)
        self.search_input.textChanged.connect(self.on_text_changed)
        
        # Buttons
        self.prev_button.clicked.connect(self.on_prev)
        self.next_button.clicked.connect(self.on_next)
        self.close_button.clicked.connect(self.on_close)
        
        # Checkboxes
        self.case_sensitive_check.stateChanged.connect(self.on_search)
        self.whole_word_check.stateChanged.connect(self.on_search)
        
    def on_search(self):
        """Handle search request."""
        text = self.search_input.text()
        case_sensitive = self.case_sensitive_check.isChecked()
        whole_word = self.whole_word_check.isChecked()
        
        self.search_requested.emit(text, case_sensitive, whole_word)
        
    def on_text_changed(self, text):
        """
        Handle text changed event.
        
        Args:
            text (str): The new text.
        """
        # Enable/disable buttons based on text
        enabled = bool(text)
        self.prev_button.setEnabled(enabled)
        self.next_button.setEnabled(enabled)
            
    def on_prev(self):
        """Handle previous button click."""
        # Emit search signal with reverse flag
        text = self.search_input.text()
        case_sensitive = self.case_sensitive_check.isChecked()
        whole_word = self.whole_word_check.isChecked()
        
        self.search_requested.emit(text, case_sensitive, whole_word)
        
    def on_next(self):
        """Handle next button click."""
        # Emit search signal
        self.on_search()
        
    def on_close(self):
        """Handle close button click."""
        self.hide()
        self.close_requested.emit()
        
    def show_search_bar(self):
        """Show the search bar and focus the input."""
        self.show()
        self.search_input.setFocus()
        self.search_input.selectAll()
        
    def hide_search_bar(self):
        """Hide the search bar."""
        self.hide()
        
    def set_theme(self, theme):
        """
        Set the theme for the search bar.
        
        Args:
            theme (str): The theme to apply ('dark' or 'light').
        """
        # Update config
        self.config['ui'] = self.config.get('ui', {})
        self.config['ui']['theme'] = theme
        
        # Apply theme
        if theme == 'dark':
            bg_color = "#2d2d2d"
            fg_color = "#f0f0f0"
            border_color = "#3c3c3c"
        else:  # light theme
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            border_color = "#cccccc"
            
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                color: {fg_color};
                border: none;
                border-top: 1px solid {border_color};
            }}
            
            QLineEdit {{
                background-color: {bg_color};
                color: {fg_color};
                border: 1px solid {border_color};
                border-radius: 3px;
                padding: 3px 5px;
                min-width: 200px;
            }}
            
            QPushButton, QToolButton {{
                background-color: transparent;
                color: {fg_color};
                border: 1px solid {border_color};
                border-radius: 3px;
                padding: 3px 5px;
                min-width: 80px;
            }}
            
            QPushButton:hover, QToolButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
            
            QPushButton:pressed, QToolButton:pressed {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
            
            QCheckBox {{
                spacing: 5px;
            }}
            
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
                border: 1px solid {border_color};
                border-radius: 3px;
            }}
            
            QCheckBox::indicator:checked {{
                background-color: #3c7fb1;
            }}
        """)


class TerminalSearchHighlighter:
    """Highlighter for search results in the terminal."""
    
    def __init__(self, terminal_widget):
        """
        Initialize the highlighter.
        
        Args:
            terminal_widget (QTextEdit): The terminal widget.
        """
        self.terminal_widget = terminal_widget
        self.search_text = ""
        self.case_sensitive = False
        self.whole_word = False
        self.current_match = -1
        self.matches = []
        
    def search(self, text, case_sensitive=False, whole_word=False, backwards=False):
        """
        Search for text in the terminal.
        
        Args:
            text (str): The text to search for.
            case_sensitive (bool, optional): Whether the search is case sensitive.
            whole_word (bool, optional): Whether to match whole words only.
            backwards (bool, optional): Whether to search backwards.
            
        Returns:
            bool: True if a match was found, False otherwise.
        """
        if not text:
            self.clear_highlights()
            return False
            
        # Store search parameters
        self.search_text = text
        self.case_sensitive = case_sensitive
        self.whole_word = whole_word
        
        # Find all matches
        self.find_all_matches()
        
        # If no matches, return False
        if not self.matches:
            return False
            
        # If current match is -1, set it to the first match
        if self.current_match == -1:
            self.current_match = 0
        elif backwards:
            # Move to previous match
            self.current_match = (self.current_match - 1) % len(self.matches)
        else:
            # Move to next match
            self.current_match = (self.current_match + 1) % len(self.matches)
            
        # Highlight the current match
        self.highlight_current_match()
        
        return True
        
    def find_all_matches(self):
        """Find all matches in the terminal."""
        # Clear previous matches
        self.matches = []
        
        # Get the document
        document = self.terminal_widget.document()
        
        # Create a cursor for searching
        cursor = QTextCursor(document)
        
        # Set up search flags
        flags = QTextDocument.FindFlags()
        if self.case_sensitive:
            flags |= QTextDocument.FindCaseSensitively
        if self.whole_word:
            flags |= QTextDocument.FindWholeWords
            
        # Find all matches
        while True:
            cursor = document.find(self.search_text, cursor, flags)
            if cursor.isNull():
                break
            self.matches.append(QTextCursor(cursor))
            
    def highlight_current_match(self):
        """Highlight the current match."""
        if not self.matches or self.current_match < 0 or self.current_match >= len(self.matches):
            return
            
        # Get the current match cursor
        cursor = self.matches[self.current_match]
        
        # Select the match
        self.terminal_widget.setTextCursor(cursor)
        
        # Ensure the match is visible
        self.terminal_widget.ensureCursorVisible()
        
    def clear_highlights(self):
        """Clear all highlights."""
        self.search_text = ""
        self.matches = []
        self.current_match = -1
        
        # Reset the cursor
        cursor = self.terminal_widget.textCursor()
        cursor.clearSelection()
        self.terminal_widget.setTextCursor(cursor)
