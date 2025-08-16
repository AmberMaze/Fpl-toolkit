# Technical Stack

Comprehensive overview of the FPL Toolkit's architecture, technology choices, and implementation patterns.

## 🏗️ Architecture Overview

The FPL Toolkit follows a **layered architecture** with optional dependencies and graceful fallbacks:

```
┌─────────────────────────────────────────────────────┐
│                  Frontend Layer                     │
│  ┌─────────────────┐    ┌─────────────────────────┐ │
│  │   Next.js App   │    │   Streamlit Dashboard   │ │
│  │   (Vercel)      │    │   (Local/Render)        │ │
│  └─────────────────┘    └─────────────────────────┘ │
└─────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────┐
│                  Service Layer                      │
│  ┌─────────────────────────────────────────────────┐ │
│  │           FastAPI REST API                      │ │
│  │  • Team-centric endpoints                       │ │
│  │  • Mobile-optimized responses                   │ │
│  │  • Dependency injection                         │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────┐
│                 Analysis Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Projections │  │  Decisions  │  │   Fixtures  │  │
│  │   Module    │  │   Module    │  │   Module    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────┐
│                   AI Layer                          │
│  ┌─────────────────────────────────────────────────┐ │
│  │           FPL Advisor                           │ │
│  │  • Heuristic recommendations                    │ │
│  │  • Optional ML models                           │ │
│  │  • Graceful degradation                         │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────┐
│                  API Layer                          │
│  ┌─────────────────────────────────────────────────┐ │
│  │           FPL Client                            │ │
│  │  • Automatic caching (1hr TTL)                  │ │
│  │  • Rate limiting protection                     │ │
│  │  • Context manager pattern                      │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────┐
│                Database Layer                       │
│  ┌─────────────┐              ┌─────────────────┐   │
│  │   SQLite    │    ────►     │   PostgreSQL    │   │
│  │  (Default)  │              │  (Production)   │   │
│  └─────────────┘              └─────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## 🚀 Frontend Technologies

### Next.js Application

**Framework**: Next.js 14 with App Router
- **TypeScript**: Full type safety across the application
- **Tailwind CSS**: Utility-first styling with custom FPL theme
- **React 18**: Modern React with server components
- **API Integration**: Type-safe client for Python backend

**Key Features**:
- Server-side rendering (SSR) for performance
- Static generation for marketing pages
- Mobile-first responsive design
- Glass-morphism UI effects
- Progressive Web App (PWA) ready

**Deployment**: 
- **Platform**: Vercel (recommended)
- **Build**: Standalone output for optimization
- **CDN**: Global edge distribution
- **Environment**: Production/staging configurations

### Streamlit Dashboard

**Framework**: Streamlit with custom styling
- **Plotly**: Interactive charts and visualizations
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Custom CSS**: FPL-branded professional styling

**Key Features**:
- Real-time data updates
- Interactive player comparisons
- AI-powered recommendations
- Mobile-responsive layouts
- Export capabilities (CSV, PNG)

## ⚡ Backend Technologies

### FastAPI Service Layer

**Framework**: FastAPI with async/await
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: ORM with async support
- **Dependency Injection**: Clean separation of concerns
- **OpenAPI**: Automatic documentation generation

**Key Patterns**:
```python
# Context manager for resource management
with FPLClient() as client:
    players = client.get_players()

# Dependency injection
@app.get("/players")
async def get_players(
    client: FPLClient = Depends(get_fpl_client),
    db: Session = Depends(get_session)
):
    return await client.get_players()
```

### Analysis Layer

**Core Modules**:

1. **Projections** (`projections.py`)
   - Statistical models for player performance prediction
   - Form analysis and trend detection
   - Confidence scoring algorithms

2. **Decisions** (`decisions.py`)  
   - Transfer scenario analysis
   - Captain choice optimization
   - Budget allocation strategies

3. **Fixtures** (`fixtures.py`)
   - Difficulty rating algorithms
   - Schedule analysis
   - Home/away advantage calculations

**Mathematical Models**:
- **Form Weighting**: Recent performance exponential decay
- **Fixture Difficulty**: Team strength differential analysis
- **Expected Values**: xG/xA integration with FPL scoring
- **Confidence Scoring**: Multi-factor reliability assessment

### AI & Machine Learning

**Core Framework**: FPLAdvisor with graceful degradation

**Models Used**:
- **sentence-transformers**: `all-MiniLM-L6-v2` for player similarity
- **Hugging Face transformers**: Sentiment analysis pipeline
- **Custom heuristics**: Rule-based recommendation engine

**Fallback Strategy**:
```python
try:
    from sentence_transformers import SentenceTransformer
    self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
except ImportError:
    self.embedder = None  # Use heuristic-only mode
```

## 🗄️ Database Architecture

### SQLAlchemy Models

**Core Entities**:

```python
class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    team_id = Column(Integer, nullable=False)
    position = Column(String, nullable=False)
    cost = Column(Float, nullable=False)
    
    # Relationships
    history = relationship("GameweekHistory", back_populates="player")
    projections = relationship("Projection", back_populates="player")

class GameweekHistory(Base):
    __tablename__ = "gameweek_history"
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    gameweek = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False)
    minutes = Column(Integer, nullable=False)

class Projection(Base):
    __tablename__ = "projections"
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    gameweek = Column(Integer, nullable=False)
    expected_points = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
```

### Database Fallback Pattern

```python
def get_session():
    """Repository pattern with automatic fallback"""
    if DATABASE_URL and "postgresql" in DATABASE_URL:
        return get_postgresql_session()
    else:
        return get_sqlite_session()
