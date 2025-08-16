# Troubleshooting Guide

Comprehensive troubleshooting guide for common issues and their solutions.

## 🔧 Installation Issues

### Python Environment Problems

**Issue**: `Python 3.10+ required` error
```bash
❌ Python 3.10+ required. Found: 3.8
```

**Solutions**:
1. **Update Python** (Recommended):
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install python3.11 python3.11-venv
   
   # macOS with Homebrew
   brew install python@3.11
   
   # Windows - Download from python.org
   ```

2. **Use pyenv** for version management:
   ```bash
   # Install pyenv
   curl https://pyenv.run | bash
   
   # Install Python 3.11
   pyenv install 3.11.0
   pyenv local 3.11.0
   ```

**Issue**: Virtual environment creation fails
```bash
❌ Failed to create virtual environment
```

**Solutions**:
```bash
# Ensure venv module is available
python3 -m pip install --user virtualenv

# Alternative: use virtualenv directly
python3 -m virtualenv venv

# If permissions issue
sudo chown -R $USER:$USER .
```

### Dependency Installation Problems

**Issue**: AI dependencies fail to install
```bash
❌ Failed to install sentence-transformers
```

**Solutions**:
1. **Install without AI first**:
   ```bash
   pip install -e ".[dev,web,postgresql]"
   # Add AI later: pip install -e ".[ai]"
   ```

2. **Platform-specific solutions**:
   ```bash
   # macOS M1/M2 (Apple Silicon)
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   
   # Linux with limited resources
   pip install sentence-transformers --no-deps
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

3. **Memory constraints**:
   ```bash
   # Install with minimal cache
   pip install --no-cache-dir -e ".[ai]"
   
   # Or use swap space
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

**Issue**: PostgreSQL dependencies fail
```bash
❌ Failed to install psycopg2-binary
```

**Solutions**:
```bash
# Install system dependencies first
# Ubuntu/Debian
sudo apt-get install libpq-dev python3-dev

# macOS
brew install postgresql

# CentOS/RHEL
sudo yum install postgresql-devel python3-devel

# Then install Python package
pip install psycopg2-binary
```

## 🗄️ Database Issues

### Connection Problems

**Issue**: Database connection refused
```bash
❌ could not connect to server: Connection refused
```

**Solutions**:
1. **Check PostgreSQL status**:
   ```bash
   # Check if PostgreSQL is running
   sudo systemctl status postgresql
   
   # Start if not running
   sudo systemctl start postgresql
   ```

2. **Verify connection string**:
   ```bash
   # Test connection manually
   psql $DATABASE_URL -c "SELECT 1;"
   
   # Check environment variable
   echo $DATABASE_URL
   ```

3. **Fallback to SQLite**:
   ```bash
   # Remove PostgreSQL URL to use SQLite
   unset DATABASE_URL
   # Or comment out in .env file
   ```

**Issue**: Database permission denied
```bash
❌ FATAL: permission denied for database
```

**Solutions**:
```bash
# Create user and database
sudo -u postgres createuser --interactive $USER
sudo -u postgres createdb fpl_toolkit -O $USER

# Grant permissions
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fpl_toolkit TO $USER;"
```

### Migration Issues

**Issue**: Database schema outdated
```bash
❌ Table 'players' doesn't exist
```

**Solutions**:
```bash
# Reset and reinitialize database
fpl-toolkit init --reset

# Or manually drop and recreate
rm fpl_toolkit.db  # For SQLite
fpl-toolkit init
```

**Issue**: Data corruption
```bash
❌ Database is malformed
```

**Solutions**:
```bash
# SQLite repair
sqlite3 fpl_toolkit.db ".recover" | sqlite3 fpl_toolkit_repaired.db
mv fpl_toolkit_repaired.db fpl_toolkit.db

# PostgreSQL repair
pg_dump $DATABASE_URL > backup.sql
dropdb fpl_toolkit && createdb fpl_toolkit
psql $DATABASE_URL < backup.sql
```

## 🌐 API & Server Issues

### Server Won't Start

**Issue**: Port already in use
```bash
❌ Error: [Errno 48] Address already in use
```

**Solutions**:
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
fpl-toolkit serve --port 8080

# Check what's using the port
netstat -tulpn | grep 8000
```

**Issue**: Import errors on startup
```bash
❌ ModuleNotFoundError: No module named 'src.fpl_toolkit'
```

**Solutions**:
```bash
# Ensure you're in the right directory
cd /path/to/Fpl-toolkit

# Activate virtual environment
source venv/bin/activate

# Reinstall in development mode
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

### API Connection Issues

**Issue**: FPL API rate limiting
```bash
❌ HTTP 429: Too Many Requests
```

**Solutions**:
```bash
# Wait and retry (automatic in client)
# Check cache status
fpl-toolkit cache-status

