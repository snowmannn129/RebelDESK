# RebelDESK Documentation

Welcome to the RebelDESK documentation. This guide will help you get started with RebelDESK, a lightweight, AI-powered IDE that integrates with the RebelSUITE ecosystem.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [User Interface](#user-interface)
5. [Features](#features)
6. [Configuration](#configuration)
7. [Plugin System](#plugin-system)
8. [AI Code Assistance](#ai-code-assistance)
9. [Integration with RebelSUITE](#integration-with-rebelsuite)
10. [Troubleshooting](#troubleshooting)
11. [API Reference](#api-reference)
12. [Contributing](#contributing)

## Introduction

RebelDESK is a lightweight, AI-powered IDE that integrates with the RebelSUITE ecosystem. It provides a modern development environment with advanced features for code editing, debugging, and AI-assisted programming.

## Installation

### Prerequisites

- Python 3.10 or higher
- PyQt6
- Git

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/snowmannn129/RebelDESK.git
   cd RebelDESK
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/main.py
   ```

## Getting Started

After installing RebelDESK, you can start using it by following these steps:

1. Launch the application by running `python src/main.py`
2. Create a new file or open an existing file
3. Start coding with AI-powered assistance

## User Interface

The RebelDESK user interface consists of the following components:

- **Menu Bar**: Contains menus for File, Edit, View, Tools, and Help
- **Toolbars**: Contains buttons for common actions
- **Editor Area**: The main area where you edit your code
- **File Browser**: Shows the files in your project
- **Output Panel**: Shows output from your code and the IDE

## Features

RebelDESK includes the following features:

- **Multi-language support** for Python, C++, JavaScript, Lua, TypeScript, Rust, and more
- **AI-powered coding assistance** including code completion, error detection, linting, and optimization
- **Deep debugging tools** with breakpoints, step-through execution, and real-time variable inspection
- **Plugin support** for extending functionality
- **Integrated terminal** for executing scripts and code
- **File management system** with project-based organization
- **Seamless integration with RebelSUITE components**
- **Cross-device, real-time collaboration** for multi-user live editing
- **Extensive theming and UI customization**
- **Offline-first architecture** with cloud sync capabilities

### Feature Documentation

- [Code Editor](features/code_editor.md): A powerful code editor with syntax highlighting, line numbers, and more
- [Natural Language Code Generation](features/natural_language_code_generation.md): Generate code from natural language descriptions using AI

## Configuration

RebelDESK can be configured using the settings dialog or by editing the configuration files directly. The configuration files are located in the following directories:

- **Windows**: `%APPDATA%\RebelDESK`
- **macOS**: `~/Library/Application Support/RebelDESK`
- **Linux**: `~/.config/RebelDESK`

## Plugin System

RebelDESK includes a powerful plugin system that allows you to extend its functionality. Plugins can be installed from the Plugin Manager or manually by copying them to the plugins directory.

### Creating Plugins

To create a plugin for RebelDESK, you need to create a Python module that implements the Plugin interface. See the [Plugin API Reference](#plugin-api-reference) for more information.

## AI Code Assistance

RebelDESK includes AI-powered code assistance features that help you write better code faster. These features include:

- **Code completion**: Suggests code completions as you type
- **Error detection**: Identifies errors in your code and suggests fixes
- **Code optimization**: Suggests ways to optimize your code
- **Natural language code generation**: Generates code from natural language descriptions and inserts it directly into your editor

## Integration with RebelSUITE

RebelDESK integrates with other RebelSUITE components:

- **RebelCODE**: AI-powered scripting and debugging
- **RebelFLOW**: Workflow automation
- **RebelENGINE**: Game engine debugging support
- **RebelCAD**: CAD scripting support
- **RebelSCRIBE**: Documentation generation

## Troubleshooting

If you encounter issues with RebelDESK, check the following:

1. Make sure you have the correct version of Python installed
2. Make sure all dependencies are installed correctly
3. Check the log file for error messages
4. Check the [GitHub Issues](https://github.com/snowmannn129/RebelDESK/issues) for known issues

## API Reference

### Main API

The main API for RebelDESK is documented in the [API Reference](api/index.md).

### Plugin API Reference

The plugin API for RebelDESK is documented in the [Plugin API Reference](api/plugin.md).

## Contributing

We welcome contributions to RebelDESK! To contribute, follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
