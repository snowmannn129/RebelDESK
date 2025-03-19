"""
Tests for the Natural Language Code Generation Dialog.
"""

import pytest
from unittest.mock import patch, MagicMock

from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt

from src.ui.natural_language_code_dialog import NaturalLanguageCodeDialog
from src.ai import NaturalLanguageCodeGenerator

# Skip the test if PyQt is not available
pytestmark = pytest.mark.skipif(
    not hasattr(pytest, "qt_available") or not pytest.qt_available,
    reason="PyQt is not available"
)

class TestNaturalLanguageCodeDialog:
    """Tests for the Natural Language Code Generation Dialog."""
    
    @pytest.fixture
    def app(self):
        """Create a QApplication instance."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
    
    @pytest.fixture
    def dialog(self, app):
        """Create a NaturalLanguageCodeDialog instance."""
        with patch("src.ai.natural_language_code_generation.NaturalLanguageCodeGenerator.is_available", return_value=True):
            dialog = NaturalLanguageCodeDialog()
            yield dialog
            dialog.close()
    
    def test_dialog_initialization(self, dialog):
        """Test that the dialog initializes correctly."""
        assert dialog.windowTitle() == "Generate Code from Natural Language"
        assert dialog.size().width() >= 800
        assert dialog.size().height() >= 600
        
        # Check that the UI components are created
        assert hasattr(dialog, "description_edit")
        assert hasattr(dialog, "language_combo")
        assert hasattr(dialog, "context_edit")
        assert hasattr(dialog, "code_edit")
        assert hasattr(dialog, "explanation_edit")
        assert hasattr(dialog, "generate_button")
        assert hasattr(dialog, "insert_button")
        assert hasattr(dialog, "close_button")
        
        # Check that the language combo box has items
        assert dialog.language_combo.count() > 0
        assert dialog.language_combo.currentText() == "Python"
        
        # Check that the explanation checkbox is checked by default
        assert dialog.explanation_checkbox.isChecked()
        
        # Check that the insert button is disabled by default
        assert not dialog.insert_button.isEnabled()
    
    @patch("src.ai.natural_language_code_generation.NaturalLanguageCodeGenerator.generate_code_with_explanation")
    def test_generate_code_with_explanation(self, mock_generate, dialog):
        """Test generating code with explanation."""
        # Mock the generate_code_with_explanation method
        mock_generate.return_value = {
            "success": True,
            "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    else:\n        return n * factorial(n-1)",
            "explanation": "This function calculates the factorial of a number using recursion.",
            "language": "python"
        }
        
        # Set the description
        dialog.description_edit.setText("Create a function to calculate the factorial of a number")
        
        # Generate the code
        dialog._generate_code()
        
        # Check that the generate_code_with_explanation method was called with the correct arguments
        mock_generate.assert_called_once()
        args, kwargs = mock_generate.call_args
        assert kwargs["description"] == "Create a function to calculate the factorial of a number"
        assert kwargs["language"] == "python"
        assert kwargs["context"] is None
        
        # Check that the code and explanation are displayed
        assert "def factorial(n):" in dialog.code_edit.toPlainText()
        assert "recursion" in dialog.explanation_edit.toPlainText()
        
        # Check that the explanation group is visible
        assert dialog.explanation_group.isVisible()
        
        # Check that the insert button is enabled
        assert dialog.insert_button.isEnabled()
    
    @patch("src.ai.natural_language_code_generation.NaturalLanguageCodeGenerator.generate_code")
    def test_generate_code_without_explanation(self, mock_generate, dialog):
        """Test generating code without explanation."""
        # Mock the generate_code method
        mock_generate.return_value = {
            "success": True,
            "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    else:\n        return n * factorial(n-1)",
            "language": "python"
        }
        
        # Set the description
        dialog.description_edit.setText("Create a function to calculate the factorial of a number")
        
        # Uncheck the explanation checkbox
        dialog.explanation_checkbox.setChecked(False)
        
        # Generate the code
        dialog._generate_code()
        
        # Check that the generate_code method was called with the correct arguments
        mock_generate.assert_called_once()
        args, kwargs = mock_generate.call_args
        assert kwargs["description"] == "Create a function to calculate the factorial of a number"
        assert kwargs["language"] == "python"
        assert kwargs["context"] is None
        
        # Check that the code is displayed
        assert "def factorial(n):" in dialog.code_edit.toPlainText()
        
        # Check that the explanation group is not visible
        assert not dialog.explanation_group.isVisible()
        
        # Check that the insert button is enabled
        assert dialog.insert_button.isEnabled()
    
    @patch("src.ai.natural_language_code_generation.NaturalLanguageCodeGenerator.generate_code_with_explanation")
    def test_generate_code_with_context(self, mock_generate, dialog):
        """Test generating code with context."""
        # Mock the generate_code_with_explanation method
        mock_generate.return_value = {
            "success": True,
            "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    else:\n        return n * factorial(n-1)",
            "explanation": "This function calculates the factorial of a number using recursion.",
            "language": "python"
        }
        
        # Set the description and context
        dialog.description_edit.setText("Create a function to calculate the factorial of a number")
        dialog.context_edit.setText("def fibonacci(n):\n    if n <= 1:\n        return n\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)")
        
        # Generate the code
        dialog._generate_code()
        
        # Check that the generate_code_with_explanation method was called with the correct arguments
        mock_generate.assert_called_once()
        args, kwargs = mock_generate.call_args
        assert kwargs["description"] == "Create a function to calculate the factorial of a number"
        assert kwargs["language"] == "python"
        assert "fibonacci" in kwargs["context"]
    
    @patch("src.ai.natural_language_code_generation.NaturalLanguageCodeGenerator.generate_code_with_explanation")
    def test_generate_code_error(self, mock_generate, dialog, monkeypatch):
        """Test generating code with an error."""
        # Mock the generate_code_with_explanation method
        mock_generate.return_value = {
            "success": False,
            "error": "Test error",
            "code": "",
            "explanation": "",
            "language": "python"
        }
        
        # Mock the QMessageBox.warning method
        mock_warning = MagicMock()
        monkeypatch.setattr("PyQt5.QtWidgets.QMessageBox.warning", mock_warning)
        
        # Set the description
        dialog.description_edit.setText("Create a function to calculate the factorial of a number")
        
        # Generate the code
        dialog._generate_code()
        
        # Check that the generate_code_with_explanation method was called
        mock_generate.assert_called_once()
        
        # Check that the warning message box was shown
        mock_warning.assert_called_once()
        args, kwargs = mock_warning.call_args
        assert "Error Generating Code" in args[1]
        assert "Test error" in args[2]
        
        # Check that the insert button is still disabled
        assert not dialog.insert_button.isEnabled()
    
    def test_insert_code(self, dialog):
        """Test inserting the generated code."""
        # Create a mock callback function
        mock_callback = MagicMock()
        dialog.on_code_generated = mock_callback
        
        # Set some code
        dialog.code_edit.setText("def factorial(n):\n    if n <= 1:\n        return 1\n    else:\n        return n * factorial(n-1)")
        
        # Enable the insert button
        dialog.insert_button.setEnabled(True)
        
        # Click the insert button
        dialog._insert_code()
        
        # Check that the callback function was called with the correct code
        mock_callback.assert_called_once()
        args, kwargs = mock_callback.call_args
        assert "def factorial(n):" in args[0]
        
        # Check that the dialog was accepted
        assert dialog.result() == QDialog.Accepted
    
    def test_missing_description(self, dialog, monkeypatch):
        """Test generating code with a missing description."""
        # Mock the QMessageBox.warning method
        mock_warning = MagicMock()
        monkeypatch.setattr("PyQt5.QtWidgets.QMessageBox.warning", mock_warning)
        
        # Generate the code without setting a description
        dialog._generate_code()
        
        # Check that the warning message box was shown
        mock_warning.assert_called_once()
        args, kwargs = mock_warning.call_args
        assert "Missing Description" in args[1]
