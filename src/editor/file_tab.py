"""
RebelDESK file tab component.

This module provides a file tab component for RebelDESK.
"""

import os
import logging
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt

from .code_editor import CodeEditor

logger = logging.getLogger(__name__)

class FileTab(QWidget):
    """
    File tab component for RebelDESK.
    
    This component provides a tab for editing a file, including a code editor
    and file operations like save and save as.
    """
    
    # Signal emitted when the file is modified
    fileModified = pyqtSignal(bool)
    
    # Signal emitted when the cursor position changes
    cursorPositionChanged = pyqtSignal(int, int)  # line, column
    
    def __init__(self, parent=None, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the file tab.
        
        Args:
            parent: The parent widget.
            file_path: The path to the file to open.
            config: Configuration dictionary for the tab.
        """
        super().__init__(parent)
        
        self.file_path = file_path
        self.config = config or {}
        self.modified = False
        
        # Set up the UI
        self._setup_ui()
        
        # Load the file if provided
        if file_path:
            self.load_file(file_path)
    
    def _setup_ui(self):
        """Set up the UI components."""
        # Create the layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the code editor
        self.editor = CodeEditor(self, self.config.get("editor", {}))
        
        # Connect signals
        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.cursorPositionChanged.connect(self._on_cursor_position_changed)
        
        # Add the editor to the layout
        layout.addWidget(self.editor)
        
        # Set the layout
        self.setLayout(layout)
    
    def _on_text_changed(self):
        """Handle text changed events."""
        if not self.modified:
            self.modified = True
            self.fileModified.emit(True)
            
            # Update the tab title
            if self.parent() and hasattr(self.parent(), "setTabText"):
                index = self.parent().indexOf(self)
                title = self._get_tab_title()
                self.parent().setTabText(index, title)
    
    def _on_cursor_position_changed(self, line, column):
        """
        Handle cursor position changed events.
        
        Args:
            line: The line number (1-based).
            column: The column number (1-based).
        """
        self.cursorPositionChanged.emit(line, column)
    
    def _get_tab_title(self) -> str:
        """
        Get the title for the tab.
        
        Returns:
            str: The tab title.
        """
        if self.file_path:
            title = os.path.basename(self.file_path)
        else:
            title = "Untitled"
        
        if self.modified:
            title += " *"
        
        return title
    
    def load_file(self, file_path: str) -> bool:
        """
        Load a file into the editor.
        
        Args:
            file_path: The path to the file to load.
            
        Returns:
            bool: True if the file was loaded successfully, False otherwise.
        """
        # Validate file path
        if not file_path or not isinstance(file_path, str):
            logger.error(f"Invalid file path: {file_path}")
            QMessageBox.critical(
                self,
                "Error",
                f"Invalid file path: {file_path}"
            )
            return False
            
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            QMessageBox.critical(
                self,
                "Error",
                f"File not found: {file_path}"
            )
            return False
            
        try:
            # Check file size before loading
            file_size = os.path.getsize(file_path)
            max_size = self.config.get("max_file_size", 10 * 1024 * 1024)  # Default: 10MB
            
            if file_size > max_size:
                logger.warning(f"File size ({file_size} bytes) exceeds maximum ({max_size} bytes): {file_path}")
                response = QMessageBox.question(
                    self,
                    "Large File",
                    f"The file is {file_size / 1024 / 1024:.2f} MB, which may cause performance issues. Do you want to continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if response != QMessageBox.Yes:
                    return False
            
            # Load file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            self.editor.set_text(content)
            self.file_path = file_path
            self.modified = False
            
            # Update the tab title
            if self.parent() and hasattr(self.parent(), "setTabText"):
                index = self.parent().indexOf(self)
                title = self._get_tab_title()
                self.parent().setTabText(index, title)
            
            logger.info(f"File loaded successfully: {file_path}")
            return True
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error loading file {file_path}: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load file: The file contains invalid characters or is not a text file."
            )
            return False
        except PermissionError as e:
            logger.error(f"Permission error loading file {file_path}: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load file: You don't have permission to read this file."
            )
            return False
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load file: {str(e)}"
            )
            return False
    
    def save_file(self) -> bool:
        """
        Save the file.
        
        Returns:
            bool: True if the file was saved successfully, False otherwise.
        """
        if not self.file_path:
            return self.save_file_as()
        
        # Create a backup of the file if it exists
        if os.path.exists(self.file_path):
            try:
                backup_path = f"{self.file_path}.bak"
                with open(self.file_path, "r", encoding="utf-8") as src:
                    with open(backup_path, "w", encoding="utf-8") as dst:
                        dst.write(src.read())
                logger.info(f"Created backup of {self.file_path} at {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup of {self.file_path}: {e}")
                # Continue with save operation even if backup fails
        
        try:
            # Get the text to save
            text = self.editor.get_text()
            
            # Write to a temporary file first
            temp_path = f"{self.file_path}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            # Rename the temporary file to the actual file
            # This ensures an atomic write operation
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            os.rename(temp_path, self.file_path)
            
            self.modified = False
            self.fileModified.emit(False)
            
            # Update the tab title
            if self.parent() and hasattr(self.parent(), "setTabText"):
                index = self.parent().indexOf(self)
                title = self._get_tab_title()
                self.parent().setTabText(index, title)
            
            logger.info(f"File saved successfully: {self.file_path}")
            return True
        except PermissionError as e:
            logger.error(f"Permission error saving file {self.file_path}: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save file: You don't have permission to write to this file."
            )
            return False
        except IOError as e:
            logger.error(f"I/O error saving file {self.file_path}: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save file: I/O error - {str(e)}"
            )
            return False
        except Exception as e:
            logger.error(f"Error saving file {self.file_path}: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save file: {str(e)}"
            )
            return False
    
    def save_file_as(self) -> bool:
        """
        Save the file with a new name.
        
        Returns:
            bool: True if the file was saved successfully, False otherwise.
        """
        try:
            # Get the initial directory
            initial_dir = ""
            if self.file_path:
                initial_dir = os.path.dirname(self.file_path)
            elif self.config.get("default_save_dir"):
                initial_dir = self.config.get("default_save_dir")
            
            # Get the file filter based on the current file extension
            file_filter = "All Files (*)"
            if self.file_path:
                ext = os.path.splitext(self.file_path)[1].lower()
                if ext == ".py":
                    file_filter = "Python Files (*.py);;All Files (*)"
                elif ext == ".txt":
                    file_filter = "Text Files (*.txt);;All Files (*)"
                elif ext == ".md":
                    file_filter = "Markdown Files (*.md);;All Files (*)"
                elif ext == ".json":
                    file_filter = "JSON Files (*.json);;All Files (*)"
                elif ext == ".html":
                    file_filter = "HTML Files (*.html);;All Files (*)"
                elif ext == ".css":
                    file_filter = "CSS Files (*.css);;All Files (*)"
                elif ext == ".js":
                    file_filter = "JavaScript Files (*.js);;All Files (*)"
            
            # Show the save dialog
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self,
                "Save File As",
                os.path.join(initial_dir, os.path.basename(self.file_path or "untitled")),
                "All Files (*);;Python Files (*.py);;Text Files (*.txt);;Markdown Files (*.md);;JSON Files (*.json);;HTML Files (*.html);;CSS Files (*.css);;JavaScript Files (*.js)",
                file_filter
            )
            
            if not file_path:
                logger.debug("Save As canceled by user")
                return False
            
            # Check if the file already exists
            if os.path.exists(file_path):
                response = QMessageBox.question(
                    self,
                    "File Exists",
                    f"The file '{file_path}' already exists. Do you want to overwrite it?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if response != QMessageBox.Yes:
                    logger.debug("User chose not to overwrite existing file")
                    return False
            
            # Check if we have write permission to the directory
            dir_path = os.path.dirname(file_path)
            if not os.access(dir_path, os.W_OK):
                logger.error(f"No write permission to directory: {dir_path}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"You don't have permission to write to the directory: {dir_path}"
                )
                return False
            
            # Update the file path and save
            old_path = self.file_path
            self.file_path = file_path
            
            # Try to save the file
            if not self.save_file():
                # If save fails, restore the old path
                self.file_path = old_path
                return False
            
            logger.info(f"File saved as: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error in save_file_as: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save file: {str(e)}"
            )
            return False
    
    def insert_text(self, text: str):
        """
        Insert text at the current cursor position.
        
        Args:
            text: The text to insert.
        """
        self.editor.insert_text(text)
    
    def get_text(self) -> str:
        """
        Get the current text in the editor.
        
        Returns:
            str: The current text.
        """
        return self.editor.get_text()
    
    def set_text(self, text: str):
        """
        Set the text in the editor.
        
        Args:
            text: The text to set.
        """
        self.editor.set_text(text)
    
    def get_selected_text(self) -> str:
        """
        Get the currently selected text.
        
        Returns:
            str: The selected text.
        """
        return self.editor.get_selected_text()
    
    def get_cursor_position(self) -> tuple:
        """
        Get the current cursor position.
        
        Returns:
            tuple: A tuple of (line, column).
        """
        return self.editor.get_cursor_position()
    
    def set_cursor_position(self, line: int, column: int):
        """
        Set the cursor position.
        
        Args:
            line: The line number (1-based).
            column: The column number (1-based).
        """
        self.editor.set_cursor_position(line, column)
    
    def goto_line(self, line: int):
        """
        Go to the specified line.
        
        Args:
            line: The line number (1-based).
        """
        self.editor.goto_line(line)
    
    def is_modified(self) -> bool:
        """
        Check if the file has been modified.
        
        Returns:
            bool: True if the file has been modified, False otherwise.
        """
        return self.modified
    
    def get_file_path(self) -> Optional[str]:
        """
        Get the file path.
        
        Returns:
            Optional[str]: The file path, or None if the file has not been saved.
        """
        return self.file_path