```

**SQLite** (Development):
- File-based storage
- Zero configuration
- Automatic creation
- Perfect for testing

**PostgreSQL** (Production):
- High performance
- Concurrent access
- ACID compliance
- Recommended for deployment

## 🔌 API Integration

### FPL API Client

**Pattern**: Context manager with automatic caching

```python
class FPLClient:
    def __init__(self):
        self.session = requests.Session()
        self.cache = TTLCache(maxsize=100, ttl=3600)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
    
    @cached_property
    def get_players(self):
        """Cached for 1 hour"""
        return self._fetch_players()
```

**Key Features**:
- **Rate Limiting**: Built-in delays to protect FPL API
- **Caching**: 1-hour TTL for static data, 15-minute for live data
- **Error Handling**: Graceful degradation on API failures
- **Session Management**: Automatic connection pooling

### REST API Design

**Principles**:
- **Mobile-first**: Limited array sizes (3-5 items)
- **Team-centric**: Endpoints focused on team analysis
- **Consistent responses**: Standard error and success formats
- **Type safety**: Full Pydantic validation

**Example Endpoint**:
```python
@app.get("/team/{team_id}/advisor")
async def get_team_advisor(
    team_id: int,
    horizon: int = 5,
    free_transfers: int = 1,
    client: FPLClient = Depends(get_fpl_client)
):
    # Implementation
    pass
```

## 🛠️ Development Tools

### Code Quality

**Formatting & Linting**:
- **Black**: Code formatting
- **Ruff**: Fast linting and import sorting
- **MyPy**: Static type checking
- **Pre-commit**: Automated quality checks

**Testing**:
- **pytest**: Test framework with fixtures
- **Coverage**: Code coverage reporting
- **Mock**: External API mocking
- **Parametrized tests**: Multiple scenario testing

### VS Code Integration

**Extensions** (25 included):
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "typescript.preferences.quoteStyle": "double"
}
```

**Tasks** (15 automated):
- Build, test, format, serve workflows
- Frontend and backend development
- Database management
- Deployment preparation

## 📦 Package Management

### Python Dependencies

**Core** (`pyproject.toml`):
```toml
[project]
dependencies = [
    "requests>=2.31.0",
    "pandas>=2.0.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
web = ["fastapi>=0.104.0", "uvicorn>=0.24.0", "streamlit>=1.28.0"]
ai = ["sentence-transformers>=2.2.0", "transformers>=4.35.0"]
postgresql = ["psycopg2-binary>=2.9.0"]
dev = ["pytest>=7.0.0", "black>=23.0.0", "ruff>=0.1.0"]
```

### Frontend Dependencies

**Core** (`package.json`):
```json
{
  "dependencies": {
    "next": "14.0.3",
    "react": "^18.2.0",
    "typescript": "^5.3.2",
    "tailwindcss": "^3.3.6"
  },
  "devDependencies": {
    "@types/node": "^20.9.2",
    "@types/react": "^18.2.37",
    "eslint": "^8.54.0"
  }
}
```

## 🚀 Deployment Architecture

### Production Stack

**Frontend** (Vercel):
- Next.js standalone output
- Edge runtime optimization
- Automatic HTTPS/CDN
- Environment variable management

**Backend** (Render/Railway):
- Docker containerization
- PostgreSQL database
- Auto-scaling
- Health check monitoring

**Alternative** (Docker):
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e ".[web,ai,postgresql]"

EXPOSE 8000
CMD ["fpl-toolkit", "serve", "--host", "0.0.0.0"]
```

### Environment Configuration

**Development**:
```bash
DATABASE_URL=sqlite:///fpl_toolkit.db
CACHE_TTL_SECONDS=3600
ENABLE_ADVANCED_METRICS=true
```

**Production**:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
CACHE_TTL_SECONDS=1800
ENABLE_ADVANCED_METRICS=true
PORT=8000
```

## 🔒 Security Considerations

### API Security

- **Input Validation**: Pydantic models prevent injection
- **Rate Limiting**: Client-side caching reduces load
- **CORS**: Configurable for production deployment
- **SQL Injection**: SQLAlchemy ORM protection

### Data Privacy

- **No Personal Data**: Only public FPL API data
- **Local Storage**: SQLite option for privacy
- **Caching**: TTL-based automatic cleanup
- **Anonymization**: No user tracking

## 📊 Performance Optimization

### Caching Strategy

**Multi-level Caching**:
1. **Client Cache**: 1-hour TTL for static data
2. **Database Cache**: Efficient query patterns
3. **CDN Cache**: Static asset optimization
4. **Browser Cache**: Frontend asset caching

### Database Optimization

**Query Patterns**:
- Indexed lookups on player_id, gameweek
- Batch operations for bulk data
- Connection pooling for concurrent access
- Lazy loading for relationships

### Frontend Optimization

**Next.js Features**:
- **Code Splitting**: Route-based bundles
- **Image Optimization**: Automatic WebP conversion
- **Bundle Analysis**: webpack-bundle-analyzer
- **Tree Shaking**: Unused code elimination

## 🔮 Extensibility

### Plugin Architecture

**Optional Dependencies**:
- AI features are completely optional
- Database backends are swappable
- Frontend can be replaced or extended
- New analysis modules can be added

**Integration Points**:
- **API Endpoints**: Easy to extend with new routes
- **Analysis Modules**: Pluggable algorithm implementations
- **Data Sources**: Extensible beyond FPL API
- **UI Components**: Reusable component library

---

*This technical stack provides a solid foundation for a production-ready FPL analysis platform with room for growth and customization.*