# Clear cache if needed
fpl-toolkit cache-clear

# Reduce request frequency
export CACHE_TTL_SECONDS=7200  # 2 hours
```

**Issue**: FPL API timeout
```bash
❌ Request timeout after 30 seconds
```

**Solutions**:
```bash
# Check internet connection
curl -I https://fantasy.premierleague.com/api/bootstrap-static/

# Try with increased timeout
export FPL_API_TIMEOUT=60

# Use cached data if available
fpl-toolkit serve --use-cache-only
```

### CORS Issues

**Issue**: Frontend can't connect to API
```bash
❌ Access to fetch blocked by CORS policy
```

**Solutions**:
1. **Development setup**:
   ```bash
   # Start API with CORS enabled
   fpl-toolkit serve --cors-allow-all
   
   # Or set specific origins
   export CORS_ORIGINS=http://localhost:3000,http://localhost:8501
   ```

2. **Production setup**:
   ```python
   # In production config
   CORS_ORIGINS = [
       "https://your-frontend.vercel.app",
       "https://your-domain.com"
   ]
   ```

## 🎨 Frontend Issues

### Next.js Build Problems

**Issue**: Build fails with TypeScript errors
```bash
❌ Type error: Property 'xxx' does not exist
```

**Solutions**:
```bash
# Update API types
cd frontend
npm run generate-types

# Check TypeScript config
npx tsc --noEmit

# Skip type checking for emergency build
npm run build -- --no-type-check
```

**Issue**: Environment variables not loaded
```bash
❌ NEXT_PUBLIC_API_URL is undefined
```

**Solutions**:
```bash
# Check environment file exists
ls frontend/.env.local

# Verify variable names start with NEXT_PUBLIC_
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local

# Restart development server
cd frontend && npm run dev
```

### Streamlit Issues

**Issue**: Streamlit won't start
```bash
❌ ModuleNotFoundError: No module named 'streamlit'
```

**Solutions**:
```bash
# Install streamlit
pip install streamlit

# Or install with web dependencies
pip install -e ".[web]"

# Check installation
streamlit --version
```

**Issue**: Streamlit cache errors
```bash
❌ StreamlitAPIException: st.cache is deprecated
```

**Solutions**:
```bash
# Clear Streamlit cache
streamlit cache clear

# Update to latest version
pip install --upgrade streamlit

# Check for deprecated functions
grep -r "st\.cache" streamlit_app.py
```

## 🤖 AI Feature Issues

### Model Loading Problems

**Issue**: AI models won't download
```bash
❌ Failed to download sentence-transformers model
```

**Solutions**:
```bash
# Check internet connection
curl -I https://huggingface.co/

# Download manually
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Model downloaded successfully')
"

# Use offline mode if needed
export TRANSFORMERS_OFFLINE=1
```

**Issue**: Out of memory during AI processing
```bash
❌ RuntimeError: CUDA out of memory
```

**Solutions**:
```bash
# Force CPU usage
export CUDA_VISIBLE_DEVICES=""

# Reduce batch size
export AI_BATCH_SIZE=1

# Use lightweight models
export AI_MODEL_NAME="all-MiniLM-L6-v2"  # Smaller model
```

### AI Features Disabled

**Issue**: AI features not available
```bash
⚠️ AI features disabled - install dependencies
```

**Solutions**:
```bash
# Install AI dependencies
pip install -e ".[ai]"

# Verify installation
python -c "
try:
    from sentence_transformers import SentenceTransformer
    print('✅ AI features available')
except ImportError:
    print('❌ AI features unavailable')
"

# Check which specific package is missing
python -c "
try:
    import torch
    print('✅ PyTorch available')
except ImportError:
    print('❌ PyTorch missing')
    
try:
    import transformers
    print('✅ Transformers available')
except ImportError:
    print('❌ Transformers missing')
"
```

## 🐳 Docker Issues

### Build Problems

**Issue**: Docker build fails
```bash
❌ failed to solve with frontend dockerfile.v0
```

**Solutions**:
```bash
# Clean Docker cache
docker system prune -a

# Build with no cache
docker build --no-cache -t fpl-toolkit .

# Check for syntax errors
docker build --dry-run -t fpl-toolkit .
```

**Issue**: Container won't start
```bash
❌ Error: No such file or directory
```

**Solutions**:
```bash
# Check file permissions
ls -la scripts/setup.sh
chmod +x scripts/setup.sh

# Verify base image
docker pull python:3.11-slim

# Run with debug
docker run -it fpl-toolkit /bin/bash
```

### Container Runtime Issues

**Issue**: Database connection from container
```bash
❌ Connection refused to localhost:5432
```

**Solutions**:
```bash
# Use host networking
docker run --network host fpl-toolkit

