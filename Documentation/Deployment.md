# Personal Deployment Guide

Complete guide for deploying the FPL Toolkit to free hosting platforms for personal use with tyshub.xyz domain.

## 🚀 Personal Deployment Strategy

The FPL Toolkit is optimized for **free hosting solutions** perfect for personal use:

```
┌─────────────────────────────────────────────────────────┐
│                Personal Hosting Setup                   │
├─────────────────────────────────────────────────────────┤
│  Frontend (Free Hosting)        Backend (Free Hosting)  │
│  ┌─────────────────┐           ┌─────────────────────┐  │
│  │  tyshub.xyz     │  ──────── │   Railway/Render    │  │
│  │  Cloudflare     │           │   Free PostgreSQL   │  │
│  │  Vercel/Netlify │           │   Auto-deploy      │  │
│  └─────────────────┘           └─────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 🌐 Frontend Deployment Options

### Option 1: Cloudflare Pages (Recommended for tyshub.xyz)

**Why Cloudflare Pages?**
- ✅ **Unlimited builds** (no build minute limits like Netlify)
- ✅ **Free custom domain** (perfect for tyshub.xyz)
- ✅ **Global CDN** with excellent performance
- ✅ **Free SSL** certificates
- ✅ **Edge workers** for advanced functionality

**Setup Steps:**
1. **Connect Repository**: Link your GitHub repo to Cloudflare Pages
2. **Build Configuration**:
   ```bash
   Build command: cd frontend && npm run build
   Build output directory: frontend/.next
   Root directory: frontend
   ```
3. **Custom Domain Setup**:
   - In Cloudflare Pages dashboard, add custom domain: `tyshub.xyz`
   - In Porkbun DNS settings, add CNAME record:
     ```
     CNAME  @  your-project.pages.dev
     ```

**Environment Variables**:
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_APP_NAME=FPL Toolkit
NODE_VERSION=18
```

### Option 2: Vercel (Good alternative)

**Pros**: Excellent Next.js integration, automatic deployments
**Cons**: Build time limits on free tier (100 hours/month - should be sufficient for personal use)

**Setup**:
```json
{
  "framework": "nextjs",
  "rootDirectory": "frontend",
  "buildCommand": "npm run build",
  "outputDirectory": ".next"
}
```

**Custom Domain (tyshub.xyz)**:
1. Add domain in Vercel dashboard
2. Update DNS at Porkbun:
   ```
   CNAME  @  cname.vercel-dns.com
   ```

### Option 3: Netlify (Backup option)

**Limitation**: 300 build minutes/month on free tier
**Best for**: Static sites with infrequent updates

**netlify.toml**:
```toml
[build]
  base = "frontend"
  command = "npm run build"
  publish = ".next"
```

## ⚡ Backend Deployment (Free Hosting)

### Railway (Recommended for Personal Use)

**Why Railway?**
- ✅ **$5/month free credits** (enough for personal use)
- ✅ **Automatic PostgreSQL** database included
- ✅ **Zero configuration** deployment
- ✅ **GitHub integration** with auto-deploys
- ✅ **Better reliability** than free Render tier

**Setup Steps:**
1. **Connect Repository**:
   ```bash
   # Install Railway CLI (optional)
   npm install -g @railway/cli
   
   # Or use web dashboard
   # Connect GitHub repo at railway.app
   ```

2. **Configuration**:
   Railway auto-detects Python projects. Create `railway.toml`:
   ```toml
   [build]
   builder = "NIXPACKS"
   
   [deploy]
   startCommand = "fpl-toolkit serve --host 0.0.0.0 --port $PORT"
   
   [env]
   PYTHON_VERSION = "3.11"
   ```

3. **Database**: Railway automatically provides PostgreSQL
4. **Environment Variables** (auto-configured):
   ```bash
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   PORT=${{PORT}}
   CACHE_TTL_SECONDS=1800
   ```

### Render (Alternative Free Option)

