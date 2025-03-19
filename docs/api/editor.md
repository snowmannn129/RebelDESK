# Editor API Reference

This document provides a reference for the RebelDESK Editor API, which includes the `CodeEditor` and `FileTab` classes.

## CodeEditor

The `CodeEditor` class provides a code editor component with syntax highlighting, line numbers, and other features.

### Class Definition

```python
class CodeEditor(QPlainTextEdit):
    """
    Code editor component for RebelDESK.
    
    This component provides a code editor with syntax highlighting,
    line numbers, and other features useful for editing code.
    """
    
    # Signal emitted when the cursor position changes
    cursorPositionChanged = pyqtSignal(int, int)  # line, column
    
    def __init__(self, parent=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the code editor.
        
        Args:
            parent: The parent widget.
            config: Configuration dictionary for the editor.
        """
```

### Properties

- `line_number_area`: The line number area widget.
- `config`: The configuration dictionary for the editor.
- `syntax_highlighter`: The incremental syntax highlighter for the editor.

### Methods

#### `_setup_editor()`

Set up the editor appearance and behavior.

#### `line_number_area_width() -> int`

Calculate the width of the line number area.

**Returns**:
- `int`: The width of the line number area in pixels.

#### `_update_line_number_area_width(_)`

Update the width of the line number area.

**Args**:
- `_`: The new block count (unused).

#### `_update_line_number_area(rect, dy)`

Update the line number area when the editor viewport scrolls.

**Args**:
- `rect`: The rectangle that needs to be updated.
- `dy`: The vertical scroll amount.

#### `resizeEvent(event)`

Handle resize events.

**Args**:
- `event`: The resize event.

#### `line_number_area_paint_event(event)`

Paint the line number area.

**Args**:
- `event`: The paint event.

#### `_highlight_current_line()`

Highlight the current line.

#### `_emit_cursor_position()`

Emit the cursor position changed signal.

#### `insert_text(text: str)`

Insert text at the current cursor position.

**Args**:
- `text`: The text to insert.

#### `get_text() -> str`

Get the current text in the editor.

**Returns**:
- `str`: The current text.

#### `set_text(text: str)`

Set the text in the editor.

**Args**:
- `text`: The text to set.

#### `get_selected_text() -> str`

Get the currently selected text.

**Returns**:
- `str`: The selected text.

#### `get_cursor_position() -> tuple`

Get the current cursor position.

**Returns**:
- `tuple`: A tuple of (line, column).

#### `set_cursor_position(line: int, column: int)`

Set the cursor position.

**Args**:
- `line`: The line number (1-based).
- `column`: The column number (1-based).

#### `goto_line(line: int)`

Go to the specified line.

**Args**:
- `line`: The line number (1-based).

#### `get_syntax_highlighter() -> IncrementalSyntaxHighlighter`

Get the syntax highlighter.

**Returns**:
- `IncrementalSyntaxHighlighter`: The syntax highlighter.

#### `set_syntax_highlighter_batch_size(batch_size: int)`

Set the batch size for the syntax highlighter.

**Args**:
- `batch_size`: The number of blocks to process in one batch.

#### `set_syntax_highlighter_max_time(max_time: int)`

Set the maximum time for the syntax highlighter.

**Args**:
- `max_time`: The maximum time in milliseconds.

#### `rehighlight()`

Rehighlight the entire document.

## FileTab

The `FileTab` class provides a tab for editing a file, including a code editor and file operations.

### Class Definition

```python
class FileTab(QWidget):
    """
    File tab component for RebelDESK.
    
    This component provides a tab for editing a file, including a code editor
    and file operations like save and save as.
    """
    
    # Signal emitted when the file is modified
    fileModified = pyqtSignal(bool)
    
    # Signal emitted when the cursor position changes
    cursorPositionChanged = pyqtSignal(int, int)  # line, column
    
    def __init__(self, parent=None, file_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the file tab.
        
        Args:
            parent: The parent widget.
            file_path: The path to the file to open.
            config: Configuration dictionary for the tab.
        """
```

### Properties

- `file_path`: The path to the file being edited.
- `config`: The configuration dictionary for the tab.
- `modified`: Whether the file has been modified.
- `editor`: The code editor widget.

### Methods

#### `_setup_ui()`

Set up the UI components.

#### `_on_text_changed()`

Handle text changed events.

#### `_on_cursor_position_changed(line, column)`

Handle cursor position changed events.

**Args**:
- `line`: The line number (1-based).
- `column`: The column number (1-based).

#### `_get_tab_title() -> str`

Get the title for the tab.

**Returns**:
- `str`: The tab title.

#### `load_file(file_path: str) -> bool`

Load a file into the editor.

**Args**:
- `file_path`: The path to the file to load.

**Returns**:
- `bool`: True if the file was loaded successfully, False otherwise.

#### `save_file() -> bool`

Save the file.

**Returns**:
- `bool`: True if the file was saved successfully, False otherwise.

#### `save_file_as() -> bool`

Save the file with a new name.