# Or use docker-compose
docker-compose up

# Connect to host database
export DATABASE_URL=postgresql://user:pass@host.docker.internal:5432/db
```

## 🔍 Performance Issues

### Slow Response Times

**Issue**: API responses taking too long
```bash
⚠️ Request took 15 seconds
```

**Solutions**:
```bash
# Check cache status
curl http://localhost:8000/cache-stats

# Enable query logging
export DEBUG=true
fpl-toolkit serve --debug

# Profile slow queries
pip install line_profiler
kernprof -l -v src/fpl_toolkit/analysis/projections.py
```

**Issue**: High memory usage
```bash
⚠️ Memory usage: 2GB+
```

**Solutions**:
```bash
# Monitor memory usage
top -p $(pgrep -f "fpl-toolkit")

# Reduce cache size
export CACHE_SIZE=50  # Default: 100

# Use pagination for large queries
fpl-toolkit players --limit 20

# Clear caches periodically
fpl-toolkit cache-clear
```

### Frontend Performance

**Issue**: Slow page loads
```bash
⚠️ First contentful paint: 5s
```

**Solutions**:
```bash
# Build with optimization
cd frontend
npm run build
npm run start

# Check bundle size
npm run analyze

# Optimize images
npm install next-optimized-images
```

## 🔒 Security Issues

### Authentication Problems

**Issue**: API key authentication failing
```bash
❌ Invalid API key
```

**Solutions**:
```bash
# Check API key format
echo $FPL_API_KEY | wc -c

# Regenerate API key
fpl-toolkit generate-api-key

# Use environment variable
export FPL_API_KEY=your_key_here
```

### HTTPS Certificate Issues

**Issue**: SSL certificate verification failed
```bash
❌ SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions**:
```bash
# Update certificates
# macOS
/Applications/Python\ 3.11/Install\ Certificates.command

# Ubuntu
sudo apt-get update && sudo apt-get install ca-certificates

# Disable SSL verification (NOT recommended for production)
export PYTHONHTTPSVERIFY=0
```

## 📊 Data Issues

### Stale Data

**Issue**: Data seems outdated
```bash
⚠️ Last update: 2 days ago
```

**Solutions**:
```bash
# Force cache refresh
fpl-toolkit cache-refresh

# Check FPL API status
curl -I https://fantasy.premierleague.com/api/bootstrap-static/

# Manually update data
fpl-toolkit update-data --force
```

**Issue**: Missing player data
```bash
❌ Player 123 not found
```

**Solutions**:
```bash
# Refresh player database
fpl-toolkit sync-players

# Check FPL API directly
curl https://fantasy.premierleague.com/api/bootstrap-static/ | jq '.elements[] | select(.id==123)'

# Reset database if corrupted
fpl-toolkit init --reset
```

## 🆘 Emergency Procedures

### Complete Reset

When everything is broken:
```bash
# 1. Stop all services
pkill -f "fpl-toolkit"
pkill -f "streamlit"

# 2. Clean environment
rm -rf venv
rm fpl_toolkit.db
rm -rf __pycache__ .pytest_cache

# 3. Fresh install
git pull origin main
./scripts/setup.sh

# 4. Verify installation
pytest tests/ -v
```

### Backup & Recovery

**Create backup**:
```bash
# Database backup
cp fpl_toolkit.db fpl_toolkit_backup_$(date +%Y%m%d).db

# Configuration backup
cp .env .env.backup

# Code backup
git stash push -m "Backup before troubleshooting"
```

**Restore from backup**:
```bash
# Restore database
cp fpl_toolkit_backup_20240115.db fpl_toolkit.db

# Restore configuration
cp .env.backup .env

# Restore code
git stash pop
```

## 📞 Getting Additional Help

### Diagnostic Information

When reporting issues, include:
```bash
# System information
python --version
pip list | grep -E "(fpl|streamlit|fastapi)"
uname -a

# Application logs
fpl-toolkit serve --debug 2>&1 | tee debug.log

# Database status
fpl-toolkit db-status

# Cache status
fpl-toolkit cache-stats
```

### Support Channels

1. **GitHub Issues**: https://github.com/AmberMaze/Fpl-toolkit/issues
2. **Documentation**: Check all files in `Documentation/`
3. **Stack Overflow**: Tag your questions with `fpl-toolkit`
4. **Community Discord**: Join our community (link in README)

### Contributing Fixes

Found a solution? Help others:
1. Fork the repository
2. Add your fix to this troubleshooting guide
3. Submit a pull request
4. Help improve the documentation

---

*If you can't find a solution here, please [open an issue](https://github.com/AmberMaze/Fpl-toolkit/issues) with detailed error messages and system information.*