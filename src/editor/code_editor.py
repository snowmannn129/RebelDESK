"""
RebelDESK code editor component.

This module provides a code editor component for RebelDESK.
"""

import logging
import time
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import QPlainTextEdit, QWidget
from PyQt5.QtGui import (
    QFont, QTextOption, QColor, QPainter, QTextFormat, 
    QSyntaxHighlighter, QTextCharFormat
)
from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal, QTimer

from .incremental_syntax_highlighter import IncrementalSyntaxHighlighter

logger = logging.getLogger(__name__)

class LineNumberArea(QWidget):
    """
    Widget for displaying line numbers in the code editor.
    """
    
    def __init__(self, editor):
        """
        Initialize the line number area.
        
        Args:
            editor: The code editor widget.
        """
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self) -> QSize:
        """
        Return the recommended size for the widget.
        
        Returns:
            QSize: The recommended size.
        """
        return QSize(self.editor.line_number_area_width(), 0)
    
    def paintEvent(self, event):
        """
        Paint the line number area.
        
        Args:
            event: The paint event.
        """
        self.editor.line_number_area_paint_event(event)

class CodeEditor(QPlainTextEdit):
    """
    Code editor component for RebelDESK.
    
    This component provides a code editor with syntax highlighting,
    line numbers, and other features useful for editing code.
    """
    
    # Signal emitted when the cursor position changes
    cursorPositionChanged = pyqtSignal(int, int)  # line, column
    
    def __init__(self, parent=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the code editor.
        
        Args:
            parent: The parent widget.
            config: Configuration dictionary for the editor.
        """
        super().__init__(parent)
        
        self.config = config or {}
        
        # Set up the editor
        self._setup_editor()
        
        # Create the line number area
        self.line_number_area = LineNumberArea(self)
        
        # Connect signals
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self.cursorPositionChanged.connect(self._emit_cursor_position)
        
        # Initial setup
        self._update_line_number_area_width(0)
        self._highlight_current_line()
    
    def _setup_editor(self):
        """Set up the editor appearance and behavior."""
        # Set font
        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Set tab width
        tab_width = self.config.get("tab_width", 4)
        self.setTabStopWidth(tab_width * self.fontMetrics().width(' '))
        
        # Set word wrap mode
        self.setWordWrapMode(QTextOption.NoWrap)
        
        # Set line numbers visible
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        
        # Set highlight current line
        self.setExtraSelections([])
        
        # Set up syntax highlighting
        self.syntax_highlighter = IncrementalSyntaxHighlighter(self.document())
        
        # Configure the syntax highlighter
        batch_size = self.config.get("syntax_highlighter_batch_size", 50)
        max_highlighting_time = self.config.get("syntax_highlighter_max_time", 20)
        
        self.syntax_highlighter.set_batch_size(batch_size)
        self.syntax_highlighter.set_max_highlighting_time(max_highlighting_time)
    
    def line_number_area_width(self) -> int:
        """
        Calculate the width of the line number area.
        
        Returns:
            int: The width of the line number area in pixels.
        """
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        space = 3 + self.fontMetrics().width('9') * digits
        return space
    
    def _update_line_number_area_width(self, _):
        """
        Update the width of the line number area.
        
        Args:
            _: The new block count (unused).
        """
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def _update_line_number_area(self, rect, dy):
        """
        Update the line number area when the editor viewport scrolls.
        
        Args:
            rect: The rectangle that needs to be updated.
            dy: The vertical scroll amount.
        """
        try:
            if dy:
                self.line_number_area.scroll(0, dy)
            else:
                self.line_number_area.update(
                    0, rect.y(), self.line_number_area.width(), rect.height()
                )
            
            if rect.contains(self.viewport().rect()):
                self._update_line_number_area_width(0)
        except Exception as e:
            logger.error(f"Error updating line number area: {e}", exc_info=True)
    
    def resizeEvent(self, event):
        """
        Handle resize events.
        
        Args:
            event: The resize event.
        """
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )
    
    def line_number_area_paint_event(self, event):
        """
        Paint the line number area.
        
        Args:
            event: The paint event.
        """
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(Qt.lightGray).lighter(120))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(
                    0, top, self.line_number_area.width(), self.fontMetrics().height(),
                    Qt.AlignRight, number
                )
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
    
    def _highlight_current_line(self):
        """Highlight the current line."""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            
            line_color = QColor(Qt.yellow).lighter(180)
            
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def _emit_cursor_position(self):
        """Emit the cursor position changed signal."""
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.cursorPositionChanged.emit(line, column)
    
    def insert_text(self, text: str):
        """
        Insert text at the current cursor position.
        
        Args:
            text: The text to insert.
        """
        self.insertPlainText(text)
    
    def get_text(self) -> str:
        """
        Get the current text in the editor.
        
        Returns:
            str: The current text.
        """
        return self.toPlainText()
    
    def set_text(self, text: str):
        """
        Set the text in the editor.
        
        Args:
            text: The text to set.
        """
        self.setPlainText(text)
    
    def get_selected_text(self) -> str:
        """
        Get the currently selected text.
        
        Returns:
            str: The selected text.
        """
        cursor = self.textCursor()
        return cursor.selectedText()
    
    def get_cursor_position(self) -> tuple:
        """
        Get the current cursor position.
        
        Returns:
            tuple: A tuple of (line, column).
        """
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        return (line, column)
    
    def set_cursor_position(self, line: int, column: int):
        """
        Set the cursor position.
        
        Args:
            line: The line number (1-based).
            column: The column number (1-based).
        """
        # Convert to 0-based indices
        line = max(0, line - 1)
        column = max(0, column - 1)
        
        # Create a cursor at the specified position
        cursor = self.textCursor()
        cursor.movePosition(cursor.Start)
        cursor.movePosition(cursor.Down, cursor.MoveAnchor, line)
        cursor.movePosition(cursor.Right, cursor.MoveAnchor, column)
        
        # Set the cursor
        self.setTextCursor(cursor)
    
    def goto_line(self, line: int):
        """
        Go to the specified line.
        
        Args:
            line: The line number (1-based).
        """
        self.set_cursor_position(line, 1)
        
    def get_syntax_highlighter(self) -> IncrementalSyntaxHighlighter:
        """
        Get the syntax highlighter.
        
        Returns:
            IncrementalSyntaxHighlighter: The syntax highlighter.
        """
        return self.syntax_highlighter
    
    def set_syntax_highlighter_batch_size(self, batch_size: int):
        """
        Set the batch size for the syntax highlighter.
        
        Args:
            batch_size (int): The number of blocks to process in one batch.
        """
        if hasattr(self, 'syntax_highlighter'):
            self.syntax_highlighter.set_batch_size(batch_size)
    
    def set_syntax_highlighter_max_time(self, max_time: int):
        """
        Set the maximum time for the syntax highlighter.
        
        Args:
            max_time (int): The maximum time in milliseconds.
        """
        if hasattr(self, 'syntax_highlighter'):
            self.syntax_highlighter.set_max_highlighting_time(max_time)
    
    def rehighlight(self):
        """Rehighlight the entire document."""
        if hasattr(self, 'syntax_highlighter'):
            self.syntax_highlighter.rehighlight()
