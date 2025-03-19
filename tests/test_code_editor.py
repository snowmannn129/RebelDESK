"""
Tests for the code editor component.
"""

import pytest
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QTextCursor

from src.editor import CodeEditor
from src.editor.incremental_syntax_highlighter import IncrementalSyntaxHighlighter

# Skip the test if PyQt is not available
pytestmark = pytest.mark.skipif(
    not hasattr(pytest, "qt_available") or not pytest.qt_available,
    reason="PyQt is not available"
)

class TestCodeEditor:
    """Tests for the code editor component."""
    
    @pytest.fixture
    def app(self):
        """Create a QApplication instance."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
    
    @pytest.fixture
    def editor(self, app):
        """Create a CodeEditor instance."""
        editor = CodeEditor()
        yield editor
        editor.deleteLater()
    
    def test_editor_initialization(self, editor):
        """Test that the editor initializes correctly."""
        assert editor is not None
        assert hasattr(editor, "line_number_area")
        assert editor.line_number_area is not None
    
    def test_editor_text_operations(self, editor):
        """Test text operations in the editor."""
        # Set text
        test_text = "def test_function():\n    return 'Hello, World!'"
        editor.set_text(test_text)
        
        # Get text
        assert editor.get_text() == test_text
        
        # Insert text
        editor.set_cursor_position(1, 1)  # Line 1, column 1
        editor.insert_text("# ")
        assert editor.get_text() == "# def test_function():\n    return 'Hello, World!'"
        
        # Get cursor position
        line, column = editor.get_cursor_position()
        assert line == 1
        assert column == 3
        
        # Set cursor position
        editor.set_cursor_position(2, 5)  # Line 2, column 5
        line, column = editor.get_cursor_position()
        assert line == 2
        assert column == 5
        
        # Goto line
        editor.goto_line(1)
        line, column = editor.get_cursor_position()
        assert line == 1
        assert column == 1
    
    def test_editor_selection(self, editor, qtbot):
        """Test text selection in the editor."""
        # Set text
        test_text = "Line 1\nLine 2\nLine 3"
        editor.set_text(test_text)
        
        # Select text programmatically
        cursor = editor.textCursor()
        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 6)  # Select "Line 1"
        editor.setTextCursor(cursor)
        
        # Get selected text
        assert editor.get_selected_text() == "Line 1"
    
    def test_line_number_area_width(self, editor):
        """Test that the line number area width is calculated correctly."""
        # Set text with multiple lines
        test_text = "\n".join([f"Line {i}" for i in range(1, 101)])
        editor.set_text(test_text)
        
        # Check that the line number area width is greater than 0
        assert editor.line_number_area_width() > 0
        
        # Check that the line number area width increases with more lines
        width_100_lines = editor.line_number_area_width()
        
        # Add more lines
        more_lines = "\n".join([f"Line {i}" for i in range(101, 1001)])
        editor.set_text(test_text + "\n" + more_lines)
        
        # Check that the width increased
        width_1000_lines = editor.line_number_area_width()
        assert width_1000_lines > width_100_lines
    
    def test_syntax_highlighter_initialization(self, editor):
        """Test that the syntax highlighter is initialized correctly."""
        # Check that the syntax highlighter is initialized
        assert hasattr(editor, "syntax_highlighter")
        assert editor.syntax_highlighter is not None
        assert isinstance(editor.syntax_highlighter, IncrementalSyntaxHighlighter)
        
        # Check that the syntax highlighter is attached to the document
        assert editor.syntax_highlighter.document() == editor.document()
    
    def test_syntax_highlighter_configuration(self, editor):
        """Test syntax highlighter configuration methods."""
        # Get the initial batch size
        initial_batch_size = editor.syntax_highlighter.batch_size
        
        # Set a new batch size
        new_batch_size = initial_batch_size * 2
        editor.set_syntax_highlighter_batch_size(new_batch_size)
        
        # Check that the batch size was updated
        assert editor.syntax_highlighter.batch_size == new_batch_size
        
        # Get the initial max highlighting time
        initial_max_time = editor.syntax_highlighter.max_highlighting_time
        
        # Set a new max highlighting time
        new_max_time = initial_max_time * 2
        editor.set_syntax_highlighter_max_time(new_max_time)
        
        # Check that the max highlighting time was updated
        assert editor.syntax_highlighter.max_highlighting_time == new_max_time
    
    def test_syntax_highlighter_rehighlight(self, editor, qtbot):
        """Test the rehighlight method."""
        # Set some text
        test_text = "def test_function():\n    return 'Hello, World!'"
        editor.set_text(test_text)
        
        # Process events
        QApplication.processEvents()
        
        # Clear the modified blocks
        editor.syntax_highlighter.clear_modified_blocks()
        
        # Check that the modified blocks are cleared
        assert editor.syntax_highlighter.get_modified_block_count() == 0
        
        # Rehighlight the document
        editor.rehighlight()
        
        # Process events
        QApplication.processEvents()
        
        # Wait for highlighting to complete
        self.wait_for_highlighting(editor.syntax_highlighter)
        
        # Check that the modified blocks are set
        assert editor.syntax_highlighter.get_modified_block_count() > 0
    
    def test_syntax_highlighter_performance(self, editor, qtbot):
        """Test the performance of the syntax highlighter."""
        # Set a large amount of text
        test_text = "\n".join([f"def function_{i}():\n    return 'Hello, World!'" for i in range(1000)])
        
        # Set a small batch size for testing
        editor.set_syntax_highlighter_batch_size(10)
        
        # Set a small max highlighting time for testing
        editor.set_syntax_highlighter_max_time(5)
        
        # Measure the time to set the text
        start_time = time.time()
        editor.set_text(test_text)
        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Check that the time is reasonable (less than 1 second)
        # This is a rough check, as the actual time will depend on the system
        assert elapsed_time < 1000
        
        # Process events
        QApplication.processEvents()
        
        # Check that there are dirty blocks
        assert editor.syntax_highlighter.get_dirty_block_count() > 0
        
        # Wait for highlighting to complete
        self.wait_for_highlighting(editor.syntax_highlighter)
        
        # Check that the dirty blocks are cleared
        assert editor.syntax_highlighter.get_dirty_block_count() == 0
    
    def wait_for_highlighting(self, highlighter, timeout: int = 5000):
        """
        Wait for highlighting to complete.
        
        Args:
            highlighter: The syntax highlighter.
            timeout (int, optional): The timeout in milliseconds. Defaults to 5000.
        """
        # Create a timer
        timer = QTimer()
        timer.setSingleShot(True)
        timer.start(timeout)
        
        # Process events until highlighting is complete or timeout
        while highlighter.get_dirty_block_count() > 0 and timer.isActive():
            QApplication.processEvents()
            time.sleep(0.01)  # Sleep to avoid high CPU usage
