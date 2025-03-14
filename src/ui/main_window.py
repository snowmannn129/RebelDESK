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
from PyQt5.QtCore import Qt, QSize, QSettings, QTimer
from PyQt5.QtGui import QIcon, QKeySequence

# Import will be implemented in future steps
# from src.ui.editor import CodeEditor
# from src.ui.terminal import Terminal
# from src.backend.file_manager import FileManager

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
        
        # Will be implemented in future steps
        # self.file_manager = FileManager(self.config)
        
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
        
        # Terminal area (will be implemented in future steps)
        # self.terminal = Terminal()
        # self.main_splitter.addWidget(self.terminal)
        
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
        
    def _load_settings(self):
        """Load application settings."""
        # Will be implemented in future steps
        pass
        
    def _save_settings(self):
        """Save application settings."""
        # Will be implemented in future steps
        pass
        
    def new_file(self):
        """Create a new file."""
        # Will be implemented in future steps
        logger.info("New file action triggered")
        
    def open_file(self):
        """Open an existing file."""
        # Will be implemented in future steps
        logger.info("Open file action triggered")
        
    def save_file(self):
        """Save the current file."""
        # Will be implemented in future steps
        logger.info("Save file action triggered")
        
    def save_file_as(self):
        """Save the current file with a new name."""
        # Will be implemented in future steps
        logger.info("Save file as action triggered")
        
    def close_tab(self, index):
        """
        Close the tab at the given index.
        
        Args:
            index (int): Index of the tab to close.
        """
        # Will be implemented in future steps
        logger.info(f"Close tab action triggered for tab {index}")
        
    def close_current_tab(self):
        """Close the current tab."""
        current_index = self.editor_tabs.currentIndex()
        if current_index >= 0:
            self.close_tab(current_index)
            
    def closeEvent(self, event):
        """
        Handle the window close event.
        
        Args:
            event (QCloseEvent): The close event.
        """
        # Check for unsaved changes
        # Will be implemented in future steps
        
        # Save settings
        self._save_settings()
        
        # Accept the event
        event.accept()
