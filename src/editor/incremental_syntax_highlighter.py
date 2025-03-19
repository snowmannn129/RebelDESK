#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Incremental Syntax Highlighter for RebelDESK.

This module provides an incremental syntax highlighter that only rehighlights
the modified parts of a document, improving performance for large files.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Set, Tuple

from PyQt5.QtCore import Qt, QRegExp, QObject, QTimer
from PyQt5.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QFont, QColor, 
    QTextDocument, QTextBlock, QTextCursor
)

logger = logging.getLogger(__name__)

class HighlightingRule:
    """A rule for syntax highlighting."""
    
    def __init__(self, pattern: str, format: QTextCharFormat):
        """
        Initialize the highlighting rule.
        
        Args:
            pattern (str): The regex pattern to match.
            format (QTextCharFormat): The text format to apply.
        """
        self.pattern = QRegExp(pattern)
        self.format = format


class IncrementalSyntaxHighlighter(QSyntaxHighlighter):
    """
    A syntax highlighter that only rehighlights the modified parts of a document.
    
    This highlighter improves performance for large files by only rehighlighting
    the blocks that have been modified, rather than the entire document.
    """
    
    def __init__(self, document: QTextDocument):
        """
        Initialize the syntax highlighter.
        
        Args:
            document (QTextDocument): The document to highlight.
        """
        super().__init__(document)
        
        # Initialize state
        self.highlighting_rules: List[HighlightingRule] = []
        self.modified_blocks: Set[int] = set()
        self.dirty_blocks: Set[int] = set()
        self.is_rehighlighting = False
        self.batch_size = 50  # Number of blocks to process in one batch
        self.max_highlighting_time = 20  # Maximum time in ms to spend highlighting
        
        # Create a timer for deferred highlighting
        self.highlight_timer = QTimer(self)
        self.highlight_timer.setSingleShot(True)
        self.highlight_timer.timeout.connect(self.highlight_dirty_blocks)
        
        # Connect to the document's contentsChange signal
        document.contentsChange.connect(self.handle_contents_change)
        
        # Set up default highlighting rules
        self.setup_highlighting_rules()
        
    def setup_highlighting_rules(self):
        """Set up the default highlighting rules."""
        # Create formats
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(120, 120, 250))
        keyword_format.setFontWeight(QFont.Bold)
        
        class_format = QTextCharFormat()
        class_format.setForeground(QColor(200, 120, 50))
        class_format.setFontWeight(QFont.Bold)
        
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(120, 200, 120))
        
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(220, 120, 120))
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(120, 120, 120))
        comment_format.setFontItalic(True)
        
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(180, 180, 0))
        
        # Create rules
        
        # Python keywords
        keywords = [
            "and", "as", "assert", "break", "class", "continue", "def",
            "del", "elif", "else", "except", "False", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda", "None",
            "nonlocal", "not", "or", "pass", "raise", "return", "True",
            "try", "while", "with", "yield"
        ]
        
        for keyword in keywords:
            pattern = f"\\b{keyword}\\b"
            self.highlighting_rules.append(HighlightingRule(pattern, keyword_format))
            
        # Class names
        self.highlighting_rules.append(
            HighlightingRule("\\bclass\\b\\s*(\\w+)", class_format)
        )
        
        # Function definitions
        self.highlighting_rules.append(
            HighlightingRule("\\bdef\\b\\s*(\\w+)", function_format)
        )
        
        # Strings (single quotes)
        self.highlighting_rules.append(
            HighlightingRule("'[^']*'", string_format)
        )
        
        # Strings (double quotes)
        self.highlighting_rules.append(
            HighlightingRule("\"[^\"]*\"", string_format)
        )
        
        # Comments
        self.highlighting_rules.append(
            HighlightingRule("#[^\n]*", comment_format)
        )
        
        # Numbers
        self.highlighting_rules.append(
            HighlightingRule("\\b[0-9]+\\b", number_format)
        )
        
    def handle_contents_change(self, position: int, removed: int, added: int):
        """
        Handle document contents change.
        
        Args:
            position (int): The position where the change occurred.
            removed (int): The number of characters removed.
            added (int): The number of characters added.
        """
        # Find the affected blocks
        document = self.document()
        if document is None:
            return
            
        # Find the first affected block
        block = document.findBlock(position)
        if not block.isValid():
            return
            
        # Mark the affected blocks as dirty
        first_block_number = block.blockNumber()
        
        # Find the last affected block
        last_position = position + added
        last_block = document.findBlock(last_position)
        if not last_block.isValid():
            last_block = document.lastBlock()
            
        last_block_number = last_block.blockNumber()
        
        # Mark all blocks in the range as dirty
        for block_number in range(first_block_number, last_block_number + 1):
            self.dirty_blocks.add(block_number)
            
        # Schedule highlighting
        self.schedule_highlighting()
        
    def schedule_highlighting(self):
        """Schedule highlighting of dirty blocks."""
        if not self.highlight_timer.isActive():
            self.highlight_timer.start(10)  # Start after 10ms
            
    def highlight_dirty_blocks(self):
        """Highlight the dirty blocks."""
        # Check if there are dirty blocks
        if not self.dirty_blocks:
            return
            
        # Set rehighlighting flag
        self.is_rehighlighting = True
        
        try:
            # Get the document
            document = self.document()
            if document is None:
                return
                
            # Get the start time
            start_time = time.time()
            
            # Process dirty blocks in batches
            blocks_processed = 0
            
            # Convert dirty blocks to a list and sort
            dirty_blocks = sorted(self.dirty_blocks)
            
            for block_number in dirty_blocks:
                # Check if we've exceeded the maximum time
                elapsed_time = (time.time() - start_time) * 1000
                if elapsed_time > self.max_highlighting_time:
                    # We've spent too much time highlighting, schedule the rest for later
                    break
                    
                # Get the block
                block = document.findBlockByNumber(block_number)
                if not block.isValid():
                    # Block is no longer valid, remove from dirty blocks
                    self.dirty_blocks.remove(block_number)
                    continue
                    
                # Highlight the block
                self.highlight_block(block.text(), block)
                
                # Remove from dirty blocks
                self.dirty_blocks.remove(block_number)
                
                # Increment counter
                blocks_processed += 1
                
                # Check if we've processed enough blocks
                if blocks_processed >= self.batch_size:
                    break
                    
            # If there are still dirty blocks, schedule another highlighting pass
            if self.dirty_blocks:
                self.schedule_highlighting()
        finally:
            # Reset rehighlighting flag
            self.is_rehighlighting = False
            
    def highlightBlock(self, text: str):
        """
        Highlight a block of text.
        
        This method is called by the QSyntaxHighlighter framework.
        
        Args:
            text (str): The text to highlight.
        """
        # If we're already rehighlighting, don't do anything
        if self.is_rehighlighting:
            return
            
        # Get the current block
        block = self.currentBlock()
        
        # Add to modified blocks
        self.modified_blocks.add(block.blockNumber())
        
        # Add to dirty blocks
        self.dirty_blocks.add(block.blockNumber())
        
        # Schedule highlighting
        self.schedule_highlighting()
        
    def highlight_block(self, text: str, block: QTextBlock):
        """
        Highlight a block of text.
        
        Args:
            text (str): The text to highlight.
            block (QTextBlock): The block to highlight.
        """
        # Apply highlighting rules
        for rule in self.highlighting_rules:
            expression = rule.pattern
            index = expression.indexIn(text)
            
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, rule.format)
                index = expression.indexIn(text, index + length)
                
    def rehighlight(self):
        """Rehighlight the entire document."""
        # Mark all blocks as dirty
        document = self.document()
        if document is None:
            return
            
        for block_number in range(document.blockCount()):
            self.dirty_blocks.add(block_number)
            self.modified_blocks.add(block_number)
            
        # Schedule highlighting
        self.schedule_highlighting()
        
    def rehighlight_block(self, block: QTextBlock):
        """
        Rehighlight a specific block.
        
        Args:
            block (QTextBlock): The block to rehighlight.
        """
        if block.isValid():
            block_number = block.blockNumber()
            self.dirty_blocks.add(block_number)
            self.modified_blocks.add(block_number)
            self.schedule_highlighting()
            
    def set_batch_size(self, batch_size: int):
        """
        Set the batch size for highlighting.
        
        Args:
            batch_size (int): The number of blocks to process in one batch.
        """
        self.batch_size = max(1, batch_size)
        
    def set_max_highlighting_time(self, max_time: int):
        """
        Set the maximum time to spend highlighting.
        
        Args:
            max_time (int): The maximum time in milliseconds.
        """
        self.max_highlighting_time = max(1, max_time)
        
    def get_dirty_block_count(self) -> int:
        """
        Get the number of dirty blocks.
        
        Returns:
            int: The number of dirty blocks.
        """
        return len(self.dirty_blocks)
        
    def get_modified_block_count(self) -> int:
        """
        Get the number of modified blocks.
        
        Returns:
            int: The number of modified blocks.
        """
        return len(self.modified_blocks)
        
    def clear_modified_blocks(self):
        """Clear the set of modified blocks."""
        self.modified_blocks.clear()