**Returns**:
- `bool`: True if the file was saved successfully, False otherwise.

#### `insert_text(text: str)`

Insert text at the current cursor position.

**Args**:
- `text`: The text to insert.

#### `get_text() -> str`

Get the current text in the editor.

**Returns**:
- `str`: The current text.

#### `set_text(text: str)`

Set the text in the editor.

**Args**:
- `text`: The text to set.

#### `get_selected_text() -> str`

Get the currently selected text.

**Returns**:
- `str`: The selected text.

#### `get_cursor_position() -> tuple`

Get the current cursor position.

**Returns**:
- `tuple`: A tuple of (line, column).

#### `set_cursor_position(line: int, column: int)`

Set the cursor position.

**Args**:
- `line`: The line number (1-based).
- `column`: The column number (1-based).

#### `goto_line(line: int)`

Go to the specified line.

**Args**:
- `line`: The line number (1-based).

#### `is_modified() -> bool`

Check if the file has been modified.

**Returns**:
- `bool`: True if the file has been modified, False otherwise.

#### `get_file_path() -> Optional[str]`

Get the file path.

**Returns**:
- `Optional[str]`: The file path, or None if the file has not been saved.

## IncrementalSyntaxHighlighter

The `IncrementalSyntaxHighlighter` class provides an incremental syntax highlighter that only rehighlights the modified parts of a document, improving performance for large files.

### Class Definition

```python
class IncrementalSyntaxHighlighter(QSyntaxHighlighter):
    """
    A syntax highlighter that only rehighlights the modified parts of a document.
    
    This highlighter improves performance for large files by only rehighlighting
    the blocks that have been modified, rather than the entire document.
    """
    
    def __init__(self, document: QTextDocument):
        """
        Initialize the syntax highlighter.
        
        Args:
            document (QTextDocument): The document to highlight.
        """
```

### Properties

- `highlighting_rules`: The list of highlighting rules.
- `modified_blocks`: The set of modified block numbers.
- `dirty_blocks`: The set of block numbers that need to be rehighlighted.
- `batch_size`: The number of blocks to process in one batch.
- `max_highlighting_time`: The maximum time in milliseconds to spend highlighting.

### Methods

#### `setup_highlighting_rules()`

Set up the default highlighting rules.

#### `handle_contents_change(position: int, removed: int, added: int)`

Handle document contents change.

**Args**:
- `position`: The position where the change occurred.
- `removed`: The number of characters removed.
- `added`: The number of characters added.

#### `schedule_highlighting()`

Schedule highlighting of dirty blocks.

#### `highlight_dirty_blocks()`

Highlight the dirty blocks.

#### `highlightBlock(text: str)`

Highlight a block of text. This method is called by the QSyntaxHighlighter framework.

**Args**:
- `text`: The text to highlight.

#### `highlight_block(text: str, block: QTextBlock)`

Highlight a block of text.

**Args**:
- `text`: The text to highlight.
- `block`: The block to highlight.

#### `rehighlight()`

Rehighlight the entire document.

#### `rehighlight_block(block: QTextBlock)`

Rehighlight a specific block.

**Args**:
- `block`: The block to rehighlight.

#### `set_batch_size(batch_size: int)`

Set the batch size for highlighting.

**Args**:
- `batch_size`: The number of blocks to process in one batch.

#### `set_max_highlighting_time(max_time: int)`

Set the maximum time to spend highlighting.

**Args**:
- `max_time`: The maximum time in milliseconds.

#### `get_dirty_block_count() -> int`

Get the number of dirty blocks.

**Returns**:
- `int`: The number of dirty blocks.

#### `get_modified_block_count() -> int`

Get the number of modified blocks.

**Returns**:
- `int`: The number of modified blocks.

#### `clear_modified_blocks()`

Clear the set of modified blocks.

## Usage Examples

### Creating a Code Editor

```python
from src.editor import CodeEditor

# Create a code editor
editor = CodeEditor()

# Set text in the editor
editor.set_text("def hello_world():\n    print('Hello, World!')")

# Get the text from the editor
text = editor.get_text()

# Insert text at the current cursor position
editor.insert_text("# This is a comment\n")

# Set the cursor position
editor.set_cursor_position(2, 5)  # Line 2, column 5

# Go to a specific line
editor.goto_line(1)  # Go to line 1

# Configure the syntax highlighter
editor.set_syntax_highlighter_batch_size(100)
editor.set_syntax_highlighter_max_time(30)

# Rehighlight the document
editor.rehighlight()
```

### Creating a File Tab

```python
from src.editor import FileTab

# Create a file tab
file_tab = FileTab()

# Set text in the file tab
file_tab.set_text("def hello_world():\n    print('Hello, World!')")

# Load a file
file_tab.load_file("path/to/file.py")

# Save the file
file_tab.save_file()

# Save the file with a new name
file_tab.save_file_as()

# Check if the file has been modified
if file_tab.is_modified():
    print("The file has been modified")

# Get the file path
file_path = file_tab.get_file_path()
