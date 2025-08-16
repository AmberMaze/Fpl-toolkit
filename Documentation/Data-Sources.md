# Data Sources and Database Schema

This document describes the data sources used by the FPL Toolkit and the database schema for storing and managing FPL data.

## Data Sources

### Primary Source: FPL Official API

The toolkit primarily uses the official Fantasy Premier League API:

**Base URL**: `https://fantasy.premierleague.com/api/`

#### Key Endpoints

1. **Bootstrap Static** (`/bootstrap-static/`)
   - Complete league data including players, teams, gameweeks
   - Updated regularly throughout the season
   - Contains current player prices, points, and statistics

2. **Player Details** (`/element-summary/{player_id}/`)
   - Detailed player history and upcoming fixtures
   - Gameweek-by-gameweek performance data
   - Historical data from previous seasons

3. **Fixtures** (`/fixtures/`)
   - Match schedule and results
   - Team difficulty ratings
   - Kickoff times and match status

#### Data Refresh Strategy
```python
# Caching configuration
CACHE_TTL_SECONDS = 3600  # 1 hour default
RATE_LIMIT_PER_MINUTE = 60  # Respectful rate limiting

# Cache implementation
class FPLClient:
    def _is_cache_valid(self, key):
        return datetime.now() - cache_time < timedelta(seconds=self._cache_ttl)
```

### Rate Limiting and Ethics

The toolkit implements responsible API usage:
- **Automatic caching**: Reduces unnecessary API calls
- **Request throttling**: Limits requests per minute
- **Graceful fallbacks**: Handles API unavailability
- **Error handling**: Robust response to API changes

## Database Schema

### Engine Configuration

The toolkit supports both SQLite and PostgreSQL:

```python
# Automatic database selection
def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url  # PostgreSQL or custom
    else:
        return f"sqlite:///{os.getcwd()}/fpl_toolkit.db"  # Fallback
```

### Core Tables

#### 1. Players Table

Stores comprehensive player information:

```sql
CREATE TABLE players (
    id INTEGER PRIMARY KEY,
    fpl_id INTEGER UNIQUE NOT NULL,           -- Official FPL player ID
    name VARCHAR(100) NOT NULL,
    team_id INTEGER NOT NULL,
    position VARCHAR(20) NOT NULL,            -- GK, DEF, MID, FWD
    cost FLOAT NOT NULL,                      -- Current cost in millions
    total_points INTEGER DEFAULT 0,
    selected_by_percent FLOAT DEFAULT 0.0,
    form FLOAT DEFAULT 0.0,                   -- Recent form rating
    points_per_game FLOAT DEFAULT 0.0,
    minutes INTEGER DEFAULT 0,
    goals_scored INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    clean_sheets INTEGER DEFAULT 0,
    goals_conceded INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    bonus INTEGER DEFAULT 0,
    bps INTEGER DEFAULT 0,                    -- Bonus Points System
    influence FLOAT DEFAULT 0.0,
    creativity FLOAT DEFAULT 0.0,
    threat FLOAT DEFAULT 0.0,
    ict_index FLOAT DEFAULT 0.0,             -- ICT Index
    status VARCHAR(20) DEFAULT 'a',          -- a=available, i=injured, etc.
    news TEXT DEFAULT '',
    chance_of_playing_this_round INTEGER,
    chance_of_playing_next_round INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. Gameweek History Table

Tracks player performance over time:

```sql
CREATE TABLE gameweek_history (
    id INTEGER PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    gameweek INTEGER NOT NULL,
    total_points INTEGER DEFAULT 0,
    minutes INTEGER DEFAULT 0,
    goals_scored INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    clean_sheets INTEGER DEFAULT 0,
    goals_conceded INTEGER DEFAULT 0,
    own_goals INTEGER DEFAULT 0,
    penalties_saved INTEGER DEFAULT 0,
    penalties_missed INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    bonus INTEGER DEFAULT 0,
    bps INTEGER DEFAULT 0,
    influence FLOAT DEFAULT 0.0,
    creativity FLOAT DEFAULT 0.0,
    threat FLOAT DEFAULT 0.0,
    ict_index FLOAT DEFAULT 0.0,
    value FLOAT DEFAULT 0.0,                 -- Player value at time
    transfers_balance INTEGER DEFAULT 0,
    selected INTEGER DEFAULT 0,
    transfers_in INTEGER DEFAULT 0,
    transfers_out INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. Projections Table

Stores calculated player projections:

```sql
CREATE TABLE projections (
    id INTEGER PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    gameweek INTEGER NOT NULL,
    projected_points FLOAT NOT NULL,
    projected_minutes INTEGER DEFAULT 0,
    confidence_score FLOAT DEFAULT 0.5,     -- 0-1 confidence rating
    fixture_difficulty FLOAT DEFAULT 3.0,   -- 1=easy, 5=difficult
    form_factor FLOAT DEFAULT 1.0,
    home_advantage BOOLEAN DEFAULT FALSE,
    opponent_team_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. Decision Scenarios Table

Records transfer analysis results:

```sql
CREATE TABLE decision_scenarios (
    id INTEGER PRIMARY KEY,
    scenario_name VARCHAR(200) NOT NULL,
    player_out_id INTEGER,                  -- Player being transferred out
    player_in_id INTEGER,                   -- Player being transferred in
    cost_change FLOAT DEFAULT 0.0,          -- Net cost difference
    projected_points_gain FLOAT DEFAULT 0.0, -- Expected points gain
    horizon_gameweeks INTEGER DEFAULT 5,     -- Analysis timeframe
    confidence_score FLOAT DEFAULT 0.5,
    risk_score FLOAT DEFAULT 0.5,           -- Higher = more risky
    reasoning TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes and Performance

#### Recommended Indexes
```sql
-- Player lookups
CREATE INDEX idx_players_fpl_id ON players(fpl_id);
CREATE INDEX idx_players_team_position ON players(team_id, position);
CREATE INDEX idx_players_cost ON players(cost);
CREATE INDEX idx_players_status ON players(status);

-- Gameweek history queries
CREATE INDEX idx_history_player_gameweek ON gameweek_history(player_id, gameweek);
CREATE INDEX idx_history_gameweek ON gameweek_history(gameweek);

-- Projection lookups
CREATE INDEX idx_projections_player_gameweek ON projections(player_id, gameweek);
CREATE INDEX idx_projections_gameweek ON projections(gameweek);

-- Decision scenario tracking
CREATE INDEX idx_scenarios_created_at ON decision_scenarios(created_at);
CREATE INDEX idx_scenarios_players ON decision_scenarios(player_out_id, player_in_id);
```

## Repository Pattern

### CRUD Operations

The toolkit uses a repository pattern for database operations:

```python
class PlayerRepository:
    def upsert(self, player_data):
        """Insert or update player data."""
        
    def get_by_fpl_id(self, fpl_id):
        """Get player by official FPL ID."""
        
    def get_by_position(self, position):
        """Get all players in a position."""
        
    def search(self, name_query):
        """Search players by name."""
```

### Example Usage
```python
from fpl_toolkit.db.repository import PlayerRepository
from fpl_toolkit.db.engine import get_session

# Initialize repository
session = get_session()
player_repo = PlayerRepository(session)

# Upsert player data
player_data = {
    "fpl_id": 123,
    "name": "Example Player",
    "team_id": 1,
    "position": "MID",
    "cost": 8.5,
    "total_points": 150
}
player = player_repo.upsert(player_data)

# Query operations
midfielders = player_repo.get_by_position("MID")
search_results = player_repo.search("Salah")
```

## Data Migration and Updates

### Initial Setup
```python
from fpl_toolkit.db.engine import init_db

# Create all tables
init_db()
```

### Regular Data Updates
```python
from fpl_toolkit.api.client import FPLClient
from fpl_toolkit.db.repository import PlayerRepository

def update_player_data():
    """Update player data from FPL API."""
    with FPLClient() as client:
        players = client.get_players()
        
        repo = PlayerRepository()
        for player_data in players:
            # Transform API data to database format
            db_player = transform_player_data(player_data)
            repo.upsert(db_player)

def transform_player_data(api_player):
    """Transform API format to database format."""
    return {
        "fpl_id": api_player["id"],
        "name": f"{api_player['first_name']} {api_player['second_name']}",
        "team_id": api_player["team"],
        "position": get_position_name(api_player["element_type"]),
        "cost": api_player["now_cost"] / 10.0,
        "total_points": api_player["total_points"],
        # ... additional fields
    }
```

## Data Validation and Integrity

### Validation Rules
```python
def validate_player_data(player_data):
    """Validate player data before database insertion."""
    required_fields = ["fpl_id", "name", "team_id", "position", "cost"]
    
    for field in required_fields:
        if field not in player_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate ranges
    if not (1 <= player_data["team_id"] <= 20):
        raise ValueError("Invalid team_id")
    
    if player_data["position"] not in ["GK", "DEF", "MID", "FWD"]:
        raise ValueError("Invalid position")
    
    if not (0 <= player_data["cost"] <= 20):
        raise ValueError("Invalid cost range")
```

### Data Consistency
- **Foreign key constraints**: Ensure referential integrity
- **Unique constraints**: Prevent duplicate FPL IDs
- **Check constraints**: Validate data ranges
- **Timestamps**: Track data freshness and updates

## Backup and Recovery

### SQLite Backup
```bash
# Simple file copy for SQLite
cp fpl_toolkit.db fpl_toolkit_backup.db

# Or use SQLite backup command
sqlite3 fpl_toolkit.db ".backup fpl_toolkit_backup.db"
```

### PostgreSQL Backup
```bash
# Full database backup
pg_dump fpl_toolkit > fpl_toolkit_backup.sql

# Compressed backup
pg_dump fpl_toolkit | gzip > fpl_toolkit_backup.sql.gz

# Restore from backup
psql fpl_toolkit < fpl_toolkit_backup.sql
```

## Performance Optimization

### Query Optimization
```python
# Use appropriate indexes
session.query(Player).filter(Player.fpl_id == 123)  # Uses index

# Batch operations for bulk updates
session.bulk_insert_mappings(Player, player_data_list)

# Efficient joins
session.query(Player, GameweekHistory).join(GameweekHistory)
```

### Connection Pooling
```python
# PostgreSQL connection pooling
engine = create_engine(
    database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### Monitoring
```python
# Log slow queries
engine = create_engine(database_url, echo=True)  # Development only

# Query performance monitoring
import time
start_time = time.time()
result = session.query(Player).all()
query_time = time.time() - start_time
logger.info(f"Query took {query_time:.2f} seconds")
```

## Security Considerations

### Database Security
- **Environment variables**: Store credentials securely
- **Connection encryption**: Use SSL for PostgreSQL
- **Access control**: Limit database user permissions
- **SQL injection**: Use parameterized queries (SQLAlchemy ORM)

### Data Privacy
- **Personal data**: FPL data is public, but be mindful of user data
- **API keys**: If using premium APIs, secure API keys
- **Logging**: Don't log sensitive information

```python
# Secure database URL handling
import os
from urllib.parse import urlparse

def get_secure_db_url():
    """Get database URL with security considerations."""
    db_url = os.getenv("DATABASE_URL")
    
    if db_url and db_url.startswith("postgresql"):
        # Parse URL to ensure SSL
        parsed = urlparse(db_url)
        if "sslmode" not in parsed.query:
            db_url += "?sslmode=require"
    
    return db_url
```