"""
Pytest configuration file for RebelDESK tests.
"""

import os
import sys
import pytest
from PyQt5.QtWidgets import QApplication

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

@pytest.fixture(scope="session")
def qapp():
    """
    Create a QApplication instance for the tests.
    
    This fixture has session scope, so it will be created once for the entire test session.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

@pytest.fixture
def qtbot(qapp, qtbot):
    """
    Create a QtBot instance for the tests.
    
    This fixture depends on the qapp fixture to ensure that a QApplication instance exists.
    """
    return qtbot
