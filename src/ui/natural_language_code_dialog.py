"""
Natural Language Code Generation Dialog.

This module provides a dialog for generating code from natural language descriptions.
"""

import logging
from typing import Optional, Dict, Any, Callable

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QPushButton, QComboBox, QCheckBox, QSplitter, QWidget,
    QMessageBox, QApplication, QGroupBox, QFormLayout
)
from PyQt5.QtGui import QFont, QTextCursor

from src.ai import NaturalLanguageCodeGenerator

logger = logging.getLogger(__name__)

class NaturalLanguageCodeDialog(QDialog):
    """
    Dialog for generating code from natural language descriptions.
    
    This dialog allows users to enter a natural language description of code
    they want to generate, select a programming language, and optionally provide
    context code to help guide the generation.
    """
    
    def __init__(
        self, 
        parent=None, 
        config: Optional[Dict[str, Any]] = None,
        on_code_generated: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize the dialog.
        
        Args:
            parent: The parent widget.
            config: Configuration dictionary for the dialog.
            on_code_generated: Callback function to call when code is generated.
                The function should take a string parameter containing the generated code.
        """
        super().__init__(parent)
        
        self.config = config or {}
        self.on_code_generated = on_code_generated
        
        # Create the code generator
        self.code_generator = NaturalLanguageCodeGenerator(self.config.get("ai", {}))
        
        # Set up the UI
        self._setup_ui()
        
        # Check if the code generator is available
        if not self.code_generator.is_available():
            QMessageBox.warning(
                self,
                "Local AI Server Not Available",
                "The local AI server is not available. Please start the server and try again."
            )
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Generate Code from Natural Language")
        self.resize(800, 600)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create a splitter for the input and output sections
        splitter = QSplitter(Qt.Vertical)
        
        # Input section
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        # Description input
        description_group = QGroupBox("Natural Language Description")
        description_layout = QVBoxLayout(description_group)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText(
            "Enter a description of the code you want to generate...\n\n"
            "For example:\n"
            "- A function that calculates the factorial of a number\n"
            "- A class that represents a bank account with deposit and withdraw methods\n"
            "- A function that sorts a list of dictionaries by a specific key"
        )
        description_layout.addWidget(self.description_edit)
        
        input_layout.addWidget(description_group)
        
        # Options group
        options_group = QGroupBox("Options")
        options_layout = QFormLayout(options_group)
        
        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "Python", "JavaScript", "TypeScript", "Java", "C++", 
            "C#", "Rust", "Go", "Ruby", "PHP", "Swift", "Kotlin", "Lua"
        ])
        options_layout.addRow("Language:", self.language_combo)
        
        # Include explanation checkbox
        self.explanation_checkbox = QCheckBox("Include explanation")
        self.explanation_checkbox.setChecked(True)
        options_layout.addRow("", self.explanation_checkbox)
        
        input_layout.addWidget(options_group)
        
        # Context code input (optional)
        context_group = QGroupBox("Context Code (Optional)")
        context_layout = QVBoxLayout(context_group)
        
        self.context_edit = QTextEdit()
        self.context_edit.setPlaceholderText(
            "Enter existing code to provide context for the generation...\n\n"
            "This can help the AI understand the coding style, variable names, etc."
        )
        context_layout.addWidget(self.context_edit)
        
        input_layout.addWidget(context_group)
        
        # Add the input widget to the splitter
        splitter.addWidget(input_widget)
        
        # Output section
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        
        # Generated code output
        output_group = QGroupBox("Generated Code")
        output_group_layout = QVBoxLayout(output_group)
        
        self.code_edit = QTextEdit()
        self.code_edit.setReadOnly(True)
        self.code_edit.setFont(QFont("Courier New", 10))
        output_group_layout.addWidget(self.code_edit)
        
        output_layout.addWidget(output_group)
        
        # Explanation output
        self.explanation_group = QGroupBox("Explanation")
        explanation_layout = QVBoxLayout(self.explanation_group)
        
        self.explanation_edit = QTextEdit()
        self.explanation_edit.setReadOnly(True)
        explanation_layout.addWidget(self.explanation_edit)
        
        output_layout.addWidget(self.explanation_group)
        
        # Add the output widget to the splitter
        splitter.addWidget(output_widget)
        
        # Set initial splitter sizes
        splitter.setSizes([300, 300])
        
        # Add the splitter to the main layout
        main_layout.addWidget(splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("Generate Code")
        self.generate_button.clicked.connect(self._generate_code)
        button_layout.addWidget(self.generate_button)
        
        self.insert_button = QPushButton("Insert Code")
        self.insert_button.clicked.connect(self._insert_code)
        self.insert_button.setEnabled(False)
        button_layout.addWidget(self.insert_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
    
    def _generate_code(self):
        """Generate code from the natural language description."""
        description = self.description_edit.toPlainText().strip()
        
        if not description:
            QMessageBox.warning(
                self,
                "Missing Description",
                "Please enter a natural language description of the code you want to generate."
            )
            return
        
        # Get the selected language
        language = self.language_combo.currentText().lower()
        
        # Get the context code (if any)
        context = self.context_edit.toPlainText().strip() or None
        
        # Show a busy cursor
        QApplication.setOverrideCursor(Qt.WaitCursor)
        
        try:
            # Generate the code
            if self.explanation_checkbox.isChecked():
                result = self.code_generator.generate_code_with_explanation(
                    description=description,
                    language=language,
                    context=context
                )
                
                if result["success"]:
                    self.code_edit.setText(result["code"])
                    self.explanation_edit.setText(result["explanation"])
                    self.explanation_group.setVisible(True)
                    self.insert_button.setEnabled(True)
                else:
                    QMessageBox.warning(
                        self,
                        "Error Generating Code",
                        f"An error occurred while generating code: {result.get('error', 'Unknown error')}"
                    )
            else:
                result = self.code_generator.generate_code(
                    description=description,
                    language=language,
                    context=context
                )
                
                if result["success"]:
                    self.code_edit.setText(result["code"])
                    self.explanation_group.setVisible(False)
                    self.insert_button.setEnabled(True)
                else:
                    QMessageBox.warning(
                        self,
                        "Error Generating Code",
                        f"An error occurred while generating code: {result.get('error', 'Unknown error')}"
                    )
        except Exception as e:
            logger.error(f"Error generating code: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while generating code: {str(e)}"
            )
        finally:
            # Restore the cursor
            QApplication.restoreOverrideCursor()
    
    def _insert_code(self):
        """Insert the generated code into the editor."""
        if self.on_code_generated:
            code = self.code_edit.toPlainText()
            self.on_code_generated(code)
            self.accept()
    
    def sizeHint(self) -> QSize:
        """Return the recommended size for the dialog."""
        return QSize(800, 600)
