#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Editor for RebelDESK.

This module defines the code editor component with syntax highlighting,
line numbering, and other features.
"""

import os
import logging
import re
from pathlib import Path

from PyQt5.QtWidgets import (
    QPlainTextEdit, QWidget, QTextEdit, QVBoxLayout, 
    QApplication, QFileDialog, QMessageBox, QScrollBar,
    QMenu, QAction
)
from src.ai.code_completion import CodeCompletionManager
from src.ai.code_linting import CodeLinter
from src.utils.config_manager import ConfigManager
from src.ui.editor.completion_widget import CompletionWidget
from src.ui.editor.code_explanation_dialog import CodeExplanationDialog
from src.ui.editor.test_generation_dialog import TestGenerationDialog
from src.ui.editor.linting_widget import LintingWidget
from PyQt5.QtGui import (
    QColor, QTextFormat, QPainter, QTextCharFormat, 
    QFont, QTextCursor, QSyntaxHighlighter, QFontMetrics
)
from PyQt5.QtCore import (
    Qt, QRect, QSize, pyqtSignal, QEvent, QRegExp, 
    QTimer, QPoint, QRectF
)

from pygments import highlight
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound

logger = logging.getLogger(__name__)

class BreakpointArea(QWidget):
    """Widget for displaying breakpoints."""
    
    def __init__(self, editor):
        """
        Initialize the breakpoint area.
        
        Args:
            editor (CodeEditor): The parent editor widget.
        """
        super().__init__(editor)
        self.editor = editor
        self.setMouseTracking(True)
        
    def sizeHint(self):
        """
        Calculate the size hint for the breakpoint area.
        
        Returns:
            QSize: The recommended size.
        """
        return QSize(self.editor.breakpoint_area_width(), 0)
        
    def paintEvent(self, event):
        """
        Paint the breakpoint area.
        
        Args:
            event (QPaintEvent): The paint event.
        """
        self.editor.breakpoint_area_paint_event(event)
        
    def mousePressEvent(self, event):
        """
        Handle mouse press events.
        
        Args:
            event (QMouseEvent): The mouse event.
        """
        # Toggle breakpoint when clicking in the breakpoint area
        block_number = self.editor.blockNumberAt(event.pos().y())
        if block_number >= 0:
            self.editor.toggle_breakpoint(block_number + 1)  # Convert to 1-based line number


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


class FoldingArea(QWidget):
    """Widget for displaying code folding markers."""
    
    def __init__(self, editor):
        """
        Initialize the folding area.
        
        Args:
            editor (CodeEditor): The parent editor widget.
        """
        super().__init__(editor)
        self.editor = editor
        self.setMouseTracking(True)
        
    def sizeHint(self):
        """
        Calculate the size hint for the folding area.
        
        Returns:
            QSize: The recommended size.
        """
        return QSize(self.editor.folding_area_width(), 0)
        
    def paintEvent(self, event):
        """
        Paint the folding area.
        
        Args:
            event (QPaintEvent): The paint event.
        """
        self.editor.folding_area_paint_event(event)
        
    def mousePressEvent(self, event):
        """
        Handle mouse press events.
        
        Args:
            event (QMouseEvent): The mouse event.
        """
        # Toggle folding when clicking on a fold marker
        block_number = self.editor.blockNumberAt(event.pos().y())
        if block_number >= 0:
            block = self.editor.document().findBlockByNumber(block_number)
            if self.editor.is_foldable_block(block):
                self.editor.toggle_fold(block_number)


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
            self.language = language.lower() if language else None
            self._setup_highlighter()
            self.rehighlight()
            
    def set_style(self, style_name):
        """
        Set the style for syntax highlighting.
        
        Args:
            style_name (str): The name of the Pygments style.
        """
        # Convert style name to lowercase for consistency
        style_name = style_name.lower()
        
        # Map common theme names to Pygments style names
        style_map = {
            'github': 'github',
            'github-light': 'github',
            'dracula': 'dracula',
            'monokai': 'monokai',
            'solarized': 'solarized-light',
            'solarized-light': 'solarized-light',
            'solarized-dark': 'solarized-dark',
            'nord': 'nord'
        }
        
        # Use mapped style name if available, otherwise use the original
        pygments_style = style_map.get(style_name, style_name)
        
        if pygments_style != self.style_name:
            self.style_name = pygments_style
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
    
    # Signal emitted when a breakpoint is toggled
    breakpoint_toggled = pyqtSignal(str, int, bool)  # file_path, line, enabled
    
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
        self.breakpoint_area = BreakpointArea(self)
        self.line_number_area = LineNumberArea(self)
        self.folding_area = FoldingArea(self)
        self.unsaved_changes = False
        
        # Code folding data structures
        self.folded_blocks = {}  # Maps block numbers to their folded state
        self.fold_indicators = {}  # Maps block numbers to their fold indicators
        
        # Breakpoints
        self.breakpoints = set()  # Set of line numbers (1-based)
        
        # Initialize code completion
        self.completion_manager = CodeCompletionManager(self.config)
        
        self._setup_editor()
        self._connect_signals()
        
        # Initialize widgets after editor setup
        self.completion_widget = CompletionWidget(self, self.completion_manager)
        
        # Initialize linting widget but don't add it directly to the layout
        # It will be shown in a dialog when needed
        self.linting_widget = LintingWidget(None, self.config)  # Set parent to None
        self.linting_widget.issue_selected.connect(self.goto_line_column)
        
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
        
        # Set up line numbers, breakpoint area, and folding area
        folding_enabled = self.config.get("ui", {}).get("editor", {}).get("code_folding", True)
        left_margin = self.breakpoint_area_width() + self.line_number_area_width()
        if folding_enabled:
            left_margin += self.folding_area_width()
        self.setViewportMargins(left_margin, 0, 0, 0)
        
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
        
        # Connect completion widget signals
        if hasattr(self, 'completion_widget'):
            self.completion_widget.completion_selected.connect(self.on_completion_selected)
        
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
        # Check if line numbers are enabled
        if not self.config.get('ui', {}).get('editor', {}).get('line_numbers', True):
            return 0
            
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
            
        space = 3 + self.fontMetrics().width('9') * digits
        return space
        
    def folding_area_width(self):
        """
        Calculate the width of the folding area.
        
        Returns:
            int: The width in pixels.
        """
        return 16  # Fixed width for folding markers
        
    def breakpoint_area_width(self):
        """
        Calculate the width of the breakpoint area.
        
        Returns:
            int: The width in pixels.
        """
        return 20  # Fixed width for breakpoint markers
        
    def breakpoint_area_paint_event(self, event):
        """
        Paint the breakpoint area.
        
        Args:
            event (QPaintEvent): The paint event.
        """
        painter = QPainter(self.breakpoint_area)
        
        # Use theme-specific colors
        theme = self.config.get('ui', {}).get('theme', 'dark')
        if theme == 'dark':
            bg_color = QColor("#2d2d2d")  # Dark background
            breakpoint_color = QColor("#ff5555")  # Red for breakpoints
        else:
            bg_color = QColor("#e0e0e0")  # Light background
            breakpoint_color = QColor("#ff0000")  # Red for breakpoints
            
        painter.fillRect(event.rect(), bg_color)
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                # Check if this line has a breakpoint
                if block_number + 1 in self.breakpoints:  # Convert to 1-based line number
                    # Draw breakpoint marker (red circle)
                    rect = QRectF(4, top + 4, 12, 12)
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(breakpoint_color)
                    painter.drawEllipse(rect)
                    
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
            
    def toggle_breakpoint(self, line):
        """
        Toggle a breakpoint at the specified line.
        
        Args:
            line (int): The line number (1-based).
            
        Returns:
            bool: True if the breakpoint was added, False if it was removed.
        """
        if line in self.breakpoints:
            # Remove breakpoint
            self.breakpoints.remove(line)
            added = False
        else:
            # Add breakpoint
            self.breakpoints.add(line)
            added = True
            
        # Update the breakpoint area
        self.breakpoint_area.update()
        
        # Emit signal if a file is open
        if self.current_file:
            self.breakpoint_toggled.emit(self.current_file, line, added)
            
        return added
        
    def set_breakpoint(self, line, enabled=True):
        """
        Set a breakpoint at the specified line.
        
        Args:
            line (int): The line number (1-based).
            enabled (bool, optional): Whether the breakpoint is enabled.
            
        Returns:
            bool: True if the breakpoint was added, False if it was already set.
        """
        if enabled:
            if line not in self.breakpoints:
                self.breakpoints.add(line)
                self.breakpoint_area.update()
                return True
        else:
            if line in self.breakpoints:
                self.breakpoints.remove(line)
                self.breakpoint_area.update()
                return True
                
        return False
        
    def clear_breakpoints(self):
        """Clear all breakpoints."""
        self.breakpoints.clear()
        self.breakpoint_area.update()
        
    def updateLineNumberAreaWidth(self, _):
        """
        Update the line number area width.
        
        Args:
            _ (int): The new block count (unused).
        """
        folding_enabled = self.config.get("ui", {}).get("editor", {}).get("code_folding", True)
        left_margin = self.breakpoint_area_width() + self.line_number_area_width()
        if folding_enabled:
            left_margin += self.folding_area_width()
        self.setViewportMargins(left_margin, 0, 0, 0)
        
    def updateLineNumberArea(self, rect, dy):
        """
        Update the line number area when the editor viewport is scrolled.
        
        Args:
            rect (QRect): The rectangle that needs to be updated.
            dy (int): The vertical scroll amount.
        """
        if dy:
            self.breakpoint_area.scroll(0, dy)
            self.line_number_area.scroll(0, dy)
            if hasattr(self, 'folding_area'):
                self.folding_area.scroll(0, dy)
        else:
            self.breakpoint_area.update(0, rect.y(), self.breakpoint_area.width(), rect.height())
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
            if hasattr(self, 'folding_area'):
                self.folding_area.update(0, rect.y(), self.folding_area.width(), rect.height())
            
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
        breakpoint_width = self.breakpoint_area_width()
        line_number_width = self.line_number_area_width()
        folding_width = self.folding_area_width()
        
        # Position the breakpoint area
        self.breakpoint_area.setGeometry(QRect(cr.left(), cr.top(), breakpoint_width, cr.height()))
        
        # Position the line number area
        self.line_number_area.setGeometry(QRect(cr.left() + breakpoint_width, cr.top(), line_number_width, cr.height()))
        
        # Position the folding area
        folding_enabled = self.config.get("ui", {}).get("editor", {}).get("code_folding", True)
        if folding_enabled:
            self.folding_area.setGeometry(QRect(cr.left() + breakpoint_width + line_number_width, cr.top(), folding_width, cr.height()))
        
    def line_number_area_paint_event(self, event):
        """
        Paint the line number area.
        
        Args:
            event (QPaintEvent): The paint event.
        """
        painter = QPainter(self.line_number_area)
        
        # Use theme-specific colors
        theme = self.config.get('ui', {}).get('theme', 'dark')
        if theme == 'dark':
            bg_color = QColor("#2d2d2d")  # Dark background
            text_color = QColor("#8f908a")  # Light gray text
        else:
            bg_color = QColor("#e0e0e0")  # Light background
            text_color = QColor("#505050")  # Dark gray text
            
        painter.fillRect(event.rect(), bg_color)
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(text_color)
                painter.drawText(QRect(0, int(top), self.line_number_area.width(), self.fontMetrics().height()),
                                Qt.AlignRight, number)
                                
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
            
    def folding_area_paint_event(self, event):
        """
        Paint the folding area.
        
        Args:
            event (QPaintEvent): The paint event.
        """
        if not self.config.get("ui", {}).get("editor", {}).get("code_folding", True):
            return
            
        painter = QPainter(self.folding_area)
        
        # Use theme-specific colors
        theme = self.config.get('ui', {}).get('theme', 'dark')
        if theme == 'dark':
            bg_color = QColor("#2d2d2d")  # Dark background
            fold_color = QColor("#8f908a")  # Light gray for fold markers
            fold_highlight = QColor("#a6a6a6")  # Lighter gray for hover
        else:
            bg_color = QColor("#e0e0e0")  # Light background
            fold_color = QColor("#505050")  # Dark gray for fold markers
            fold_highlight = QColor("#303030")  # Darker gray for hover
            
        painter.fillRect(event.rect(), bg_color)
        
        # Update fold indicators
        self.update_fold_indicators()
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                # Check if this block is foldable
                if self.is_foldable_block(block):
                    # Draw fold indicator
                    rect = QRectF(2, top + 2, 12, 12)
                    painter.setPen(fold_color)
                    
                    # Check if this block is folded
                    if block_number in self.folded_blocks and self.folded_blocks[block_number]:
                        # Draw + symbol for folded block
                        painter.drawRect(rect)
                        painter.drawLine(QPoint(int(rect.left() + 3), int(rect.center().y())),
                                        QPoint(int(rect.right() - 3), int(rect.center().y())))
                        painter.drawLine(QPoint(int(rect.center().x()), int(rect.top() + 3)),
                                        QPoint(int(rect.center().x()), int(rect.bottom() - 3)))
                    else:
                        # Draw - symbol for unfolded block
                        painter.drawRect(rect)
                        painter.drawLine(QPoint(int(rect.left() + 3), int(rect.center().y())),
                                        QPoint(int(rect.right() - 3), int(rect.center().y())))
                                
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
            
    def highlightCurrentLine(self):
        """Highlight the current line."""
        # Check if line highlighting is enabled in settings
        self.highlight_current_line = self.config.get('ui', {}).get('editor', {}).get('highlight_current_line', True)
        
        if not self.highlight_current_line:
            # Clear any existing selections if highlighting is disabled
            self.setExtraSelections([])
            return
            
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            
            # Use theme-specific colors
            theme = self.config.get('ui', {}).get('theme', 'dark')
            if theme == 'dark':
                line_color = QColor("#3e3d32")  # Slightly lighter than dark background
            else:
                line_color = QColor("#e8e8e8")  # Slightly darker than light background
                
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
            
        self.setExtraSelections(extra_selections)
        
    def contextMenuEvent(self, event):
        """
        Handle context menu events.
        
        Args:
            event (QContextMenuEvent): The context menu event.
        """
        menu = self.createStandardContextMenu()
        
        # Add separator before custom actions
        menu.addSeparator()
        
        # Add actions if text is selected
        cursor = self.textCursor()
        if cursor.hasSelection():
            explain_action = QAction("Explain Code", self)
            explain_action.triggered.connect(self.explain_selected_code)
            menu.addAction(explain_action)
            
            generate_tests_action = QAction("Generate Tests", self)
            generate_tests_action.triggered.connect(self.generate_tests_for_selected_code)
            menu.addAction(generate_tests_action)
            
            lint_action = QAction("Lint Code", self)
            lint_action.triggered.connect(self.lint_selected_code)
            menu.addAction(lint_action)
            
            # Add refactoring action
            refactor_action = QAction("Refactor...", self)
            refactor_action.triggered.connect(self.refactor_selected_code)
            menu.addAction(refactor_action)
        else:
            # Add lint action for the entire file
            lint_file_action = QAction("Lint File", self)
            lint_file_action.triggered.connect(self.lint_file)
            menu.addAction(lint_file_action)
            
        # Add code folding actions
        if self.config.get("ui", {}).get("editor", {}).get("code_folding", True):
            menu.addSeparator()
            
            fold_action = QAction("Fold Current Block", self)
            fold_action.triggered.connect(self.fold_current_block)
            menu.addAction(fold_action)
            
            unfold_action = QAction("Unfold Current Block", self)
            unfold_action.triggered.connect(self.unfold_current_block)
            menu.addAction(unfold_action)
            
            fold_all_action = QAction("Fold All", self)
            fold_all_action.triggered.connect(self.fold_all)
            menu.addAction(fold_all_action)
            
            unfold_all_action = QAction("Unfold All", self)
            unfold_all_action.triggered.connect(self.unfold_all)
            menu.addAction(unfold_all_action)
        
        menu.exec_(event.globalPos())
    
    def explain_selected_code(self):
        """Show dialog to explain the selected code."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            
            # Create and show the explanation dialog
            dialog = CodeExplanationDialog(self, self.config)
            dialog.set_code(selected_text, self.language)
            dialog.exec_()
            
    def generate_tests_for_selected_code(self):
        """Show dialog to generate tests for the selected code."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            
            # Create and show the test generation dialog
            dialog = TestGenerationDialog(self, self.config)
            dialog.set_code(selected_text, self.language)
            dialog.exec_()
            
    def lint_selected_code(self):
        """Lint the selected code."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            
            # Set the code in the linting widget
            self.linting_widget.set_code(selected_text, self.language)
            
            # Show the linting widget as a dialog
            self._show_linting_dialog(selected_text)
            
    def lint_file(self):
        """Lint the entire file."""
        code = self.toPlainText()
        
        # Set the code in the linting widget
        self.linting_widget.set_code(code, self.language)
        
        # Show the linting widget as a dialog
        self._show_linting_dialog(code)
        
    def refactor_selected_code(self):
        """Show dialog to refactor the selected code."""
        from src.ui.code_refactoring import RefactoringDialog
        
        cursor = self.textCursor()
        if cursor.hasSelection():
            # Get the selected text and its position
            selection_start = cursor.selectionStart()
            selection_end = cursor.selectionEnd()
            
            # Create and show the refactoring dialog
            dialog = RefactoringDialog(self, self.config)
            dialog.set_code(self.toPlainText(), selection_start, selection_end)
            
            # Connect the refactoring_applied signal
            dialog.refactoring_applied.connect(self._on_refactoring_applied)
            
            # Show the dialog
            dialog.exec_()
            
    def _on_refactoring_applied(self, refactored_code, info):
        """
        Handle refactoring applied.
        
        Args:
            refactored_code (str): The refactored code.
            info (dict): Additional information about the refactoring.
        """
        # Replace the entire content with the refactored code
        self.setPlainText(refactored_code)
        
        # Mark the document as having unsaved changes
        self.unsaved_changes = True
        
        # Log the refactoring
        operation_name = info.get('operation_name', 'Unknown')
        logger.info(f"Applied refactoring operation: {operation_name}")
        
    def _show_linting_dialog(self, code):
        """
        Show the linting widget in a dialog.
        
        Args:
            code (str): The code to lint.
        """
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Code Linting")
        dialog.resize(800, 600)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Add linting widget
        layout.addWidget(self.linting_widget)
        
        # Create button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Create close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        
        # Add button layout
        layout.addLayout(button_layout)
        
        # Lint the code
        self.linting_widget.lint_code(code, self.language)
        
        # Show dialog
        dialog.exec_()
        
    def goto_line_column(self, line: int, column: int):
        """
        Go to the specified line and column.
        
        Args:
            line (int): The line number (1-based).
            column (int): The column number (1-based).
        """
        # Adjust for 0-based indexing
        line = max(0, line - 1)
        column = max(0, column - 1)
        
        # Create cursor at the specified position
        cursor = QTextCursor(self.document().findBlockByLineNumber(line))
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, column)
        
        # Set cursor and ensure it's visible
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        self.setFocus()
    
    def keyPressEvent(self, event):
        """
        Handle key press events.
        
        Args:
            event (QKeyEvent): The key event.
        """
        # Handle completion widget key events if it's visible
        if hasattr(self, 'completion_widget') and self.completion_widget.isVisible():
            # Let the completion widget handle navigation keys
            if event.key() in [Qt.Key_Down, Qt.Key_Up, Qt.Key_Return, Qt.Key_Enter, Qt.Key_Escape, Qt.Key_Tab]:
                self.completion_widget.keyPressEvent(event)
                if event.isAccepted():
                    return
        
        # Handle code folding shortcuts
        if self.config.get("ui", {}).get("editor", {}).get("code_folding", True):
            # Fold/unfold with Alt+Plus and Alt+Minus
            if event.modifiers() == Qt.AltModifier:
                if event.key() == Qt.Key_Plus:
                    self.fold_current_block()
                    return
                elif event.key() == Qt.Key_Minus:
                    self.unfold_current_block()
                    return
                    
            # Fold all with Ctrl+Alt+Plus, unfold all with Ctrl+Alt+Minus
            if event.modifiers() == (Qt.ControlModifier | Qt.AltModifier):
                if event.key() == Qt.Key_Plus:
                    self.fold_all()
                    return
                elif event.key() == Qt.Key_Minus:
                    self.unfold_all()
                    return
        
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
        
    # Code folding methods
    def update_fold_indicators(self):
        """Update the fold indicators for all blocks."""
        block = self.document().begin()
        while block.isValid():
            block_number = block.blockNumber()
            if self.is_foldable_block(block):
                self.fold_indicators[block_number] = True
            else:
                if block_number in self.fold_indicators:
                    del self.fold_indicators[block_number]
            block = block.next()
            
    def is_foldable_block(self, block):
        """
        Check if a block is foldable.
        
        Args:
            block (QTextBlock): The block to check.
            
        Returns:
            bool: True if the block is foldable, False otherwise.
        """
        # A block is foldable if it has indented blocks after it
        if not block.isValid():
            return False
            
        text = block.text()
        if not text.strip():
            return False
            
        # Check if this block ends with a colon (function/class/loop/etc.)
        if text.rstrip().endswith(':'):
            # Check if there are indented blocks after this one
            next_block = block.next()
            if next_block.isValid():
                next_text = next_block.text()
                # Check if the next block is indented
                if next_text.startswith(' ') or next_text.startswith('\t'):
                    return True
                    
        return False
        
    def get_fold_range(self, block_number):
        """
        Get the range of blocks to fold.
        
        Args:
            block_number (int): The block number to start folding from.
            
        Returns:
            tuple: A tuple of (start_block, end_block) or None if not foldable.
        """
        block = self.document().findBlockByNumber(block_number)
        if not self.is_foldable_block(block):
            return None
            
        # Get the indentation level of this block
        text = block.text()
        indent_level = 0
        for char in text:
            if char == ' ':
                indent_level += 1
            elif char == '\t':
                indent_level += self.config.get("ui", {}).get("editor", {}).get("tab_size", 4)
            else:
                break
                
        # Find the end of the fold
        end_block = block
        next_block = block.next()
        while next_block.isValid():
            next_text = next_block.text()
            
            # Skip empty lines
            if not next_text.strip():
                end_block = next_block
                next_block = next_block.next()
                continue
                
            # Calculate the indentation level of the next block
            next_indent = 0
            for char in next_text:
                if char == ' ':
                    next_indent += 1
                elif char == '\t':
                    next_indent += self.config.get("ui", {}).get("editor", {}).get("tab_size", 4)
                else:
                    break
                    
            # If the next block has less or equal indentation, we've reached the end of the fold
            if next_indent <= indent_level:
                break
                
            end_block = next_block
            next_block = next_block.next()
            
        return (block, end_block)
        
    def toggle_fold(self, block_number):
        """
        Toggle folding for a block.
        
        Args:
            block_number (int): The block number to toggle folding for.
        """
        # Check if the block is already folded
        if block_number in self.folded_blocks and self.folded_blocks[block_number]:
            self.unfold_block(block_number)
        else:
            self.fold_block(block_number)
            
    def fold_block(self, block_number):
        """
        Fold a block.
        
        Args:
            block_number (int): The block number to fold.
        """
        fold_range = self.get_fold_range(block_number)
        if not fold_range:
            return
            
        start_block, end_block = fold_range
        
        # Hide all blocks in the range except the first one
        block = start_block.next()
        while block.isValid() and block.blockNumber() <= end_block.blockNumber():
            block.setVisible(False)
            block = block.next()
            
        # Mark the block as folded
        self.folded_blocks[block_number] = True
        
        # Update the document
        self.document().markContentsDirty(start_block.position(), end_block.position() + end_block.length())
        
        # Update the viewport
        self.viewport().update()
        
    def unfold_block(self, block_number):
        """
        Unfold a block.
        
        Args:
            block_number (int): The block number to unfold.
        """
        fold_range = self.get_fold_range(block_number)
        if not fold_range:
            return
            
        start_block, end_block = fold_range
        
        # Show all blocks in the range
        block = start_block.next()
        while block.isValid() and block.blockNumber() <= end_block.blockNumber():
            block.setVisible(True)
            block = block.next()
            
        # Mark the block as unfolded
        self.folded_blocks[block_number] = False
        
        # Update the document
        self.document().markContentsDirty(start_block.position(), end_block.position() + end_block.length())
        
        # Update the viewport
        self.viewport().update()
        
    def fold_current_block(self):
        """Fold the current block."""
        cursor = self.textCursor()
        block_number = cursor.blockNumber()
        self.fold_block(block_number)
        
    def unfold_current_block(self):
        """Unfold the current block."""
        cursor = self.textCursor()
        block_number = cursor.blockNumber()
        self.unfold_block(block_number)
        
    def fold_all(self):
        """Fold all foldable blocks."""
        block = self.document().begin()
        while block.isValid():
            if self.is_foldable_block(block):
                self.fold_block(block.blockNumber())
            block = block.next()
            
    def unfold_all(self):
        """Unfold all folded blocks."""
        for block_number in list(self.folded_blocks.keys()):
            if self.folded_blocks[block_number]:
                self.unfold_block(block_number)
                
    def blockNumberAt(self, y_position):
        """
        Get the block number at a given y position.
        
        Args:
            y_position (int): The y position.
            
        Returns:
            int: The block number, or -1 if no block is found.
        """
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= y_position:
            if top <= y_position and y_position <= bottom:
                return block_number
                
            block = block.next()
            if not block.isValid():
                break
                
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
            
        return -1
        
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
                language = lexer.name.lower()
                self.language = language
                if self.highlighter:
                    self.highlighter.language = language  # Set directly on the highlighter
                    self.highlighter._setup_highlighter()
                    self.highlighter.rehighlight()
            except ClassNotFound:
                # Default to Python if language can't be determined
                language = "python"
                self.language = language
                if self.highlighter:
                    self.highlighter.language = language  # Set directly on the highlighter
                    self.highlighter._setup_highlighter()
                    self.highlighter.rehighlight()
                
            # Ensure syntax theme is set in config
            if 'syntax' not in self.config:
                self.config['syntax'] = {}
            if 'theme' not in self.config['syntax']:
                self.config['syntax']['theme'] = 'monokai'
                
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
            self.document().setModified(False)
            
            # Emit signal that file has changed
            self.file_changed.emit(save_path)
            
            logger.info(f"Saved file: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving file {save_path}: {e}", exc_info=True)
            return False
            
    def on_completion_selected(self, completion):
        """
        Handle completion selection.
        
        Args:
            completion (dict): The selected completion.
        """
        # Log the selected completion
        logger.debug(f"Completion selected: {completion.get('text')} ({completion.get('provider')})")
    
    def set_theme(self, theme):
        """
        Set the theme for the editor.
        
        Args:
            theme (str): The theme to apply ('dark' or 'light').
        """
        # Update the syntax highlighting style based on the theme
        syntax_theme = self.config.get('syntax', {}).get('theme', 'monokai')
        if self.highlighter:
            self.highlighter.set_style(syntax_theme)
        
        # Apply theme-specific colors
        if theme == 'dark':
            # Set dark theme colors
            self.setStyleSheet("""
                QPlainTextEdit {
                    background-color: #1e1e1e;
                    color: #f0f0f0;
                    border: none;
                }
            """)
            
            # Update line number area colors
            self.line_number_area.setStyleSheet("""
                background-color: #2d2d2d;
                color: #8f908a;
            """)
            
            # Update current line highlight color
            if self.highlight_current_line:
                self.highlightCurrentLine()
        else:
            # Set light theme colors
            self.setStyleSheet("""
                QPlainTextEdit {
                    background-color: #f5f5f5;
                    color: #000000;
                    border: none;
                }
            """)
            
            # Update line number area colors
            self.line_number_area.setStyleSheet("""
                background-color: #e0e0e0;
                color: #505050;
            """)
            
            # Update current line highlight color
            if self.highlight_current_line:
                self.highlightCurrentLine()
        
        # Update the config
        self.config['ui']['theme'] = theme
        
        logger.info(f"Applied {theme} theme to editor")
    
    def has_unsaved_changes(self):
        """
        Check if the editor has unsaved changes.
        
        Returns:
            bool: True if there are unsaved changes, False otherwise.
        """
        return self.unsaved_changes or self.document().isModified()
