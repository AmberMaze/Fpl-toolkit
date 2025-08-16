#!/bin/bash
# FPL Toolkit - Intelligent Setup Script
# Automatically detects environment and installs appropriate dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    FPL Toolkit Setup                        ║"
echo "║          Fantasy Premier League Analysis Platform            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Configuration
PYTHON_MIN_VERSION="3.10"
NODE_MIN_VERSION="18"

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

version_compare() {
    if [[ "$(printf '%s\n' "$2" "$1" | sort -V | head -n1)" = "$2" ]]; then
        return 0
    else
        return 1
    fi
}

check_python() {
    log_info "Checking Python installation..."
    
    if ! check_command python3; then
        log_error "Python 3 is not installed. Please install Python $PYTHON_MIN_VERSION+ first."
        echo "  Visit: https://www.python.org/downloads/"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    
    if version_compare "$PYTHON_VERSION" "$PYTHON_MIN_VERSION"; then
        log_success "Python $PYTHON_VERSION detected (>= $PYTHON_MIN_VERSION required)"
        return 0
    else
        log_error "Python $PYTHON_MIN_VERSION+ required. Found: $PYTHON_VERSION"
        echo "  Please upgrade Python: https://www.python.org/downloads/"
        exit 1
    fi
}

check_node() {
    log_info "Checking Node.js installation (optional for frontend)..."
    
    if check_command node; then
        NODE_VERSION=$(node --version 2>/dev/null | sed 's/v//' | cut -d'.' -f1)
        if [[ $NODE_VERSION -ge $NODE_MIN_VERSION ]]; then
            log_success "Node.js v$NODE_VERSION detected"
            return 0
        else
            log_warning "Node.js v$NODE_MIN_VERSION+ recommended. Found: v$NODE_VERSION"
            return 1
        fi
    else
        log_warning "Node.js not found. Frontend development will be limited."
        log_info "  To install: https://nodejs.org/"
        return 1
    fi
}

setup_python_env() {
    log_info "Setting up Python environment..."
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
        log_success "Virtual environment created"
    else
        log_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    source venv/bin/activate || {
        log_error "Failed to activate virtual environment"
        exit 1
    }
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip --quiet
    log_success "Pip upgraded"
}

detect_ai_availability() {
    log_info "Detecting AI/ML capabilities..."
    
    # Check if we can install AI dependencies
    python3 -c "
import subprocess
import sys
try:
    # Try to import existing AI packages
    import sentence_transformers
    print('ai_available')
except ImportError:
    try:
        # Test if we can install AI packages (check for compatible environment)
        import platform
        import distutils.util
        # Basic compatibility check
        if platform.machine() in ['x86_64', 'AMD64', 'aarch64', 'arm64']:
            print('ai_installable')
        else:
            print('ai_not_available')
    except:
        print('ai_not_available')
" 2>/dev/null || echo 'ai_not_available'
}

install_dependencies() {
    log_info "Installing FPL Toolkit dependencies..."
    
    # Determine installation profile
    local install_profile="[dev,web,postgresql]"
    
    # Check AI availability
    local ai_status=$(detect_ai_availability)
    
    if [[ "$ai_status" == "ai_available" ]] || [[ "$ai_status" == "ai_installable" ]] || [[ "$1" == "--force-ai" ]]; then
        install_profile="[dev,web,ai,postgresql]"
        log_info "Installing with AI/ML features..."
        
        # Install AI dependencies with fallback
        if ! pip install -e "$install_profile" --quiet 2>/dev/null; then
            log_warning "AI installation failed, falling back to core features..."
            install_profile="[dev,web,postgresql]"
            pip install -e "$install_profile" --quiet
        fi
    else
        log_warning "Installing without AI features (can be added later)"
        log_info "  To add AI later: pip install -e '.[ai]'"
        pip install -e "$install_profile" --quiet
    fi
    
    # Verify installation
    if python -c "import src.fpl_toolkit.cli" 2>/dev/null; then
        log_success "FPL Toolkit core installation verified"
    else
        log_error "Installation verification failed"
        exit 1
    fi
}

setup_configuration() {
    log_info "Setting up configuration..."
    
    # Create .env file
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success ".env file created from template"
        else
            # Create basic .env file
            cat > .env << EOF
# FPL Toolkit Configuration
# Database (SQLite by default, PostgreSQL for production)
# DATABASE_URL=postgresql://username:password@localhost:5432/fpl_toolkit

# API Settings
CACHE_TTL_SECONDS=3600
ENABLE_ADVANCED_METRICS=true

# Development
DEBUG=true
EOF
            log_success ".env file created with defaults"
        fi
    else
        log_success ".env file already exists"
    fi
}

