#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Window for RebelDESK.

This module defines the main application window and its components.
"""

import os
import logging
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QAction, QFileDialog, 
    QMessageBox, QVBoxLayout, QHBoxLayout, QWidget,
    QSplitter, QToolBar, QStatusBar, QMenuBar, QMenu
)
from src.ui.settings.settings_panel import SettingsPanel
from PyQt5.QtCore import Qt, QSize, QSettings, QTimer
from PyQt5.QtGui import QIcon, QKeySequence, QFont

from src.ui.editor import CodeEditor
from src.backend.terminal import Terminal
from src.backend.file_manager import FileManager
from src.utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window for RebelDESK."""
    
    def __init__(self, config):
        """
        Initialize the main window.
        
        Args:
            config (dict): Application configuration.
        """
        super().__init__()
        
        self.config = config
        self.current_file = None
        self.unsaved_changes = False
        
        # Configuration manager
        self.config_manager = ConfigManager()
        
        # Initialize file manager
        self.file_manager = FileManager(self.config)
        
        self._setup_ui()
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_statusbar()
        self._connect_signals()
        self._load_settings()
        
        self.setWindowTitle("RebelDESK")
        logger.info("Main window initialized")
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main splitter (editor and terminal)
        self.main_splitter = QSplitter(Qt.Vertical)
        self.main_layout.addWidget(self.main_splitter)
        
        # Editor area
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.setMovable(True)
        self.main_splitter.addWidget(self.editor_tabs)
        
        # Terminal area
        self.terminal = Terminal(self, self.config)
        self.main_splitter.addWidget(self.terminal)
        
        # Set initial splitter sizes
        self.main_splitter.setSizes([700, 300])
        
        # Set window size
        window_width = self.config.get('ui', {}).get('window', {}).get('default_width', 1200)
        window_height = self.config.get('ui', {}).get('window', {}).get('default_height', 800)
        self.resize(window_width, window_height)
        
        # Maximize if configured
        if self.config.get('ui', {}).get('window', {}).get('start_maximized', False):
            self.showMaximized()
            
    def _create_actions(self):
        """Create actions for menus and toolbars."""
        # File actions
        self.new_action = QAction("New", self)
        self.new_action.setShortcut(QKeySequence.New)
        self.new_action.setStatusTip("Create a new file")
        
        self.open_action = QAction("Open", self)
        self.open_action.setShortcut(QKeySequence.Open)
        self.open_action.setStatusTip("Open an existing file")
        
        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.setStatusTip("Save the current file")
        
        self.save_as_action = QAction("Save As", self)
        self.save_as_action.setShortcut(QKeySequence.SaveAs)
        self.save_as_action.setStatusTip("Save the current file with a new name")
        
        self.close_tab_action = QAction("Close Tab", self)
        self.close_tab_action.setShortcut(QKeySequence.Close)
        self.close_tab_action.setStatusTip("Close the current tab")
        
        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut(QKeySequence.Quit)
        self.exit_action.setStatusTip("Exit the application")
        
        # Edit actions
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.setStatusTip("Undo the last action")
        
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence.Redo)
        self.redo_action.setStatusTip("Redo the last undone action")
        
        self.cut_action = QAction("Cut", self)
        self.cut_action.setShortcut(QKeySequence.Cut)
        self.cut_action.setStatusTip("Cut the selected text")
        
        self.copy_action = QAction("Copy", self)
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.setStatusTip("Copy the selected text")
        
        self.paste_action = QAction("Paste", self)
        self.paste_action.setShortcut(QKeySequence.Paste)
        self.paste_action.setStatusTip("Paste text from the clipboard")
        
        self.select_all_action = QAction("Select All", self)
        self.select_all_action.setShortcut(QKeySequence.SelectAll)
        self.select_all_action.setStatusTip("Select all text")
        
        self.find_action = QAction("Find", self)
        self.find_action.setShortcut(QKeySequence.Find)
        self.find_action.setStatusTip("Find text")
        
        self.replace_action = QAction("Replace", self)
        self.replace_action.setShortcut(QKeySequence.Replace)
        self.replace_action.setStatusTip("Replace text")
        
        # View actions
        self.toggle_terminal_action = QAction("Toggle Terminal", self)
        self.toggle_terminal_action.setShortcut("Ctrl+`")
        self.toggle_terminal_action.setStatusTip("Show or hide the terminal")
        
        # Settings actions
        self.settings_action = QAction("Settings", self)
        self.settings_action.setShortcut("Ctrl+,")
        self.settings_action.setStatusTip("Open settings panel")
        
        # Run actions
        self.run_action = QAction("Run", self)
        self.run_action.setShortcut("F5")
        self.run_action.setStatusTip("Run the current file")
        
    def _create_menus(self):
        """Create the application menus."""
        # File menu
        self.file_menu = self.menuBar().addMenu("&File")
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.close_tab_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        
        # Edit menu
        self.edit_menu = self.menuBar().addMenu("&Edit")
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.cut_action)
        self.edit_menu.addAction(self.copy_action)
        self.edit_menu.addAction(self.paste_action)
        self.edit_menu.addAction(self.select_all_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.find_action)
        self.edit_menu.addAction(self.replace_action)
        
        # View menu
        self.view_menu = self.menuBar().addMenu("&View")
        self.view_menu.addAction(self.toggle_terminal_action)
        
        # Settings menu
        self.settings_menu = self.menuBar().addMenu("&Settings")
        self.settings_menu.addAction(self.settings_action)
        
        # Run menu
        self.run_menu = self.menuBar().addMenu("&Run")
        self.run_menu.addAction(self.run_action)
        
        # Help menu
        self.help_menu = self.menuBar().addMenu("&Help")
        # Help actions will be added in future steps
        
    def _create_toolbars(self):
        """Create the application toolbars."""
        # File toolbar
        self.file_toolbar = self.addToolBar("File")
        self.file_toolbar.setMovable(False)
        self.file_toolbar.addAction(self.new_action)
        self.file_toolbar.addAction(self.open_action)
        self.file_toolbar.addAction(self.save_action)
        
        # Edit toolbar
        self.edit_toolbar = self.addToolBar("Edit")
        self.edit_toolbar.setMovable(False)
        self.edit_toolbar.addAction(self.undo_action)
        self.edit_toolbar.addAction(self.redo_action)
        self.edit_toolbar.addSeparator()
        self.edit_toolbar.addAction(self.cut_action)
        self.edit_toolbar.addAction(self.copy_action)
        self.edit_toolbar.addAction(self.paste_action)
        
        # Run toolbar
        self.run_toolbar = self.addToolBar("Run")
        self.run_toolbar.setMovable(False)
        self.run_toolbar.addAction(self.run_action)
        
    def _create_statusbar(self):
        """Create the status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Line and column indicator
        self.line_col_label = QWidget()
        self.statusbar.addPermanentWidget(self.line_col_label)
        
        # File type indicator
        self.file_type_label = QWidget()
        self.statusbar.addPermanentWidget(self.file_type_label)
        
        # Set initial status message
        self.statusbar.showMessage("Ready")
        
    def _connect_signals(self):
        """Connect signals to slots."""
        # File actions
        self.new_action.triggered.connect(self.new_file)
        self.open_action.triggered.connect(self.open_file)
        self.save_action.triggered.connect(self.save_file)
        self.save_as_action.triggered.connect(self.save_file_as)
        self.close_tab_action.triggered.connect(self.close_current_tab)
        self.exit_action.triggered.connect(self.close)
        
        # Tab close button
        self.editor_tabs.tabCloseRequested.connect(self.close_tab)
        
        # Settings action
        self.settings_action.triggered.connect(self.open_settings)
        
        # View actions
        self.toggle_terminal_action.triggered.connect(self.toggle_terminal)
        
        # Run actions
        self.run_action.triggered.connect(self.run_current_file)
        
    def _load_settings(self):
        """Load application settings."""
        # Load theme settings
        theme = self.config.get('ui', {}).get('theme', 'dark')
        self._apply_theme(theme)
        
        # Load other settings as needed
        
    def _apply_theme(self, theme):
        """
        Apply the selected theme to the application.
        
        Args:
            theme (str): The theme to apply ('dark', 'light', or 'system').
        """
        if theme == 'system':
            # Determine system theme (simplified implementation)
            # In a real implementation, this would detect the system theme
            theme = 'dark'  # Default to dark if system theme can't be determined
        
        # Apply theme to main window
        if theme == 'dark':
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #1e1e1e;
                    color: #f0f0f0;
                }
                QMenuBar, QMenu {
                    background-color: #2d2d2d;
                    color: #f0f0f0;
                }
                QMenuBar::item:selected, QMenu::item:selected {
                    background-color: #3e3d32;
                }
                QToolBar {
                    background-color: #2d2d2d;
                    border: none;
                }
                QStatusBar {
                    background-color: #2d2d2d;
                    color: #f0f0f0;
                }
                QTabWidget::pane {
                    border: 1px solid #3c3c3c;
                }
                QTabBar::tab {
                    background-color: #2d2d2d;
                    color: #f0f0f0;
                    padding: 5px 10px;
                    border: 1px solid #3c3c3c;
                }
                QTabBar::tab:selected {
                    background-color: #1e1e1e;
                }
                QSplitter::handle {
                    background-color: #3c3c3c;
                }
            """)
        else:  # light theme
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #f5f5f5;
                    color: #000000;
                }
                QMenuBar, QMenu {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QMenuBar::item:selected, QMenu::item:selected {
                    background-color: #e0e0e0;
                }
                QToolBar {
                    background-color: #f0f0f0;
                    border: none;
                }
                QStatusBar {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QTabWidget::pane {
                    border: 1px solid #cccccc;
                }
                QTabBar::tab {
                    background-color: #e0e0e0;
                    color: #000000;
                    padding: 5px 10px;
                    border: 1px solid #cccccc;
                }
                QTabBar::tab:selected {
                    background-color: #f5f5f5;
                }
                QSplitter::handle {
                    background-color: #cccccc;
                }
            """)
        
        # Update the theme in the config
        self.config['ui']['theme'] = theme
        
        # Update the theme for all open editors
        for i in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(i)
            if hasattr(editor, 'set_theme'):
                editor.set_theme(theme)
        
        # Update the theme for the terminal
        if hasattr(self.terminal, 'set_theme'):
            self.terminal.set_theme(theme)
        
        logger.info(f"Applied {theme} theme")
    
    def _save_settings(self):
        """Save application settings."""
        # Save the current configuration
        self.config_manager.save_config(self.config)
        
    def new_file(self):
        """Create a new file."""
        # Create a new editor
        editor = CodeEditor(self, self.config)
        
        # Add the editor to the tab widget
        self.editor_tabs.addTab(editor, "Untitled")
        
        # Set the current tab to the new editor
        self.editor_tabs.setCurrentWidget(editor)
        
        logger.info("New file created")
        
    def open_file(self):
        """Open an existing file."""
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*);;Python Files (*.py);;Text Files (*.txt)"
        )
        
        if file_path:
            # Check if the file is already open
            for i in range(self.editor_tabs.count()):
                editor = self.editor_tabs.widget(i)
                if editor.current_file == file_path:
                    # File is already open, switch to its tab
                    self.editor_tabs.setCurrentIndex(i)
                    return
            
            # Create a new editor
            editor = CodeEditor(self, self.config)
            
            # Load the file
            if editor.load_file(file_path):
                # Add the editor to the tab widget
                file_name = os.path.basename(file_path)
                self.editor_tabs.addTab(editor, file_name)
                
                # Set the current tab to the new editor
                self.editor_tabs.setCurrentWidget(editor)
                
                # Add to recent files
                self.file_manager.add_recent_file(file_path)
                
                logger.info(f"Opened file: {file_path}")
            else:
                # Failed to load file
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to open file: {file_path}"
                )
        
    def save_file(self):
        """Save the current file."""
        # Get the current editor
        editor = self.editor_tabs.currentWidget()
        if not editor:
            return
            
        # If the file has no path, use save as
        if not editor.current_file:
            self.save_file_as()
            return
            
        # Save the file
        if editor.save_file():
            # Update the tab title
            file_name = os.path.basename(editor.current_file)
            self.editor_tabs.setTabText(self.editor_tabs.currentIndex(), file_name)
            
            # Update status bar
            self.statusbar.showMessage(f"Saved: {editor.current_file}", 3000)
            
            logger.info(f"Saved file: {editor.current_file}")
        else:
            # Failed to save file
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save file: {editor.current_file}"
            )
        
    def save_file_as(self):
        """Save the current file with a new name."""
        # Get the current editor
        editor = self.editor_tabs.currentWidget()
        if not editor:
            return
            
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            "",
            "All Files (*);;Python Files (*.py);;Text Files (*.txt)"
        )
        
        if file_path:
            # Save the file
            if editor.save_file(file_path):
                # Update the tab title
                file_name = os.path.basename(file_path)
                self.editor_tabs.setTabText(self.editor_tabs.currentIndex(), file_name)
                
                # Update status bar
                self.statusbar.showMessage(f"Saved: {file_path}", 3000)
                
                logger.info(f"Saved file as: {file_path}")
            else:
                # Failed to save file
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save file as: {file_path}"
                )
        
    def close_tab(self, index):
        """
        Close the tab at the given index.
        
        Args:
            index (int): Index of the tab to close.
        """
        # Get the editor at the given index
        editor = self.editor_tabs.widget(index)
        if not editor:
            return
            
        # Check for unsaved changes
        if editor.has_unsaved_changes():
            # Ask the user if they want to save
            response = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"The file has unsaved changes. Do you want to save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if response == QMessageBox.Save:
                # Save the file
                if not editor.current_file:
                    # File has no path, use save as
                    self.editor_tabs.setCurrentIndex(index)
                    if not self.save_file_as():
                        # User cancelled save as
                        return
                else:
                    # Save the file
                    if not editor.save_file():
                        # Failed to save
                        QMessageBox.critical(
                            self,
                            "Error",
                            f"Failed to save file: {editor.current_file}"
                        )
                        return
            elif response == QMessageBox.Cancel:
                # User cancelled
                return
        
        # Remove the tab
        self.editor_tabs.removeTab(index)
        
        logger.info(f"Closed tab {index}")
        
    def close_current_tab(self):
        """Close the current tab."""
        current_index = self.editor_tabs.currentIndex()
        if current_index >= 0:
            self.close_tab(current_index)
            
    def open_settings(self):
        """Open the settings panel."""
        settings_panel = SettingsPanel(self, self.config_manager)
        if settings_panel.exec_():
            # Settings were accepted, reload configuration
            old_theme = self.config.get('ui', {}).get('theme', 'dark')
            self.config = self.config_manager.load_config()
            new_theme = self.config.get('ui', {}).get('theme', 'dark')
            
            # Apply theme if it changed
            if old_theme != new_theme:
                self._apply_theme(new_theme)
            
            # Update other UI settings
            # Update font settings for editors
            font_family = self.config.get('ui', {}).get('font', {}).get('family', "Consolas, 'Courier New', monospace")
            font_size = self.config.get('ui', {}).get('font', {}).get('size', 12)
            
            for i in range(self.editor_tabs.count()):
                editor = self.editor_tabs.widget(i)
                if editor:
                    font = QFont(font_family.split(",")[0].strip().strip("'\""))
                    font.setPointSize(font_size)
                    editor.setFont(font)
            
            # Update status bar
            self.statusbar.showMessage("Settings updated", 3000)
            
            logger.info("Settings updated")
            
    def toggle_terminal(self):
        """Show or hide the terminal."""
        if self.terminal.isVisible():
            self.terminal.hide()
        else:
            self.terminal.show()
            
    def run_current_file(self):
        """Run the current file in the terminal."""
        # Get the current editor
        editor = self.editor_tabs.currentWidget()
        if not editor or not editor.current_file:
            # No file to run
            self.statusbar.showMessage("No file to run", 3000)
            return
            
        # Save the file first
        if editor.has_unsaved_changes():
            if not editor.save_file():
                # Failed to save
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save file: {editor.current_file}"
                )
                return
                
        # Run the file in the terminal
        self.terminal.show()  # Make sure the terminal is visible
        session_name = self.terminal.run_file(editor.current_file)
        
        if session_name:
            self.statusbar.showMessage(f"Running: {editor.current_file}", 3000)
        else:
            self.statusbar.showMessage(f"Cannot run file: {editor.current_file}", 3000)
            
    def closeEvent(self, event):
        """
        Handle the window close event.
        
        Args:
            event (QCloseEvent): The close event.
        """
        # Check for unsaved changes
        for i in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(i)
            if editor.has_unsaved_changes():
                # Ask the user if they want to save
                response = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    f"There are unsaved changes. Do you want to save before closing?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    QMessageBox.Save
                )
                
                if response == QMessageBox.Save:
                    # Save all unsaved files
                    for j in range(self.editor_tabs.count()):
                        editor = self.editor_tabs.widget(j)
                        if editor.has_unsaved_changes():
                            self.editor_tabs.setCurrentIndex(j)
                            if not editor.current_file:
                                # File has no path, use save as
                                if not self.save_file_as():
                                    # User cancelled save as
                                    event.ignore()
                                    return
                            else:
                                # Save the file
                                if not editor.save_file():
                                    # Failed to save
                                    QMessageBox.critical(
                                        self,
                                        "Error",
                                        f"Failed to save file: {editor.current_file}"
                                    )
                                    event.ignore()
                                    return
                elif response == QMessageBox.Cancel:
                    # User cancelled
                    event.ignore()
                    return
                
                # Only need to ask once
                break
        
        # Save settings
        self._save_settings()
        
        # Accept the event
        event.accept()
