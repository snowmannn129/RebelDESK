#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settings Panel for RebelDESK.

This module defines the settings panel with a tabbed interface for configuring
various aspects of the application.
"""

import os
import logging
from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, 
    QLabel, QLineEdit, QSpinBox, QCheckBox, QComboBox, 
    QPushButton, QGroupBox, QFormLayout, QColorDialog,
    QDialogButtonBox, QFileDialog, QFontComboBox, QScrollArea
)
from PyQt5.QtCore import Qt, QSettings, QSize
from PyQt5.QtGui import QFont, QColor, QIcon

from src.utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class SettingsPanel(QDialog):
    """Settings panel with tabbed interface for application configuration."""
    
    def __init__(self, parent=None, config_manager=None):
        """
        Initialize the settings panel.
        
        Args:
            parent (QWidget, optional): The parent widget.
            config_manager (ConfigManager, optional): The configuration manager.
        """
        super().__init__(parent)
        
        self.config_manager = config_manager or ConfigManager()
        self.config = self.config_manager.load_config()
        self.original_config = self.config.copy()
        self.modified_settings = {}
        
        self._setup_ui()
        self._populate_settings()
        self._connect_signals()
        
        self.setWindowTitle("RebelDESK Settings")
        self.resize(800, 600)
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.appearance_tab = self._create_appearance_tab()
        self.editor_tab = self._create_editor_tab()
        self.shortcuts_tab = self._create_shortcuts_tab()
        self.ai_tab = self._create_ai_tab()
        self.plugins_tab = self._create_plugins_tab()
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.appearance_tab, "Appearance")
        self.tab_widget.addTab(self.editor_tab, "Editor")
        self.tab_widget.addTab(self.shortcuts_tab, "Keyboard Shortcuts")
        self.tab_widget.addTab(self.ai_tab, "AI Assistance")
        self.tab_widget.addTab(self.plugins_tab, "Plugins")
        
        # Button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply | QDialogButtonBox.Reset
        )
        self.main_layout.addWidget(self.button_box)
        
    def _create_appearance_tab(self):
        """
        Create the appearance settings tab.
        
        Returns:
            QWidget: The appearance tab widget.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Theme group
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "System"])
        theme_layout.addRow("Theme:", self.theme_combo)
        
        self.syntax_theme_combo = QComboBox()
        self.syntax_theme_combo.addItems(["Monokai", "GitHub", "Solarized", "Dracula", "Nord"])
        theme_layout.addRow("Syntax Highlighting Theme:", self.syntax_theme_combo)
        
        scroll_layout.addWidget(theme_group)
        
        # Font group
        font_group = QGroupBox("Font")
        font_layout = QFormLayout(font_group)
        
        self.font_combo = QFontComboBox()
        font_layout.addRow("Font Family:", self.font_combo)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        font_layout.addRow("Font Size:", self.font_size_spin)
        
        scroll_layout.addWidget(font_group)
        
        # Window group
        window_group = QGroupBox("Window")
        window_layout = QFormLayout(window_group)
        
        self.remember_size_check = QCheckBox()
        window_layout.addRow("Remember Window Size:", self.remember_size_check)
        
        self.start_maximized_check = QCheckBox()
        window_layout.addRow("Start Maximized:", self.start_maximized_check)
        
        self.default_width_spin = QSpinBox()
        self.default_width_spin.setRange(800, 4000)
        window_layout.addRow("Default Width:", self.default_width_spin)
        
        self.default_height_spin = QSpinBox()
        self.default_height_spin.setRange(600, 3000)
        window_layout.addRow("Default Height:", self.default_height_spin)
        
        scroll_layout.addWidget(window_group)
        
        # Add stretch to push everything to the top
        scroll_layout.addStretch()
        
        return tab
        
    def _create_editor_tab(self):
        """
        Create the editor settings tab.
        
        Returns:
            QWidget: The editor tab widget.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # General editor group
        editor_group = QGroupBox("General")
        editor_layout = QFormLayout(editor_group)
        
        self.tab_size_spin = QSpinBox()
        self.tab_size_spin.setRange(1, 8)
        editor_layout.addRow("Tab Size:", self.tab_size_spin)
        
        self.use_spaces_check = QCheckBox()
        editor_layout.addRow("Use Spaces for Tabs:", self.use_spaces_check)
        
        self.auto_indent_check = QCheckBox()
        editor_layout.addRow("Auto Indent:", self.auto_indent_check)
        
        self.line_numbers_check = QCheckBox()
        editor_layout.addRow("Show Line Numbers:", self.line_numbers_check)
        
        self.highlight_line_check = QCheckBox()
        editor_layout.addRow("Highlight Current Line:", self.highlight_line_check)
        
        self.word_wrap_check = QCheckBox()
        editor_layout.addRow("Word Wrap:", self.word_wrap_check)
        
        self.show_whitespace_check = QCheckBox()
        editor_layout.addRow("Show Whitespace:", self.show_whitespace_check)
        
        scroll_layout.addWidget(editor_group)
        
        # Auto-save group
        save_group = QGroupBox("Auto-Save")
        save_layout = QFormLayout(save_group)
        
        self.auto_save_check = QCheckBox()
        save_layout.addRow("Enable Auto-Save:", self.auto_save_check)
        
        self.auto_save_interval_spin = QSpinBox()
        self.auto_save_interval_spin.setRange(10, 600)
        self.auto_save_interval_spin.setSuffix(" seconds")
        save_layout.addRow("Auto-Save Interval:", self.auto_save_interval_spin)
        
        self.backup_files_check = QCheckBox()
        save_layout.addRow("Create Backup Files:", self.backup_files_check)
        
        scroll_layout.addWidget(save_group)
        
        # Default language group
        language_group = QGroupBox("Default Language")
        language_layout = QFormLayout(language_group)
        
        self.default_language_combo = QComboBox()
        self.default_language_combo.addItems([
            "Python", "JavaScript", "HTML", "CSS", "C++", "Java", "Markdown", "YAML", "JSON"
        ])
        language_layout.addRow("Default Language:", self.default_language_combo)
        
        scroll_layout.addWidget(language_group)
        
        # Add stretch to push everything to the top
        scroll_layout.addStretch()
        
        return tab
        
    def _create_shortcuts_tab(self):
        """
        Create the keyboard shortcuts settings tab.
        
        Returns:
            QWidget: The shortcuts tab widget.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # File shortcuts group
        file_group = QGroupBox("File Operations")
        file_layout = QFormLayout(file_group)
        
        self.save_shortcut = QLineEdit()
        file_layout.addRow("Save:", self.save_shortcut)
        
        self.save_as_shortcut = QLineEdit()
        file_layout.addRow("Save As:", self.save_as_shortcut)
        
        self.open_shortcut = QLineEdit()
        file_layout.addRow("Open:", self.open_shortcut)
        
        self.new_file_shortcut = QLineEdit()
        file_layout.addRow("New File:", self.new_file_shortcut)
        
        self.close_file_shortcut = QLineEdit()
        file_layout.addRow("Close File:", self.close_file_shortcut)
        
        scroll_layout.addWidget(file_group)
        
        # Edit shortcuts group
        edit_group = QGroupBox("Editing")
        edit_layout = QFormLayout(edit_group)
        
        self.undo_shortcut = QLineEdit()
        edit_layout.addRow("Undo:", self.undo_shortcut)
        
        self.redo_shortcut = QLineEdit()
        edit_layout.addRow("Redo:", self.redo_shortcut)
        
        self.cut_shortcut = QLineEdit()
        edit_layout.addRow("Cut:", self.cut_shortcut)
        
        self.copy_shortcut = QLineEdit()
        edit_layout.addRow("Copy:", self.copy_shortcut)
        
        self.paste_shortcut = QLineEdit()
        edit_layout.addRow("Paste:", self.paste_shortcut)
        
        self.find_shortcut = QLineEdit()
        edit_layout.addRow("Find:", self.find_shortcut)
        
        self.replace_shortcut = QLineEdit()
        edit_layout.addRow("Replace:", self.replace_shortcut)
        
        self.comment_shortcut = QLineEdit()
        edit_layout.addRow("Comment:", self.comment_shortcut)
        
        scroll_layout.addWidget(edit_group)
        
        # Other shortcuts group
        other_group = QGroupBox("Other")
        other_layout = QFormLayout(other_group)
        
        self.run_code_shortcut = QLineEdit()
        other_layout.addRow("Run Code:", self.run_code_shortcut)
        
        self.toggle_terminal_shortcut = QLineEdit()
        other_layout.addRow("Toggle Terminal:", self.toggle_terminal_shortcut)
        
        scroll_layout.addWidget(other_group)
        
        # Reset shortcuts button
        self.reset_shortcuts_button = QPushButton("Reset to Defaults")
        scroll_layout.addWidget(self.reset_shortcuts_button)
        
        # Add stretch to push everything to the top
        scroll_layout.addStretch()
        
        return tab
        
    def _create_ai_tab(self):
        """
        Create the AI assistance settings tab.
        
        Returns:
            QWidget: The AI tab widget.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # General AI group
        ai_group = QGroupBox("AI Code Assistance")
        ai_layout = QFormLayout(ai_group)
        
        self.ai_enable_check = QCheckBox()
        ai_layout.addRow("Enable AI Assistance:", self.ai_enable_check)
        
        self.suggestion_delay_spin = QSpinBox()
        self.suggestion_delay_spin.setRange(100, 2000)
        self.suggestion_delay_spin.setSuffix(" ms")
        ai_layout.addRow("Suggestion Delay:", self.suggestion_delay_spin)
        
        self.max_suggestions_spin = QSpinBox()
        self.max_suggestions_spin.setRange(1, 20)
        ai_layout.addRow("Maximum Suggestions:", self.max_suggestions_spin)
        
        self.context_lines_spin = QSpinBox()
        self.context_lines_spin.setRange(5, 50)
        self.context_lines_spin.setSuffix(" lines")
        ai_layout.addRow("Context Lines:", self.context_lines_spin)
        
        scroll_layout.addWidget(ai_group)
        
        # Model settings group
        model_group = QGroupBox("AI Model")
        model_layout = QFormLayout(model_group)
        
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems(["Local", "API"])
        model_layout.addRow("Model Type:", self.model_type_combo)
        
        self.local_model_path = QLineEdit()
        self.browse_model_button = QPushButton("Browse...")
        local_model_layout = QHBoxLayout()
        local_model_layout.addWidget(self.local_model_path)
        local_model_layout.addWidget(self.browse_model_button)
        model_layout.addRow("Local Model Path:", local_model_layout)
        
        self.api_endpoint = QLineEdit()
        model_layout.addRow("API Endpoint:", self.api_endpoint)
        
        self.api_key_env = QLineEdit()
        model_layout.addRow("API Key Environment Variable:", self.api_key_env)
        
        scroll_layout.addWidget(model_group)
        
        # Add stretch to push everything to the top
        scroll_layout.addStretch()
        
        return tab
        
    def _create_plugins_tab(self):
        """
        Create the plugins settings tab.
        
        Returns:
            QWidget: The plugins tab widget.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Plugin management group
        plugin_group = QGroupBox("Plugin Management")
        plugin_layout = QFormLayout(plugin_group)
        
        self.auto_update_plugins_check = QCheckBox()
        plugin_layout.addRow("Auto-Update Plugins:", self.auto_update_plugins_check)
        
        self.plugin_directory = QLineEdit()
        self.browse_plugin_dir_button = QPushButton("Browse...")
        plugin_dir_layout = QHBoxLayout()
        plugin_dir_layout.addWidget(self.plugin_directory)
        plugin_dir_layout.addWidget(self.browse_plugin_dir_button)
        plugin_layout.addRow("Plugin Directory:", plugin_dir_layout)
        
        scroll_layout.addWidget(plugin_group)
        
        # Installed plugins group
        installed_group = QGroupBox("Installed Plugins")
        installed_layout = QVBoxLayout(installed_group)
        
        # This would be populated dynamically based on installed plugins
        self.installed_plugins_label = QLabel("No plugins installed.")
        installed_layout.addWidget(self.installed_plugins_label)
        
        scroll_layout.addWidget(installed_group)
        
        # Plugin buttons
        button_layout = QHBoxLayout()
        self.install_plugin_button = QPushButton("Install Plugin...")
        self.uninstall_plugin_button = QPushButton("Uninstall Selected")
        self.enable_plugin_button = QPushButton("Enable Selected")
        self.disable_plugin_button = QPushButton("Disable Selected")
        
        button_layout.addWidget(self.install_plugin_button)
        button_layout.addWidget(self.uninstall_plugin_button)
        button_layout.addWidget(self.enable_plugin_button)
        button_layout.addWidget(self.disable_plugin_button)
        
        scroll_layout.addLayout(button_layout)
        
        # Add stretch to push everything to the top
        scroll_layout.addStretch()
        
        return tab
        
    def _populate_settings(self):
        """Populate the settings UI with values from the configuration."""
        # Appearance tab
        theme = self.config.get('ui', {}).get('theme', 'dark')
        self.theme_combo.setCurrentText(theme.capitalize())
        
        syntax_theme = self.config.get('syntax', {}).get('theme', 'monokai')
        self.syntax_theme_combo.setCurrentText(syntax_theme.capitalize())
        
        font_family = self.config.get('ui', {}).get('font', {}).get('family', "Consolas, 'Courier New', monospace")
        font_family = font_family.split(',')[0].strip().strip("'\"")
        self.font_combo.setCurrentText(font_family)
        
        font_size = self.config.get('ui', {}).get('font', {}).get('size', 12)
        self.font_size_spin.setValue(font_size)
        
        remember_size = self.config.get('ui', {}).get('window', {}).get('remember_size', True)
        self.remember_size_check.setChecked(remember_size)
        
        start_maximized = self.config.get('ui', {}).get('window', {}).get('start_maximized', False)
        self.start_maximized_check.setChecked(start_maximized)
        
        default_width = self.config.get('ui', {}).get('window', {}).get('default_width', 1200)
        self.default_width_spin.setValue(default_width)
        
        default_height = self.config.get('ui', {}).get('window', {}).get('default_height', 800)
        self.default_height_spin.setValue(default_height)
        
        # Editor tab
        tab_size = self.config.get('ui', {}).get('editor', {}).get('tab_size', 4)
        self.tab_size_spin.setValue(tab_size)
        
        use_spaces = self.config.get('ui', {}).get('editor', {}).get('use_spaces', True)
        self.use_spaces_check.setChecked(use_spaces)
        
        auto_indent = self.config.get('ui', {}).get('editor', {}).get('auto_indent', True)
        self.auto_indent_check.setChecked(auto_indent)
        
        line_numbers = self.config.get('ui', {}).get('editor', {}).get('line_numbers', True)
        self.line_numbers_check.setChecked(line_numbers)
        
        highlight_line = self.config.get('ui', {}).get('editor', {}).get('highlight_current_line', True)
        self.highlight_line_check.setChecked(highlight_line)
        
        word_wrap = self.config.get('ui', {}).get('editor', {}).get('word_wrap', False)
        self.word_wrap_check.setChecked(word_wrap)
        
        show_whitespace = self.config.get('ui', {}).get('editor', {}).get('show_whitespace', False)
        self.show_whitespace_check.setChecked(show_whitespace)
        
        auto_save = self.config.get('editor', {}).get('auto_save', True)
        self.auto_save_check.setChecked(auto_save)
        
        auto_save_interval = self.config.get('editor', {}).get('auto_save_interval', 60)
        self.auto_save_interval_spin.setValue(auto_save_interval)
        
        backup_files = self.config.get('editor', {}).get('backup_files', True)
        self.backup_files_check.setChecked(backup_files)
        
        default_language = self.config.get('editor', {}).get('default_language', 'python')
        self.default_language_combo.setCurrentText(default_language.capitalize())
        
        # Shortcuts tab
        shortcuts = self.config.get('shortcuts', {})
        
        self.save_shortcut.setText(shortcuts.get('save', 'Ctrl+S'))
        self.save_as_shortcut.setText(shortcuts.get('save_as', 'Ctrl+Shift+S'))
        self.open_shortcut.setText(shortcuts.get('open', 'Ctrl+O'))
        self.new_file_shortcut.setText(shortcuts.get('new_file', 'Ctrl+N'))
        self.close_file_shortcut.setText(shortcuts.get('close_file', 'Ctrl+W'))
        
        self.undo_shortcut.setText(shortcuts.get('undo', 'Ctrl+Z'))
        self.redo_shortcut.setText(shortcuts.get('redo', 'Ctrl+Y'))
        self.cut_shortcut.setText(shortcuts.get('cut', 'Ctrl+X'))
        self.copy_shortcut.setText(shortcuts.get('copy', 'Ctrl+C'))
        self.paste_shortcut.setText(shortcuts.get('paste', 'Ctrl+V'))
        self.find_shortcut.setText(shortcuts.get('find', 'Ctrl+F'))
        self.replace_shortcut.setText(shortcuts.get('replace', 'Ctrl+H'))
        self.comment_shortcut.setText(shortcuts.get('comment', 'Ctrl+/'))
        
        self.run_code_shortcut.setText(shortcuts.get('run_code', 'F5'))
        self.toggle_terminal_shortcut.setText(shortcuts.get('toggle_terminal', 'Ctrl+`'))
        
        # AI tab
        ai_enable = self.config.get('ai', {}).get('enable', True)
        self.ai_enable_check.setChecked(ai_enable)
        
        suggestion_delay = self.config.get('ai', {}).get('suggestion_delay', 300)
        self.suggestion_delay_spin.setValue(suggestion_delay)
        
        max_suggestions = self.config.get('ai', {}).get('max_suggestions', 5)
        self.max_suggestions_spin.setValue(max_suggestions)
        
        context_lines = self.config.get('ai', {}).get('context_lines', 10)
        self.context_lines_spin.setValue(context_lines)
        
        model_type = self.config.get('ai', {}).get('model', {}).get('type', 'local')
        self.model_type_combo.setCurrentText(model_type.capitalize())
        
        local_path = self.config.get('ai', {}).get('model', {}).get('local_path', '')
        self.local_model_path.setText(local_path)
        
        api_endpoint = self.config.get('ai', {}).get('model', {}).get('api_endpoint', '')
        self.api_endpoint.setText(api_endpoint)
        
        api_key_env = self.config.get('ai', {}).get('model', {}).get('api_key_env', 'REBELDESK_AI_API_KEY')
        self.api_key_env.setText(api_key_env)
        
        # Plugins tab
        auto_update = self.config.get('plugins', {}).get('auto_update', True)
        self.auto_update_plugins_check.setChecked(auto_update)
        
        plugin_directory = self.config.get('plugins', {}).get('plugin_directory', 'plugins')
        self.plugin_directory.setText(plugin_directory)
        
    def _connect_signals(self):
        """Connect signals to slots."""
        # Button box
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        self.button_box.button(QDialogButtonBox.Reset).clicked.connect(self.reset_settings)
        
        # Browse buttons
        self.browse_model_button.clicked.connect(self.browse_model_path)
        self.browse_plugin_dir_button.clicked.connect(self.browse_plugin_directory)
        
        # Reset shortcuts button
        self.reset_shortcuts_button.clicked.connect(self.reset_shortcuts)
        
    def browse_model_path(self):
        """Browse for a local AI model path."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Local AI Model",
            "",
            "Model Files (*.bin *.pt *.pth *.onnx);;All Files (*)"
        )
        
        if path:
            self.local_model_path.setText(path)
            
    def browse_plugin_directory(self):
        """Browse for a plugin directory."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Plugin Directory",
            ""
        )
        
        if path:
            self.plugin_directory.setText(path)
            
    def reset_shortcuts(self):
        """Reset keyboard shortcuts to default values."""
        # Default shortcuts
        self.save_shortcut.setText("Ctrl+S")
        self.save_as_shortcut.setText("Ctrl+Shift+S")
        self.open_shortcut.setText("Ctrl+O")
        self.new_file_shortcut.setText("Ctrl+N")
        self.close_file_shortcut.setText("Ctrl+W")
        
        self.undo_shortcut.setText("Ctrl+Z")
        self.redo_shortcut.setText("Ctrl+Y")
        self.cut_shortcut.setText("Ctrl+X")
        self.copy_shortcut.setText("Ctrl+C")
        self.paste_shortcut.setText("Ctrl+V")
        self.find_shortcut.setText("Ctrl+F")
        self.replace_shortcut.setText("Ctrl+H")
        self.comment_shortcut.setText("Ctrl+/")
        
        self.run_code_shortcut.setText("F5")
        self.toggle_terminal_shortcut.setText("Ctrl+`")
        
    def apply_settings(self):
        """Apply the current settings."""
        # Appearance settings
        self.config.setdefault('ui', {})
        self.config['ui']['theme'] = self.theme_combo.currentText().lower()
        
        self.config.setdefault('syntax', {})
        self.config['syntax']['theme'] = self.syntax_theme_combo.currentText().lower()
        
        self.config['ui'].setdefault('font', {})
        self.config['ui']['font']['family'] = self.font_combo.currentText()
        self.config['ui']['font']['size'] = self.font_size_spin.value()
        
        self.config['ui'].setdefault('window', {})
        self.config['ui']['window']['remember_size'] = self.remember_size_check.isChecked()
        self.config['ui']['window']['start_maximized'] = self.start_maximized_check.isChecked()
        self.config['ui']['window']['default_width'] = self.default_width_spin.value()
        self.config['ui']['window']['default_height'] = self.default_height_spin.value()
        
        # Editor settings
        self.config['ui'].setdefault('editor', {})
        self.config['ui']['editor']['tab_size'] = self.tab_size_spin.value()
        self.config['ui']['editor']['use_spaces'] = self.use_spaces_check.isChecked()
        self.config['ui']['editor']['auto_indent'] = self.auto_indent_check.isChecked()
        self.config['ui']['editor']['line_numbers'] = self.line_numbers_check.isChecked()
        self.config['ui']['editor']['highlight_current_line'] = self.highlight_line_check.isChecked()
        self.config['ui']['editor']['word_wrap'] = self.word_wrap_check.isChecked()
        self.config['ui']['editor']['show_whitespace'] = self.show_whitespace_check.isChecked()
        
        self.config.setdefault('editor', {})
        self.config['editor']['auto_save'] = self.auto_save_check.isChecked()
        self.config['editor']['auto_save_interval'] = self.auto_save_interval_spin.value()
        self.config['editor']['backup_files'] = self.backup_files_check.isChecked()
        self.config['editor']['default_language'] = self.default_language_combo.currentText().lower()
        
        # Shortcuts settings
        self.config.setdefault('shortcuts', {})
        self.config['shortcuts']['save'] = self.save_shortcut.text()
        self.config['shortcuts']['save_as'] = self.save_as_shortcut.text()
        self.config['shortcuts']['open'] = self.open_shortcut.text()
        self.config['shortcuts']['new_file'] = self.new_file_shortcut.text()
        self.config['shortcuts']['close_file'] = self.close_file_shortcut.text()
        
        self.config['shortcuts']['undo'] = self.undo_shortcut.text()
        self.config['shortcuts']['redo'] = self.redo_shortcut.text()
        self.config['shortcuts']['cut'] = self.cut_shortcut.text()
        self.config['shortcuts']['copy'] = self.copy_shortcut.text()
        self.config['shortcuts']['paste'] = self.paste_shortcut.text()
        self.config['shortcuts']['find'] = self.find_shortcut.text()
        self.config['shortcuts']['replace'] = self.replace_shortcut.text()
        self.config['shortcuts']['comment'] = self.comment_shortcut.text()
        
        self.config['shortcuts']['run_code'] = self.run_code_shortcut.text()
        self.config['shortcuts']['toggle_terminal'] = self.toggle_terminal_shortcut.text()
        
        # AI settings
        self.config.setdefault('ai', {})
        self.config['ai']['enable'] = self.ai_enable_check.isChecked()
        self.config['ai']['suggestion_delay'] = self.suggestion_delay_spin.value()
        self.config['ai']['max_suggestions'] = self.max_suggestions_spin.value()
        self.config['ai']['context_lines'] = self.context_lines_spin.value()
        
        self.config['ai'].setdefault('model', {})
        self.config['ai']['model']['type'] = self.model_type_combo.currentText().lower()
        self.config['ai']['model']['local_path'] = self.local_model_path.text()
        self.config['ai']['model']['api_endpoint'] = self.api_endpoint.text()
        self.config['ai']['model']['api_key_env'] = self.api_key_env.text()
        
        # Plugins settings
        self.config.setdefault('plugins', {})
        self.config['plugins']['auto_update'] = self.auto_update_plugins_check.isChecked()
        self.config['plugins']['plugin_directory'] = self.plugin_directory.text()
        
        # Save the configuration
        self.config_manager.save_config(self.config)
        
        # Emit signal that settings have changed
        # This would be implemented in a future step
        # self.settings_changed.emit(self.config)
        
    def reset_settings(self):
        """Reset settings to their original values."""
        self.config = self.original_config.copy()
        self._populate_settings()
        
    def accept(self):
        """Accept the dialog and save settings."""
        self.apply_settings()
        super().accept()
