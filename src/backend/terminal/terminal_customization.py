#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal customization for RebelDESK.

This module provides a dialog for customizing the terminal appearance and behavior.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget,
    QLabel, QLineEdit, QComboBox, QSpinBox, QCheckBox, QPushButton,
    QColorDialog, QFontDialog, QGroupBox, QScrollArea, QWidget,
    QSizePolicy, QDialogButtonBox, QFrame
)
from PyQt5.QtCore import Qt, QSettings, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QColor, QFont, QPalette, QFontMetrics

logger = logging.getLogger(__name__)

class ColorButton(QPushButton):
    """Button that displays and allows selection of a color."""
    
    color_changed = pyqtSignal(QColor)
    
    def __init__(self, color: QColor = None, parent=None):
        """
        Initialize the color button.
        
        Args:
            color (QColor, optional): The initial color.
            parent (QWidget, optional): The parent widget.
        """
        super().__init__(parent)
        
        self.color = color or QColor("#000000")
        self.setFixedSize(32, 24)
        self.update_color()
        
        self.clicked.connect(self.on_clicked)
        
    def update_color(self):
        """Update the button appearance based on the current color."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color.name()};
                border: 1px solid #888888;
                border-radius: 3px;
            }}
            
            QPushButton:hover {{
                border: 1px solid #000000;
            }}
        """)
        
    def on_clicked(self):
        """Handle button click to open color dialog."""
        color = QColorDialog.getColor(self.color, self, "Select Color")
        if color.isValid():
            self.color = color
            self.update_color()
            self.color_changed.emit(color)
            
    def get_color(self) -> QColor:
        """Get the current color."""
        return self.color
        
    def set_color(self, color: QColor):
        """Set the current color."""
        if color.isValid():
            self.color = color
            self.update_color()


