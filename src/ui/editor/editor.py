#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Editor for RebelDESK.

This module defines the code editor component with syntax highlighting,
line numbering, and other features.
"""

import os
import logging
from pathlib import Path

from PyQt5.QtWidgets import (
    QPlainTextEdit, QWidget, QTextEdit, QVBoxLayout, 
    QApplication, QFileDialog, QMessageBox
)
from PyQt5.QtGui import (
    QColor, QTextFormat, QPainter, QTextCharFormat, 
    QFont, QTextCursor, QSyntaxHighlighter, QFontMetrics
)
from PyQt5.QtCore import (
    Qt, QRect, QSize, pyqtSignal, QEvent, QRegExp, 
    QTimer, QPoint
)

from pygments import highlight
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound

logger = logging.getLogger(__name__)

class LineNumberArea(QWidget):
    """Widget for displaying line numbers."""
    
    def __init__(self, editor):
        """
        Initialize the line number area.
        
        Args:
            editor (CodeEditor): The parent editor widget.
        """
        super().__init__(editor)
        self.editor = editor
        
    def sizeHint(self):
        """
        Calculate the size hint for the line number area.
        
        Returns:
            QSize: The recommended size.
        """
        return QSize(self.editor.line_number_area_width(), 0)
        
    def paintEvent(self, event):
        """
        Paint the line number area.
        
        Args:
            event (QPaintEvent): The paint event.
        """
        self.editor.line_number_area_paint_event(event)


class SyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter using Pygments."""
    
    def __init__(self, parent, language=None, style_name="monokai"):
        """
        Initialize the syntax highlighter.
        
        Args:
            parent (QTextDocument): The parent text document.
            language (str, optional): The language for syntax highlighting.
            style_name (str, optional): The name of the Pygments style to use.
        """
        super().__init__(parent)
        self.language = language
        self.style_name = style_name
        self.lexer = None
        self.formatter = None
        
        self._setup_highlighter()
        
    def _setup_highlighter(self):
        """Set up the highlighter with the current language and style."""
        try:
            if self.language:
                self.lexer = get_lexer_by_name(self.language, stripall=True)
            else:
                # Default to Python if no language is specified
                self.lexer = get_lexer_by_name("python", stripall=True)
                
            style = get_style_by_name(self.style_name)
            self.formatter = HtmlFormatter(style=style)
            
        except ClassNotFound as e:
            logger.warning(f"Syntax highlighting error: {e}")
            self.lexer = None
            self.formatter = None
            
    def set_language(self, language):
        """
        Set the language for syntax highlighting.
        
        Args:
            language (str): The language name.
        """
        if language != self.language:
            self.language = language
            self._setup_highlighter()
            self.rehighlight()
            
    def set_style(self, style_name):
        """
        Set the style for syntax highlighting.
        
        Args:
            style_name (str): The name of the Pygments style.
        """
        if style_name != self.style_name:
            self.style_name = style_name
            self._setup_highlighter()
            self.rehighlight()
            
    def highlightBlock(self, text):
        """
        Highlight a block of text.
        
        Args:
            text (str): The text to highlight.
        """
        if not self.lexer or not self.formatter:
            return
            
        # Get the current block's format
        block_format = QTextCharFormat()
        
        try:
            # Highlight the text using Pygments
            highlighted = highlight(text, self.lexer, self.formatter)
            
            # Parse the HTML and apply formatting
            cursor = QTextCursor(self.document())
            cursor.setPosition(self.currentBlock().position())
            
            # Apply basic formatting for now
            # In a future implementation, we'll parse the HTML and apply more detailed formatting
            if "<span" in highlighted:
                # There is some highlighting to apply
                block_format.setForeground(QColor("#f8f8f2"))  # Default Monokai text color
                self.setFormat(0, len(text), block_format)
                
                # Apply different colors for keywords, strings, etc.
                # This is a simplified approach; a more complete implementation would parse the HTML
                keyword_format = QTextCharFormat()
                keyword_format.setForeground(QColor("#66d9ef"))  # Monokai keyword color
                
                string_format = QTextCharFormat()
                string_format.setForeground(QColor("#e6db74"))  # Monokai string color
                
                comment_format = QTextCharFormat()
                comment_format.setForeground(QColor("#75715e"))  # Monokai comment color
                
                # Apply keyword formatting for common keywords
                for keyword in ["def", "class", "import", "from", "return", "if", "else", "elif", "for", "while", "try", "except", "with"]:
                    index = text.find(keyword)
                    while index >= 0:
                        # Check if it's a whole word
                        if (index == 0 or not text[index-1].isalnum()) and (index + len(keyword) == len(text) or not text[index + len(keyword)].isalnum()):
                            self.setFormat(index, len(keyword), keyword_format)
                        index = text.find(keyword, index + 1)
                
                # Apply string formatting
                in_string = False
                string_start = 0
                for i, char in enumerate(text):
                    if char in ['"', "'"]:
                        if not in_string:
                            in_string = True
                            string_start = i
                        else:
                            in_string = False
                            self.setFormat(string_start, i - string_start + 1, string_format)
                
                # Apply comment formatting
                comment_index = text.find("#")
                if comment_index >= 0:
                    self.setFormat(comment_index, len(text) - comment_index, comment_format)
            
        except Exception as e:
            logger.error(f"Error highlighting block: {e}", exc_info=True)


