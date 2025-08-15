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

### Python Testing Integration

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

## 🎯 Comprehensive Configuration (Updated)

This setup provides full-featured development capabilities without redundancy:

- **All essential development tools** for Python, web development, database management
- **No overlapping functionality** - each extension serves a unique purpose  
- **Smart tool selection** - comprehensive toolset staying under 128 tools to avoid degraded performance
- **Project-specific optimizations** for FPL domain knowledge and workflows

## 🗂️ Enhanced Configuration Files

### `.vscode/extensions.json` - Balanced Extension Ecosystem (25 extensions)

**Core Python Stack (4 extensions):**

- `ms-python.python`: Core Python support with debugging
- `ms-python.vscode-pylance`: Advanced language server with IntelliSense
- `ms-python.black-formatter`: Code formatting (no overlap with other formatters)
- `charliermarsh.ruff`: Fast linting (replaces flake8, pylint, isort)

**AI & Data Science (2 extensions):**

- `ms-toolsai.jupyter`: Notebook support for ML development
- `github.copilot` + `github.copilot-chat`: AI pair programming

**Web Development (4 extensions):**

- `esbenp.prettier-vscode`: Web file formatting
- `humao.rest-client`: HTTP request testing
- `rangav.vscode-thunder-client`: Advanced API client
- `42crunch.vscode-openapi`: OpenAPI/Swagger support

**Database Management (2 extensions):**

- `ms-ossdata.vscode-postgresql`: PostgreSQL management
- `qwtel.sqlite-viewer`: SQLite inspection

**Infrastructure (2 extensions):**

- `ms-azuretools.vscode-docker`: Docker integration
- `ms-vscode-remote.remote-containers`: Container development

**Productivity (6 extensions):**

- `streetsidesoftware.code-spell-checker`: Spell checking with FPL terms
- `usernamehw.errorlens`: Inline error display
- `eamodio.gitlens`: Enhanced Git features
- `gruntfuggly.todo-tree`: Task management
- `yzhang.markdown-all-in-one`: Comprehensive Markdown support
- `bierner.markdown-mermaid`: Diagram support

**Configuration (2 extensions):**

- `mikestead.dotenv`: Environment file support
- `editorconfig.editorconfig`: Cross-editor configuration

### `.vscode/tasks.json` - Comprehensive Development Tasks (15 tasks)

**Build & Setup:**

- Install Dependencies, Setup Environment

**Testing (3 focused tasks):**

- Run Tests: Basic test execution
- Run Tests with Coverage: Full coverage reporting  
- Quick Test: Fast feedback with early exit

**Code Quality (3 complementary tasks):**

- Format Code: Black formatting only
- Lint Code: Ruff linting only
- Format & Lint: Combined workflow

**Development Servers (2 background tasks):**

- Start FastAPI Server: Debug-ready with hot reload
- Start Streamlit: Frontend development

**Database & Infrastructure:**

- Initialize Database, Build/Run Docker Container

**Utilities:**

- Clean Cache: Remove Python bytecode

### `.vscode/launch.json` - Comprehensive Debugging (8 configurations)

**Application Debugging:**

- FastAPI Server, Streamlit App, FPL CLI

**Testing Debugging:**

- All Tests, Current Test File, Failed Tests, API Endpoints

**General:**

- Debug Current File

### `.vscode/copilot-mcp.json` - Enhanced AI Integration

**Multi-environment support:**

- Production API, Local development, FPL API access
- Smart capability declarations for focused tool usage

## 🚀 Key Optimizations Made

**Removed Redundancies:**

- ❌ Multiple Python linters (using only Ruff)
- ❌ Separate import sorters (Ruff handles this)  
- ❌ MyPy extension (Pylance provides type checking)
- ❌ Multiple test frameworks (pytest only)
- ❌ Duplicate Git tools (GitLens + built-in Git)

**Smart Tool Selection:**

- ✅ Comprehensive but non-overlapping extensions
- ✅ Essential productivity tools only
- ✅ Project-specific optimizations
- ✅ Performance-conscious configurations

## 🎯 Tool Count Optimization Result

**Target**: Stay well under 128 tools to avoid performance degradation

**Strategy**:

- Comprehensive extensions (25 total) providing full functionality
- Each extension serves unique purpose - no overlaps
- Smart unwantedRecommendations to prevent tool bloat
- Focused MCP server capabilities
- Streamlined but complete task definitions

**Result**: Feature-rich development environment optimized for performance and productivity.

This configuration provides a comprehensive, efficient, and enjoyable development environment specifically optimized for the FPL Toolkit project while maintaining performance and avoiding tool redundancy.
