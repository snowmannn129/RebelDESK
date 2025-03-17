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
    QSplitter, QToolBar, QStatusBar, QMenuBar, QMenu, QPlainTextEdit
)
from PyQt5.QtCore import Qt, QSize, QSettings, QTimer, QRegExp
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QTextCursor
from PyQt5.QtGui import QTextDocument

from src.ui.editor import CodeEditor
from src.backend.terminal import Terminal
from src.backend.file_manager import FileManager
from src.utils.config_manager import ConfigManager
from src.plugins.plugin_manager import PluginManager
from src.ui.theme_manager import ThemeManager
from src.ui.file_browser import (
    FileBrowser, RecentFilesWidget, BookmarksWidget, 
    FileTypeManager, UnsavedChangesTracker, FileBrowserWithBreakpoints
)
from src.ui.file_browser.unsaved_changes_dialog import UnsavedChangesDialog
from src.ui.debugger import DebuggerInterface
from src.backend.debugger import DebuggerBackend, BreakpointManager
from src.ui.git import GitInterface
from src.ui.code_navigation import CodeNavigator
from src.ui.editor.find_replace_dialog import FindReplaceDialog
from src.ui.editor.advanced_search_replace_dialog import AdvancedSearchReplaceDialog
from src.ui.project_templates import ProjectTemplatesDialog
from src.ui.documentation_browser import DocumentationBrowser
from src.ui.collaborative_editing import CollaborativeDialog, SessionPanel
from src.backend.collaborative_editing import CollaborativeSession
from src.ui.code_optimization import CodeOptimizationDialog
from src.ui.security_vulnerability_detection import SecurityVulnerabilityDetectionDialog
from src.ui.settings import SettingsPanel

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
        
        # Initialize plugin manager
        self.plugin_manager = PluginManager(self.config)
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(self.config)
        
        # Initialize breakpoint manager and debugger backend
        self.breakpoint_manager = BreakpointManager(self.config)
        self.debugger_backend = DebuggerBackend(self.config)
        
        self._setup_ui()
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_statusbar()
        self._connect_signals()
        self._load_settings()
        self._load_plugins()
        
        self.setWindowTitle("RebelDESK")
        logger.info("Main window initialized")
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main horizontal splitter (file browser and editor area)
        self.horizontal_splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.horizontal_splitter)
        
        # Left side container for file browser, recent files, and bookmarks
        self.left_container = QWidget()
        self.left_layout = QVBoxLayout(self.left_container)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(0)
        self.horizontal_splitter.addWidget(self.left_container)
        
        # Tab widget for file browser, recent files, and bookmarks
        self.left_tabs = QTabWidget()
        self.left_layout.addWidget(self.left_tabs)
        
        # Initialize file type manager
        self.file_type_manager = FileTypeManager(self.config)
        
        # Initialize unsaved changes tracker
        self.unsaved_changes_tracker = UnsavedChangesTracker(self)
        
        # File browser tab with breakpoint indicators
        self.file_browser = FileBrowserWithBreakpoints(self, self.config, self.breakpoint_manager)
        self.left_tabs.addTab(self.file_browser, "Files")
        
        # Recent files tab
        self.recent_files_widget = RecentFilesWidget(self, self.config, self.file_manager)
        self.left_tabs.addTab(self.recent_files_widget, "Recent")
        
        # Bookmarks tab
        self.bookmarks_widget = BookmarksWidget(self, self.config)
        self.left_tabs.addTab(self.bookmarks_widget, "Bookmarks")
        
        # Right side container
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_splitter.addWidget(self.right_container)
        
        # Vertical splitter for editor and bottom panel
        self.vertical_splitter = QSplitter(Qt.Vertical)
        self.right_layout.addWidget(self.vertical_splitter)
        
        # Editor area
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.setMovable(True)
        self.vertical_splitter.addWidget(self.editor_tabs)
        
        # Bottom panel with tabs
        self.bottom_tabs = QTabWidget()
        self.vertical_splitter.addWidget(self.bottom_tabs)
        
        # Terminal tab
        self.terminal = Terminal(self, self.config)
        self.bottom_tabs.addTab(self.terminal, "Terminal")
        
        # Debugger tab
        self.debugger = DebuggerInterface(self, self.config)
        self.bottom_tabs.addTab(self.debugger, "Debugger")
        
        # Connect debugger signals
        self._connect_debugger_signals()
        
        # Git tab
        self.git_interface = GitInterface(self, self.config)
        self.bottom_tabs.addTab(self.git_interface, "Git")
        
        # Code navigation tab
        self.code_navigator = CodeNavigator(self, self.config)
        self.bottom_tabs.addTab(self.code_navigator, "Code Navigation")
        
        # Set initial splitter sizes
        self.horizontal_splitter.setSizes([200, 800])
        self.vertical_splitter.setSizes([700, 300])
        
        # Set window size
        window_width = self.config.get('ui', {}).get('window', {}).get('default_width', 1200)
        window_height = self.config.get('ui', {}).get('window', {}).get('default_height', 800)
        self.resize(window_width, window_height)
        
        # Maximize if configured
        if self.config.get('ui', {}).get('window', {}).get('start_maximized', False):
            self.showMaximized()
            
    def _load_plugins(self):
        """Load and initialize plugins."""
        logger.info("Loading plugins")
        
        # Load all available plugins
        results = self.plugin_manager.load_plugins()
        
        # Log results
        for plugin_id, success in results.items():
            if success:
                logger.info(f"Loaded plugin: {plugin_id}")
            else:
                logger.warning(f"Failed to load plugin: {plugin_id}")
                
        # Get enabled plugins
        enabled_plugins = self.plugin_manager.get_enabled_plugins()
        logger.info(f"Enabled plugins: {', '.join(enabled_plugins.keys()) if enabled_plugins else 'None'}")
        
    def _create_actions(self):
        """Create actions for menus and toolbars."""
        # File actions
        self.new_action = QAction("New File", self)
        self.new_action.setShortcut(QKeySequence.New)
        self.new_action.setStatusTip("Create a new file")
        
        self.new_project_action = QAction("New Project", self)
        self.new_project_action.setShortcut("Ctrl+Shift+N")
        self.new_project_action.setStatusTip("Create a new project from a template")
        
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
        
        # Code optimization action
        self.optimize_code_action = QAction("Optimize Code", self)
        self.optimize_code_action.setShortcut("Ctrl+Shift+O")
        self.optimize_code_action.setStatusTip("Analyze and optimize code")
        
        # Security vulnerability detection action
        self.security_vulnerability_detection_action = QAction("Detect Security Vulnerabilities", self)
        self.security_vulnerability_detection_action.setShortcut("Ctrl+Shift+S")
        self.security_vulnerability_detection_action.setStatusTip("Detect security vulnerabilities in code")
        
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
        self.file_menu.addAction(self.new_project_action)
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
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.optimize_code_action)
        self.edit_menu.addAction(self.security_vulnerability_detection_action)
        
        # View menu
        self.view_menu = self.menuBar().addMenu("&View")
        self.view_menu.addAction(self.toggle_terminal_action)
        
        # Settings menu
        self.settings_menu = self.menuBar().addMenu("&Settings")
        self.settings_menu.addAction(self.settings_action)
        
        # Plugins menu
        self.plugins_menu = self.menuBar().addMenu("&Plugins")
        # Plugin actions will be added in _update_plugins_menu
        self._update_plugins_menu()
        
        # Run menu
        self.run_menu = self.menuBar().addMenu("&Run")
        self.run_menu.addAction(self.run_action)
        
        # Help menu
        self.help_menu = self.menuBar().addMenu("&Help")
        
        # About action
        self.about_action = QAction("About RebelDESK", self)
        self.about_action.setStatusTip("Show information about RebelDESK")
        self.about_action.triggered.connect(self._on_about)
        self.help_menu.addAction(self.about_action)
        
        # Documentation action
        self.documentation_action = QAction("Documentation", self)
        self.documentation_action.setStatusTip("View RebelDESK documentation")
        self.documentation_action.triggered.connect(self._on_documentation)
        self.help_menu.addAction(self.documentation_action)
        
        # Collaborative menu
        self.collaborative_menu = self.menuBar().addMenu("&Collaborate")
        
        # Start collaborative session action
        self.start_collaborative_action = QAction("Start Collaborative Session", self)
        self.start_collaborative_action.setStatusTip("Start a collaborative editing session")
        self.start_collaborative_action.triggered.connect(self._on_start_collaborative)
        self.collaborative_menu.addAction(self.start_collaborative_action)
        
        # Join collaborative session action
        self.join_collaborative_action = QAction("Join Collaborative Session", self)
        self.join_collaborative_action.setStatusTip("Join an existing collaborative editing session")
        self.join_collaborative_action.triggered.connect(self._on_join_collaborative)
        self.collaborative_menu.addAction(self.join_collaborative_action)
        
    def _on_start_collaborative(self):
        """Handle start collaborative session action."""
        # Get the current editor
        editor = self.editor_tabs.currentWidget()
        if not editor:
            QMessageBox.warning(
                self,
                "No File Open",
                "Please open a file before starting a collaborative session."
            )
            return
            
        # Check if the file is saved
        if not editor.current_file:
            QMessageBox.warning(
                self,
                "File Not Saved",
                "Please save the file before starting a collaborative session."
            )
            return
            
        # Create and show the collaborative dialog
        dialog = CollaborativeDialog(self, self.config)
        
        # Set the current file
        dialog.set_current_file(editor.current_file)
        
        # Connect signals
        dialog.session_created.connect(self._on_session_created)
        
        # Show the dialog
        dialog.exec_()
        
    def _on_join_collaborative(self):
        """Handle join collaborative session action."""
        # Create and show the collaborative dialog
        dialog = CollaborativeDialog(self, self.config)
        
        # Connect signals
        dialog.session_joined.connect(self._on_session_joined)
        
        # Switch to the join tab
        dialog.tab_widget.setCurrentIndex(1)
        
        # Show the dialog
        dialog.exec_()
        
    def _on_session_created(self, session):
        """
        Handle session created signal.
        
        Args:
            session (CollaborativeSession): The created session.
        """
        # Check if the session panel tab already exists
        for i in range(self.bottom_tabs.count()):
            if self.bottom_tabs.tabText(i) == "Collaborative Session":
                # Session panel tab already exists, switch to it
                self.bottom_tabs.setCurrentIndex(i)
                
                # Get the session panel
                session_panel = self.bottom_tabs.widget(i)
                
                # Set the session
                session_panel.set_session(session)
                
                # Set the user ID
                session_panel.set_user_id(session.user_manager.get_users()[0]["user_id"])
                
                return
        
        # Create a new session panel
        session_panel = SessionPanel(self, session, self.config)
        
        # Set the user ID
        session_panel.set_user_id(session.user_manager.get_users()[0]["user_id"])
        
        # Add the session panel to the bottom tabs
        self.bottom_tabs.addTab(session_panel, "Collaborative Session")
        
        # Set the current tab to the session panel
        self.bottom_tabs.setCurrentWidget(session_panel)
        
        # Update status bar
        self.statusbar.showMessage("Collaborative session started", 3000)
        
        logger.info(f"Created collaborative session: {session.session_id}")
        
    def _on_session_joined(self, session):
        """
        Handle session joined signal.
        
        Args:
            session (CollaborativeSession): The joined session.
        """
        # Check if the session panel tab already exists
        for i in range(self.bottom_tabs.count()):
            if self.bottom_tabs.tabText(i) == "Collaborative Session":
                # Session panel tab already exists, switch to it
                self.bottom_tabs.setCurrentIndex(i)
                
                # Get the session panel
                session_panel = self.bottom_tabs.widget(i)
                
                # Set the session
                session_panel.set_session(session)
                
                # Set the user ID
                for user in session.get_users():
                    if user["role"] != "owner":
                        session_panel.set_user_id(user["user_id"])
                        break
                
                return
        
        # Create a new session panel
        session_panel = SessionPanel(self, session, self.config)
        
        # Set the user ID
        for user in session.get_users():
            if user["role"] != "owner":
                session_panel.set_user_id(user["user_id"])
                break
        
        # Add the session panel to the bottom tabs
        self.bottom_tabs.addTab(session_panel, "Collaborative Session")
        
        # Set the current tab to the session panel
        self.bottom_tabs.setCurrentWidget(session_panel)
        
        # Update status bar
        self.statusbar.showMessage("Joined collaborative session", 3000)
        
        logger.info(f"Joined collaborative session: {session.session_id}")
        
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
        self.new_project_action.triggered.connect(self.new_project)
        self.open_action.triggered.connect(self.open_file)
        self.save_action.triggered.connect(self.save_file)
        self.save_as_action.triggered.connect(self.save_file_as)
        self.close_tab_action.triggered.connect(self.close_current_tab)
        self.exit_action.triggered.connect(self.close)
        
        # File browser signals
        self.file_browser.file_selected.connect(self.open_file_from_browser)
        
        # Recent files signals
        self.recent_files_widget.file_selected.connect(self.open_file_from_browser)
        
        # Bookmarks signals
        self.bookmarks_widget.file_selected.connect(self.open_file_from_browser)
        self.bookmarks_widget.directory_selected.connect(self.file_browser.set_root_path)
        
        # Unsaved changes tracker signals
        self.unsaved_changes_tracker.status_changed.connect(self._on_unsaved_changes_status_changed)
        
        # Edit actions
        self.undo_action.triggered.connect(self._on_undo)
        self.redo_action.triggered.connect(self._on_redo)
        self.cut_action.triggered.connect(self._on_cut)
        self.copy_action.triggered.connect(self._on_copy)
        self.paste_action.triggered.connect(self._on_paste)
        self.select_all_action.triggered.connect(self._on_select_all)
        self.find_action.triggered.connect(self._on_find)
        self.replace_action.triggered.connect(self._on_replace)
        self.optimize_code_action.triggered.connect(self._on_optimize_code)
        self.security_vulnerability_detection_action.triggered.connect(self._on_security_vulnerability_detection)
        
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
        
    def _update_plugins_menu(self):
        """Update the plugins menu with available plugins."""
        # Clear the menu
        self.plugins_menu.clear()
        
        # Add action to open plugin manager
        self.manage_plugins_action = QAction("Manage Plugins", self)
        self.manage_plugins_action.setStatusTip("Manage installed plugins")
        self.manage_plugins_action.triggered.connect(self.open_plugin_manager)
        self.plugins_menu.addAction(self.manage_plugins_action)
        
        # Add separator
        self.plugins_menu.addSeparator()
        
        # Add available plugins
        plugin_info_list = self.plugin_manager.get_all_plugin_info()
        
        if not plugin_info_list:
            # No plugins available
            no_plugins_action = QAction("No plugins available", self)
            no_plugins_action.setEnabled(False)
            self.plugins_menu.addAction(no_plugins_action)
        else:
            # Add each plugin
            for plugin_info in plugin_info_list:
                plugin_id = plugin_info["id"]
                plugin_name = plugin_info["name"]
                plugin_enabled = plugin_info["enabled"]
                
                # Create action for the plugin
                plugin_action = QAction(plugin_name, self)
                plugin_action.setCheckable(True)
                plugin_action.setChecked(plugin_enabled)
                plugin_action.setData(plugin_id)
                plugin_action.triggered.connect(self._on_plugin_toggled)
                
                # Add to menu
                self.plugins_menu.addAction(plugin_action)
                
            # Add separator
            self.plugins_menu.addSeparator()
            
            # Add plugin settings submenu
            self.plugin_settings_menu = self.plugins_menu.addMenu("Plugin Settings")
            
            # Add settings for each enabled plugin
            enabled_plugins = {p["id"]: p for p in plugin_info_list if p["enabled"]}
            
            if not enabled_plugins:
                # No enabled plugins
                no_settings_action = QAction("No enabled plugins", self)
                no_settings_action.setEnabled(False)
                self.plugin_settings_menu.addAction(no_settings_action)
            else:
                # Add settings for each enabled plugin
                for plugin_id, plugin_info in enabled_plugins.items():
                    plugin_name = plugin_info["name"]
                    
                    # Create action for the plugin settings
                    settings_action = QAction(f"{plugin_name} Settings", self)
                    settings_action.setData(plugin_id)
                    settings_action.triggered.connect(self._on_plugin_settings)
                    
                    # Add to menu
                    self.plugin_settings_menu.addAction(settings_action)
    
    def _on_plugin_toggled(self):
        """Handle plugin toggle action."""
        action = self.sender()
        if not action:
            return
            
        plugin_id = action.data()
        enabled = action.isChecked()
        
        if enabled:
            # Enable the plugin
            success = self.plugin_manager.enable_plugin(plugin_id)
            if not success:
                # Failed to enable
                action.setChecked(False)
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to enable plugin: {plugin_id}"
                )
        else:
            # Disable the plugin
            success = self.plugin_manager.disable_plugin(plugin_id)
            if not success:
                # Failed to disable
                action.setChecked(True)
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to disable plugin: {plugin_id}"
                )
                
        # Update the plugins menu
        self._update_plugins_menu()
        
    def _on_plugin_settings(self):
        """Handle plugin settings action."""
        action = self.sender()
        if not action:
            return
            
        plugin_id = action.data()
        plugin = self.plugin_manager.get_plugin(plugin_id)
        
        if not plugin:
            return
            
        # Get UI component for settings
        settings_component = plugin.create_ui_component("theme.settings", self)
        
        if settings_component:
            # Create dialog for settings
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"{plugin.name} Settings")
            
            layout = QVBoxLayout(dialog)
            layout.addWidget(settings_component)
            
            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            button_box.accepted.connect(dialog.accept)
            layout.addWidget(button_box)
            
            dialog.exec_()
        else:
            # No settings UI available
            QMessageBox.information(
                self,
                "Plugin Settings",
                f"No settings available for {plugin.name}"
            )
            
    def open_plugin_manager(self):
        """Open the plugin manager dialog."""
        # This would open a more comprehensive plugin manager dialog
        # For now, just show a message
        QMessageBox.information(
            self,
            "Plugin Manager",
            "Plugin manager dialog not implemented yet.\n\nUse the Plugins menu to enable/disable plugins."
        )
        
    def set_theme(self, theme):
        """
        Set the application theme.
        
        Args:
            theme (str): The theme to apply ('dark' or 'light').
        """
        # Apply theme to the main window
        self.theme_manager.apply_theme(theme)
        
        # Apply theme to all components
        self.file_browser.set_theme(theme)
        self.recent_files_widget.set_theme(theme)
        self.bookmarks_widget.set_theme(theme)
        
        # Update terminal appearance (it doesn't have a set_theme method)
        if hasattr(self.terminal, '_update_appearance'):
            self.terminal._update_appearance()
            
        self.debugger.set_theme(theme)
        self.git_interface.set_theme(theme)
        
        # CodeNavigator doesn't have a set_theme method
        
        # Apply theme to all editors
        for i in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(i)
            if hasattr(editor, 'set_theme'):
                editor.set_theme(theme)
                
        # Update config
        self.config['ui']['theme'] = theme
        self.config_manager.save_config(self.config)
        
    def _apply_theme(self, theme):
        """
        Apply the specified theme to the application.
        
        Args:
            theme (str): The theme to apply ('dark' or 'light').
        """
        self.set_theme(theme)
        
    def _connect_debugger_signals(self):
        """Connect debugger signals to slots."""
        # Connect debugger backend signals
        self.debugger_backend.stopped_at_breakpoint.connect(self.debugger.on_breakpoint_hit)
        self.debugger_backend.stopped_at_exception.connect(self.debugger.on_execution_paused)
        self.debugger_backend.continued.connect(self.debugger.on_execution_resumed)
        self.debugger_backend.debugging_stopped.connect(self.debugger.on_execution_finished)
        self.debugger_backend.variables_updated.connect(self.debugger.on_variable_updated)
        self.debugger_backend.error.connect(self.debugger.on_error_occurred)
        
        # Connect debugger interface signals
        self.debugger.breakpoint_added.connect(self.breakpoint_manager.add_breakpoint)
        self.debugger.breakpoint_removed.connect(self.breakpoint_manager.remove_breakpoint)
        
        # Connect enable/disable signals to update_breakpoint with appropriate parameters
        self.debugger.breakpoint_enabled.connect(
            lambda file_path, line: self.breakpoint_manager.update_breakpoint(file_path, line, enabled=True)
        )
        self.debugger.breakpoint_disabled.connect(
            lambda file_path, line: self.breakpoint_manager.update_breakpoint(file_path, line, enabled=False)
        )
        
    def _on_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About RebelDESK",
            "RebelDESK - A lightweight, modular IDE with AI-assisted coding capabilities.\n\n"
            "Version: 1.0.0\n"
            "© 2025 RebelDESK Team"
        )
        
    def _on_documentation(self):
        """Show the documentation browser."""
        # Create and show the documentation browser
        doc_browser = DocumentationBrowser(self, self.config)
        doc_browser.show()
        
    def _on_undo(self):
        """Handle undo action."""
        editor = self.editor_tabs.currentWidget()
        if editor:
            editor.undo()
            
    def _on_redo(self):
        """Handle redo action."""
        editor = self.editor_tabs.currentWidget()
        if editor:
            editor.redo()
            
    def _on_cut(self):
        """Handle cut action."""
        editor = self.editor_tabs.currentWidget()
        if editor:
            editor.cut()
            
    def _on_copy(self):
        """Handle copy action."""
        editor = self.editor_tabs.currentWidget()
        if editor:
            editor.copy()
            
    def _on_paste(self):
        """Handle paste action."""
        editor = self.editor_tabs.currentWidget()
        if editor:
            editor.paste()
            
    def _on_select_all(self):
        """Handle select all action."""
        editor = self.editor_tabs.currentWidget()
        if editor:
            editor.selectAll()
            
    def _on_find(self):
        """Handle find action."""
        editor = self.editor_tabs.currentWidget()
        if editor:
            # Create and show the find/replace dialog
            dialog = FindReplaceDialog(self, editor)
            dialog.show()
            
    def _on_replace(self):
        """Handle replace action."""
        editor = self.editor_tabs.currentWidget()
        if editor:
            # Create and show the find/replace dialog with replace tab active
            dialog = FindReplaceDialog(self, editor)
            dialog.tab_widget.setCurrentIndex(1)  # Switch to replace tab
            dialog.show()
            
    def _on_optimize_code(self):
        """Handle optimize code action."""
        # Get the current editor
        editor = self.editor_tabs.currentWidget()
        if not editor:
            QMessageBox.warning(
                self,
                "No File Open",
                "Please open a file before optimizing code."
            )
            return
            
        # Get the code from the editor
        code = editor.toPlainText()
        if not code.strip():
            QMessageBox.warning(
                self,
                "Empty File",
                "The current file is empty. Nothing to optimize."
            )
            return
            
        # Get the file path and language
        file_path = editor.current_file
        language = None
        
        # Try to determine language from file extension
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.py']:
                language = 'python'
            elif ext in ['.js']:
                language = 'javascript'
            elif ext in ['.ts']:
                language = 'typescript'
            elif ext in ['.java']:
                language = 'java'
            elif ext in ['.cpp', '.cc', '.cxx', '.c++', '.c']:
                language = 'cpp'
            elif ext in ['.html', '.htm']:
                language = 'html'
            elif ext in ['.css']:
                language = 'css'
                
        # Create and show the code optimization dialog
        dialog = CodeOptimizationDialog(self, self.config)
        
        # Set the code to analyze
        dialog.set_code(code, file_path, language)
        
        # Connect the suggestion applied signal
        dialog.suggestion_applied.connect(self._on_optimization_suggestion_applied)
        
        # Apply theme
        theme = self.config.get('ui', {}).get('theme', 'dark')
        dialog.set_theme(theme)
        
        # Show the dialog
        dialog.exec_()
        
    def _on_security_vulnerability_detection(self):
        """Handle security vulnerability detection action."""
        # Get the current editor
        editor = self.editor_tabs.currentWidget()
        if not editor:
            QMessageBox.warning(
                self,
                "No File Open",
                "Please open a file before detecting security vulnerabilities."
            )
            return
            
        # Get the code from the editor
        code = editor.toPlainText()
        if not code.strip():
            QMessageBox.warning(
                self,
                "Empty File",
                "The current file is empty. Nothing to analyze."
            )
            return
            
        # Get the file path and language
        file_path = editor.current_file
        language = None
        
        # Try to determine language from file extension
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.py']:
                language = 'python'
            elif ext in ['.js']:
                language = 'javascript'
            elif ext in ['.ts']:
                language = 'typescript'
            elif ext in ['.java']:
                language = 'java'
            elif ext in ['.cpp', '.cc', '.cxx', '.c++', '.c']:
                language = 'cpp'
            elif ext in ['.php']:
                language = 'php'
            elif ext in ['.rb']:
                language = 'ruby'
            elif ext in ['.go']:
                language = 'go'
            elif ext in ['.cs']:
                language = 'csharp'
            elif ext in ['.sql']:
                language = 'sql'
                
        # Create and show the security vulnerability detection dialog
        dialog = SecurityVulnerabilityDetectionDialog(self, self.config)
        
        # Set the code to analyze
        dialog.set_code(code, file_path, language)
        
        # Connect the vulnerability fixed signal
        dialog.vulnerability_fixed.connect(self._on_vulnerability_fixed)
        
        # Apply theme
        theme = self.config.get('ui', {}).get('theme', 'dark')
        dialog.set_theme(theme)
        
        # Show the dialog
        dialog.exec_()
        
    def _on_vulnerability_fixed(self, fix):
        """
        Handle vulnerability fixed.
        
        Args:
            fix (dict): The fix that was applied.
        """
        # Get the current editor
        editor = self.editor_tabs.currentWidget()
        if not editor:
            return
            
        # Get the line number and replacement text
        line_number = fix.get("line", 0)
        replacement = fix.get("replacement", "")
        
        if line_number > 0 and replacement:
            # Get the current cursor
            cursor = editor.textCursor()
            
            # Move to the specified line
            cursor.movePosition(QTextCursor.Start)
            for _ in range(line_number - 1):
                cursor.movePosition(QTextCursor.Down)
                
            # Select the line
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            
            # Replace the line with the replacement text
            cursor.insertText(replacement)
            
            # Update the editor
            editor.setTextCursor(cursor)
            editor.ensureCursorVisible()
            
            # Mark the file as modified
            editor.document().setModified(True)
            self.unsaved_changes_tracker.set_status(editor, True)
            
    def _on_optimization_suggestion_applied(self, suggestion):
        """
        Handle optimization suggestion applied.
        
        Args:
            suggestion (dict): The suggestion that was applied.
        """
        # Get the current editor
        editor = self.editor_tabs.currentWidget()
        if not editor:
            return
            
        # Get the line number and replacement text
        line_number = suggestion.get("line", 0)
        replacement = suggestion.get("replacement", "")
        
        if line_number > 0 and replacement:
            # Get the current cursor
            cursor = editor.textCursor()
            
            # Move to the specified line
            cursor.movePosition(QTextCursor.Start)
            for _ in range(line_number - 1):
                cursor.movePosition(QTextCursor.Down)
                
            # Select the line
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            
            # Replace the line with the replacement text
            cursor.insertText(replacement)
            
            # Update the editor
            editor.setTextCursor(cursor)
            editor.ensureCursorVisible()
            
            # Mark the file as modified
            editor.document().setModified(True)
            self.unsaved_changes_tracker.set_status(editor, True)
            
    def _on_unsaved_changes_status_changed(self, editor, has_unsaved_changes):
        """
        Handle unsaved changes status changed.
        
        Args:
            editor (CodeEditor): The editor whose status changed.
            has_unsaved_changes (bool): Whether the editor has unsaved changes.
        """
        # Update the tab text to indicate unsaved changes
        for i in range(self.editor_tabs.count()):
            if self.editor_tabs.widget(i) == editor:
                tab_text = self.editor_tabs.tabText(i)
                if has_unsaved_changes and not tab_text.endswith('*'):
                    self.editor_tabs.setTabText(i, tab_text + '*')
                elif not has_unsaved_changes and tab_text.endswith('*'):
                    self.editor_tabs.setTabText(i, tab_text[:-1])
                break
                
    def new_file(self):
        """Create a new file."""
        # Create a new editor
        editor = CodeEditor(self, self.config)
        
        # Add the editor to the tabs
        index = self.editor_tabs.addTab(editor, "Untitled")
        
        # Set the current tab to the new editor
        self.editor_tabs.setCurrentIndex(index)
        
        # Apply theme
        theme = self.config.get('ui', {}).get('theme', 'dark')
        editor.set_theme(theme)
        
        # Set focus to the editor
        editor.setFocus()
        
    def new_project(self):
        """Create a new project from a template."""
        # Create and show the project templates dialog
        from src.backend.project_templates.template_manager import TemplateManager
        template_manager = TemplateManager()
        dialog = ProjectTemplatesDialog(self, template_manager)
        
        # Connect signals
        dialog.project_created.connect(self._on_project_created)
        
        # Show the dialog
        dialog.exec_()
        
    def _on_project_created(self, project_path):
        """
        Handle project created signal.
        
        Args:
            project_path (str): The path to the created project.
        """
        # Update the file browser to show the new project
        self.file_browser.set_root_path(project_path)
        
        # Show a success message
        QMessageBox.information(
            self,
            "Project Created",
            f"Project created successfully at:\n{project_path}"
        )
        
    def open_file(self):
        """Open a file."""
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*)"
        )
        
        if file_path:
            self._open_file(file_path)
            
    def open_file_from_browser(self, file_path):
        """
        Open a file from the file browser.
        
        Args:
            file_path (str): The path to the file to open.
        """
        self._open_file(file_path)
        
    def _open_file(self, file_path):
        """
        Open a file.
        
        Args:
            file_path (str): The path to the file to open.
        """
        # Check if the file is already open
        for i in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(i)
            if editor.current_file == file_path:
                # File is already open, switch to it
                self.editor_tabs.setCurrentIndex(i)
                return
                
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Create a new editor
            editor = CodeEditor(self, self.config)
            
            # Set the file content
            editor.setPlainText(content)
            
            # Set the current file
            editor.current_file = file_path
            
            # Determine language from file extension
            try:
                from pygments.lexers import get_lexer_for_filename
                lexer = get_lexer_for_filename(file_path)
                language = lexer.name.lower()
                editor.language = language
                if editor.highlighter:
                    editor.highlighter.language = language
                    editor.highlighter._setup_highlighter()
                    editor.highlighter.rehighlight()
            except Exception as e:
                logger.warning(f"Failed to set language for {file_path}: {e}")
            
            # Add the editor to the tabs
            file_name = os.path.basename(file_path)
            index = self.editor_tabs.addTab(editor, file_name)
            
            # Set the current tab to the new editor
            self.editor_tabs.setCurrentIndex(index)
            
            # Apply theme
            theme = self.config.get('ui', {}).get('theme', 'dark')
            editor.set_theme(theme)
            
            # Add to recent files
            self.file_manager.add_recent_file(file_path)
            self.recent_files_widget.update_recent_files()
            
            # Set focus to the editor
            editor.setFocus()
            
            # Update status bar
            self.statusbar.showMessage(f"Opened {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open file: {str(e)}"
            )
            
    def save_file(self):
        """Save the current file."""
        editor = self.editor_tabs.currentWidget()
        if not editor:
            return
            
        if not editor.current_file:
            # No file path, use save as
            self.save_file_as()
        else:
            # Save to the current file path
            self._save_file(editor, editor.current_file)
            
    def save_file_as(self):
        """Save the current file with a new name."""
        editor = self.editor_tabs.currentWidget()
        if not editor:
            return
            
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            "",
            "All Files (*)"
        )
        
        if file_path:
            self._save_file(editor, file_path)
            
    def _save_file(self, editor, file_path):
        """
        Save a file.
        
        Args:
            editor (CodeEditor): The editor containing the file content.
            file_path (str): The path to save the file to.
        """
        try:
            # Get the content
            content = editor.toPlainText()
            
            # Write to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Update the editor's current file
            editor.current_file = file_path
            
            # Update the tab text
            for i in range(self.editor_tabs.count()):
                if self.editor_tabs.widget(i) == editor:
                    file_name = os.path.basename(file_path)
                    self.editor_tabs.setTabText(i, file_name)
                    break
                    
            # Mark the file as saved
            editor.document().setModified(False)
            editor.unsaved_changes = False  # Directly set the flag
            self.unsaved_changes_tracker.set_status(editor, False)
            
            # Add to recent files
            self.file_manager.add_recent_file(file_path)
            self.recent_files_widget.update_recent_files()
            
            # Update status bar
            self.statusbar.showMessage(f"Saved {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save file: {str(e)}"
            )
            
    def close_tab(self, index):
        """
        Close a tab.
        
        Args:
            index (int): The index of the tab to close.
        """
        editor = self.editor_tabs.widget(index)
        if not editor:
            return
            
        # Check for unsaved changes
        if editor.document().isModified():
            # Show unsaved changes dialog
            dialog = UnsavedChangesDialog(self, editor.current_file)
            result = dialog.exec_()
            
            if result == UnsavedChangesDialog.Save:
                # Save and close
                if not editor.current_file:
                    # No file path, use save as
                    file_path, _ = QFileDialog.getSaveFileName(
                        self,
                        "Save File As",
                        "",
                        "All Files (*)"
                    )
                    
                    if file_path:
                        self._save_file(editor, file_path)
                        self.editor_tabs.removeTab(index)
                    # If no file path provided, don't close
                else:
                    # Save to the current file path
                    self._save_file(editor, editor.current_file)
                    self.editor_tabs.removeTab(index)
            elif result == UnsavedChangesDialog.Discard:
                # Close without saving
                self.editor_tabs.removeTab(index)
            # If cancel, don't close
        else:
            # No unsaved changes, close directly
            self.editor_tabs.removeTab(index)
            
    def close_current_tab(self):
        """Close the current tab."""
        index = self.editor_tabs.currentIndex()
        if index >= 0:
            self.close_tab(index)
            
    def toggle_terminal(self):
        """Show or hide the terminal."""
        # Get the terminal tab index
        for i in range(self.bottom_tabs.count()):
            if self.bottom_tabs.tabText(i) == "Terminal":
                terminal_index = i
                break
        else:
            return
            
        # Toggle visibility
        if self.bottom_tabs.currentIndex() == terminal_index:
            # Terminal is visible, hide it
            self.vertical_splitter.setSizes([1, 0])
        else:
            # Terminal is not visible, show it
            self.bottom_tabs.setCurrentIndex(terminal_index)
            self.vertical_splitter.setSizes([2, 1])
            
    def open_settings(self):
        """Open the settings panel."""
        # Create and show the settings panel
        self.settings_panel = SettingsPanel(self, self.config_manager)
        result = self.settings_panel.exec_()
        
        # If the dialog was accepted, apply the settings to all open editors
        if result == SettingsPanel.Accepted:
            # Get the updated config
            self.config = self.config_manager.load_config()
            
            # Apply settings to all open editors
            for i in range(self.editor_tabs.count()):
                editor = self.editor_tabs.widget(i)
                if editor:
                    # Apply font settings
                    font_family = self.config.get('ui', {}).get('font', {}).get('family', 'Consolas')
                    font_size = self.config.get('ui', {}).get('font', {}).get('size', 12)
                    font = QFont(font_family)
                    font.setPointSize(font_size)
                    editor.setFont(font)
                    
                    # Apply line number settings
                    editor.updateLineNumberAreaWidth(0)
                    
                    # Apply current line highlight settings
                    editor.highlightCurrentLine()
                    
                    # Apply other editor settings
                    editor.config = self.config
        
    def run_current_file(self):
        """Run the current file."""
        editor = self.editor_tabs.currentWidget()
        if not editor or not editor.current_file:
            QMessageBox.warning(
                self,
                "No File Open",
                "Please open a file before running."
            )
            return
            
        # Save the file first
        self.save_file()
        
        # Get the file path
        file_path = editor.current_file
        
        # Get the file extension
        ext = os.path.splitext(file_path)[1].lower()
        
        # Determine the command to run based on the file extension
        command = None
        if ext == '.py':
            command = f"python \"{file_path}\""
        elif ext == '.js':
            command = f"node \"{file_path}\""
        elif ext == '.html' or ext == '.htm':
            # Open in default browser
            import webbrowser
            webbrowser.open(file_path)
            return
        elif ext == '.java':
            # Compile and run Java
            file_name = os.path.basename(file_path)
            class_name = os.path.splitext(file_name)[0]
            command = f"javac \"{file_path}\" && java -cp \"{os.path.dirname(file_path)}\" {class_name}"
        elif ext in ['.cpp', '.cc', '.cxx', '.c++']:
            # Compile and run C++
            output_path = os.path.splitext(file_path)[0]
            command = f"g++ \"{file_path}\" -o \"{output_path}\" && \"{output_path}\""
        elif ext == '.c':
            # Compile and run C
            output_path = os.path.splitext(file_path)[0]
            command = f"gcc \"{file_path}\" -o \"{output_path}\" && \"{output_path}\""
        else:
            QMessageBox.warning(
                self,
                "Unsupported File Type",
                f"Running files with extension {ext} is not supported."
            )
            return
            
        # Run the command in the terminal
        if command:
            self.terminal.run_command(command)
            
            # Show the terminal
            for i in range(self.bottom_tabs.count()):
                if self.bottom_tabs.tabText(i) == "Terminal":
                    self.bottom_tabs.setCurrentIndex(i)
                    break
                    
            # Make sure the terminal is visible
            self.vertical_splitter.setSizes([2, 1])
