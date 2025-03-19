"""
RebelDESK main window implementation.
"""

from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QToolBar, QDockWidget, QTabWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QSettings, QSize, QPoint
from PyQt5.QtGui import QIcon, QKeySequence

import os
import logging

from src.editor import FileTab

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    Main window for the RebelDESK application.
    """
    
    def __init__(self):
        """
        Initialize the main window.
        """
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("RebelDESK")
        self.setMinimumSize(800, 600)
        
        # Initialize UI components
        self._init_ui()
        
        # Load settings
        self._load_settings()
        
        logger.info("Main window initialized")
    
    def _init_ui(self):
        """
        Initialize the UI components.
        """
        # Create central widget
        self.central_tab_widget = QTabWidget()
        self.central_tab_widget.setTabsClosable(True)
        self.central_tab_widget.setMovable(True)
        self.central_tab_widget.tabCloseRequested.connect(self._on_tab_close_requested)
        self.setCentralWidget(self.central_tab_widget)
        
        # Create menus
        self._create_menus()
        
        # Create toolbars
        self._create_toolbars()
        
        # Create dock widgets
        self._create_dock_widgets()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
    
    def _create_menus(self):
        """
        Create the menu bar.
        """
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.setStatusTip("Create a new file")
        new_action.triggered.connect(self._on_new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setStatusTip("Open an existing file")
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setStatusTip("Save the current file")
        save_action.triggered.connect(self._on_save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.setStatusTip("Save the current file with a new name")
        save_as_action.triggered.connect(self._on_save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.setStatusTip("Undo the last action")
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.setStatusTip("Redo the last undone action")
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.setStatusTip("Cut the selected text")
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.setStatusTip("Copy the selected text")
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.setStatusTip("Paste the clipboard text")
        edit_menu.addAction(paste_action)
        
        # View menu
        view_menu = self.menuBar().addMenu("&View")
        
        # Tools menu
        tools_menu = self.menuBar().addMenu("&Tools")
        
        # AI submenu
        ai_menu = QMenu("&AI", self)
        tools_menu.addMenu(ai_menu)
        
        # Natural Language Code Generation
        nlcg_action = QAction("&Generate Code from Description", self)
        nlcg_action.setStatusTip("Generate code from a natural language description using AI")
        nlcg_action.triggered.connect(self._on_generate_code_from_description)
        ai_menu.addAction(nlcg_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.setStatusTip("Show the application's About box")
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _create_toolbars(self):
        """
        Create the toolbars.
        """
        # File toolbar
        file_toolbar = QToolBar("File")
        file_toolbar.setObjectName("file_toolbar")
        self.addToolBar(file_toolbar)
        
        # Edit toolbar
        edit_toolbar = QToolBar("Edit")
        edit_toolbar.setObjectName("edit_toolbar")
        self.addToolBar(edit_toolbar)
    
    def _create_dock_widgets(self):
        """
        Create the dock widgets.
        """
        # File browser dock
        file_browser_dock = QDockWidget("Files", self)
        file_browser_dock.setObjectName("file_browser_dock")
        file_browser_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, file_browser_dock)
        
        # Output dock
        output_dock = QDockWidget("Output", self)
        output_dock.setObjectName("output_dock")
        output_dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, output_dock)
    
    def _load_settings(self):
        """
        Load application settings.
        """
        settings = QSettings()
        
        # Restore window geometry
        geometry = settings.value("MainWindow/geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            # Default size and position
            self.resize(1024, 768)
            self.move(100, 100)
        
        # Restore window state
        state = settings.value("MainWindow/state")
        if state:
            self.restoreState(state)
    
    def _save_settings(self):
        """
        Save application settings.
        """
        settings = QSettings()
        
        # Save window geometry
        settings.setValue("MainWindow/geometry", self.saveGeometry())
        
        # Save window state
        settings.setValue("MainWindow/state", self.saveState())
    
    def closeEvent(self, event):
        """
        Handle the window close event.
        """
        # Save settings
        self._save_settings()
        
        # Accept the event
        event.accept()
    
    def _get_current_file_tab(self) -> FileTab:
        """
        Get the current file tab.
        
        Returns:
            FileTab: The current file tab, or None if there is no current tab.
        """
        current_index = self.central_tab_widget.currentIndex()
        if current_index >= 0:
            return self.central_tab_widget.widget(current_index)
        return None
    
    def _on_new_file(self):
        """
        Handle the New File action.
        """
        # Create a new file tab
        file_tab = FileTab(self)
        
        # Add the tab to the central tab widget
        index = self.central_tab_widget.addTab(file_tab, "Untitled")
        
        # Set the new tab as the current tab
        self.central_tab_widget.setCurrentIndex(index)
        
        # Set focus to the editor
        file_tab.editor.setFocus()
        
        self.statusBar().showMessage("New file created", 2000)
    
    def _on_open_file(self):
        """
        Handle the Open File action.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*);;Python Files (*.py);;Text Files (*.txt)"
        )
        
        if file_path:
            # Check if the file is already open
            for i in range(self.central_tab_widget.count()):
                tab = self.central_tab_widget.widget(i)
                if isinstance(tab, FileTab) and tab.get_file_path() == file_path:
                    # File is already open, just switch to it
                    self.central_tab_widget.setCurrentIndex(i)
                    return
            
            # Create a new file tab
            file_tab = FileTab(self, file_path)
            
            # Add the tab to the central tab widget
            index = self.central_tab_widget.addTab(file_tab, os.path.basename(file_path))
            
            # Set the new tab as the current tab
            self.central_tab_widget.setCurrentIndex(index)
            
            # Set focus to the editor
            file_tab.editor.setFocus()
            
            self.statusBar().showMessage(f"Opened {file_path}", 2000)
    
    def _on_save_file(self):
        """
        Handle the Save File action.
        """
        file_tab = self._get_current_file_tab()
        if file_tab:
            if file_tab.save_file():
                self.statusBar().showMessage("File saved", 2000)
        else:
            QMessageBox.warning(
                self,
                "No File Open",
                "There is no file open to save."
            )
    
    def _on_save_file_as(self):
        """
        Handle the Save File As action.
        """
        file_tab = self._get_current_file_tab()
        if file_tab:
            if file_tab.save_file_as():
                # Update the tab title
                index = self.central_tab_widget.currentIndex()
                self.central_tab_widget.setTabText(index, os.path.basename(file_tab.get_file_path()))
                
                self.statusBar().showMessage(f"Saved as {file_tab.get_file_path()}", 2000)
        else:
            QMessageBox.warning(
                self,
                "No File Open",
                "There is no file open to save."
            )
    
    def _on_generate_code_from_description(self):
        """
        Handle the Generate Code from Description action.
        """
        from .natural_language_code_dialog import NaturalLanguageCodeDialog
        
        # Get the application configuration
        settings = QSettings()
        config = {
            "ai": {
                "base_url": settings.value("AI/base_url", "http://127.0.0.1:1234"),
                "model_name": settings.value("AI/model_name", "deepseek-r1-distill-llama-8b"),
                "default_language": settings.value("AI/default_language", "python")
            }
        }
        
        # Create the dialog
        dialog = NaturalLanguageCodeDialog(
            parent=self,
            config=config,
            on_code_generated=self._on_code_generated
        )
        
        # Show the dialog
        dialog.exec_()
    
    def _on_tab_close_requested(self, index):
        """
        Handle the tab close requested event.
        
        Args:
            index: The index of the tab to close.
        """
        file_tab = self.central_tab_widget.widget(index)
        if isinstance(file_tab, FileTab) and file_tab.is_modified():
            # Ask the user if they want to save the file
            response = QMessageBox.question(
                self,
                "Save Changes",
                f"The file '{file_tab.get_file_path() or 'Untitled'}' has been modified. Do you want to save the changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if response == QMessageBox.Save:
                # Save the file
                if not file_tab.save_file():
                    # Save failed, don't close the tab
                    return
            elif response == QMessageBox.Cancel:
                # Cancel the close
                return
        
        # Close the tab
        self.central_tab_widget.removeTab(index)
    
    def _on_code_generated(self, code: str):
        """
        Handle the code generated from the Natural Language Code Generation dialog.
        
        Args:
            code: The generated code.
        """
        if not code:
            logger.warning("No code was generated")
            QMessageBox.warning(
                self,
                "No Code Generated",
                "No code was generated. Please try again with a different description."
            )
            return
            
        try:
            file_tab = self._get_current_file_tab()
            if file_tab:
                # Ask the user if they want to insert the code at the cursor position
                # or create a new file
                response = QMessageBox.question(
                    self,
                    "Insert Code",
                    "Do you want to insert the generated code at the cursor position in the current file?",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                    QMessageBox.Yes
                )
                
                if response == QMessageBox.Yes:
                    # Insert the code into the current editor
                    file_tab.insert_text(code)
                    self.statusBar().showMessage("Code inserted successfully", 2000)
                elif response == QMessageBox.No:
                    # Create a new file with the generated code
                    self._create_new_file_with_code(code)
                # If Cancel, do nothing
            else:
                # No file tab open, create a new one
                self._create_new_file_with_code(code)
        except Exception as e:
            logger.error(f"Error handling generated code: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to handle generated code: {str(e)}"
            )
    
    def _create_new_file_with_code(self, code: str):
        """
        Create a new file with the given code.
        
        Args:
            code: The code to put in the new file.
        """
        try:
            # Try to determine the language from the code
            language = self._detect_language_from_code(code)
            
            # Create a new file tab
            file_tab = FileTab(self)
            file_tab.set_text(code)
            
            # Add the tab to the central tab widget
            tab_title = f"Untitled{self._get_language_extension(language)}"
            index = self.central_tab_widget.addTab(file_tab, tab_title)
            
            # Set the new tab as the current tab
            self.central_tab_widget.setCurrentIndex(index)
            
            # Set focus to the editor
            file_tab.editor.setFocus()
            
            self.statusBar().showMessage(f"Code generated in new {language} file", 2000)
        except Exception as e:
            logger.error(f"Error creating new file with code: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create new file: {str(e)}"
            )
    
    def _detect_language_from_code(self, code: str) -> str:
        """
        Detect the programming language from the code.
        
        Args:
            code: The code to detect the language from.
            
        Returns:
            str: The detected language.
        """
        # Simple language detection based on keywords and syntax
        code = code.lower()
        
        # Check for Python
        if "def " in code or "import " in code or "class " in code and ":" in code:
            return "python"
        
        # Check for JavaScript/TypeScript
        if "function " in code or "const " in code or "let " in code or "var " in code:
            if "interface " in code or "type " in code or ": " in code:
                return "typescript"
            return "javascript"
        
        # Check for HTML
        if "<!doctype html>" in code or "<html" in code or "<body" in code:
            return "html"
        
        # Check for CSS
        if "{" in code and "}" in code and ":" in code and ";" in code and not "function" in code:
            return "css"
        
        # Check for Java
        if "public class " in code or "private class " in code or "protected class " in code:
            return "java"
        
        # Check for C++
        if "#include <" in code or "int main(" in code or "std::" in code:
            return "cpp"
        
        # Default to plain text
        return "text"
    
    def _get_language_extension(self, language: str) -> str:
        """
        Get the file extension for a language.
        
        Args:
            language: The language.
            
        Returns:
            str: The file extension.
        """
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "html": ".html",
            "css": ".css",
            "java": ".java",
            "cpp": ".cpp",
            "text": ".txt"
        }
        
        return extensions.get(language, "")
    
    def _on_about(self):
        """
        Handle the About action.
        """
        QMessageBox.about(
            self,
            "About RebelDESK",
            "RebelDESK v0.1.0\n\n"
            "A lightweight, AI-powered IDE that integrates with the RebelSUITE ecosystem.\n\n"
            "© 2025 RebelSUITE"
        )
