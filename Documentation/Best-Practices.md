# Best Practices

Development and usage best practices for the FPL Toolkit.

## 🏗️ Development Best Practices

### Code Organization

**Follow the layered architecture**:
```python
# ✅ Good: Use dependency injection
from fpl_toolkit.api.client import FPLClient
from fpl_toolkit.db.engine import get_session

@app.get("/players")
async def get_players(
    client: FPLClient = Depends(get_fpl_client),
    session: Session = Depends(get_session)
):
    return await client.get_players()

# ❌ Bad: Direct instantiation
def get_players():
    client = FPLClient()  # No context management
    return client.get_players()
```

**Use context managers**:
```python
# ✅ Good: Proper resource management
with FPLClient() as client:
    players = client.get_players()

# ✅ Good: AI advisor context
with FPLAdvisor() as advisor:
    advice = advisor.analyze_team(player_ids)

# ❌ Bad: Resource leaks
client = FPLClient()
players = client.get_players()  # Session not closed
```

### Error Handling Patterns

**Analysis functions should return dictionaries with error keys**:
```python
# ✅ Good: Consistent error format
def analyze_player(player_id: int) -> Dict[str, Any]:
    if not player_id:
        return {"error": "Player ID is required"}
    
    try:
        # Analysis logic
        return {"player_id": player_id, "analysis": result}
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

# ❌ Bad: Raising exceptions
def analyze_player(player_id: int):
    if not player_id:
        raise ValueError("Player ID required")  # Don't do this
```

**API endpoints should use proper HTTP status codes**:
```python
# ✅ Good: Proper status codes
@app.get("/player/{player_id}")
async def get_player(player_id: int):
    try:
        player = await get_player_data(player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        return player
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Data Formatting Standards

**Cost formatting**:
```python
# ✅ Good: Always divide FPL API costs by 10
cost_millions = fpl_cost / 10.0

# ✅ Good: Consistent player naming
name = f"{first_name} {second_name}".strip()

# ✅ Good: Confidence scores 0-1 range
confidence_score = min(max(score, 0.0), 1.0)
```

**Position handling**:
```python
# ✅ Good: Use constants
POSITIONS = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
position = POSITIONS.get(element_type, "Unknown")

# ❌ Bad: Magic numbers
if element_type == 4:  # What does 4 mean?
    position = "Forward"
```

### Testing Practices

**Mock external APIs**:
```python
# ✅ Good: Mock FPL API calls
@pytest.fixture
def mock_fpl_client():
    with patch('src.fpl_toolkit.api.client.FPLClient') as mock:
        mock.return_value.__enter__.return_value.get_players.return_value = [
            {"id": 1, "name": "Test Player", "cost": 100}
        ]
        yield mock

def test_player_analysis(mock_fpl_client):
    result = analyze_player(1)
    assert "error" not in result
```

**Test both success and error scenarios**:
```python
def test_player_analysis_success():
    result = analyze_player(123)
    assert "analysis" in result
    assert result["player_id"] == 123

def test_player_analysis_invalid_id():
    result = analyze_player(0)
    assert "error" in result
    assert "Player ID" in result["error"]
```

## 🎯 Usage Best Practices

### API Client Usage

**Always use caching**:
```python
# ✅ Good: Let the client handle caching
with FPLClient() as client:
    players = client.get_players()  # Cached automatically

# ❌ Bad: Bypassing cache
response = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
```

**Respect rate limits**:
```python
# ✅ Good: Built-in rate limiting
client = FPLClient()  # Has automatic delays

# ❌ Bad: Aggressive requests
for i in range(100):
    requests.get(fpl_url)  # Will get rate limited
```

### Database Best Practices

**Use the repository pattern**:
```python
# ✅ Good: Use get_session()
from fpl_toolkit.db.engine import get_session

session = get_session()  # Handles SQLite/PostgreSQL automatically

# ❌ Bad: Direct database access
engine = create_engine("sqlite:///fpl.db")
```

**Handle database errors gracefully**:
```python
# ✅ Good: Graceful degradation
try:
    session = get_session()
    players = session.query(Player).all()
except Exception as e:
    logger.warning(f"Database error: {e}")
    # Fall back to API or cached data
    players = fallback_get_players()