class TerminalCustomizationDialog(QDialog):
    """Dialog for customizing the terminal appearance and behavior."""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, config: Dict[str, Any] = None, parent=None):
        """
        Initialize the terminal customization dialog.
        
        Args:
            config (Dict[str, Any], optional): The current terminal configuration.
            parent (QWidget, optional): The parent widget.
        """
        super().__init__(parent)
        
        self.config = config or {}
        self.setWindowTitle("Terminal Customization")
        self.resize(600, 500)
        
        self._setup_ui()
        self._load_config()
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        # Appearance tab
        self.appearance_tab = QWidget()
        self.tab_widget.addTab(self.appearance_tab, "Appearance")
        self._setup_appearance_tab()
        
        # Behavior tab
        self.behavior_tab = QWidget()
        self.tab_widget.addTab(self.behavior_tab, "Behavior")
        self._setup_behavior_tab()
        
        # Advanced tab
        self.advanced_tab = QWidget()
        self.tab_widget.addTab(self.advanced_tab, "Advanced")
        self._setup_advanced_tab()
        
        # Button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        self.layout.addWidget(self.button_box)
        
        # Connect signals
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        
    def _setup_appearance_tab(self):
        """Set up the appearance tab."""
        layout = QVBoxLayout(self.appearance_tab)
        
        # Font group
        font_group = QGroupBox("Font")
        font_layout = QFormLayout(font_group)
        
        # Font family
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "Consolas", "Courier New", "DejaVu Sans Mono", "Fira Code", "Inconsolata",
            "JetBrains Mono", "Menlo", "Monaco", "Source Code Pro", "Ubuntu Mono"
        ])
        font_layout.addRow("Font Family:", self.font_family_combo)
        
        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        font_layout.addRow("Font Size:", self.font_size_spin)
        
        # Font button
        font_button_layout = QHBoxLayout()
        self.font_button = QPushButton("Select Font...")
        self.font_button.clicked.connect(self.on_select_font)
        font_button_layout.addWidget(self.font_button)
        font_button_layout.addStretch()
        font_layout.addRow("", font_button_layout)
        
        layout.addWidget(font_group)
        
        # Colors group
        colors_group = QGroupBox("Colors")
        colors_layout = QFormLayout(colors_group)
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Custom"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        colors_layout.addRow("Theme:", self.theme_combo)
        
        # Background color
        self.bg_color_button = ColorButton()
        colors_layout.addRow("Background:", self.bg_color_button)
        
        # Foreground color
        self.fg_color_button = ColorButton()
        colors_layout.addRow("Foreground:", self.fg_color_button)
        
        # Selection color
        self.selection_color_button = ColorButton()
        colors_layout.addRow("Selection:", self.selection_color_button)
        
        # Cursor color
        self.cursor_color_button = ColorButton()
        colors_layout.addRow("Cursor:", self.cursor_color_button)
        
        layout.addWidget(colors_group)
        
        # ANSI Colors group
        ansi_group = QGroupBox("ANSI Colors")
        ansi_layout = QFormLayout(ansi_group)
        
        # Basic colors
        self.ansi_colors = {}
        
        # Black
        self.ansi_colors[0] = ColorButton(QColor("#000000"))
        ansi_layout.addRow("Black:", self.ansi_colors[0])
        
        # Red
        self.ansi_colors[1] = ColorButton(QColor("#cd0000"))
        ansi_layout.addRow("Red:", self.ansi_colors[1])
        
        # Green
        self.ansi_colors[2] = ColorButton(QColor("#00cd00"))
        ansi_layout.addRow("Green:", self.ansi_colors[2])
        
        # Yellow
        self.ansi_colors[3] = ColorButton(QColor("#cdcd00"))
        ansi_layout.addRow("Yellow:", self.ansi_colors[3])
        
        # Blue
        self.ansi_colors[4] = ColorButton(QColor("#0000ee"))
        ansi_layout.addRow("Blue:", self.ansi_colors[4])
        
        # Magenta
        self.ansi_colors[5] = ColorButton(QColor("#cd00cd"))
        ansi_layout.addRow("Magenta:", self.ansi_colors[5])
        
        # Cyan
        self.ansi_colors[6] = ColorButton(QColor("#00cdcd"))
        ansi_layout.addRow("Cyan:", self.ansi_colors[6])
        
        # White
        self.ansi_colors[7] = ColorButton(QColor("#e5e5e5"))
        ansi_layout.addRow("White:", self.ansi_colors[7])
        
        layout.addWidget(ansi_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
    def _setup_behavior_tab(self):
        """Set up the behavior tab."""
        layout = QVBoxLayout(self.behavior_tab)
        
        # Cursor group
        cursor_group = QGroupBox("Cursor")
        cursor_layout = QFormLayout(cursor_group)
        
        # Cursor style
        self.cursor_style_combo = QComboBox()
        self.cursor_style_combo.addItems(["Block", "Underline", "I-Beam"])
        cursor_layout.addRow("Cursor Style:", self.cursor_style_combo)
        
        # Cursor blink
        self.cursor_blink_check = QCheckBox("Cursor Blink")
        cursor_layout.addRow("", self.cursor_blink_check)
        
        layout.addWidget(cursor_group)
        
        # Scrolling group
        scrolling_group = QGroupBox("Scrolling")
        scrolling_layout = QFormLayout(scrolling_group)
        
        # Scrollback lines
        self.scrollback_spin = QSpinBox()
        self.scrollback_spin.setRange(100, 100000)
        self.scrollback_spin.setValue(1000)
        self.scrollback_spin.setSingleStep(100)
        scrolling_layout.addRow("Scrollback Lines:", self.scrollback_spin)
        
        # Scroll on output
        self.scroll_output_check = QCheckBox("Scroll on Output")
        scrolling_layout.addRow("", self.scroll_output_check)
        
        # Scroll on keystroke
        self.scroll_keystroke_check = QCheckBox("Scroll on Keystroke")
        scrolling_layout.addRow("", self.scroll_keystroke_check)
        
        layout.addWidget(scrolling_group)
        
        # Input group
        input_group = QGroupBox("Input")
        input_layout = QFormLayout(input_group)
        
        # Tab size
        self.tab_size_spin = QSpinBox()
        self.tab_size_spin.setRange(1, 8)
        self.tab_size_spin.setValue(4)
        input_layout.addRow("Tab Size:", self.tab_size_spin)
        
        # Auto-wrap
        self.auto_wrap_check = QCheckBox("Auto-wrap Text")
        input_layout.addRow("", self.auto_wrap_check)
        
        layout.addWidget(input_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
    def _setup_advanced_tab(self):
        """Set up the advanced tab."""
        layout = QVBoxLayout(self.advanced_tab)
        
        # Shell group
        shell_group = QGroupBox("Shell")
        shell_layout = QFormLayout(shell_group)
        
        # Shell path
        self.shell_path_edit = QLineEdit()
        shell_layout.addRow("Shell Path:", self.shell_path_edit)
        
        # Shell arguments
        self.shell_args_edit = QLineEdit()
        shell_layout.addRow("Shell Arguments:", self.shell_args_edit)
        
        layout.addWidget(shell_group)
        
        # Environment group
        env_group = QGroupBox("Environment")
        env_layout = QVBoxLayout(env_group)
        
        # Environment variables
        self.env_vars_layout = QFormLayout()
        env_layout.addLayout(self.env_vars_layout)
        
        # Add variable button
        add_var_button = QPushButton("Add Environment Variable")
        add_var_button.clicked.connect(self.on_add_env_var)
        env_layout.addWidget(add_var_button)
        
        layout.addWidget(env_group)
        
        # Performance group
        perf_group = QGroupBox("Performance")
        perf_layout = QFormLayout(perf_group)
        
        # Update interval
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setRange(10, 1000)
        self.update_interval_spin.setValue(100)
        self.update_interval_spin.setSingleStep(10)
        self.update_interval_spin.setSuffix(" ms")
        perf_layout.addRow("Update Interval:", self.update_interval_spin)
        
        # Buffer size
        self.buffer_size_spin = QSpinBox()
        self.buffer_size_spin.setRange(1, 100)
        self.buffer_size_spin.setValue(10)
        self.buffer_size_spin.setSuffix(" MB")
        perf_layout.addRow("Buffer Size:", self.buffer_size_spin)
        
        layout.addWidget(perf_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
    def _load_config(self):
        """Load the current configuration into the UI."""
        # Appearance
        font_family = self.config.get('ui', {}).get('font', {}).get('family', "Consolas, 'Courier New', monospace")
        font_size = self.config.get('ui', {}).get('font', {}).get('size', 12)
        
        # Parse font family (may contain multiple fonts)
        font_families = [f.strip().strip("'\"") for f in font_family.split(',')]
        if font_families and font_families[0] in [self.font_family_combo.itemText(i) for i in range(self.font_family_combo.count())]:
            self.font_family_combo.setCurrentText(font_families[0])
        
        self.font_size_spin.setValue(font_size)
        
        # Theme
        theme = self.config.get('ui', {}).get('theme', 'dark')
        self.theme_combo.setCurrentText(theme.capitalize())
        
        # Colors
        if theme == 'dark':
            self.bg_color_button.set_color(QColor("#1e1e1e"))
            self.fg_color_button.set_color(QColor("#f0f0f0"))
            self.selection_color_button.set_color(QColor("#264f78"))
            self.cursor_color_button.set_color(QColor("#aeafad"))
        else:  # light theme
            self.bg_color_button.set_color(QColor("#f5f5f5"))
            self.fg_color_button.set_color(QColor("#000000"))
            self.selection_color_button.set_color(QColor("#add6ff"))
            self.cursor_color_button.set_color(QColor("#000000"))
            
        # ANSI Colors
        ansi_colors = self.config.get('ui', {}).get('ansi_colors', {})
        for i in range(8):
            color_key = f'color{i}'
            if color_key in ansi_colors:
                self.ansi_colors[i].set_color(QColor(ansi_colors[color_key]))
                
        # Behavior
        cursor_style = self.config.get('ui', {}).get('cursor', {}).get('style', 'block')
        self.cursor_style_combo.setCurrentText(cursor_style.capitalize())
        
        cursor_blink = self.config.get('ui', {}).get('cursor', {}).get('blink', True)
        self.cursor_blink_check.setChecked(cursor_blink)
        
        scrollback = self.config.get('ui', {}).get('scrollback', 1000)
        self.scrollback_spin.setValue(scrollback)
        
        scroll_output = self.config.get('ui', {}).get('scroll_on_output', True)
        self.scroll_output_check.setChecked(scroll_output)
        
        scroll_keystroke = self.config.get('ui', {}).get('scroll_on_keystroke', True)
        self.scroll_keystroke_check.setChecked(scroll_keystroke)
        
        tab_size = self.config.get('ui', {}).get('tab_size', 4)
        self.tab_size_spin.setValue(tab_size)
        
        auto_wrap = self.config.get('ui', {}).get('auto_wrap', False)
        self.auto_wrap_check.setChecked(auto_wrap)
        
        # Advanced
        shell_path = self.config.get('shell', {}).get('path', '')
        self.shell_path_edit.setText(shell_path)
        
        shell_args = self.config.get('shell', {}).get('args', '')
        self.shell_args_edit.setText(shell_args)
        
        # Environment variables
        env_vars = self.config.get('shell', {}).get('env', {})
        for name, value in env_vars.items():
            self.add_env_var(name, value)
            
        # Performance
        update_interval = self.config.get('performance', {}).get('update_interval', 100)
        self.update_interval_spin.setValue(update_interval)
        
        buffer_size = self.config.get('performance', {}).get('buffer_size', 10)
        self.buffer_size_spin.setValue(buffer_size)
        
    def on_theme_changed(self, theme):
        """
        Handle theme change.
        
        Args:
            theme (str): The new theme.
        """
        if theme == "Dark":
            self.bg_color_button.set_color(QColor("#1e1e1e"))
            self.fg_color_button.set_color(QColor("#f0f0f0"))
            self.selection_color_button.set_color(QColor("#264f78"))
            self.cursor_color_button.set_color(QColor("#aeafad"))
            
            # ANSI Colors
            self.ansi_colors[0].set_color(QColor("#000000"))  # Black
            self.ansi_colors[1].set_color(QColor("#cd0000"))  # Red
            self.ansi_colors[2].set_color(QColor("#00cd00"))  # Green
            self.ansi_colors[3].set_color(QColor("#cdcd00"))  # Yellow
            self.ansi_colors[4].set_color(QColor("#0000ee"))  # Blue
            self.ansi_colors[5].set_color(QColor("#cd00cd"))  # Magenta
            self.ansi_colors[6].set_color(QColor("#00cdcd"))  # Cyan
            self.ansi_colors[7].set_color(QColor("#e5e5e5"))  # White
        elif theme == "Light":
            self.bg_color_button.set_color(QColor("#f5f5f5"))
            self.fg_color_button.set_color(QColor("#000000"))
            self.selection_color_button.set_color(QColor("#add6ff"))
            self.cursor_color_button.set_color(QColor("#000000"))
            
            # ANSI Colors
            self.ansi_colors[0].set_color(QColor("#000000"))  # Black
            self.ansi_colors[1].set_color(QColor("#cd0000"))  # Red
            self.ansi_colors[2].set_color(QColor("#00cd00"))  # Green
            self.ansi_colors[3].set_color(QColor("#cdcd00"))  # Yellow
            self.ansi_colors[4].set_color(QColor("#0000ee"))  # Blue
            self.ansi_colors[5].set_color(QColor("#cd00cd"))  # Magenta
            self.ansi_colors[6].set_color(QColor("#00cdcd"))  # Cyan
            self.ansi_colors[7].set_color(QColor("#e5e5e5"))  # White
            
    def on_select_font(self):
        """Handle font selection."""
        current_font = QFont(self.font_family_combo.currentText(), self.font_size_spin.value())
        font, ok = QFontDialog.getFont(current_font, self, "Select Font")
        if ok:
            # Update the font family and size
            self.font_family_combo.setCurrentText(font.family())
            self.font_size_spin.setValue(font.pointSize())
            
    def on_add_env_var(self):
        """Handle adding an environment variable."""
        self.add_env_var("", "")
        
    def add_env_var(self, name, value):
        """
        Add an environment variable to the UI.
        
        Args:
            name (str): The variable name.
            value (str): The variable value.
        """
        # Create a horizontal layout for the variable
        var_layout = QHBoxLayout()
        
        # Name edit
        name_edit = QLineEdit(name)
        name_edit.setPlaceholderText("Variable Name")
        var_layout.addWidget(name_edit)
        
        # Value edit
        value_edit = QLineEdit(value)
        value_edit.setPlaceholderText("Variable Value")
        var_layout.addWidget(value_edit)
        
        # Remove button
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_env_var(var_layout))
        var_layout.addWidget(remove_button)
        
        # Add to the form layout
        self.env_vars_layout.addRow("", var_layout)
        
    def remove_env_var(self, layout):
        """
        Remove an environment variable from the UI.
        
        Args:
            layout (QLayout): The layout containing the variable.
        """
        # Remove all widgets from the layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Remove the layout from the form layout
        self.env_vars_layout.removeRow(layout)
        
    def get_env_vars(self):
        """
        Get the environment variables from the UI.
        
        Returns:
            Dict[str, str]: The environment variables.
        """
        env_vars = {}
        
        # Iterate through the form layout
        for i in range(self.env_vars_layout.rowCount()):
            # Get the layout at the current row
            layout_item = self.env_vars_layout.itemAt(i, QFormLayout.FieldRole)
            if layout_item and layout_item.layout():
                layout = layout_item.layout()
                
                # Get the name and value edits
                name_edit = layout.itemAt(0).widget()
                value_edit = layout.itemAt(1).widget()
                
                # Add to the dictionary if the name is not empty
                name = name_edit.text().strip()
                if name:
                    env_vars[name] = value_edit.text()
                    
        return env_vars
        
    def get_config(self):
        """
        Get the configuration from the UI.
        
        Returns:
            Dict[str, Any]: The configuration.
        """
        config = {}
        
        # UI settings
        config['ui'] = {
            'font': {
                'family': self.font_family_combo.currentText(),
                'size': self.font_size_spin.value()
            },
            'theme': self.theme_combo.currentText().lower(),
            'colors': {
                'background': self.bg_color_button.get_color().name(),
                'foreground': self.fg_color_button.get_color().name(),
                'selection': self.selection_color_button.get_color().name(),
                'cursor': self.cursor_color_button.get_color().name()
            },
            'ansi_colors': {
                f'color{i}': self.ansi_colors[i].get_color().name() for i in range(8)
            },
            'cursor': {
                'style': self.cursor_style_combo.currentText().lower(),
                'blink': self.cursor_blink_check.isChecked()
            },
            'scrollback': self.scrollback_spin.value(),
            'scroll_on_output': self.scroll_output_check.isChecked(),
            'scroll_on_keystroke': self.scroll_keystroke_check.isChecked(),
            'tab_size': self.tab_size_spin.value(),
            'auto_wrap': self.auto_wrap_check.isChecked()
        }
        
        # Shell settings
        config['shell'] = {
            'path': self.shell_path_edit.text(),
            'args': self.shell_args_edit.text(),
            'env': self.get_env_vars()
        }
        
        # Performance settings
        config['performance'] = {
            'update_interval': self.update_interval_spin.value(),
            'buffer_size': self.buffer_size_spin.value()
        }
        
        return config
        
    def apply_settings(self):
        """Apply the current settings."""
        self.config = self.get_config()
        self.settings_changed.emit(self.config)
        
    def accept(self):
        """Handle dialog acceptance."""
        self.apply_settings()
        super().accept()
