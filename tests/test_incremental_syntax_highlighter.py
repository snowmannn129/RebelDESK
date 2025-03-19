#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the incremental syntax highlighter.
"""

import unittest
import sys
import time
from typing import List, Set

from PyQt5.QtWidgets import QApplication, QPlainTextEdit
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QTextDocument, QTextCursor

from src.editor.incremental_syntax_highlighter import IncrementalSyntaxHighlighter

class TestIncrementalSyntaxHighlighter(unittest.TestCase):
    """Tests for the incremental syntax highlighter."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test class."""
        # Create the application
        cls.app = QApplication.instance() or QApplication([])
        
    def setUp(self):
        """Set up the test."""
        # Create a text edit
        self.text_edit = QPlainTextEdit()
        
        # Create a document
        self.document = self.text_edit.document()
        
        # Create a highlighter
        self.highlighter = IncrementalSyntaxHighlighter(self.document)
        
        # Set batch size to a small value for testing
        self.highlighter.set_batch_size(5)
        
        # Set max highlighting time to a small value for testing
        self.highlighter.set_max_highlighting_time(10)
        
    def tearDown(self):
        """Clean up after the test."""
        # Delete the highlighter
        self.highlighter.setDocument(None)
        self.highlighter.deleteLater()
        
        # Delete the text edit
        self.text_edit.deleteLater()
        
    def test_initialization(self):
        """Test that the highlighter is initialized correctly."""
        # Check that the highlighter is attached to the document
        self.assertEqual(self.highlighter.document(), self.document)
        
        # Check that the highlighting rules are set up
        self.assertGreater(len(self.highlighter.highlighting_rules), 0)
        
        # Check that the batch size is set correctly
        self.assertEqual(self.highlighter.batch_size, 5)
        
        # Check that the max highlighting time is set correctly
        self.assertEqual(self.highlighter.max_highlighting_time, 10)
        
    def test_handle_contents_change(self):
        """Test that the highlighter handles contents change correctly."""
        # Set some text
        self.text_edit.setPlainText("def test_function():\n    pass")
        
        # Process events
        QApplication.processEvents()
        
        # Check that the dirty blocks are set
        self.assertGreater(self.highlighter.get_dirty_block_count(), 0)
        
        # Wait for highlighting to complete
        self.wait_for_highlighting()
        
        # Check that the dirty blocks are cleared
        self.assertEqual(self.highlighter.get_dirty_block_count(), 0)
        
        # Check that the modified blocks are set
        self.assertGreater(self.highlighter.get_modified_block_count(), 0)
        
    def test_highlight_dirty_blocks(self):
        """Test that the highlighter highlights dirty blocks correctly."""
        # Set some text
        self.text_edit.setPlainText("def test_function():\n    pass")
        
        # Process events
        QApplication.processEvents()
        
        # Wait for highlighting to complete
        self.wait_for_highlighting()
        
        # Check that the dirty blocks are cleared
        self.assertEqual(self.highlighter.get_dirty_block_count(), 0)
        
        # Modify the text
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText("\n\ndef another_function():\n    return True")
        
        # Process events
        QApplication.processEvents()
        
        # Check that the dirty blocks are set
        self.assertGreater(self.highlighter.get_dirty_block_count(), 0)
        
        # Wait for highlighting to complete
        self.wait_for_highlighting()
        
        # Check that the dirty blocks are cleared
        self.assertEqual(self.highlighter.get_dirty_block_count(), 0)
        
    def test_rehighlight(self):
        """Test that the highlighter rehighlights the entire document correctly."""
        # Set some text
        self.text_edit.setPlainText("def test_function():\n    pass\n\ndef another_function():\n    return True")
        
        # Process events
        QApplication.processEvents()
        
        # Wait for highlighting to complete
        self.wait_for_highlighting()
        
        # Check that the dirty blocks are cleared
        self.assertEqual(self.highlighter.get_dirty_block_count(), 0)
        
        # Clear the modified blocks
        self.highlighter.clear_modified_blocks()
        
        # Check that the modified blocks are cleared
        self.assertEqual(self.highlighter.get_modified_block_count(), 0)
        
        # Rehighlight the document
        self.highlighter.rehighlight()
        
        # Process events
        QApplication.processEvents()
        
        # Check that the dirty blocks are set
        self.assertGreater(self.highlighter.get_dirty_block_count(), 0)
        
        # Wait for highlighting to complete
        self.wait_for_highlighting()
        
        # Check that the dirty blocks are cleared
        self.assertEqual(self.highlighter.get_dirty_block_count(), 0)
        
        # Check that the modified blocks are set
        self.assertGreater(self.highlighter.get_modified_block_count(), 0)
        
    def test_rehighlight_block(self):
        """Test that the highlighter rehighlights a specific block correctly."""
        # Set some text
        self.text_edit.setPlainText("def test_function():\n    pass\n\ndef another_function():\n    return True")
        
        # Process events
        QApplication.processEvents()
        
        # Wait for highlighting to complete
        self.wait_for_highlighting()
        
        # Check that the dirty blocks are cleared
        self.assertEqual(self.highlighter.get_dirty_block_count(), 0)
        
        # Clear the modified blocks
        self.highlighter.clear_modified_blocks()
        
        # Check that the modified blocks are cleared
        self.assertEqual(self.highlighter.get_modified_block_count(), 0)
        
        # Rehighlight a specific block
        block = self.document.findBlockByLineNumber(3)  # Line 4 (0-based)
        self.highlighter.rehighlight_block(block)
        
        # Process events
        QApplication.processEvents()
        
        # Check that the dirty blocks are set
        self.assertGreater(self.highlighter.get_dirty_block_count(), 0)
        
        # Wait for highlighting to complete
        self.wait_for_highlighting()
        
        # Check that the dirty blocks are cleared
        self.assertEqual(self.highlighter.get_dirty_block_count(), 0)
        
        # Check that the modified blocks are set
        self.assertGreater(self.highlighter.get_modified_block_count(), 0)
        
    def test_batch_processing(self):
        """Test that the highlighter processes blocks in batches."""
        # Set a large amount of text
        text = "\n".join([f"def function_{i}():\n    pass" for i in range(20)])
        self.text_edit.setPlainText(text)
        
        # Process events
        QApplication.processEvents()
        
        # Check that the dirty blocks are set
        self.assertGreater(self.highlighter.get_dirty_block_count(), 0)
        
        # Get the initial dirty block count
        initial_count = self.highlighter.get_dirty_block_count()
        
        # Process one batch
        self.highlighter.highlight_dirty_blocks()
        
        # Check that some blocks were processed
        self.assertLess(self.highlighter.get_dirty_block_count(), initial_count)
        
        # Wait for highlighting to complete
        self.wait_for_highlighting()
        
        # Check that the dirty blocks are cleared
        self.assertEqual(self.highlighter.get_dirty_block_count(), 0)
        
    def test_max_highlighting_time(self):
        """Test that the highlighter respects the maximum highlighting time."""
        # Set a large amount of text
        text = "\n".join([f"def function_{i}():\n    pass" for i in range(100)])
        self.text_edit.setPlainText(text)
        
        # Process events
        QApplication.processEvents()
        
        # Set a very small max highlighting time
        self.highlighter.set_max_highlighting_time(1)
        
        # Process one batch
        start_time = time.time()
        self.highlighter.highlight_dirty_blocks()
        elapsed_time = (time.time() - start_time) * 1000
        
        # Check that the highlighting time was limited
        self.assertLessEqual(elapsed_time, 50)  # Allow some overhead
        
        # Reset the max highlighting time
        self.highlighter.set_max_highlighting_time(10)
        
        # Wait for highlighting to complete
        self.wait_for_highlighting()
        
    def wait_for_highlighting(self, timeout: int = 1000):
        """
        Wait for highlighting to complete.
        
        Args:
            timeout (int, optional): The timeout in milliseconds. Defaults to 1000.
        """
        # Create a timer
        timer = QTimer()
        timer.setSingleShot(True)
        timer.start(timeout)
        
        # Process events until highlighting is complete or timeout
        while self.highlighter.get_dirty_block_count() > 0 and timer.isActive():
            QApplication.processEvents()
            time.sleep(0.01)  # Sleep to avoid high CPU usage


if __name__ == "__main__":
    unittest.main()