```

### AI Feature Implementation

**Optional dependency pattern**:
```python
# ✅ Good: Graceful fallback
try:
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    ai_available = True
except ImportError:
    embedder = None
    ai_available = False

def get_similar_players(player_id):
    if ai_available and embedder:
        return ai_similarity_search(player_id)
    else:
        return heuristic_similarity_search(player_id)
```

**Model loading best practices**:
```python
# ✅ Good: Lazy loading with error handling
class FPLAdvisor:
    def __init__(self):
        self._embedder = None
    
    @property
    def embedder(self):
        if self._embedder is None:
            try:
                self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                logger.warning(f"Failed to load AI model: {e}")
                self._embedder = False
        return self._embedder if self._embedder else None
```

## 🚀 Deployment Best Practices

### Environment Configuration

**Use environment-specific configs**:
```bash
# ✅ Good: Environment-specific settings
# .env.development
DATABASE_URL=sqlite:///fpl_toolkit.db
DEBUG=true
CACHE_TTL_SECONDS=300

# .env.production  
DATABASE_URL=postgresql://user:pass@host:port/db
DEBUG=false
CACHE_TTL_SECONDS=3600
```

**Secure sensitive data**:
```bash
# ✅ Good: Use secrets management
DATABASE_URL=${DATABASE_URL}  # From environment
API_KEY=${SECRET_API_KEY}     # From secret store

# ❌ Bad: Hardcoded secrets
DATABASE_URL=postgresql://admin:password123@host/db
```

### Performance Optimization

**Implement proper caching**:
```python
# ✅ Good: Multi-level caching
@lru_cache(maxsize=128)
def expensive_calculation(player_id):
    return complex_analysis(player_id)

# Database query caching
@cached(cache=TTLCache(maxsize=100, ttl=3600))
def get_player_history(player_id):
    return session.query(GameweekHistory).filter_by(player_id=player_id).all()
```

**Optimize database queries**:
```python
# ✅ Good: Efficient queries with joins
players_with_history = session.query(Player).join(GameweekHistory).all()

# ❌ Bad: N+1 query problem
players = session.query(Player).all()
for player in players:
    history = session.query(GameweekHistory).filter_by(player_id=player.id).all()
```

### Security Best Practices

**Input validation**:
```python
# ✅ Good: Validate all inputs
@app.get("/player/{player_id}")
async def get_player(player_id: int = Path(..., ge=1, le=1000)):
    # player_id is guaranteed to be 1-1000
    return await get_player_data(player_id)

# ✅ Good: Use Pydantic models
class TransferRequest(BaseModel):
    player_out_id: int = Field(..., ge=1, le=1000)
    player_in_id: int = Field(..., ge=1, le=1000)
    horizon_gameweeks: int = Field(default=5, ge=1, le=38)
```

**CORS configuration**:
```python
# ✅ Good: Restrictive CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# ❌ Bad: Allow all origins in production
allow_origins=["*"]  # Security risk
```

## 📱 Frontend Best Practices

### Next.js Development

**Use TypeScript consistently**:
```typescript
// ✅ Good: Full type safety
interface PlayerData {
  id: number;
  name: string;
  cost: number;
  position: 'GK' | 'DEF' | 'MID' | 'FWD';
}

const PlayerCard: React.FC<{ player: PlayerData }> = ({ player }) => {
  return <div>{player.name}</div>;
};

// ❌ Bad: Using any types
const PlayerCard = ({ player }: any) => {
  return <div>{player.name}</div>;
};
```

**Implement proper error boundaries**:
```typescript
// ✅ Good: Error boundary component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}
```

### Streamlit Best Practices

**Use session state for performance**:
```python
# ✅ Good: Cache expensive operations
@st.cache_data(ttl=3600)
def load_player_data():
    with FPLClient() as client:
        return client.get_players()

# ✅ Good: Use session state for user selections
if "selected_players" not in st.session_state:
    st.session_state.selected_players = []
```

**Optimize UI rendering**:
```python
# ✅ Good: Use columns for layout
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Points", player.total_points)
with col2:
    st.metric("Cost", f"£{player.cost}m")
with col3:
    st.metric("Form", player.form)

# ❌ Bad: Unnecessary recomputation
for player in players:
    expensive_calculation(player)  # Recalculated on every run