initialize_database() {
    log_info "Initializing database..."
    
    if python -m fpl_toolkit.cli init 2>/dev/null; then
        log_success "Database initialized successfully"
    else
        log_warning "Database initialization failed (may already exist)"
    fi
}

setup_frontend() {
    if [[ "$NODE_AVAILABLE" == "true" ]] && [ -d "frontend" ]; then
        log_info "Setting up frontend dependencies..."
        
        cd frontend
        
        if [ -f "package.json" ]; then
            if npm install --silent 2>/dev/null; then
                log_success "Frontend dependencies installed"
                
                # Test build
                if npm run build >/dev/null 2>&1; then
                    log_success "Frontend build test passed"
                else
                    log_warning "Frontend build test failed (may need configuration)"
                fi
            else
                log_warning "Frontend dependency installation failed"
            fi
        else
            log_warning "No package.json found in frontend directory"
        fi
        
        cd ..
    fi
}

run_tests() {
    log_info "Running verification tests..."
    
    if pytest tests/ --tb=short -q --disable-warnings 2>/dev/null; then
        log_success "All tests passed"
    else
        log_warning "Some tests failed (check configuration if needed)"
    fi
}

show_success_message() {
    echo
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   🎉 Setup Complete! 🎉                     ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo
    echo -e "  ${GREEN}1. Activate environment:${NC}"
    echo -e "     ${YELLOW}source venv/bin/activate${NC}"
    echo
    echo -e "  ${GREEN}2. Start the API server:${NC}"
    echo -e "     ${YELLOW}fpl-toolkit serve --reload${NC}"
    echo
    echo -e "  ${GREEN}3. Start Streamlit dashboard:${NC}"
    echo -e "     ${YELLOW}fpl-toolkit streamlit${NC}"
    
    if [[ "$NODE_AVAILABLE" == "true" ]] && [ -d "frontend" ]; then
        echo
        echo -e "  ${GREEN}4. Start frontend (optional):${NC}"
        echo -e "     ${YELLOW}cd frontend && npm run dev${NC}"
    fi
    
    echo
    echo -e "${BLUE}🛠️ Available Commands:${NC}"
    echo -e "  ${YELLOW}fpl-toolkit --help${NC}          # Show all CLI commands"
    echo -e "  ${YELLOW}fpl-toolkit serve${NC}           # Start FastAPI server"
    echo -e "  ${YELLOW}fpl-toolkit streamlit${NC}       # Start Streamlit app"
    echo -e "  ${YELLOW}fpl-toolkit init${NC}            # Initialize database"
    echo -e "  ${YELLOW}pytest${NC}                      # Run tests"
    echo -e "  ${YELLOW}black src/ tests/${NC}          # Format code"
    echo -e "  ${YELLOW}ruff check src/ tests/${NC}     # Lint code"
    echo
    echo -e "${BLUE}🌐 Access Points:${NC}"
    echo -e "  ${YELLOW}API:${NC}        http://localhost:8000"
    echo -e "  ${YELLOW}Docs:${NC}       http://localhost:8000/docs"
    echo -e "  ${YELLOW}Streamlit:${NC}  http://localhost:8501"
    
    if [[ "$NODE_AVAILABLE" == "true" ]] && [ -d "frontend" ]; then
        echo -e "  ${YELLOW}Frontend:${NC}   http://localhost:3000"
    fi
    
    echo
    echo -e "${BLUE}📚 Documentation:${NC} ${YELLOW}Documentation/README.md${NC}"
    echo
}

# Main execution
main() {
    echo -e "${BLUE}🚀 Starting intelligent setup process...${NC}"
    echo
    
    # Parse arguments
    FORCE_AI=false
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force-ai)
                FORCE_AI=true
                shift
                ;;
            --help|-h)
                echo "FPL Toolkit Setup Script"
                echo ""
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --force-ai    Force AI dependency installation (even if detection fails)"
                echo "  --help, -h    Show this help message"
                echo ""
                exit 0
                ;;
            *)
                log_warning "Unknown option: $1"
                shift
                ;;
        esac
    done
    
    # Check prerequisites
    check_python
    NODE_AVAILABLE=$(check_node && echo "true" || echo "false")
    
    # Setup Python environment
    setup_python_env
    
    # Install dependencies
    if [[ "$FORCE_AI" == "true" ]]; then
        install_dependencies --force-ai
    else
        install_dependencies
    fi
    
    # Setup configuration
    setup_configuration
    
    # Initialize database
    initialize_database
    
    # Setup frontend if available
    setup_frontend
    
    # Run verification tests
    run_tests
    
    # Show success message
    show_success_message
}

# Run main function with all arguments
main "$@"