class CodeEditor(QPlainTextEdit):
    """Code editor widget with syntax highlighting and line numbers."""
    
    # Signal emitted when the file is changed
    file_changed = pyqtSignal(str)
    
    def __init__(self, parent=None, config=None):
        """
        Initialize the code editor.
        
        Args:
            parent (QWidget, optional): The parent widget.
            config (dict, optional): Configuration settings.
        """
        super().__init__(parent)
        
        self.config = config or {}
        self.current_file = None
        self.language = None
        self.highlighter = None
        self.line_number_area = LineNumberArea(self)
        self.unsaved_changes = False
        
        self._setup_editor()
        self._connect_signals()
        
    def _setup_editor(self):
        """Set up the editor appearance and behavior."""
        # Set up font
        font_family = self.config.get("ui", {}).get("font", {}).get("family", "Consolas, 'Courier New', monospace")
        font_size = self.config.get("ui", {}).get("font", {}).get("size", 12)
        font = QFont(font_family.split(",")[0].strip().strip("'\""))
        font.setPointSize(font_size)
        self.setFont(font)
        
        # Set up tab size
        tab_size = self.config.get("ui", {}).get("editor", {}).get("tab_size", 4)
        self.setTabStopWidth(tab_size * QFontMetrics(font).width(' '))
        
        # Set up line wrapping
        word_wrap = self.config.get("ui", {}).get("editor", {}).get("word_wrap", False)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth if word_wrap else QPlainTextEdit.NoWrap)
        
        # Set up line numbers
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        
        # Set up syntax highlighting
        self.highlighter = SyntaxHighlighter(self.document())
        
        # Set up auto-indentation
        self.auto_indent = self.config.get("ui", {}).get("editor", {}).get("auto_indent", True)
        
        # Set up current line highlighting
        self.highlight_current_line = self.config.get("ui", {}).get("editor", {}).get("highlight_current_line", True)
        if self.highlight_current_line:
            self.highlightCurrentLine()
            
        # Set up auto-save
        self.auto_save = self.config.get("editor", {}).get("auto_save", True)
        self.auto_save_interval = self.config.get("editor", {}).get("auto_save_interval", 60)
        
        if self.auto_save:
            self.auto_save_timer = QTimer(self)
            self.auto_save_timer.timeout.connect(self.save_file)
            self.auto_save_timer.start(self.auto_save_interval * 1000)
            
    def _connect_signals(self):
        """Connect signals to slots."""
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.textChanged.connect(self.onTextChanged)
        
    def onTextChanged(self):
        """Handle text changed event."""
        self.unsaved_changes = True
        
        # Reset auto-save timer if auto-save is enabled
        if self.auto_save and self.current_file:
            self.auto_save_timer.stop()
            self.auto_save_timer.start(self.auto_save_interval * 1000)
            
    def line_number_area_width(self):
        """
        Calculate the width of the line number area.
        
        Returns:
            int: The width in pixels.
        """
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
            
        space = 3 + self.fontMetrics().width('9') * digits
        return space
        
    def updateLineNumberAreaWidth(self, _):
        """
        Update the line number area width.
        
        Args:
            _ (int): The new block count (unused).
        """
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        
    def updateLineNumberArea(self, rect, dy):
        """
        Update the line number area when the editor viewport is scrolled.
        
        Args:
            rect (QRect): The rectangle that needs to be updated.
            dy (int): The vertical scroll amount.
        """
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
            
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)
            
    def resizeEvent(self, event):
        """
        Handle resize events.
        
        Args:
            event (QResizeEvent): The resize event.
        """
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
        
    def line_number_area_paint_event(self, event):
        """
        Paint the line number area.
        
        Args:
            event (QPaintEvent): The paint event.
        """
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#2d2d2d"))  # Dark background for line numbers
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#8f908a"))  # Light gray for line numbers
                painter.drawText(QRect(0, int(top), self.line_number_area.width(), self.fontMetrics().height()),
                                Qt.AlignRight, number)
                                
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
            
    def highlightCurrentLine(self):
        """Highlight the current line."""
        if not self.highlight_current_line:
            return
            
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            
            line_color = QColor("#3e3d32")  # Slightly lighter than background for current line
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
            
        self.setExtraSelections(extra_selections)
        
    def keyPressEvent(self, event):
        """
        Handle key press events.
        
        Args:
            event (QKeyEvent): The key event.
        """
        # Handle auto-indentation
        if self.auto_indent and event.key() == Qt.Key_Return:
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            
            # Get the indentation of the current line
            indentation = ""
            for char in text:
                if char in [' ', '\t']:
                    indentation += char
                else:
                    break
                    
            # Add extra indentation if the line ends with a colon
            if text.rstrip().endswith(':'):
                if self.config.get("ui", {}).get("editor", {}).get("use_spaces", True):
                    tab_size = self.config.get("ui", {}).get("editor", {}).get("tab_size", 4)
                    indentation += ' ' * tab_size
                else:
                    indentation += '\t'
                    
            # Insert the indentation after the newline
            super().keyPressEvent(event)
            self.insertPlainText(indentation)
            return
            
        # Handle tab key
        if event.key() == Qt.Key_Tab:
            if self.config.get("ui", {}).get("editor", {}).get("use_spaces", True):
                tab_size = self.config.get("ui", {}).get("editor", {}).get("tab_size", 4)
                self.insertPlainText(' ' * tab_size)
                return
                
        super().keyPressEvent(event)
        
    def set_language(self, language):
        """
        Set the language for syntax highlighting.
        
        Args:
            language (str): The language name.
        """
        self.language = language
        if self.highlighter:
            self.highlighter.set_language(language)
            
    def set_style(self, style_name):
        """
        Set the style for syntax highlighting.
        
        Args:
            style_name (str): The name of the Pygments style.
        """
        if self.highlighter:
            self.highlighter.set_style(style_name)
            
    def load_file(self, file_path):
        """
        Load a file into the editor.
        
        Args:
            file_path (str): Path to the file to load.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Get the file manager from the parent window
            file_manager = None
            if hasattr(self.parent(), 'file_manager'):
                file_manager = self.parent().file_manager
            
            # Load the file content
            if file_manager:
                content, error = file_manager.open_file(file_path)
                if error:
                    logger.error(f"Error loading file {file_path}: {error}")
                    return False
            else:
                # Fallback to direct file loading if file manager is not available
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Temporarily disconnect the textChanged signal to prevent setting unsaved_changes to True
            self.textChanged.disconnect(self.onTextChanged)
            
            self.setPlainText(content)
            self.current_file = file_path
            self.unsaved_changes = False
            
            # Reconnect the textChanged signal
            self.textChanged.connect(self.onTextChanged)
            
            # Determine language from file extension
            try:
                lexer = get_lexer_for_filename(file_path)
                self.set_language(lexer.name.lower())
            except ClassNotFound:
                # Default to Python if language can't be determined
                self.set_language("python")
                
            # Emit signal that file has changed
            self.file_changed.emit(file_path)
            
            logger.info(f"Loaded file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}", exc_info=True)
            return False
            
    def save_file(self, file_path=None):
        """
        Save the current file.
        
        Args:
            file_path (str, optional): Path to save the file to.
                If None, uses the current file path.
                
        Returns:
            bool: True if successful, False otherwise.
        """
        if not file_path and not self.current_file:
            return False
            
        save_path = file_path or self.current_file
        
        try:
            # Get the file manager from the parent window
            file_manager = None
            if hasattr(self.parent(), 'file_manager'):
                file_manager = self.parent().file_manager
            
            # Save the file content
            content = self.toPlainText()
            if file_manager:
                success, error = file_manager.save_file(save_path, content)
                if not success:
                    logger.error(f"Error saving file {save_path}: {error}")
                    return False
            else:
                # Fallback to direct file saving if file manager is not available
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
            self.current_file = save_path
            self.unsaved_changes = False
            
            # Emit signal that file has changed
            self.file_changed.emit(save_path)
            
            logger.info(f"Saved file: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving file {save_path}: {e}", exc_info=True)
            return False
            
    def has_unsaved_changes(self):
        """
        Check if the editor has unsaved changes.
        
        Returns:
            bool: True if there are unsaved changes, False otherwise.
        """
        return self.unsaved_changes
