#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the Settings Panel component.

This module contains tests for the settings panel UI component.
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt

# Add src directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ui.settings.settings_panel import SettingsPanel
from src.utils.config_manager import ConfigManager


@pytest.fixture
def app():
    """Create a QApplication instance for the tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # app.quit()  # Don't quit the app to avoid segfaults in pytest-qt


@pytest.fixture
def config_manager():
    """Create a mock ConfigManager for testing."""
    config_manager = MagicMock(spec=ConfigManager)
    
    # Mock configuration
    test_config = {
        'ui': {
            'theme': 'dark',
            'font': {
                'family': 'Consolas',
                'size': 12
            },
            'window': {
                'remember_size': True,
                'start_maximized': False,
                'default_width': 1200,
                'default_height': 800
            },
            'editor': {
                'tab_size': 4,
                'use_spaces': True,
                'auto_indent': True,
                'line_numbers': True,
                'highlight_current_line': True,
                'word_wrap': False,
                'show_whitespace': False
            }
        },
        'editor': {
            'auto_save': True,
            'auto_save_interval': 60,
            'backup_files': True,
            'default_language': 'python'
        },
        'syntax': {
            'theme': 'monokai'
        },
        'shortcuts': {
            'save': 'Ctrl+S',
            'save_as': 'Ctrl+Shift+S',
            'open': 'Ctrl+O',
            'new_file': 'Ctrl+N',
            'close_file': 'Ctrl+W',
            'undo': 'Ctrl+Z',
            'redo': 'Ctrl+Y',
            'cut': 'Ctrl+X',
            'copy': 'Ctrl+C',
            'paste': 'Ctrl+V',
            'find': 'Ctrl+F',
            'replace': 'Ctrl+H',
            'comment': 'Ctrl+/',
            'run_code': 'F5',
            'toggle_terminal': 'Ctrl+`'
        },
        'ai': {
            'enable': True,
            'suggestion_delay': 300,
            'max_suggestions': 5,
            'context_lines': 10,
            'model': {
                'type': 'local',
                'local_path': '',
                'api_endpoint': '',
                'api_key_env': 'REBELDESK_AI_API_KEY'
            }
        },
        'plugins': {
            'auto_update': True,
            'plugin_directory': 'plugins'
        }
    }
    
    config_manager.load_config.return_value = test_config
    config_manager.save_config.return_value = True
    
    return config_manager


@pytest.fixture
def settings_panel(app, config_manager):
    """Create a SettingsPanel instance for testing."""
    panel = SettingsPanel(config_manager=config_manager)
    yield panel
    panel.close()


def test_settings_panel_init(settings_panel):
    """Test that the settings panel initializes correctly."""
    assert settings_panel is not None
    assert isinstance(settings_panel, QDialog)
    assert settings_panel.windowTitle() == "RebelDESK Settings"
    
    # Check that the tab widget has the correct tabs
    assert settings_panel.tab_widget.count() == 5
    assert settings_panel.tab_widget.tabText(0) == "Appearance"
    assert settings_panel.tab_widget.tabText(1) == "Editor"
    assert settings_panel.tab_widget.tabText(2) == "Keyboard Shortcuts"
    assert settings_panel.tab_widget.tabText(3) == "AI Assistance"
    assert settings_panel.tab_widget.tabText(4) == "Plugins"


def test_settings_panel_appearance_tab(settings_panel):
    """Test the appearance tab of the settings panel."""
    # Check theme combo box
    assert settings_panel.theme_combo.currentText() == "Dark"
    assert settings_panel.theme_combo.count() == 3
    
    # Check syntax theme combo box
    assert settings_panel.syntax_theme_combo.currentText() == "Monokai"
    assert settings_panel.syntax_theme_combo.count() == 5
    
    # Check font combo box and size
    assert settings_panel.font_combo.currentText() == "Consolas"
    assert settings_panel.font_size_spin.value() == 12
    
    # Check window settings
    assert settings_panel.remember_size_check.isChecked() is True
    assert settings_panel.start_maximized_check.isChecked() is False
    assert settings_panel.default_width_spin.value() == 1200
    assert settings_panel.default_height_spin.value() == 800


def test_settings_panel_editor_tab(settings_panel):
    """Test the editor tab of the settings panel."""
    # Select the editor tab
    settings_panel.tab_widget.setCurrentIndex(1)
    
    # Check editor settings
    assert settings_panel.tab_size_spin.value() == 4
    assert settings_panel.use_spaces_check.isChecked() is True
    assert settings_panel.auto_indent_check.isChecked() is True
    assert settings_panel.line_numbers_check.isChecked() is True
    assert settings_panel.highlight_line_check.isChecked() is True
    assert settings_panel.word_wrap_check.isChecked() is False
    assert settings_panel.show_whitespace_check.isChecked() is False
    
    # Check auto-save settings
    assert settings_panel.auto_save_check.isChecked() is True
    assert settings_panel.auto_save_interval_spin.value() == 60
    assert settings_panel.backup_files_check.isChecked() is True
    
    # Check default language
    assert settings_panel.default_language_combo.currentText() == "Python"


def test_settings_panel_shortcuts_tab(settings_panel):
    """Test the keyboard shortcuts tab of the settings panel."""
    # Select the shortcuts tab
    settings_panel.tab_widget.setCurrentIndex(2)
    
    # Check file operation shortcuts
    assert settings_panel.save_shortcut.text() == "Ctrl+S"
    assert settings_panel.save_as_shortcut.text() == "Ctrl+Shift+S"
    assert settings_panel.open_shortcut.text() == "Ctrl+O"
    assert settings_panel.new_file_shortcut.text() == "Ctrl+N"
    assert settings_panel.close_file_shortcut.text() == "Ctrl+W"
    
    # Check editing shortcuts
    assert settings_panel.undo_shortcut.text() == "Ctrl+Z"
    assert settings_panel.redo_shortcut.text() == "Ctrl+Y"
    assert settings_panel.cut_shortcut.text() == "Ctrl+X"
    assert settings_panel.copy_shortcut.text() == "Ctrl+C"
    assert settings_panel.paste_shortcut.text() == "Ctrl+V"
    assert settings_panel.find_shortcut.text() == "Ctrl+F"
    assert settings_panel.replace_shortcut.text() == "Ctrl+H"
    assert settings_panel.comment_shortcut.text() == "Ctrl+/"
    
    # Check other shortcuts
    assert settings_panel.run_code_shortcut.text() == "F5"
    assert settings_panel.toggle_terminal_shortcut.text() == "Ctrl+`"


def test_settings_panel_ai_tab(settings_panel):
    """Test the AI assistance tab of the settings panel."""
    # Select the AI tab
    settings_panel.tab_widget.setCurrentIndex(3)
    
    # Check AI settings
    assert settings_panel.ai_enable_check.isChecked() is True
    assert settings_panel.suggestion_delay_spin.value() == 300
    assert settings_panel.max_suggestions_spin.value() == 5
    assert settings_panel.context_lines_spin.value() == 10
    
    # Check model settings
    assert settings_panel.model_type_combo.currentText() == "Local"
    assert settings_panel.local_model_path.text() == ""
    assert settings_panel.api_endpoint.text() == ""
    assert settings_panel.api_key_env.text() == "REBELDESK_AI_API_KEY"


def test_settings_panel_plugins_tab(settings_panel):
    """Test the plugins tab of the settings panel."""
    # Select the plugins tab
    settings_panel.tab_widget.setCurrentIndex(4)
    
    # Check plugin settings
    assert settings_panel.auto_update_plugins_check.isChecked() is True
    assert settings_panel.plugin_directory.text() == "plugins"


def test_settings_panel_apply_settings(settings_panel, config_manager):
    """Test applying settings changes."""
    # Change some settings
    settings_panel.theme_combo.setCurrentText("Light")
    settings_panel.font_size_spin.setValue(14)
    settings_panel.tab_size_spin.setValue(2)
    settings_panel.auto_save_check.setChecked(False)
    
    # Apply the settings
    settings_panel.apply_settings()
    
    # Check that save_config was called with the updated config
    config_manager.save_config.assert_called_once()
    saved_config = config_manager.save_config.call_args[0][0]
    
    # Check that the config was updated correctly
    assert saved_config['ui']['theme'] == 'light'
    assert saved_config['ui']['font']['size'] == 14
    assert saved_config['ui']['editor']['tab_size'] == 2
    assert saved_config['editor']['auto_save'] is False


def test_settings_panel_reset_settings(settings_panel, config_manager):
    """Test resetting settings to their original values."""
    # Change some settings
    settings_panel.theme_combo.setCurrentText("Light")
    settings_panel.font_size_spin.setValue(14)
    
    # Reset the settings
    settings_panel.reset_settings()
    
    # Check that the settings were reset
    assert settings_panel.theme_combo.currentText() == "Dark"
    assert settings_panel.font_size_spin.value() == 12


def test_settings_panel_reset_shortcuts(settings_panel):
    """Test resetting keyboard shortcuts to default values."""
    # Change some shortcuts
    settings_panel.save_shortcut.setText("Ctrl+Alt+S")
    settings_panel.undo_shortcut.setText("Ctrl+Alt+Z")
    
    # Reset the shortcuts
    settings_panel.reset_shortcuts()
    
    # Check that the shortcuts were reset
    assert settings_panel.save_shortcut.text() == "Ctrl+S"
    assert settings_panel.undo_shortcut.text() == "Ctrl+Z"


def test_settings_panel_accept(settings_panel, config_manager):
    """Test accepting the dialog and saving settings."""
    # Change some settings
    settings_panel.theme_combo.setCurrentText("Light")
    
    # Mock the accept method of the parent class
    with patch.object(QDialog, 'accept') as mock_accept:
        # Accept the dialog
        settings_panel.accept()
        
        # Check that save_config was called
        config_manager.save_config.assert_called_once()
        
        # Check that the parent accept method was called
        mock_accept.assert_called_once()