```

## 🔍 Monitoring & Maintenance

### Logging Best Practices

**Structured logging**:
```python
# ✅ Good: Structured logging with context
import structlog

logger = structlog.get_logger()

def analyze_transfer(player_out_id, player_in_id):
    logger.info(
        "Starting transfer analysis",
        player_out_id=player_out_id,
        player_in_id=player_in_id,
        timestamp=datetime.utcnow()
    )
    
    try:
        result = perform_analysis()
        logger.info("Transfer analysis completed", result=result)
        return result
    except Exception as e:
        logger.error("Transfer analysis failed", error=str(e))
        raise
```

**Log levels appropriately**:
```python
# ✅ Good: Appropriate log levels
logger.debug("Cache hit for player data")           # Debug info
logger.info("User requested transfer analysis")     # Normal operation
logger.warning("FPL API rate limit approaching")    # Potential issue
logger.error("Database connection failed")          # Error condition
logger.critical("Service unavailable")              # System failure
```

### Health Monitoring

**Implement comprehensive health checks**:
```python
# ✅ Good: Multi-component health check
@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "components": {}
    }
    
    # Check database
    try:
        session = get_session()
        session.execute("SELECT 1")
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check FPL API
    try:
        with FPLClient() as client:
            client.get_bootstrap_static()
        health_status["components"]["fpl_api"] = "healthy"
    except Exception as e:
        health_status["components"]["fpl_api"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status
```

### Performance Monitoring

**Track key metrics**:
```python
# ✅ Good: Performance tracking
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} completed", duration=duration)
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed", duration=duration, error=str(e))
            raise
    return wrapper

@monitor_performance
async def analyze_team(team_id):
    # Analysis logic
    pass
```

## 📚 Documentation Best Practices

### Code Documentation

**Use comprehensive docstrings**:
```python
# ✅ Good: Detailed docstring
def calculate_horizon_projection(
    player_id: int, 
    horizon_gameweeks: int = 5
) -> Dict[str, Any]:
    """Calculate multi-gameweek projection for a player.
    
    Args:
        player_id: FPL player ID (1-1000)
        horizon_gameweeks: Number of gameweeks to project (1-38)
        
    Returns:
        Dictionary containing:
        - projected_points: Total expected points
        - confidence_score: Reliability of projection (0-1)
        - breakdown: Points breakdown by category
        - risk_factors: List of potential issues
        
    Raises:
        ValueError: If player_id is invalid
        
    Example:
        >>> projection = calculate_horizon_projection(123, 5)
        >>> print(projection['projected_points'])
        42.5
    """
```

**Document API endpoints thoroughly**:
```python
# ✅ Good: Comprehensive API documentation
@app.get(
    "/team/{team_id}/advisor",
    response_model=TeamAdvisorResponse,
    summary="Get AI-powered team advice",
    description="""
    Analyze a team and provide AI-powered recommendations.
    
    The advisor automatically:
    - Fetches current team picks from FPL API
    - Analyzes each player's performance and fixtures
    - Identifies transfer opportunities
    - Provides strategic recommendations
    
    **Rate Limit**: 60 requests per minute
    **Cache**: Results cached for 15 minutes
    """,
    responses={
        200: {"description": "Team analysis completed successfully"},
        404: {"description": "Team not found"},
        429: {"description": "Rate limit exceeded"},
    }
)
async def get_team_advisor(team_id: int):
    # Implementation
    pass
```

### README Best Practices

**Include all essential information**:
- Clear project description and goals
- Installation instructions (one-command setup)
- Usage examples with actual commands
- Feature overview with screenshots
- Deployment instructions
- Contributing guidelines
- License information

**Use badges for quick status overview**:
```markdown
[![Build Status](https://github.com/AmberMaze/Fpl-toolkit/workflows/CI/badge.svg)](https://github.com/AmberMaze/Fpl-toolkit/actions)
[![Coverage](https://codecov.io/gh/AmberMaze/Fpl-toolkit/branch/main/graph/badge.svg)](https://codecov.io/gh/AmberMaze/Fpl-toolkit)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
```

---

*Following these best practices ensures maintainable, scalable, and user-friendly code. For specific implementation examples, see the codebase and [Technical Stack](./Technical-Stack.md) documentation.*