**Free Tier Limitations**: 
- ✅ Free tier available
- ⚠️ **Spins down after 15 mins** of inactivity (slow cold starts)
- ⚠️ **750 hours/month limit** (may not be enough for always-on)

**Setup Only if Railway Credits Run Out**:
```yaml
# render.yaml
services:
  - type: web
    name: fpl-toolkit-api
    env: python
    buildCommand: pip install -e ".[web,ai,postgresql]"
    startCommand: fpl-toolkit serve --host 0.0.0.0 --port $PORT
    plan: free  # Limited but functional
```

### Fly.io (Another Alternative)

**Free Tier**: 
- ✅ **3 VMs** with 256MB RAM each
- ✅ **3GB storage** included
- ✅ **Always-on capability**

**Setup**:
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

## 🗄️ Database Options (Free)

### Railway PostgreSQL (Included)
- ✅ **Automatic with Railway** backend deployment
- ✅ **No separate setup** required
- ✅ **Reliable and fast**

### Supabase (Alternative)
- ✅ **500MB free database**
- ✅ **Real-time features** (if needed later)
- ✅ **Excellent dashboard**

**Setup**:
```bash
# Connection string from Supabase dashboard
DATABASE_URL=postgresql://postgres:password@db.project.supabase.co:5432/postgres
```

### PlanetScale (Alternative)
- ✅ **10GB free storage**
- ✅ **Serverless MySQL**
- ✅ **Branching feature** for development

## 📱 tyshub.xyz Domain Configuration

### DNS Setup at Porkbun

**For Cloudflare Pages (Recommended)**:
```bash
# In Porkbun DNS management:
Type: CNAME
Name: @
Content: your-project.pages.dev
TTL: Auto
```

**For Vercel**:
```bash
# In Porkbun DNS management:
Type: CNAME  
Name: @
Content: cname.vercel-dns.com
TTL: Auto
```

**Subdomain for API** (optional):
```bash
# If you want api.tyshub.xyz for backend
Type: CNAME
Name: api
Content: your-backend.railway.app
TTL: Auto
```

### SSL Configuration
- **Cloudflare Pages**: Automatic SSL
- **Vercel**: Automatic SSL  
- **All platforms**: Free Let's Encrypt certificates

## 🐳 Local Docker Development

**docker-compose.yml** (for local development):
```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./fpl_toolkit.db
      - CACHE_TTL_SECONDS=300
    volumes:
      - ./src:/app/src

  # Optional: Local PostgreSQL for development
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=fpl_toolkit
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Run locally**:
```bash
# Full stack development
docker-compose up -d

# Just backend with SQLite
docker-compose up backend
```

## 🔧 Environment Configuration

### Personal Production Environment

**Frontend (.env.production)**:
```bash
# tyshub.xyz frontend configuration
NEXT_PUBLIC_API_URL=https://api.tyshub.xyz
NEXT_PUBLIC_APP_NAME=Personal FPL Toolkit
NEXT_PUBLIC_DOMAIN=tyshub.xyz
```

**Backend (.env.production)**:
```bash
# Personal backend configuration
DATABASE_URL=postgresql://...  # From Railway/Supabase
CACHE_TTL_SECONDS=1800
ENABLE_ADVANCED_METRICS=true

