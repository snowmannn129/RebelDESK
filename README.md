# RebelDESK

RebelDESK is a lightweight, AI-powered IDE that integrates with the RebelSUITE ecosystem. It provides a modern development environment with advanced features for code editing, debugging, and AI-assisted programming.

## Features

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

## Project Structure

```
RebelDESK/
├── src/                 # Core source code
│   ├── ui/              # UI components
│   ├── backend/         # Core logic
│   ├── ai/              # AI-assisted automation
│   ├── editor/          # Code editor components
│   ├── plugins/         # Plugin architecture
│   ├── language/        # Language support
│   ├── utils/           # Utility functions
│   └── main.py          # Primary execution file
├── docs/                # Documentation
├── tests/               # Unit and integration tests
├── config/              # Configuration settings
├── examples/            # Example projects and usage
└── offline_models/      # Local AI models
```

## Getting Started

### Prerequisites

- Python 3.10 or higher
- PyQt6
- Git

### Installation

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

## Development

### Setting Up a Development Environment

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```
   pip install -r requirements-dev.txt
   ```

3. Run tests:
   ```
   pytest
   ```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Integration with RebelSUITE

RebelDESK integrates with other RebelSUITE components:

- **RebelCODE**: AI-powered scripting and debugging
- **RebelFLOW**: Workflow automation
- **RebelENGINE**: Game engine debugging support
- **RebelCAD**: CAD scripting support
- **RebelSCRIBE**: Documentation generation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The RebelSUITE development team
- Contributors to the open-source libraries used in this project
