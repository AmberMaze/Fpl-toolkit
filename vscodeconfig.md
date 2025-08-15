# VS Code Configuration for FPL Toolkit

This document explains the comprehensive VS Code setup for the FPL Toolkit project, designed to optimize development experience for Python, FastAPI, Streamlit, and AI/ML development.

## 🗂️ Configuration Files Overview

### `.vscode/settings.json`
Contains workspace-specific settings that enhance the development experience for this Fantasy Premier League toolkit.

### `.vscode/launch.json`
Debugging configurations for different components of the application.

### `.vscode/tasks.json`
Automated tasks for common development workflows.

### `.vscode/extensions.json`
Recommended extensions for optimal development experience.

### `.vscode/copilot-mcp.json`
GitHub Copilot MCP (Model Context Protocol) configuration for enhanced AI assistance.

## 🐍 Python Development Configuration

### Language Server & Analysis
- **Pylance**: Advanced Python language server with type checking, auto-completion, and intelligent suggestions
- **Type Checking**: Set to "basic" mode for optimal balance between accuracy and performance
- **Auto Imports**: Enabled for faster development
- **Extra Paths**: Configured to include `./src` for proper module resolution

### Code Quality Tools
- **Black**: Primary code formatter with 88-character line length (matches pyproject.toml)
- **Ruff**: Fast Python linter and formatter for code quality
- **MyPy**: Static type checker integration
- **Auto-format on save**: Ensures consistent code style

### Testing Integration
- **Pytest**: Configured as primary testing framework
- **Auto-discovery**: Tests are automatically discovered on save
- **Coverage**: Integrated test coverage reporting
- **Debug configurations**: Dedicated launch configs for testing

## 🚀 Application Development

### FastAPI Development
- **Debug Configuration**: Full debugging support for FastAPI server
- **Auto-reload**: Development server with hot reloading
- **REST Client**: Integrated API testing capabilities
- **OpenAPI Support**: Schema validation and documentation

### Streamlit Development
- **Debug Support**: Dedicated debugging configuration for Streamlit app
- **Live Preview**: Automatic browser refresh during development
- **Mobile Testing**: Configured for responsive design testing

### Database Development
- **PostgreSQL Support**: Advanced database management and querying
- **SQLite Viewer**: For local database inspection
- **Query Testing**: Integrated database testing tools

## 🤖 AI/ML Development

### Jupyter Integration
- **Notebook Support**: Full Jupyter notebook functionality
- **Kernel Management**: Automatic kernel restart and management
- **Data Visualization**: Enhanced plotting and data exploration

### GitHub Copilot Enhancement
- **Project-Specific Instructions**: Custom instructions loaded from `.github/copilot-instructions.md`
- **Toolset Configuration**: Specialized FPL toolkit context
- **MCP Integration**: Enhanced AI assistance with custom tools

## 🛠️ Development Workflow

### Automated Tasks
All tasks are accessible via `Ctrl+Shift+P` → "Tasks: Run Task":

1. **Install Dependencies**: Installs all project dependencies including optional ones
2. **Run Tests**: Executes pytest with verbose output
3. **Run Tests with Coverage**: Generates HTML coverage reports
4. **Format Code (Black)**: Formats entire codebase
5. **Lint Code (Ruff)**: Checks code quality and style
6. **Type Check (MyPy)**: Static type analysis
7. **Start FastAPI Server**: Launches development server with auto-reload
8. **Start Streamlit App**: Launches Streamlit frontend
9. **Initialize Database**: Sets up database schema
10. **Build Docker Image**: Creates production Docker image
11. **Run All Checks**: Sequential execution of all quality checks

### Debug Configurations
Accessible via `F5` or Debug panel:

1. **FastAPI Server (Debug)**: Debug FastAPI application with breakpoints
2. **Streamlit App (Debug)**: Debug Streamlit frontend
3. **FPL CLI**: Debug command-line interface
4. **Run Current Python File**: Debug any Python file
5. **Debug Tests**: Debug pytest with breakpoints
6. **Debug Current Test File**: Debug specific test file

## 📦 Extensions Ecosystem

### Core Python Extensions
- `ms-python.python`: Core Python support
- `ms-python.debugpy`: Modern Python debugging
- `ms-python.vscode-pylance`: Advanced language server
- `ms-python.black-formatter`: Code formatting
- `charliermarsh.ruff`: Fast linting and formatting

### Web Development
- `humao.rest-client`: API testing
- `rangav.vscode-thunder-client`: Advanced HTTP client
- `esbenp.prettier-vscode`: Web file formatting
- `bradlc.vscode-tailwindcss`: CSS framework support

### Database & Infrastructure
- `ms-ossdata.vscode-postgresql`: PostgreSQL management
- `qwtel.sqlite-viewer`: SQLite database inspection
- `ms-azuretools.vscode-docker`: Docker integration

### AI/ML Development
- `ms-toolsai.jupyter`: Jupyter notebook support
- `ms-toolsai.datawrangler`: Data analysis tools
- `github.copilot`: AI pair programming
- `github.copilot-chat`: Conversational AI assistance

