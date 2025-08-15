# FPL Toolkit AI Coding Instructions

## Architecture Overview

This is a Fantasy Premier League (FPL) analysis toolkit with a **layered architecture**:

- **API Layer** (`src/fpl_toolkit/api/`): FPL API client with caching (`FPLClient` class)
- **Service Layer** (`src/fpl_toolkit/service/`): FastAPI REST endpoints + team-specific endpoints
- **Analysis Layer** (`src/fpl_toolkit/analysis/`): Core business logic (projections, decisions, fixtures)
- **AI Layer** (`src/fpl_toolkit/ai/`): Heuristic advisor + optional ML models
- **Database Layer** (`src/fpl_toolkit/db/`): SQLAlchemy models with SQLite fallback
- **CLI Interface** (`src/fpl_toolkit/cli.py`): Rich command-line tools

**Key architectural pattern**: Optional dependencies with graceful fallbacks - AI models, PostgreSQL, and web frameworks are optional extras.

## Essential Development Patterns

### Database Architecture

Use the **fallback pattern** - SQLite by default, PostgreSQL optional:

```python
# Always use the repository pattern via get_session()
from fpl_toolkit.db.engine import get_session
session = get_session()
```

### Client Pattern

Always use `FPLClient` as context manager for proper resource cleanup:

```python
with FPLClient() as client:
    players = client.get_players()
```

Cache is automatic (1hr TTL) - never bypass it.

### AI Module Pattern

The `FPLAdvisor` class gracefully degrades:

- Full AI features with sentence-transformers installed
- Heuristic-only mode without ML dependencies
- Always provide meaningful fallbacks in `_try_load_models()`

### Service Layer Conventions

- FastAPI endpoints use dependency injection (`Depends()`)
- Mobile-optimized responses (limit arrays to 3-5 items)
- Team-centric endpoints in `team_endpoints.py` (e.g., `/team/{id}/advisor`)
- All endpoints include error handling with proper HTTP status codes

## Critical Development Workflows

### Testing Commands

```bash
# Full test suite with coverage
pytest --cov=src/fpl_toolkit

# API endpoint tests
pytest tests/test_api_endpoints.py -v

# AI advisor tests
pytest tests/test_ai_advisor.py -v
```

### Local Development

```bash
# CLI development
fpl-toolkit serve --reload

# Streamlit development
fpl-toolkit streamlit --port 8501

# Database initialization
fpl-toolkit init
```

### Build & Deploy

```bash
# Docker build (matches Render deployment)
docker build -t fpl-toolkit .

# Package installation with optional deps
pip install '.[dev,web,ai,postgresql]'
```

## Project-Specific Conventions

### Error Handling Pattern

Always return dict with "error" key for analysis functions:

```python
if not player_data:
    return {"error": f"Player {player_id} not found"}
```

### Data Formatting

- Costs always in millions (divide FPL API by 10.0)
- Player names: `f"{first_name} {second_name}".strip()`
- Projections always include confidence_score (0-1 range)

### Optional Dependency Pattern

Use try/except imports with meaningful fallbacks:

```python
try:
    from sentence_transformers import SentenceTransformer
    self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
except ImportError:
    self.embedder = None
```

### CLI Design Philosophy

- Rich output with emojis and formatting
- Progressive disclosure (basic → detailed with flags)
- Always show concrete examples in help text

## Integration Points

### FPL API Integration

- Base URL: `https://fantasy.premierleague.com/api`
- Rate limiting: Built into `FPLClient` with automatic caching
- Bootstrap endpoint: Primary data source for players/teams/gameweeks

### Database Models

- `Player`: Core player data with relationships to history/projections
- `GameweekHistory`: Historical performance tracking
- `Projection`: Future gameweek predictions
- `DecisionScenario`: Transfer analysis storage

### External ML Models

- sentence-transformers: "all-MiniLM-L6-v2" for embeddings
- Hugging Face transformers: For sentiment analysis
- Always provide heuristic fallbacks when models unavailable

## File Patterns

### Analysis Module Structure

Each analysis module exports main functions directly:

- `projections.py` → `calculate_horizon_projection()`
- `decisions.py` → `analyze_transfer_scenario()`
- `fixtures.py` → `compute_fixture_difficulty()`

### Test File Structure

- Prefix: `test_*.py`
- Use `pytest.fixture` for common setup
- Mock external APIs in tests (`unittest.mock.patch`)
- Test both success and error scenarios

### Configuration

Environment variables in `.env`:

- `DATABASE_URL` for PostgreSQL
- `CACHE_TTL_SECONDS` for API caching
- `ENABLE_ADVANCED_METRICS` for xG/xA features

## Key Gotchas

1. **FPL API element types**: 1=GK, 2=DEF, 3=MID, 4=FWD (not strings)
2. **Cost conversion**: Always divide FPL API costs by 10.0
3. **Session management**: Use context managers for both `FPLClient` and `FPLAdvisor`
4. **Import paths**: Always use relative imports within package (`from ..api.client`)
5. **Mobile responsiveness**: Limit data arrays in API responses (mobile bandwidth)
