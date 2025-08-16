# Setup & Installation Guide

Complete guide to setting up the FPL Toolkit for development and production use.

## 🚀 Quick Setup

### Prerequisites

- **Python 3.10+** (3.11+ recommended)
- **Node.js 18+** (for frontend development)
- **Git** for version control

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/AmberMaze/Fpl-toolkit.git
cd Fpl-toolkit

# Run the intelligent setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The setup script will automatically:
- ✅ Create virtual environment
- ✅ Install all dependencies (core, web, AI if available)
- ✅ Initialize database
- ✅ Create `.env` configuration
- ✅ Run tests to verify setup

## 📦 Installation Options

### Core Installation (Minimal)

For basic FPL analysis without AI features:

```bash
pip install -e ".[dev,web,postgresql]"
```

### Full Installation (AI Included)

For complete functionality with AI/ML features:

```bash
pip install -e ".[dev,web,ai,postgresql]"
```

### Frontend Development

For Next.js frontend development:

```bash
cd frontend
npm install
npm run dev  # Development server at localhost:3000
```

## 🔧 Manual Setup

If you prefer manual setup or need troubleshooting:

### 1. Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip
```

### 2. Install Dependencies

```bash
# Choose your installation level
pip install -e ".[dev]"                    # Basic development
pip install -e ".[dev,web]"                # + Web interface
pip install -e ".[dev,web,ai]"             # + AI features
pip install -e ".[dev,web,ai,postgresql]"  # + PostgreSQL support
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (optional)
nano .env
```

### 4. Initialize Database

```bash
# Initialize SQLite database (default)
python -m fpl_toolkit.cli init

# Or use PostgreSQL (if DATABASE_URL is set)
export DATABASE_URL="postgresql://user:pass@localhost/fpldb"
python -m fpl_toolkit.cli init
```

## 🗄️ Database Options

### SQLite (Default)

Automatic setup - no configuration needed. Perfect for:
- Local development
- Small deployments
- Testing

### PostgreSQL (Production)

For production deployments:

```bash
# Set DATABASE_URL in .env
DATABASE_URL=postgresql://username:password@localhost:5432/fpl_toolkit

# Install with PostgreSQL support
pip install -e ".[postgresql]"

# Initialize
fpl-toolkit init
```

## 🚀 Development Environment

### VS Code Setup

The repository includes complete VS Code configuration:

- **25 recommended extensions** for Python, AI, web development
- **15 development tasks** for build, test, format, serve
- **8 debug configurations** for comprehensive debugging
- **Custom settings** optimized for the project

Open in VS Code and install recommended extensions for the best experience.

### Development Commands

```bash
# Activate environment (if not already active)
source venv/bin/activate

# Start FastAPI server (auto-reload)
fpl-toolkit serve --reload

# Start Streamlit interface
fpl-toolkit streamlit

# Start Next.js frontend
cd frontend && npm run dev

# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/ --fix

# Type checking
mypy src/
```

## 🐳 Docker Setup

For containerized deployment:

```bash
# Build image
docker build -t fpl-toolkit .

# Run container
docker run -p 8000:8000 fpl-toolkit

# With environment variables
docker run -p 8000:8000 -e DATABASE_URL=postgresql://... fpl-toolkit
```

## 🌐 Vercel Deployment

### Frontend Deployment

1. **Connect Repository**: Link your GitHub repository to Vercel
2. **Configure Build**:
   - Framework Preset: **Next.js**
   - Root Directory: **frontend**
   - Build Command: `npm run build`
   - Output Directory: `.next`

3. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-api.render.com
   ```

### Backend Deployment (Render)

1. **Create Web Service** on Render
2. **Build Command**: `pip install -e ".[web,ai,postgresql]"`
3. **Start Command**: `fpl-toolkit serve --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   ```
   DATABASE_URL=postgresql://...
   PYTHON_VERSION=3.11
   ```

## ⚠️ Common Issues

### Import Errors

```bash
# Ensure proper installation
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

### Database Connection

```bash
# Reset database
rm fpl_toolkit.db
fpl-toolkit init

# Check PostgreSQL connection
psql $DATABASE_URL -c "SELECT 1;"
```

### AI Features Not Available

```bash
# Install AI dependencies
pip install -e ".[ai]"

# Verify installation
python -c "from sentence_transformers import SentenceTransformer; print('AI Ready')"
```

## 📋 Verification

Test your installation:

```bash
# Check CLI
fpl-toolkit --help

# Test API
fpl-toolkit serve &
curl http://localhost:8000/health

# Test AI (if installed)
python -c "from src.fpl_toolkit.ai.advisor import FPLAdvisor; print('AI Available')"

# Run test suite
pytest tests/ -v
```

## 🔍 Next Steps

After successful setup:

1. 📖 Read the [**Quick Start Guide**](./Quick-Start.md)
2. 🎯 Explore [**Features**](./Features.md)
3. 🛠️ Check [**API Reference**](./API-Reference.md)
4. 🚀 Plan your [**Deployment**](./Deployment.md)

---

*Need help? Check [Troubleshooting](./Troubleshooting.md) or [open an issue](https://github.com/AmberMaze/Fpl-toolkit/issues).*