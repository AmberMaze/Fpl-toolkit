# Deployment Guide

Complete guide for deploying the FPL Toolkit to production environments.

## 🚀 Deployment Architecture

The FPL Toolkit uses a **dual-deployment strategy** optimized for modern cloud platforms:

```
┌─────────────────────────────────────────────────────────┐
│                    Production Setup                     │
├─────────────────────────────────────────────────────────┤
│  Frontend (Vercel)          Backend (Render/Railway)    │
│  ┌─────────────────┐        ┌─────────────────────────┐ │
│  │   Next.js App   │ ────── │   FastAPI + Database    │ │
│  │   Static CDN    │        │   Auto-scaling          │ │
│  │   Edge Runtime  │        │   Health Monitoring     │ │
│  └─────────────────┘        └─────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 🌐 Frontend Deployment (Next.js)

### Vercel Deployment (Recommended)

**Step 1: Repository Connection**
1. Connect your GitHub repository to Vercel
2. Select the `frontend` folder as the root directory
3. Vercel auto-detects Next.js configuration

**Step 2: Build Configuration**
```json
{
  "framework": "nextjs",
  "rootDirectory": "frontend",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install"
}
```

**Step 3: Environment Variables**
```bash
# Vercel Environment Variables
NEXT_PUBLIC_API_URL=https://your-backend-api.render.com
NEXT_PUBLIC_APP_NAME=FPL Toolkit
NEXT_PUBLIC_VERSION=1.0.0
```

**Step 4: Custom Domain (Optional)**
- Add your custom domain in Vercel dashboard
- Configure DNS records as instructed
- SSL certificates are automatic

### Alternative: Netlify Deployment

**netlify.toml** (create in frontend folder):
```toml
[build]
  base = "frontend"
  command = "npm run build"
  publish = ".next"

[[redirects]]
  from = "/api/*"
  to = "https://your-backend-api.render.com/api/:splat"
  status = 200

[build.environment]
  NEXT_PUBLIC_API_URL = "https://your-backend-api.render.com"
```

### Docker Deployment

**Frontend Dockerfile**:
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

## ⚡ Backend Deployment (FastAPI)

### Render Deployment (Recommended)

**Step 1: Create Web Service**
1. Connect GitHub repository to Render
2. Select "Web Service" type
3. Choose your repository and branch

**Step 2: Service Configuration**
```yaml
# render.yaml (in repository root)
services:
  - type: web
    name: fpl-toolkit-api
    env: python
    buildCommand: pip install -e ".[web,ai,postgresql]"
    startCommand: fpl-toolkit serve --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: DATABASE_URL
        fromDatabase:
          name: fpl-toolkit-db
          property: connectionString
      - key: CACHE_TTL_SECONDS
        value: 1800

databases:
  - name: fpl-toolkit-db
    databaseName: fpl_toolkit
    user: fpl_user
    region: oregon
```

**Step 3: Database Setup**
```bash
# Render automatically provides DATABASE_URL
# Format: postgresql://user:password@host:port/database
```

**Step 4: Environment Variables**
```bash
DATABASE_URL=postgresql://...  # Auto-provided by Render
CACHE_TTL_SECONDS=1800
ENABLE_ADVANCED_METRICS=true
PORT=8000  # Auto-provided by Render
```

### Railway Deployment

**Step 1: Connect Repository**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway new fpl-toolkit
railway link
railway up
```

**Step 2: Configuration**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "start": "fpl-toolkit serve --host 0.0.0.0 --port $PORT",
  "variables": {
    "PYTHON_VERSION": "3.11",
    "DATABASE_URL": "${{Postgres.DATABASE_URL}}",
    "CACHE_TTL_SECONDS": "1800"
  }
}
```

### Docker Deployment

**Production Dockerfile**:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python packages
COPY pyproject.toml .
RUN pip install -e ".[web,ai,postgresql]"

# Copy application code
COPY src/ src/
COPY tests/ tests/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["fpl-toolkit", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

## 🗄️ Database Deployment

### PostgreSQL on Render

**Automatic Setup**:
1. Create PostgreSQL database in Render dashboard
2. Database URL automatically provided to web service
3. Connection pooling and backups included

**Manual Configuration**:
```sql
-- Database initialization (automatic via render.yaml)
CREATE DATABASE fpl_toolkit;
CREATE USER fpl_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE fpl_toolkit TO fpl_user;
```

### PostgreSQL on Railway

```bash
# Add PostgreSQL plugin
railway add postgresql

# Database URL automatically available as $DATABASE_URL
```

### Supabase (Alternative)

**Setup**:
1. Create Supabase project
2. Get connection string from dashboard
3. Configure environment variable

```bash
DATABASE_URL=postgresql://postgres:password@db.project.supabase.co:5432/postgres
```

## 🐳 Docker Compose Deployment

**docker-compose.yml** (full stack):
```yaml
version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/fpl_toolkit
      - CACHE_TTL_SECONDS=1800
    depends_on:
      - db
    volumes:
      - ./src:/app/src

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=fpl_toolkit
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

