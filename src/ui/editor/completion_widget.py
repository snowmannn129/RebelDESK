#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Completion Widget for RebelDESK.

This module provides a widget for displaying code completion suggestions.
"""

import logging
from typing import List, Dict, Any, Optional, Callable

from PyQt5.QtWidgets import (
    QListWidget, QListWidgetItem, QWidget, QLabel, QVBoxLayout, 
    QHBoxLayout, QFrame, QAbstractItemView, QStyleOption, QStyle
)
from PyQt5.QtGui import (
    QColor, QPainter, QTextCursor, QFont, QFontMetrics, QPalette,
    QKeyEvent, QKeySequence, QIcon
)
from PyQt5.QtCore import (
    Qt, QRect, QSize, pyqtSignal, QEvent, QTimer, QPoint
)

logger = logging.getLogger(__name__)

class CompletionItemWidget(QWidget):
    """Widget for displaying a completion item."""
    
    def __init__(self, completion: Dict[str, Any], parent=None):
        """
        Initialize the completion item widget.
        
        Args:
            completion (Dict[str, Any]): The completion data.
            parent (QWidget, optional): The parent widget.
        """
        super().__init__(parent)
        
        self.completion = completion
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)
        
        # Icon based on completion type
        icon_label = QLabel(self)
        icon_type = self.completion.get('type', '')
        
        if icon_type == 'function':
            icon_label.setText('ƒ')
            icon_label.setStyleSheet("color: #66d9ef;")
        elif icon_type == 'class':
            icon_label.setText('C')
            icon_label.setStyleSheet("color: #a6e22e;")
        elif icon_type == 'variable':
            icon_label.setText('v')
            icon_label.setStyleSheet("color: #fd971f;")
        elif icon_type == 'snippet':
            icon_label.setText('S')
            icon_label.setStyleSheet("color: #e6db74;")
        elif icon_type == 'suggestion':
            icon_label.setText('AI')
            icon_label.setStyleSheet("color: #ae81ff;")
        else:
            icon_label.setText('•')
            icon_label.setStyleSheet("color: #f8f8f2;")
            
        icon_label.setFixedWidth(20)
        layout.addWidget(icon_label)
        
        # Text label
        text_label = QLabel(self.completion.get('text', ''), self)
        text_label.setStyleSheet("color: #f8f8f2;")
        layout.addWidget(text_label)
        
        # Provider label (right-aligned)
        provider_label = QLabel(self.completion.get('provider', ''), self)
        provider_label.setStyleSheet("color: #75715e; font-size: 9pt;")
        provider_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(provider_label)
        
        # Set fixed height
        self.setFixedHeight(25)
        
    def paintEvent(self, event):
        """
        Paint the widget.
        
        Args:
            event (QPaintEvent): The paint event.
        """
        # This is needed for the widget to use stylesheets
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        super().paintEvent(event)


class CompletionListWidget(QListWidget):
    """List widget for displaying completion items."""
    
    def __init__(self, parent=None):
        """
        Initialize the completion list widget.
        
        Args:
            parent (QWidget, optional): The parent widget.
        """
        super().__init__(parent)
        
        # Set up the widget
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setFocusPolicy(Qt.NoFocus)
        
        # Set up the style
        self.setStyleSheet("""
            QListWidget {
                background-color: #272822;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                padding: 0px;
                outline: none;
            }
            
            QListWidget::item {
                padding: 0px;
                border: none;
            }
            
            QListWidget::item:selected {
                background-color: #3e3d32;
                border: none;
            }
        """)
        
    def add_completion(self, completion: Dict[str, Any]):
        """
        Add a completion item to the list.
        
        Args:
            completion (Dict[str, Any]): The completion data.
        """
        item = QListWidgetItem(self)
        widget = CompletionItemWidget(completion, self)
        item.setSizeHint(widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, widget)
        
    def clear_completions(self):
        """Clear all completion items."""
        self.clear()
        
    def get_selected_completion(self) -> Optional[Dict[str, Any]]:
        """
        Get the selected completion.
        
        Returns:
            Dict[str, Any]: The selected completion data, or None if no item is selected.
        """
        current_item = self.currentItem()
        if current_item:
            widget = self.itemWidget(current_item)
            if widget and hasattr(widget, 'completion'):
                return widget.completion
        return None
        
    def select_next(self):
        """Select the next item in the list."""
        current_row = self.currentRow()
        if current_row < self.count() - 1:
            self.setCurrentRow(current_row + 1)
        else:
            # Wrap around to the first item
            self.setCurrentRow(0)
            
    def select_previous(self):
        """Select the previous item in the list."""
        current_row = self.currentRow()
        if current_row > 0:
            self.setCurrentRow(current_row - 1)
        else:
            # Wrap around to the last item
            self.setCurrentRow(self.count() - 1)


class CompletionWidget(QFrame):
    """Widget for displaying code completion suggestions."""
    
    # Signal emitted when a completion is selected
    completion_selected = pyqtSignal(dict)
    
    # Signal emitted when the widget is closed
    widget_closed = pyqtSignal()
    
    def __init__(self, editor, completion_manager):
        """
        Initialize the completion widget.
        
        Args:
            editor: The editor widget.
            completion_manager: The completion manager.
        """
        super().__init__(editor.viewport())
        
        self.editor = editor
        self.completion_manager = completion_manager
        self.current_completions = []
        self.prefix = ""
        self.is_visible = False
        
        # Set up the widget
        self.setup_ui()
        
        # Connect to editor signals
        self.connect_signals()
        
        # Hide initially
        self.hide()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Set up the frame
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(1)
        
        # Set up the layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create the list widget
        self.list_widget = CompletionListWidget(self)
        layout.addWidget(self.list_widget)
        
        # Set up the style
        self.setStyleSheet("""
            CompletionWidget {
                background-color: #272822;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
            }
        """)
        
        # Set initial size
        self.resize(300, 200)
        
    def connect_signals(self):
        """Connect to editor signals."""
        # Connect to editor signals
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.cursorPositionChanged.connect(self.on_cursor_position_changed)
        
        # Connect to list widget signals
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        
    def on_text_changed(self):
        """Handle text changed event."""
        if not self.completion_manager.enabled:
            return
            
        # Request completions
        self.request_completions()
        
    def on_cursor_position_changed(self):
        """Handle cursor position changed event."""
        if not self.is_visible:
            return
            
        # Check if the cursor is still in the completion area
        cursor = self.editor.textCursor()
        current_position = cursor.position()
        
        # Get the current line
        block = cursor.block()
        block_position = block.position()
        line_text = block.text()
        line_position = current_position - block_position
        
        # Check if we're still typing the same word
        if line_position <= 0 or line_position > len(line_text):
            self.hide_completions()
            return
            
        # Get the current word
        word = ""
        for i in range(line_position - 1, -1, -1):
            if line_text[i].isalnum() or line_text[i] == '_':
                word = line_text[i] + word
            else:
                break
                
        # If the word doesn't start with the prefix, hide completions
        if not word.startswith(self.prefix):
            self.hide_completions()
            return
            
        # Update the prefix
        self.prefix = word
        
        # Filter completions based on the new prefix
        self.filter_completions()
        
    def on_item_clicked(self, item):
        """
        Handle item clicked event.
        
        Args:
            item (QListWidgetItem): The clicked item.
        """
        # Get the completion
        widget = self.list_widget.itemWidget(item)
        if widget and hasattr(widget, 'completion'):
            # Apply the completion
            self.apply_completion(widget.completion)
            
    def request_completions(self):
        """Request completions for the current cursor position."""
        if not self.completion_manager.enabled:
            return
            
        # Get current code and cursor position
        code = self.editor.toPlainText()
        cursor = self.editor.textCursor()
        cursor_position = cursor.position()
        
        # Get the current line
        block = cursor.block()
        block_position = block.position()
        line_text = block.text()
        line_position = cursor_position - block_position
        
        # Check if we're in a position to show completions
        if line_position <= 0 or line_position > len(line_text):
            self.hide_completions()
            return
            
        # Get the current word
        word = ""
        for i in range(line_position - 1, -1, -1):
            if i < 0:
                break
            if line_text[i].isalnum() or line_text[i] == '_':
                word = line_text[i] + word
            else:
                break
                
        # Only show completions if we have a word to complete
        if not word:
            self.hide_completions()
            return
            
        # Update the prefix
        self.prefix = word
        
        # Get file path and language
        file_path = self.editor.current_file if hasattr(self.editor, 'current_file') else None
        language = self.editor.language if hasattr(self.editor, 'language') else None
        
        # Request completions
        self.completion_manager.request_completions_async(
            code, cursor_position, file_path, language,
            self.show_completions
        )
        
    def show_completions(self, completions: List[Dict[str, Any]]):
        """
        Show completions in the editor.
        
        Args:
            completions (List[Dict[str, Any]]): The completions to show.
        """
        if not completions:
            self.hide_completions()
            return
            
        # Store the completions
        self.current_completions = completions
        
        # Filter completions based on the prefix
        filtered_completions = self.filter_completions()
        
        # If no completions match, hide the widget
        if not filtered_completions:
            self.hide_completions()
            return
            
        # Clear the list widget
        self.list_widget.clear_completions()
        
        # Add completions to the list widget
        for completion in filtered_completions:
            self.list_widget.add_completion(completion)
            
        # Select the first item
        self.list_widget.setCurrentRow(0)
        
        # Position the widget
        self.position_widget()
        
        # Show the widget
        self.show()
        self.is_visible = True
        
    def filter_completions(self) -> List[Dict[str, Any]]:
        """
        Filter completions based on the current prefix.
        
        Returns:
            List[Dict[str, Any]]: The filtered completions.
        """
        if not self.prefix:
            return self.current_completions
            
        # Filter completions
        filtered_completions = []
        for completion in self.current_completions:
            text = completion.get('text', '')
            if text.startswith(self.prefix):
                filtered_completions.append(completion)
                
        return filtered_completions
        
    def position_widget(self):
        """Position the widget near the cursor."""
        # Get the cursor rectangle
        cursor = self.editor.textCursor()
        cursor_rect = self.editor.cursorRect(cursor)
        
        # Convert to global coordinates
        global_pos = self.editor.viewport().mapToGlobal(cursor_rect.bottomLeft())
        
        # Adjust for the editor's scroll position
        scroll_pos = self.editor.verticalScrollBar().value()
        global_pos.setY(global_pos.y() - scroll_pos)
        
        # Convert back to local coordinates
        local_pos = self.editor.viewport().mapFromGlobal(global_pos)
        
        # Position the widget
        self.move(local_pos.x(), local_pos.y() + 5)
        
        # Ensure the widget is fully visible
        widget_rect = self.geometry()
        viewport_rect = self.editor.viewport().rect()
        
        # Adjust horizontal position if needed
        if widget_rect.right() > viewport_rect.right():
            self.move(viewport_rect.right() - widget_rect.width(), widget_rect.y())
            
        # Adjust vertical position if needed
        if widget_rect.bottom() > viewport_rect.bottom():
            # Position above the cursor
            cursor_top = cursor_rect.top()
            self.move(widget_rect.x(), cursor_top - widget_rect.height() - 5)
            
    def hide_completions(self):
        """Hide the completion widget."""
        self.hide()
        self.is_visible = False
        self.current_completions = []
        self.prefix = ""
        self.list_widget.clear_completions()
        self.widget_closed.emit()
        
    def apply_completion(self, completion: Dict[str, Any]):
        """
        Apply the selected completion.
        
        Args:
            completion (Dict[str, Any]): The completion to apply.
        """
        if not completion:
            return
            
        # Get the completion text
        text = completion.get('text', '')
        
        # Get the cursor
        cursor = self.editor.textCursor()
        
        # Get the current line
        block = cursor.block()
        block_position = block.position()
        line_text = block.text()
        line_position = cursor.position() - block_position
        
        # Calculate the start position of the word to replace
        start_pos = line_position
        for i in range(line_position - 1, -1, -1):
            if i < 0:
                break
            if line_text[i].isalnum() or line_text[i] == '_':
                start_pos = i
            else:
                break
                
        # Select the word to replace
        cursor.setPosition(block_position + start_pos)
        cursor.setPosition(block_position + line_position, QTextCursor.KeepAnchor)
        
        # Replace with the completion text
        cursor.insertText(text)
        
        # Hide the completion widget
        self.hide_completions()
        
        # Emit the completion selected signal
        self.completion_selected.emit(completion)
        
    def keyPressEvent(self, event: QKeyEvent):
        """
        Handle key press events.
        
        Args:
            event (QKeyEvent): The key event.
        """
        # Handle navigation keys
        if event.key() == Qt.Key_Down:
            self.list_widget.select_next()
            event.accept()
            return
        elif event.key() == Qt.Key_Up:
            self.list_widget.select_previous()
            event.accept()
            return
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Apply the selected completion
            completion = self.list_widget.get_selected_completion()
            if completion:
                self.apply_completion(completion)
            event.accept()
            return
        elif event.key() == Qt.Key_Escape:
            # Hide the completion widget
            self.hide_completions()
            event.accept()
            return
        elif event.key() == Qt.Key_Tab:
            # Apply the selected completion
            completion = self.list_widget.get_selected_completion()
            if completion:
                self.apply_completion(completion)
            event.accept()
            return
            
        # Pass other keys to the parent
        super().keyPressEvent(event)
