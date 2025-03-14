# RebelDESK

A lightweight, modular Integrated Development Environment (IDE) with AI-assisted coding capabilities.

## Overview

RebelDESK is designed to be a modern, efficient IDE that combines the best features of traditional code editors with cutting-edge AI assistance. Built with Python and PyQt, it offers a clean, customizable interface while maintaining high performance.

### Key Features

- **Lightweight & Fast**: Optimized for speed and minimal resource usage
- **Modular Architecture**: Easily extensible through plugins
- **AI-Powered Coding**: Intelligent code suggestions and auto-completion
- **Multi-language Support**: Syntax highlighting and tools for various programming languages
- **Customizable Interface**: Themes, layouts, and keyboard shortcuts to match your workflow

## Project Structure

```
RebelDESK/
├── src/                 # Source code
│   ├── ui/              # UI components (editor, toolbars, settings)
│   ├── backend/         # Core backend logic (file handling, compilers)
│   ├── ai/              # AI code completion & LLM integration
│   ├── plugins/         # Modular plugin system for future expansion
│   ├── utils/           # Helper functions (logging, file operations)
│   ├── tests/           # Unit tests & UI testing automation
│   ├── main.py          # Program entry point
├── requirements.txt     # Dependencies
├── config.yaml          # Configuration settings
├── README.md            # Project documentation
├── .gitignore           # Ignore unnecessary files
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/snowmannn129/RebelDESK.git
   cd RebelDESK
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python src/main.py
   ```

## Configuration

RebelDESK can be configured by editing the `config.yaml` file. This includes settings for:

- UI themes and appearance
- Default programming language
- Editor behavior (tab size, auto-indent, etc.)
- AI assistance preferences
- Plugin settings

## Development

### GitHub Workflow Automation

RebelDESK uses GitHub Actions for automated workflow management:

- **Automated Testing**: Tests run automatically on push and pull requests
- **Progress Tracking**: Checklist items in progress.md are updated when issues are closed
- **Project Board Management**: Issues move through workflow stages automatically
- **Issue Status Updates**: Scripts to synchronize project progress with GitHub issues

#### GitHub Scripts

The project includes several scripts to manage GitHub integration:

- **create_github_issues.ps1**: Generates GitHub issues from progress tracking files
- **update_github_issue_status.ps1**: Updates issue status based on project progress
- **setup_github_labels.ps1**: Sets up standardized labels for the repository

The project is hosted on GitHub at: [https://github.com/snowmannn129/RebelDESK](https://github.com/snowmannn129/RebelDESK)

The GitHub project board can be found at: [https://github.com/users/snowmannn129/projects/1](https://github.com/users/snowmannn129/projects/1)

For detailed setup instructions, see [GitHub Workflow Guide](docs/github_workflow_guide.md).

### Running Tests

```
pytest src/tests/
```

### Updating GitHub Issue Status

To update GitHub issues based on project progress:

```
# Generate GitHub issue status update commands
powershell -File scripts/update_github_issue_status.ps1

# Execute the generated commands (requires GitHub CLI)
# The commands will be in reports/github_issue_status_update_YYYYMMDD.md
```

This will:
1. Close issues for completed tasks
2. Add the "in-progress" label to tasks that are in progress
3. The project board will automatically update based on these changes

### Development Workflow

1. **Select a Task**: Choose an issue from the "To-Do" column on the project board
2. **Implement**: Create a branch and implement the feature with tests
3. **Review**: Submit a pull request for review
4. **Testing**: Ensure all tests pass
5. **Complete**: Merge the PR and close the issue (progress.md updates automatically)

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
