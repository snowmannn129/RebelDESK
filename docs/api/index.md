# RebelDESK API Reference

This document provides a reference for the RebelDESK API. It covers the main classes and functions that you can use to interact with RebelDESK programmatically.

## Table of Contents

1. [Main API](#main-api)
2. [UI API](#ui-api)
3. [Editor API](#editor-api)
4. [Plugin API](#plugin-api)
5. [AI API](#ai-api)
6. [Language API](#language-api)
7. [Utility API](#utility-api)

## Main API

The main API provides access to the core functionality of RebelDESK.

### `rebeldesk.main`

The `rebeldesk.main` module contains the main entry point for the application.

#### `main()`

The main entry point for the RebelDESK application.

**Returns:**
- `int`: The exit code of the application.

### `rebeldesk.app`

The `rebeldesk.app` module contains the application class.

#### `Application`

The main application class.

**Methods:**
- `__init__()`: Initialize the application.
- `run()`: Run the application.
- `quit()`: Quit the application.
- `get_main_window()`: Get the main window.
- `get_settings()`: Get the application settings.
- `get_plugin_manager()`: Get the plugin manager.

## UI API

The UI API provides access to the user interface components of RebelDESK.

### `rebeldesk.ui.main_window`

The `rebeldesk.ui.main_window` module contains the main window class.

#### `MainWindow`

The main window class.

**Methods:**
- `__init__()`: Initialize the main window.
- `show()`: Show the main window.
- `close()`: Close the main window.
- `get_central_widget()`: Get the central widget.
- `get_dock_widgets()`: Get the dock widgets.
- `get_toolbars()`: Get the toolbars.
- `get_status_bar()`: Get the status bar.
- `get_menu_bar()`: Get the menu bar.

## Editor API

The editor API provides access to the code editor components of RebelDESK.

For detailed documentation of the editor API, see the [Editor API Reference](editor.md).

### `rebeldesk.editor.code_editor`

The `rebeldesk.editor.code_editor` module contains the code editor class.

#### `CodeEditor`

The code editor class.

**Methods:**
- `__init__()`: Initialize the code editor.
- `set_text(text)`: Set the editor text.
- `get_text()`: Get the editor text.
- `insert_text(text)`: Insert text at the current cursor position.
- `get_selected_text()`: Get the selected text.
- `set_cursor_position(line, column)`: Set the cursor position.
- `get_cursor_position()`: Get the cursor position.
- `goto_line(line)`: Go to a specific line.
- `undo()`: Undo the last action.
- `redo()`: Redo the last undone action.
- `cut()`: Cut the selected text.
- `copy()`: Copy the selected text.
- `paste()`: Paste the clipboard text.
- `select_all()`: Select all text.
- `find(text)`: Find text in the editor.
- `replace(text, replacement)`: Replace text in the editor.

### `rebeldesk.editor.file_tab`

The `rebeldesk.editor.file_tab` module contains the file tab class.

#### `FileTab`

The file tab class.

**Methods:**
- `__init__()`: Initialize the file tab.
- `load_file(file_path)`: Load a file into the editor.
- `save_file()`: Save the file.
- `save_file_as()`: Save the file with a new name.
- `is_modified()`: Check if the file has been modified.
- `get_file_path()`: Get the file path.
- `set_text(text)`: Set the editor text.
- `get_text()`: Get the editor text.
- `insert_text(text)`: Insert text at the current cursor position.
- `get_selected_text()`: Get the selected text.
- `set_cursor_position(line, column)`: Set the cursor position.
- `get_cursor_position()`: Get the cursor position.
- `goto_line(line)`: Go to a specific line.

## Plugin API

The plugin API provides access to the plugin system of RebelDESK.

### `rebeldesk.plugins.plugin`

The `rebeldesk.plugins.plugin` module contains the plugin base class.

#### `Plugin`

The plugin base class.

**Methods:**
- `__init__()`: Initialize the plugin.
- `activate()`: Activate the plugin.
- `deactivate()`: Deactivate the plugin.
- `get_name()`: Get the plugin name.
- `get_version()`: Get the plugin version.
- `get_description()`: Get the plugin description.
- `get_author()`: Get the plugin author.
- `get_dependencies()`: Get the plugin dependencies.

### `rebeldesk.plugins.plugin_manager`

The `rebeldesk.plugins.plugin_manager` module contains the plugin manager class.

#### `PluginManager`

The plugin manager class.

**Methods:**
- `__init__()`: Initialize the plugin manager.
- `load_plugin(plugin_id)`: Load a plugin.
- `unload_plugin(plugin_id)`: Unload a plugin.
- `get_plugin(plugin_id)`: Get a plugin.
- `get_plugins()`: Get all plugins.
- `get_active_plugins()`: Get active plugins.
- `is_plugin_active(plugin_id)`: Check if a plugin is active.
- `activate_plugin(plugin_id)`: Activate a plugin.
- `deactivate_plugin(plugin_id)`: Deactivate a plugin.

## AI API

The AI API provides access to the AI code assistance features of RebelDESK.

### `rebeldesk.ai.code_completion`

The `rebeldesk.ai.code_completion` module contains the code completion provider class.

#### `CodeCompletionProvider`

The code completion provider class.

**Methods:**
- `__init__()`: Initialize the code completion provider.
- `get_completions(code, position)`: Get code completions.
- `get_signature_help(code, position)`: Get signature help.
- `get_hover_info(code, position)`: Get hover information.

### `rebeldesk.ai.error_detection`

The `rebeldesk.ai.error_detection` module contains the error detection provider class.

#### `ErrorDetectionProvider`

The error detection provider class.

**Methods:**
- `__init__()`: Initialize the error detection provider.
- `get_errors(code)`: Get errors in the code.
- `get_fixes(code, error)`: Get fixes for an error.

### `rebeldesk.ai.natural_language_code_generation`

The `rebeldesk.ai.natural_language_code_generation` module contains the natural language code generation provider class.

For detailed documentation of the natural language code generation API, see the [Natural Language Code Generation API Reference](natural_language_code_generation.md).

#### `NaturalLanguageCodeGenerator`

The natural language code generation provider class.

**Methods:**
- `__init__(config=None)`: Initialize the natural language code generator.
- `is_available()`: Check if the natural language code generator is available.
- `generate_code(description, language=None, context=None)`: Generate code from a natural language description.
- `generate_code_with_explanation(description, language=None, context=None)`: Generate code with an explanation from a natural language description.
- `improve_code(code, instructions, language=None)`: Improve existing code based on instructions.

## Language API

The language API provides access to the language support features of RebelDESK.

### `rebeldesk.language.language_server`

The `rebeldesk.language.language_server` module contains the language server client class.

#### `LanguageServerClient`

The language server client class.

**Methods:**
- `__init__()`: Initialize the language server client.
- `start()`: Start the language server.
- `stop()`: Stop the language server.
- `is_running()`: Check if the language server is running.
- `get_capabilities()`: Get the language server capabilities.
- `send_request(method, params)`: Send a request to the language server.
- `send_notification(method, params)`: Send a notification to the language server.

## Utility API

The utility API provides access to utility functions and classes of RebelDESK.

### `rebeldesk.utils.settings`

The `rebeldesk.utils.settings` module contains the settings class.

#### `Settings`

The settings class.

**Methods:**
- `__init__()`: Initialize the settings.
- `get(key, default=None)`: Get a setting value.
- `set(key, value)`: Set a setting value.
- `remove(key)`: Remove a setting.
- `clear()`: Clear all settings.
- `contains(key)`: Check if a setting exists.
- `sync()`: Sync settings to disk.

### `rebeldesk.utils.file_utils`

The `rebeldesk.utils.file_utils` module contains file utility functions.

#### Functions

- `read_file(path)`: Read a file.
- `write_file(path, content)`: Write a file.
- `copy_file(source, destination)`: Copy a file.
- `move_file(source, destination)`: Move a file.
- `delete_file(path)`: Delete a file.
- `create_directory(path)`: Create a directory.
- `delete_directory(path)`: Delete a directory.
- `list_files(path)`: List files in a directory.
- `list_directories(path)`: List directories in a directory.
- `get_file_info(path)`: Get file information.
