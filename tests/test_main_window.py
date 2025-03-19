"""
Tests for the main window.
"""

import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from rebeldesk.ui.main_window import MainWindow

@pytest.fixture
def app(qtbot):
    """
    Create a QApplication instance for the tests.
    """
    return QApplication.instance()

@pytest.fixture
def main_window(qtbot):
    """
    Create a MainWindow instance for the tests.
    """
    window = MainWindow()
    qtbot.addWidget(window)
    return window

def test_main_window_title(main_window):
    """
    Test that the main window has the correct title.
    """
    assert main_window.windowTitle() == "RebelDESK"

def test_main_window_size(main_window):
    """
    Test that the main window has the correct minimum size.
    """
    assert main_window.minimumSize().width() == 800
    assert main_window.minimumSize().height() == 600

def test_main_window_central_widget(main_window):
    """
    Test that the main window has a central widget.
    """
    assert main_window.centralWidget() is not None
    assert main_window.central_tab_widget is not None

def test_main_window_menus(main_window):
    """
    Test that the main window has the correct menus.
    """
    menu_bar = main_window.menuBar()
    assert menu_bar is not None
    
    # Check that the menu bar has the correct number of menus
    assert menu_bar.actions()[0].text() == "&File"
    assert menu_bar.actions()[1].text() == "&Edit"
    assert menu_bar.actions()[2].text() == "&View"
    assert menu_bar.actions()[3].text() == "&Tools"
    assert menu_bar.actions()[4].text() == "&Help"

def test_main_window_toolbars(main_window):
    """
    Test that the main window has the correct toolbars.
    """
    toolbars = main_window.findChildren(Qt.ToolBar)
    assert len(toolbars) == 2
    
    # Check that the toolbars have the correct names
    toolbar_names = [toolbar.windowTitle() for toolbar in toolbars]
    assert "File" in toolbar_names
    assert "Edit" in toolbar_names

def test_main_window_dock_widgets(main_window):
    """
    Test that the main window has the correct dock widgets.
    """
    dock_widgets = main_window.findChildren(Qt.DockWidget)
    assert len(dock_widgets) == 2
    
    # Check that the dock widgets have the correct names
    dock_widget_names = [dock.windowTitle() for dock in dock_widgets]
    assert "Files" in dock_widget_names
    assert "Output" in dock_widget_names

def test_main_window_status_bar(main_window):
    """
    Test that the main window has a status bar.
    """
    assert main_window.statusBar() is not None
    assert main_window.statusBar().currentMessage() == "Ready"

def test_main_window_about_dialog(main_window, qtbot, monkeypatch):
    """
    Test that the about dialog is shown when the about action is triggered.
    """
    # Mock the QMessageBox.about method
    about_called = False
    
    def mock_about(*args, **kwargs):
        nonlocal about_called
        about_called = True
    
    monkeypatch.setattr("PyQt5.QtWidgets.QMessageBox.about", mock_about)
    
    # Find the about action
    help_menu = main_window.menuBar().actions()[4].menu()
    about_action = help_menu.actions()[0]
    
    # Trigger the about action
    about_action.trigger()
    
    # Check that the about dialog was shown
    assert about_called

def test_main_window_new_file(main_window, qtbot):
    """
    Test that a new file tab is created when the new file action is triggered.
    """
    # Get the initial tab count
    initial_tab_count = main_window.central_tab_widget.count()
    
    # Find the new file action
    file_menu = main_window.menuBar().actions()[0].menu()
    new_action = file_menu.actions()[0]
    
    # Trigger the new file action
    new_action.trigger()
    
    # Check that a new tab was added
    assert main_window.central_tab_widget.count() == initial_tab_count + 1
    
    # Check that the new tab is a FileTab
    from src.editor import FileTab
    assert isinstance(main_window.central_tab_widget.widget(initial_tab_count), FileTab)
    
    # Check that the new tab is the current tab
    assert main_window.central_tab_widget.currentIndex() == initial_tab_count

def test_main_window_code_generated(main_window, qtbot, monkeypatch):
    """
    Test that generated code is handled correctly.
    """
    # Mock the QMessageBox.question method to return Yes (insert code)
    def mock_question(*args, **kwargs):
        from PyQt5.QtWidgets import QMessageBox
        return QMessageBox.Yes
    
    monkeypatch.setattr("PyQt5.QtWidgets.QMessageBox.question", mock_question)
    
    # Create a new file tab
    main_window._on_new_file()
    
    # Get the file tab
    file_tab = main_window._get_current_file_tab()
    
    # Set some initial text
    initial_text = "# Initial text"
    file_tab.set_text(initial_text)
    
    # Generate some code
    generated_code = "def hello_world():\n    print('Hello, World!')"
    
    # Call the code generated handler
    main_window._on_code_generated(generated_code)
    
    # Check that the code was inserted
    assert generated_code in file_tab.get_text()
    assert file_tab.get_text().startswith(initial_text)

def test_main_window_code_generated_new_file(main_window, qtbot, monkeypatch):
    """
    Test that generated code creates a new file when no file is open.
    """
    # Close all tabs
    while main_window.central_tab_widget.count() > 0:
        main_window.central_tab_widget.removeTab(0)
    
    # Generate some code
    generated_code = "def hello_world():\n    print('Hello, World!')"
    
    # Call the code generated handler
    main_window._on_code_generated(generated_code)
    
    # Check that a new tab was created
    assert main_window.central_tab_widget.count() == 1
    
    # Check that the new tab contains the generated code
    file_tab = main_window._get_current_file_tab()
    assert file_tab.get_text() == generated_code