# Personal settings
MAX_WORKERS=2  # Lower for personal use
DEBUG=false
CORS_ORIGINS=https://tyshub.xyz,https://www.tyshub.xyz
```

### Local Development Environment

**Setup for Development**:
```bash
# .env.local
DATABASE_URL=sqlite:///./fpl_toolkit.db
CACHE_TTL_SECONDS=300  # Faster refresh for development
DEBUG=true
CORS_ORIGINS=http://localhost:3000
```

## 📊 Personal Monitoring

### Free Monitoring Options

**UptimeRobot** (Free tier):
- ✅ **50 monitors free**
- ✅ **5-minute interval**
- ✅ **Email/SMS alerts**

**Setup**:
```bash
# Monitor these endpoints
https://tyshub.xyz/api/health
https://your-backend.railway.app/health
```

**BetterUptime** (Alternative):
- ✅ **10 monitors free**
- ✅ **1-minute interval**
- ✅ **Status page included**

### Simple Health Checks

**Backend Health**:
```http
GET /health
Response: {"status": "healthy", "database": "connected"}
```

**Frontend Health**:
```http
GET /api/health  
Response: {"status": "ok", "backend_api": "connected"}
```

## 🚀 Personal Deployment Workflow

### Recommended Setup Process

1. **Backend First** (Railway):
   ```bash
   # Connect GitHub repo to Railway
   # Railway auto-deploys on push to main
   # Note the provided URL: https://your-app.railway.app
   ```

2. **Frontend Second** (Cloudflare Pages):
   ```bash
   # Connect GitHub repo to Cloudflare Pages
   # Set environment: NEXT_PUBLIC_API_URL=https://your-app.railway.app
   # Connect custom domain: tyshub.xyz
   ```

3. **DNS Configuration** (Porkbun):
   ```bash
   # CNAME @ -> your-project.pages.dev
   # Optional: CNAME api -> your-app.railway.app
   ```

### Automated Deployment

**GitHub Actions** (optional, for advanced users):
```yaml
# .github/workflows/deploy.yml
name: Deploy to Personal Hosting

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: |
          # Railway auto-deploys via webhook
          echo "Railway handles backend deployment"
      - name: Deploy to Cloudflare Pages
        run: |
          # Cloudflare Pages auto-deploys via GitHub integration
          echo "Cloudflare Pages handles frontend deployment"
```

## 🔒 Personal Security

### Basic Security Setup

**HTTPS Everywhere**:
- ✅ Cloudflare Pages: Automatic HTTPS
- ✅ Railway: Automatic SSL
- ✅ Custom domain: Automatic certificates

**Environment Security**:
```bash
# Never commit these to GitHub
DATABASE_URL=...
API_KEYS=...

# Use platform environment variables instead
```

**Rate Limiting** (for personal use):
```python
# Gentle rate limiting for personal usage
@limiter.limit("300/minute")  # Generous for personal use
async def get_players(request: Request):
    pass
```

## 📋 Personal Deployment Checklist

### Pre-Deployment
- [ ] Test locally with `docker-compose up`
- [ ] Verify environment variables
- [ ] Test with sample FPL data
- [ ] Check mobile responsiveness

### Deployment Steps
- [ ] Deploy backend to Railway
- [ ] Verify backend health endpoint
- [ ] Deploy frontend to Cloudflare Pages
- [ ] Configure tyshub.xyz domain
- [ ] Test full application flow

### Post-Deployment
- [ ] Set up basic monitoring (UptimeRobot)
- [ ] Test from different devices
- [ ] Verify SSL certificates
- [ ] Create backup of database connection info

## 🆘 Personal Troubleshooting

### Common Issues

**Domain Not Working**:
```bash
# Check DNS propagation
dig tyshub.xyz
nslookup tyshub.xyz

# Verify CNAME in Porkbun dashboard
```

**API Connection Issues**:
```bash
# Test backend directly
curl https://your-app.railway.app/health

# Check CORS settings
curl -H "Origin: https://tyshub.xyz" -X OPTIONS https://your-app.railway.app/players
```

**Database Connection**:
```bash
# Test database connection
psql $DATABASE_URL -c "SELECT 1;"
```

### Quick Fixes

**Backend Down**: Railway free tier may pause - visit URL to wake up
**Slow Loading**: Clear CDN cache in Cloudflare dashboard
**Build Failed**: Check Node.js version (18+) and dependencies

---

*This deployment guide focuses on free hosting solutions perfect for personal use. The tyshub.xyz domain provides a professional touch while keeping costs minimal. For iOS app preparation, the API structure is ready for mobile development.*