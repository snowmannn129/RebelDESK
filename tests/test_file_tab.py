"""
Tests for the file tab component.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication, QTabWidget
from PyQt5.QtCore import Qt

from src.editor import FileTab

# Skip the test if PyQt is not available
pytestmark = pytest.mark.skipif(
    not hasattr(pytest, "qt_available") or not pytest.qt_available,
    reason="PyQt is not available"
)

class TestFileTab:
    """Tests for the file tab component."""
    
    @pytest.fixture
    def app(self):
        """Create a QApplication instance."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
    
    @pytest.fixture
    def tab_widget(self, app):
        """Create a QTabWidget instance."""
        tab_widget = QTabWidget()
        yield tab_widget
        tab_widget.deleteLater()
    
    @pytest.fixture
    def file_tab(self, app, tab_widget):
        """Create a FileTab instance."""
        file_tab = FileTab(tab_widget)
        tab_widget.addTab(file_tab, "Untitled")
        yield file_tab
        file_tab.deleteLater()
    
    def test_file_tab_initialization(self, file_tab):
        """Test that the file tab initializes correctly."""
        assert file_tab is not None
        assert hasattr(file_tab, "editor")
        assert file_tab.editor is not None
        assert file_tab.get_file_path() is None
        assert not file_tab.is_modified()
    
    def test_file_tab_text_operations(self, file_tab):
        """Test text operations in the file tab."""
        # Set text
        test_text = "def test_function():\n    return 'Hello, World!'"
        file_tab.set_text(test_text)
        
        # Get text
        assert file_tab.get_text() == test_text
        
        # Insert text
        file_tab.editor.set_cursor_position(1, 1)  # Line 1, column 1
        file_tab.insert_text("# ")
        assert file_tab.get_text() == "# def test_function():\n    return 'Hello, World!'"
        
        # Check that the file is marked as modified
        assert file_tab.is_modified()
    
    def test_file_tab_load_file(self, file_tab):
        """Test loading a file into the file tab."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            test_text = "def test_function():\n    return 'Hello, World!'"
            f.write(test_text)
            file_path = f.name
        
        try:
            # Load the file
            assert file_tab.load_file(file_path)
            
            # Check that the file path is set
            assert file_tab.get_file_path() == file_path
            
            # Check that the text is loaded
            assert file_tab.get_text() == test_text
            
            # Check that the file is not marked as modified
            assert not file_tab.is_modified()
        finally:
            # Clean up
            os.unlink(file_path)
    
    def test_file_tab_save_file(self, file_tab, monkeypatch):
        """Test saving a file from the file tab."""
        # Mock the QFileDialog.getSaveFileName method
        mock_get_save_file_name = MagicMock(return_value=("test_file.py", "Python Files (*.py)"))
        monkeypatch.setattr("PyQt5.QtWidgets.QFileDialog.getSaveFileName", mock_get_save_file_name)
        
        # Mock the open function
        mock_open = MagicMock()
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        monkeypatch.setattr("builtins.open", mock_open)
        
        # Set text
        test_text = "def test_function():\n    return 'Hello, World!'"
        file_tab.set_text(test_text)
        
        # Save the file
        assert file_tab.save_file_as()
        
        # Check that the file path is set
        assert file_tab.get_file_path() == "test_file.py"
        
        # Check that the file is not marked as modified
        assert not file_tab.is_modified()
        
        # Check that the file was written
        mock_open.assert_called_once_with("test_file.py", "w", encoding="utf-8")
        mock_file.write.assert_called_once_with(test_text)
    
    def test_file_tab_modified_signal(self, file_tab, qtbot):
        """Test that the fileModified signal is emitted when the file is modified."""
        # Connect to the fileModified signal
        with qtbot.waitSignal(file_tab.fileModified) as blocker:
            # Modify the file
            file_tab.editor.set_text("Modified text")
        
        # Check that the signal was emitted with the correct value
        assert blocker.args == [True]
    
    def test_file_tab_cursor_position_signal(self, file_tab, qtbot):
        """Test that the cursorPositionChanged signal is emitted when the cursor position changes."""
        # Set text
        file_tab.set_text("Line 1\nLine 2\nLine 3")
        
        # Connect to the cursorPositionChanged signal
        with qtbot.waitSignal(file_tab.cursorPositionChanged) as blocker:
            # Change the cursor position
            file_tab.editor.set_cursor_position(2, 3)
        
        # Check that the signal was emitted with the correct values
        assert blocker.args == [2, 3]
