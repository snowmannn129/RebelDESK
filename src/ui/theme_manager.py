#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Theme Manager for RebelDESK.

This module provides a centralized theme management system for the RebelDESK IDE.
It ensures consistent theming across all UI components.
"""

import logging
from typing import Dict, Any, Optional

from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)

class ThemeManager:
    """Manages themes for the RebelDESK IDE."""
    
    # Define theme colors
    DARK_THEME = {
        "window_background": "#1e1e1e",
        "window_foreground": "#f0f0f0",
        "menu_background": "#2d2d2d",
        "menu_foreground": "#f0f0f0",
        "menu_selected_background": "#3e3d32",
        "toolbar_background": "#2d2d2d",
        "toolbar_foreground": "#f0f0f0",
        "statusbar_background": "#2d2d2d",
        "statusbar_foreground": "#f0f0f0",
        "tab_background": "#2d2d2d",
        "tab_foreground": "#f0f0f0",
        "tab_selected_background": "#1e1e1e",
        "tab_border": "#3c3c3c",
        "splitter_handle": "#3c3c3c",
        "editor_background": "#1e1e1e",
        "editor_foreground": "#f0f0f0",
        "editor_line_number_background": "#2d2d2d",
        "editor_line_number_foreground": "#8f908a",
        "editor_current_line": "#3e3d32",
        "terminal_background": "#1e1e1e",
        "terminal_foreground": "#f0f0f0",
        "terminal_toolbar_background": "#2d2d2d",
        "terminal_toolbar_foreground": "#f0f0f0",
        "terminal_border": "#3c3c3c",
        "settings_background": "#1e1e1e",
        "settings_foreground": "#f0f0f0",
        "settings_border": "#3c3c3c",
        "dialog_background": "#1e1e1e",
        "dialog_foreground": "#f0f0f0",
        "dialog_border": "#3c3c3c",
        "button_background": "#2d2d2d",
        "button_foreground": "#f0f0f0",
        "button_hover_background": "#3e3d32",
        "button_pressed_background": "#4e4d42",
        "input_background": "#2d2d2d",
        "input_foreground": "#f0f0f0",
        "input_border": "#3c3c3c",
        "scrollbar_background": "#2d2d2d",
        "scrollbar_handle": "#3c3c3c",
        "scrollbar_hover_handle": "#4c4c4c",
        "link_color": "#66d9ef",
        "error_color": "#ff5555",
        "warning_color": "#e6db74",
        "success_color": "#a6e22e",
        "info_color": "#66d9ef",
    }
    
    LIGHT_THEME = {
        "window_background": "#f5f5f5",
        "window_foreground": "#000000",
        "menu_background": "#f0f0f0",
        "menu_foreground": "#000000",
        "menu_selected_background": "#e0e0e0",
        "toolbar_background": "#f0f0f0",
        "toolbar_foreground": "#000000",
        "statusbar_background": "#f0f0f0",
        "statusbar_foreground": "#000000",
        "tab_background": "#e0e0e0",
        "tab_foreground": "#000000",
        "tab_selected_background": "#f5f5f5",
        "tab_border": "#cccccc",
        "splitter_handle": "#cccccc",
        "editor_background": "#f5f5f5",
        "editor_foreground": "#000000",
        "editor_line_number_background": "#e0e0e0",
        "editor_line_number_foreground": "#505050",
        "editor_current_line": "#e8e8e8",
        "terminal_background": "#f5f5f5",
        "terminal_foreground": "#000000",
        "terminal_toolbar_background": "#f0f0f0",
        "terminal_toolbar_foreground": "#000000",
        "terminal_border": "#cccccc",
        "settings_background": "#f5f5f5",
        "settings_foreground": "#000000",
        "settings_border": "#cccccc",
        "dialog_background": "#f5f5f5",
        "dialog_foreground": "#000000",
        "dialog_border": "#cccccc",
        "button_background": "#e0e0e0",
        "button_foreground": "#000000",
        "button_hover_background": "#d0d0d0",
        "button_pressed_background": "#c0c0c0",
        "input_background": "#ffffff",
        "input_foreground": "#000000",
        "input_border": "#cccccc",
        "scrollbar_background": "#f0f0f0",
        "scrollbar_handle": "#cccccc",
        "scrollbar_hover_handle": "#bbbbbb",
        "link_color": "#0066cc",
        "error_color": "#cc0000",
        "warning_color": "#cc7700",
        "success_color": "#00aa00",
        "info_color": "#0066cc",
    }
    
    # Map syntax highlighting themes to UI themes
    SYNTAX_THEME_MAP = {
        "dark": {
            "default": "monokai",
            "alternatives": ["dracula", "nord", "solarized-dark"]
        },
        "light": {
            "default": "github-light",
            "alternatives": ["solarized-light", "friendly", "colorful"]
        }
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the theme manager.
        
        Args:
            config (Dict[str, Any]): The application configuration.
        """
        self.config = config
        self.current_theme = config.get('ui', {}).get('theme', 'dark')
        self.theme_colors = self.DARK_THEME if self.current_theme == 'dark' else self.LIGHT_THEME
        
    def get_color(self, color_key: str) -> QColor:
        """
        Get a color from the current theme.
        
        Args:
            color_key (str): The key of the color to get.
            
        Returns:
            QColor: The color.
        """
        color_hex = self.theme_colors.get(color_key, "#000000")
        return QColor(color_hex)
        
    def get_stylesheet(self) -> str:
        """
        Get the stylesheet for the current theme.
        
        Returns:
            str: The stylesheet.
        """
        if self.current_theme == 'dark':
            return self._get_dark_stylesheet()
        else:
            return self._get_light_stylesheet()
            
    def _get_dark_stylesheet(self) -> str:
        """
        Get the stylesheet for the dark theme.
        
        Returns:
            str: The stylesheet.
        """
        return f"""
            QMainWindow, QWidget {{
                background-color: {self.theme_colors['window_background']};
                color: {self.theme_colors['window_foreground']};
            }}
            
            QMenuBar, QMenu {{
                background-color: {self.theme_colors['menu_background']};
                color: {self.theme_colors['menu_foreground']};
            }}
            
            QMenuBar::item:selected, QMenu::item:selected {{
                background-color: {self.theme_colors['menu_selected_background']};
            }}
            
            QToolBar {{
                background-color: {self.theme_colors['toolbar_background']};
                color: {self.theme_colors['toolbar_foreground']};
                border: none;
            }}
            
            QStatusBar {{
                background-color: {self.theme_colors['statusbar_background']};
                color: {self.theme_colors['statusbar_foreground']};
            }}
            
            QTabWidget::pane {{
                border: 1px solid {self.theme_colors['tab_border']};
            }}
            
            QTabBar::tab {{
                background-color: {self.theme_colors['tab_background']};
                color: {self.theme_colors['tab_foreground']};
                padding: 5px 10px;
                border: 1px solid {self.theme_colors['tab_border']};
            }}
            
            QTabBar::tab:selected {{
                background-color: {self.theme_colors['tab_selected_background']};
            }}
            
            QSplitter::handle {{
                background-color: {self.theme_colors['splitter_handle']};
            }}
            
            QPlainTextEdit, QTextEdit {{
                background-color: {self.theme_colors['editor_background']};
                color: {self.theme_colors['editor_foreground']};
                border: none;
            }}
            
            QLineEdit {{
                background-color: {self.theme_colors['input_background']};
                color: {self.theme_colors['input_foreground']};
                border: 1px solid {self.theme_colors['input_border']};
                padding: 2px 5px;
                border-radius: 3px;
            }}
            
            QPushButton {{
                background-color: {self.theme_colors['button_background']};
                color: {self.theme_colors['button_foreground']};
                border: 1px solid {self.theme_colors['input_border']};
                padding: 5px 10px;
                border-radius: 3px;
            }}
            
            QPushButton:hover {{
                background-color: {self.theme_colors['button_hover_background']};
            }}
            
            QPushButton:pressed {{
                background-color: {self.theme_colors['button_pressed_background']};
            }}
            
            QComboBox {{
                background-color: {self.theme_colors['input_background']};
                color: {self.theme_colors['input_foreground']};
                border: 1px solid {self.theme_colors['input_border']};
                padding: 2px 5px;
                border-radius: 3px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QScrollBar:vertical {{
                background-color: {self.theme_colors['scrollbar_background']};
                width: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {self.theme_colors['scrollbar_handle']};
                min-height: 20px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {self.theme_colors['scrollbar_hover_handle']};
            }}
            
            QScrollBar:horizontal {{
                background-color: {self.theme_colors['scrollbar_background']};
                height: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {self.theme_colors['scrollbar_handle']};
                min-width: 20px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {self.theme_colors['scrollbar_hover_handle']};
            }}
            
            QScrollBar::add-line, QScrollBar::sub-line {{
                width: 0px;
                height: 0px;
            }}
            
            QScrollBar::add-page, QScrollBar::sub-page {{
                background: none;
            }}
            
            QLabel {{
                color: {self.theme_colors['window_foreground']};
            }}
            
            QCheckBox {{
                color: {self.theme_colors['window_foreground']};
            }}
            
            QRadioButton {{
                color: {self.theme_colors['window_foreground']};
            }}
            
            QGroupBox {{
                border: 1px solid {self.theme_colors['input_border']};
                margin-top: 10px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: {self.theme_colors['window_foreground']};
            }}
            
            QToolButton {{
                background-color: transparent;
                color: {self.theme_colors['toolbar_foreground']};
                border: none;
                border-radius: 3px;
                padding: 3px;
            }}
            
            QToolButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
            
            QToolButton:pressed {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
            
            QDialog {{
                background-color: {self.theme_colors['dialog_background']};
                color: {self.theme_colors['dialog_foreground']};
            }}
        """
        
    def _get_light_stylesheet(self) -> str:
        """
        Get the stylesheet for the light theme.
        
        Returns:
            str: The stylesheet.
        """
        return f"""
            QMainWindow, QWidget {{
                background-color: {self.theme_colors['window_background']};
                color: {self.theme_colors['window_foreground']};
            }}
            
            QMenuBar, QMenu {{
                background-color: {self.theme_colors['menu_background']};
                color: {self.theme_colors['menu_foreground']};
            }}
            
            QMenuBar::item:selected, QMenu::item:selected {{
                background-color: {self.theme_colors['menu_selected_background']};
            }}
            
            QToolBar {{
                background-color: {self.theme_colors['toolbar_background']};
                color: {self.theme_colors['toolbar_foreground']};
                border: none;
            }}
            
            QStatusBar {{
                background-color: {self.theme_colors['statusbar_background']};
                color: {self.theme_colors['statusbar_foreground']};
            }}
            
            QTabWidget::pane {{
                border: 1px solid {self.theme_colors['tab_border']};
            }}
            
            QTabBar::tab {{
                background-color: {self.theme_colors['tab_background']};
                color: {self.theme_colors['tab_foreground']};
                padding: 5px 10px;
                border: 1px solid {self.theme_colors['tab_border']};
            }}
            
            QTabBar::tab:selected {{
                background-color: {self.theme_colors['tab_selected_background']};
            }}
            
            QSplitter::handle {{
                background-color: {self.theme_colors['splitter_handle']};
            }}
            
            QPlainTextEdit, QTextEdit {{
                background-color: {self.theme_colors['editor_background']};
                color: {self.theme_colors['editor_foreground']};
                border: none;
            }}
            
            QLineEdit {{
                background-color: {self.theme_colors['input_background']};
                color: {self.theme_colors['input_foreground']};
                border: 1px solid {self.theme_colors['input_border']};
                padding: 2px 5px;
                border-radius: 3px;
            }}
            
            QPushButton {{
                background-color: {self.theme_colors['button_background']};
                color: {self.theme_colors['button_foreground']};
                border: 1px solid {self.theme_colors['input_border']};
                padding: 5px 10px;
                border-radius: 3px;
            }}
            
            QPushButton:hover {{
                background-color: {self.theme_colors['button_hover_background']};
            }}
            
            QPushButton:pressed {{
                background-color: {self.theme_colors['button_pressed_background']};
            }}
            
            QComboBox {{
                background-color: {self.theme_colors['input_background']};
                color: {self.theme_colors['input_foreground']};
                border: 1px solid {self.theme_colors['input_border']};
                padding: 2px 5px;
                border-radius: 3px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QScrollBar:vertical {{
                background-color: {self.theme_colors['scrollbar_background']};
                width: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {self.theme_colors['scrollbar_handle']};
                min-height: 20px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {self.theme_colors['scrollbar_hover_handle']};
            }}
            
            QScrollBar:horizontal {{
                background-color: {self.theme_colors['scrollbar_background']};
                height: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {self.theme_colors['scrollbar_handle']};
                min-width: 20px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {self.theme_colors['scrollbar_hover_handle']};
            }}
            
            QScrollBar::add-line, QScrollBar::sub-line {{
                width: 0px;
                height: 0px;
            }}
            
            QScrollBar::add-page, QScrollBar::sub-page {{
                background: none;
            }}
            
            QLabel {{
                color: {self.theme_colors['window_foreground']};
            }}
            
            QCheckBox {{
                color: {self.theme_colors['window_foreground']};
            }}
            
            QRadioButton {{
                color: {self.theme_colors['window_foreground']};
            }}
            
            QGroupBox {{
                border: 1px solid {self.theme_colors['input_border']};
                margin-top: 10px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: {self.theme_colors['window_foreground']};
            }}
            
            QToolButton {{
                background-color: transparent;
                color: {self.theme_colors['toolbar_foreground']};
                border: none;
                border-radius: 3px;
                padding: 3px;
            }}
            
            QToolButton:hover {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
            
            QToolButton:pressed {{
                background-color: rgba(0, 0, 0, 0.2);
            }}
            
            QDialog {{
                background-color: {self.theme_colors['dialog_background']};
                color: {self.theme_colors['dialog_foreground']};
            }}
        """
        
    def apply_theme(self, theme: str) -> None:
        """
        Apply a theme to the application.
        
        Args:
            theme (str): The theme to apply ('dark' or 'light').
        """
        # Update the current theme
        self.current_theme = theme
        self.theme_colors = self.DARK_THEME if theme == 'dark' else self.LIGHT_THEME
        
        # Update the config
        self.config['ui']['theme'] = theme
        
        # Get the main window
        main_window = None
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                main_window = widget
                break
                
        if not main_window:
            logger.warning("Main window not found, cannot apply theme")
            return
            
        # Apply the stylesheet to the main window
        main_window.setStyleSheet(self.get_stylesheet())
        
        # Apply theme to editor components
        self._apply_theme_to_editors(main_window)
        
        # Apply theme to terminal components
        self._apply_theme_to_terminals(main_window)
        
        # Apply theme to settings components
        self._apply_theme_to_settings(main_window)
        
        # Apply theme to plugins
        self._apply_theme_to_plugins(main_window)
        
        logger.info(f"Applied {theme} theme to application")
        
    def _apply_theme_to_editors(self, main_window: QMainWindow) -> None:
        """
        Apply the current theme to all editor components.
        
        Args:
            main_window (QMainWindow): The main window.
        """
        # Ensure 'syntax' key exists in config
        if 'syntax' not in self.config:
            self.config['syntax'] = {}
        
        # Ensure 'theme' key exists in syntax config
        if 'theme' not in self.config['syntax']:
            self.config['syntax']['theme'] = self.SYNTAX_THEME_MAP[self.current_theme]['default']
            
        # Get the syntax theme based on the UI theme
        syntax_theme = self.config['syntax']['theme']
        
        # If the syntax theme doesn't match the UI theme, use the default for the UI theme
        if self.current_theme == 'dark' and syntax_theme not in self.SYNTAX_THEME_MAP['dark']['alternatives'] + [self.SYNTAX_THEME_MAP['dark']['default']]:
            syntax_theme = self.SYNTAX_THEME_MAP['dark']['default']
        elif self.current_theme == 'light' and syntax_theme not in self.SYNTAX_THEME_MAP['light']['alternatives'] + [self.SYNTAX_THEME_MAP['light']['default']]:
            syntax_theme = self.SYNTAX_THEME_MAP['light']['default']
        
        # Update the config
        self.config['syntax']['theme'] = syntax_theme
        
        # Apply theme to all editor tabs
        if hasattr(main_window, 'editor_tabs'):
            for i in range(main_window.editor_tabs.count()):
                editor = main_window.editor_tabs.widget(i)
                if hasattr(editor, 'set_theme'):
                    editor.set_theme(self.current_theme)
                if hasattr(editor, 'set_style'):
                    editor.set_style(syntax_theme)
                    
    def _apply_theme_to_terminals(self, main_window: QMainWindow) -> None:
        """
        Apply the current theme to all terminal components.
        
        Args:
            main_window (QMainWindow): The main window.
        """
        # Apply theme to the terminal
        if hasattr(main_window, 'terminal') and hasattr(main_window.terminal, 'set_theme'):
            main_window.terminal.set_theme(self.current_theme)
            
    def _apply_theme_to_settings(self, main_window: QMainWindow) -> None:
        """
        Apply the current theme to all settings components.
        
        Args:
            main_window (QMainWindow): The main window.
        """
        # Settings are typically shown in dialogs, which will use the global stylesheet
        pass
        
    def _apply_theme_to_plugins(self, main_window: QMainWindow) -> None:
        """
        Apply the current theme to all plugin components.
        
        Args:
            main_window (QMainWindow): The main window.
        """
        # Apply theme to enabled plugins
        if hasattr(main_window, 'plugin_manager'):
            enabled_plugins = main_window.plugin_manager.get_enabled_plugins()
            for plugin_id, plugin in enabled_plugins.items():
                if hasattr(plugin, 'set_theme'):
                    plugin.set_theme(self.current_theme)
                    
    def get_syntax_theme(self) -> str:
        """
        Get the appropriate syntax theme for the current UI theme.
        
        Returns:
            str: The syntax theme name.
        """
        # Ensure 'syntax' key exists in config
        if 'syntax' not in self.config:
            self.config['syntax'] = {}
        
        # Ensure 'theme' key exists in syntax config
        if 'theme' not in self.config['syntax']:
            self.config['syntax']['theme'] = self.SYNTAX_THEME_MAP[self.current_theme]['default']
            
        # Get the syntax theme based on the UI theme
        syntax_theme = self.config['syntax']['theme']
        
        # If the syntax theme doesn't match the UI theme, use the default for the UI theme
        if self.current_theme == 'dark' and syntax_theme not in self.SYNTAX_THEME_MAP['dark']['alternatives'] + [self.SYNTAX_THEME_MAP['dark']['default']]:
            syntax_theme = self.SYNTAX_THEME_MAP['dark']['default']
        elif self.current_theme == 'light' and syntax_theme not in self.SYNTAX_THEME_MAP['light']['alternatives'] + [self.SYNTAX_THEME_MAP['light']['default']]:
            syntax_theme = self.SYNTAX_THEME_MAP['light']['default']
            
        return syntax_theme