### Productivity & Quality
- `streetsidesoftware.code-spell-checker`: Spell checking with FPL terms
- `usernamehw.errorlens`: Inline error display
- `gruntfuggly.todo-tree`: Task management
- `eamodio.gitlens`: Enhanced Git integration

## 🎯 Project-Specific Optimizations

### FPL Domain Knowledge
- **Custom Dictionary**: Includes FPL-specific terms (gameweek, xG, xA, differentials, etc.)
- **File Associations**: Proper handling of .env files, Dockerfiles, and configuration files
- **Path Intelligence**: Auto-completion for project-specific imports

### Performance Optimizations
- **Search Exclusions**: Excludes cache directories and build artifacts
- **File Watching**: Optimized file watching to avoid performance issues
- **Auto-save**: Configured for optimal development flow

### Code Quality Standards
- **Line Length**: 88 characters (Black standard)
- **Import Organization**: Automatic import sorting and organization
- **Type Hints**: Encouraged through MyPy integration
- **Test Coverage**: Integrated coverage reporting

## 🔧 Environment Configuration

### Python Environment
- **Virtual Environment**: Automatically activates `./venv/bin/python`
- **PYTHONPATH**: Configured to include `src/` directory
- **Environment Variables**: Proper handling of .env files

### Terminal Integration
- **Environment Activation**: Automatic virtual environment activation
- **Custom Environment Variables**: PYTHONPATH set for all terminals
- **Shell Integration**: Optimized for bash with environment setup

### API Development
- **Environment Variables**: Configured for local and production environments
- **Base URLs**: Pre-configured for local development and production
- **Request Testing**: Integrated REST client with environment switching

## 🚨 Quality Assurance

### Automated Checks
- **Pre-commit**: Format and lint checks on save
- **Import Organization**: Automatic import sorting
- **Error Detection**: Real-time error highlighting with ErrorLens
- **Type Safety**: Continuous type checking with Pylance

### Testing Integration
- **Auto-discovery**: Tests automatically detected and runnable
- **Coverage Reporting**: HTML and terminal coverage reports
- **Debug Testing**: Full debugging support for tests
- **Continuous Testing**: Option to run tests on file changes

## 🎨 User Experience

### Theme & Appearance
- **Tokyo Right Theme**: Consistent with project preferences
- **Error Highlighting**: Inline error and warning display
- **Code Lens**: Enhanced code navigation and references
- **Bracket Matching**: Improved bracket pair visualization

### Navigation & Search
- **Intelligent Search**: Excludes cache and build directories
- **Path Auto-completion**: Smart path suggestions
- **Symbol Navigation**: Fast navigation between functions and classes
- **File Associations**: Proper syntax highlighting for all file types

## 🔄 Workflow Integration

### Git Integration
- **Auto-fetch**: Automatic remote updates
- **Smart Commits**: Intelligent commit message suggestions
- **Pull Request Integration**: GitHub PR management
- **GitLens**: Advanced Git history and blame information

### Docker Integration
- **Container Development**: Remote container support
- **Image Building**: Integrated Docker image building
- **Registry Management**: Docker registry integration
- **Deployment**: Streamlined deployment workflow

## 📊 Monitoring & Debugging

### Real-time Feedback
- **Error Lens**: Inline error and warning display
- **Problem Matcher**: Intelligent error parsing for all tools
- **Live Debugging**: Real-time variable inspection
- **Performance Monitoring**: Resource usage tracking

### Logging & Output
- **Integrated Terminal**: Unified output for all tools
- **Task Output**: Organized task execution results
- **Debug Console**: Interactive debugging console
- **Test Results**: Comprehensive test result display

## 🎯 Why This Configuration?

### Developer Productivity
1. **Reduced Context Switching**: All tools integrated in VS Code
2. **Automated Workflows**: Common tasks are one-click operations
3. **Intelligent Assistance**: AI-powered code suggestions and debugging
4. **Quality Assurance**: Automatic code quality checks

### Project Consistency
1. **Standardized Formatting**: Consistent code style across team
2. **Shared Configuration**: All team members use same setup
3. **Automated Testing**: Consistent test execution environment
4. **Type Safety**: Shared type checking standards

### FPL Domain Expertise
1. **Domain Vocabulary**: Spell checker knows FPL terminology
2. **Project Structure**: Optimized for src/ layout and module structure
3. **API Development**: Configured for FastAPI and REST development
4. **AI/ML Workflow**: Support for machine learning and data analysis

### Scalability & Maintenance
1. **Modular Configuration**: Easy to update and maintain
2. **Extension Management**: Recommended extensions for consistency
3. **Performance Optimization**: Configured to handle large codebases
4. **Environment Flexibility**: Works with different Python versions and environments

This configuration creates a comprehensive, efficient, and enjoyable development environment specifically tailored for the FPL Toolkit project's needs while maintaining best practices for Python, web development, and AI/ML projects.
