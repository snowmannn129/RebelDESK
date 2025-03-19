# Code Editor

RebelDESK includes a powerful code editor component that provides a rich editing experience for various programming languages. The code editor is designed to be lightweight, responsive, and feature-rich, making it ideal for both simple and complex coding tasks.

## Overview

The Code Editor component provides the following features:

- Syntax highlighting for various programming languages
- Line numbers for easy code navigation
- Current line highlighting for better visibility
- Tab-based file management
- File operations (new, open, save, save as)
- Cursor position tracking
- Text selection and manipulation
- Integration with AI-powered features like Natural Language Code Generation

## Using the Code Editor

### Creating a New File

To create a new file:

1. Click on **File > New** in the menu bar
2. A new tab will be created with an empty editor
3. Start typing your code
4. Save the file when you're ready

### Opening an Existing File

To open an existing file:

1. Click on **File > Open** in the menu bar
2. Select the file you want to open in the file dialog
3. The file will be opened in a new tab

### Saving a File

To save the current file:

1. Click on **File > Save** in the menu bar
2. If the file hasn't been saved before, you'll be prompted to choose a location and filename
3. The file will be saved to disk

### Saving a File with a New Name

To save the current file with a new name:

1. Click on **File > Save As** in the menu bar
2. Choose a location and filename in the file dialog
3. The file will be saved to disk with the new name

### Closing a File

To close a file:

1. Click on the "x" button on the tab
2. If the file has unsaved changes, you'll be prompted to save them
3. The tab will be closed

## Code Editor Features

### Line Numbers

The code editor displays line numbers on the left side of the editor. This makes it easy to navigate through your code and reference specific lines.

### Current Line Highlighting

The current line (where the cursor is located) is highlighted with a subtle background color. This makes it easier to keep track of your position in the code.

### Cursor Position Tracking

The cursor position (line and column) is tracked and can be displayed in the status bar. This helps you navigate and understand your position in the code.

### Text Selection and Manipulation

You can select text in the editor using the mouse or keyboard shortcuts. Selected text can be cut, copied, pasted, or deleted using standard keyboard shortcuts or the Edit menu.

## Integration with AI Features

The Code Editor integrates seamlessly with RebelDESK's AI-powered features, such as Natural Language Code Generation. When you generate code using the AI, you can insert it directly into the current editor or create a new file with the generated code.

To use Natural Language Code Generation with the editor:

1. Open or create a file in the editor
2. Go to **Tools > AI > Generate Code from Description**
3. Enter a description of the code you want to generate
4. Click **Generate Code**
5. Review the generated code
6. Choose whether to insert the code at the current cursor position or create a new file
   - If you choose to insert the code, it will be inserted at the current cursor position
   - If you choose to create a new file, a new file will be created with the generated code and the appropriate file extension based on the detected language

## Advanced Features

### Error Handling

The Code Editor includes robust error handling to ensure a smooth user experience:

- **File Loading**: When loading a file, the editor checks for various issues such as file existence, permissions, and file size. If a file is too large, you'll be warned about potential performance issues.
- **File Saving**: When saving a file, the editor creates a backup of the existing file and uses atomic write operations to prevent data loss in case of system crashes or power failures.
- **Permission Checks**: The editor checks for read and write permissions before performing file operations, providing clear error messages if permissions are insufficient.

### File Operations

The Code Editor provides advanced file operations:

- **Atomic File Saving**: Files are saved using a two-step process that writes to a temporary file first, then renames it to the target file. This ensures that the file is either completely saved or not saved at all, preventing partial writes that could corrupt files.
- **Backup Creation**: When saving an existing file, a backup is automatically created with a `.bak` extension. This provides an extra layer of protection against data loss.
- **Large File Handling**: When opening large files, the editor warns you about potential performance issues and gives you the option to cancel the operation.

### Language Detection

When generating code or creating new files, the editor attempts to detect the programming language based on the code content. This allows it to:

- Set the appropriate file extension for new files
- Provide language-specific features and syntax highlighting
- Optimize the editing experience for the specific language

The language detection supports various languages including Python, JavaScript, TypeScript, HTML, CSS, Java, and C++.

## Keyboard Shortcuts

The Code Editor supports various keyboard shortcuts for common operations:

| Operation | Shortcut |
|-----------|----------|
| New File | Ctrl+N |
| Open File | Ctrl+O |
| Save File | Ctrl+S |
| Save As | Ctrl+Shift+S |
| Cut | Ctrl+X |
| Copy | Ctrl+C |
| Paste | Ctrl+V |
| Undo | Ctrl+Z |
| Redo | Ctrl+Y |

## Syntax Highlighting

The Code Editor includes an incremental syntax highlighter that provides efficient syntax highlighting for code files. The incremental syntax highlighter only rehighlights the modified parts of a document, which significantly improves performance for large files.

### Incremental Syntax Highlighting

Traditional syntax highlighters rehighlight the entire document whenever any part of it changes, which can cause performance issues with large files. The incremental syntax highlighter in RebelDESK addresses this issue by:

- Only rehighlighting the blocks (lines) that have been modified
- Processing blocks in batches to avoid blocking the UI
- Limiting the time spent on highlighting to maintain UI responsiveness
- Deferring highlighting until the UI is idle

This approach provides a much smoother editing experience, especially for large files.

### Syntax Highlighting Configuration

The syntax highlighter can be configured through the editor settings:

- **Batch Size**: The number of blocks to process in one batch (default: 50)
- **Maximum Highlighting Time**: The maximum time in milliseconds to spend on highlighting in one batch (default: 20ms)

These settings allow you to fine-tune the highlighting performance based on your system capabilities and preferences.

## Future Enhancements

In future versions of RebelDESK, the Code Editor will be enhanced with additional features such as:

- Syntax highlighting for more programming languages
- Code folding for better organization of large files
- Auto-indentation and code formatting
- Code completion and suggestions
- Integrated debugging capabilities
- Split view for editing multiple files side by side
- Search and replace functionality
- Bookmarks for quick navigation