**Deployment Commands**:
```bash
# Deploy full stack
docker-compose up -d

# Scale backend
docker-compose up -d --scale backend=3

# View logs
docker-compose logs -f backend

# Update deployment
docker-compose pull && docker-compose up -d
```

## 🔧 Environment Configuration

### Production Environment Variables

**Frontend (.env.production)**:
```bash
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_APP_NAME=FPL Toolkit
NEXT_PUBLIC_SENTRY_DSN=https://...  # Optional monitoring
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX     # Optional analytics
```

**Backend (.env.production)**:
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# API Configuration
CACHE_TTL_SECONDS=1800
ENABLE_ADVANCED_METRICS=true
MAX_WORKERS=4

# Optional: External Services
SENTRY_DSN=https://...              # Error monitoring
REDIS_URL=redis://...               # Enhanced caching
```

### Staging Environment

**Staging Setup**:
```bash
# Separate staging database
DATABASE_URL=postgresql://user:pass@staging-host:port/fpl_toolkit_staging

# Faster cache for testing
CACHE_TTL_SECONDS=300

# Debug mode
DEBUG=true
```

## 📊 Monitoring & Health Checks

### Health Endpoints

**Backend Health Check**:
```http
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "database": "connected",
  "cache": "operational"
}
```

**Frontend Health Check**:
```http
GET /api/health

Response:
{
  "status": "ok",
  "backend_api": "connected",
  "build_time": "2024-01-15T10:00:00Z"
}
```

### Monitoring Setup

**Uptime Monitoring** (UptimeRobot):
```bash
# Monitor these endpoints
https://your-frontend.vercel.app/api/health
https://your-backend.render.com/health
```

**Error Tracking** (Sentry):
```python
# Backend integration
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FastApiIntegration()]
)
```

```javascript
// Frontend integration
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
});
```

## 🚀 Performance Optimization

### CDN Configuration

**Vercel (Automatic)**:
- Global edge distribution
- Automatic image optimization
- Brotli compression

**Custom CDN (CloudFlare)**:
```javascript
// next.config.js
module.exports = {
  images: {
    domains: ['your-cdn.cloudflare.com'],
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
};
```

### Database Optimization

**Connection Pooling**:
```python
# Production database settings
DATABASE_URL=postgresql://user:pass@host:port/db?pool_size=20&max_overflow=30
```

**Query Optimization**:
```sql
-- Add indexes for common queries
CREATE INDEX idx_players_position ON players(position);
CREATE INDEX idx_gameweek_history_player_gw ON gameweek_history(player_id, gameweek);
CREATE INDEX idx_projections_player_gw ON projections(player_id, gameweek);
```

## 🔒 Security Configuration

### HTTPS & SSL

**Vercel**: Automatic HTTPS with custom domains
**Render**: Automatic SSL certificates
**Custom**: Use Let's Encrypt or CloudFlare

### CORS Configuration

```python
# Production CORS settings
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Rate Limiting

```python
# Production rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/players")
@limiter.limit("60/minute")
async def get_players(request: Request):
    # Implementation
    pass
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Update version numbers
- [ ] Run full test suite
- [ ] Test on staging environment
- [ ] Backup existing data
- [ ] Review environment variables

### Backend Deployment
- [ ] Deploy database migrations
- [ ] Deploy backend service
- [ ] Verify health endpoints
- [ ] Test API functionality
- [ ] Monitor error rates

### Frontend Deployment
- [ ] Update API endpoints
- [ ] Deploy frontend application
- [ ] Test user flows
- [ ] Verify mobile responsiveness
- [ ] Check performance metrics

### Post-Deployment
- [ ] Monitor application metrics
- [ ] Verify all integrations
- [ ] Test critical user paths
- [ ] Update documentation
- [ ] Notify users of updates

## 🆘 Troubleshooting

### Common Issues

**Build Failures**:
```bash
# Clear cache and rebuild
npm ci
npm run build

# Check Node.js version
node --version  # Should be 18+
```

**Database Connection**:
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Check environment variables
echo $DATABASE_URL
```

**API Connectivity**:
```bash
# Test health endpoint
curl https://your-api.render.com/health

# Check CORS configuration
curl -H "Origin: https://your-frontend.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS https://your-api.render.com/players
```

### Rollback Procedures

**Frontend Rollback**:
```bash
# Vercel: Use dashboard to rollback to previous deployment
# Or redeploy specific commit
vercel --prod --force
```

**Backend Rollback**:
```bash
# Render: Use dashboard to rollback
# Or deploy specific commit
git checkout previous-working-commit
git push origin main
```

---

*For ongoing maintenance and updates, see [Best Practices](./Best-Practices.md). For troubleshooting, see [Troubleshooting](./Troubleshooting.md).*