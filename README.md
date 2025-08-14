# FPL Toolkit

A comprehensive Fantasy Premier League (FPL) analysis and decision support toolkit with AI-powered recommendations, mobile-friendly APIs, and advanced analytics.

## Features

- 🤖 **AI-Powered Advisor**: Intelligent team analysis and transfer recommendations
- 📊 **Advanced Analytics**: Fixture difficulty, player projections, and performance metrics
- 📱 **Mobile-Friendly API**: RESTful endpoints optimized for mobile access
- 🗄️ **Database Integration**: SQLite fallback with optional PostgreSQL support
- 🌐 **Web Interface**: Streamlit app with responsive design
- ⚙️ **CLI Tools**: Command-line interface for automation and scripting

## Quick Start

### Installation

```bash
# Basic installation
pip install fpl-toolkit

# With all features (recommended)
pip install "fpl-toolkit[dev,db,web,ai]"

# For PostgreSQL support
pip install "fpl-toolkit[postgresql]"
```

### Database Setup

```bash
# Initialize database (SQLite by default)
fpl-toolkit init

# Or set PostgreSQL URL
export DATABASE_URL="postgresql://user:password@localhost:5432/fpl_toolkit"
fpl-toolkit init
```

### Quick Usage

#### CLI Interface

```bash
# Get team advice
fpl-toolkit advise 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 --budget 2.5 --free-transfers 1

# Analyze a transfer
fpl-toolkit transfer 123 456 --horizon 5

# List top players
fpl-toolkit players --position MID --max-cost 10.0

# Start API server
fpl-toolkit serve --host 0.0.0.0 --port 8000

# Start Streamlit app
fpl-toolkit streamlit --port 8501
```

#### Python API

```python
from fpl_toolkit.ai.advisor import FPLAdvisor
from fpl_toolkit.analysis.fixtures import compute_fixture_difficulty
from fpl_toolkit.analysis.decisions import analyze_transfer_scenario

# Get AI advice for your team
advisor = FPLAdvisor()
team_state = {
    "player_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "budget": 2.5,
    "free_transfers": 1,
    "horizon_gameweeks": 5
}
advice = advisor.advise_team(team_state)
print(advice["summary"])

# Analyze fixture difficulty
fixtures = compute_fixture_difficulty(team_id=1, next_n=5)
print(f"Average difficulty: {fixtures['average_difficulty']}")

# Compare transfer options
scenario = analyze_transfer_scenario(player_out_id=123, player_in_id=456)
print(f"Projected gain: {scenario['projected_points_gain']} points")
```

## Decision Support

The toolkit provides sophisticated decision support for FPL managers:

### Transfer Analysis
- **Scenario Modeling**: Compare player swaps with projected points and risk assessment
- **Target Finding**: Automatically suggest transfer targets based on budget and position
- **Multi-Transfer Planning**: Analyze multiple transfers together

### Team Evaluation
- **Underperformer Detection**: Identify players who need replacing
- **Form Analysis**: Track recent performance trends
- **Fixture Optimization**: Leverage upcoming fixture difficulty

## Database Layer

### Automatic Fallback
- **SQLite Default**: Works out of the box with local SQLite database
- **PostgreSQL Optional**: Set `DATABASE_URL` environment variable for PostgreSQL

### Data Models
- **Players**: Comprehensive player statistics and metadata
- **Gameweek History**: Historical performance tracking
- **Projections**: Future performance predictions
- **Decision Scenarios**: Transfer analysis results

### Usage
```python
from fpl_toolkit.db.engine import init_db, get_session
from fpl_toolkit.db.repository import PlayerRepository

# Initialize database
init_db()

# Use repository pattern
session = get_session()
player_repo = PlayerRepository(session)
players = player_repo.get_by_position("MID")
```

## FastAPI Usage

### Start the Server

```bash
# Development
fpl-toolkit serve --reload

# Production
uvicorn fpl_toolkit.service.api:app --host 0.0.0.0 --port 8000
```

### Key Endpoints

- `GET /health` - Health check
- `GET /players` - List players with filters
- `GET /player/{id}` - Player details
- `POST /compare` - Compare multiple players
- `POST /advisor` - Get AI team advice
- `GET /projections/{id}` - Player projections
- `POST /transfer-scenario` - Analyze transfers
- `GET /fixtures/{team_id}` - Fixture difficulty
- `GET /team/{team_id}/summary` - Team summary with captain names and enhanced breakdowns

## Advanced Metrics & Zone Adjustments

The toolkit supports optional advanced metrics to enhance player projections and breakdowns:

### Expected Goals (xG) and Assists (xA)

The system can integrate expected performance metrics to provide more accurate breakdowns:

```bash
# Enable external metrics (requires network access)
export ENABLE_UNDERSTAT=1

# Use local sample data (default)
export ENABLE_UNDERSTAT=0
```

When enabled, the system will:
- Fetch real-time xG/xA data from external sources
- Reweight goal vs assist projections based on underlying performance
- Provide more accurate attacking returns estimation

**Fallback Strategy**: If external data is unavailable, the system gracefully falls back to local sample data or heuristic calculations.

### Zone Weakness Adjustments

Historical zone weakness data can be used to adjust attacking projections:

```bash
# Custom zone weakness file
export ZONE_WEAKNESS_FILE=./data/custom_zone_weakness.json

# Use default sample (fallback if file missing)
export ZONE_WEAKNESS_FILE=./data/zone_weakness.sample.json
```

Zone adjustments consider:
- **Left/Center/Right attacking patterns**: Players attacking different zones face varying defensive strengths
- **Team-specific weaknesses**: Some teams concede more from specific areas
- **Multiplier application**: Attacking returns are adjusted by zone-specific multipliers

### Enhanced Team Breakdowns

The `/team/{team_id}/summary` endpoint provides enhanced player breakdowns:

```json
{
  "captain_name": "Erling Haaland",
  "vice_captain_name": "Mohamed Salah",
  "players": [
    {
      "name": "Erling Haaland",
      "breakdown": {
        "appearance": 1.9,
        "goals": 3.1,
        "assists": 1.2,
        "cs": 0.2,
        "bonus": 0.7,
        "misc": 0.5,
        "total": 7.6,
        "adjustments": {
          "xg_per90": 0.58,
          "xa_per90": 0.32,
          "zone_multiplier": 1.08
        }
      }
    }
  ]
}
```

### Sample Data Files

The toolkit includes sample data for development and fallback:

- `data/xgxa_sample.json`: Expected goals/assists for popular players
- `data/zone_weakness.sample.json`: Zone weakness indices for all Premier League teams

### Configuration Options

```bash
# Advanced metrics configuration
ENABLE_UNDERSTAT=1                              # Enable real-time xG/xA (default: 0)
ZONE_WEAKNESS_FILE=./data/zone_weakness.json    # Zone weakness data file
```

**Note**: When advanced metrics are unavailable, all functionality continues to work with graceful fallbacks.

## Official FPL API Usage

This toolkit respectfully uses the official Fantasy Premier League API endpoints:

### Primary Endpoints Used

- **https://fantasy.premierleague.com/api/bootstrap-static/**: Static game data (players, teams, gameweeks)
- **https://fantasy.premierleague.com/api/element-summary/{element_id}/**: Detailed player information and fixtures
- **https://fantasy.premierleague.com/api/fixtures/**: Match fixtures and results
- **https://fantasy.premierleague.com/api/event-status/**: Current gameweek status
- **https://fantasy.premierleague.com/api/entry/{team_id}/event/{gw}/picks/**: User team selections
- **https://fantasy.premierleague.com/api/entry/{team_id}/transfers/**: User transfer history

### Data Refresh Cadence

- **Static Data**: Cached for 1 hour (configurable via `CACHE_TTL_SECONDS`)
- **Live Data**: Cached for 15 minutes during active gameweeks
- **Player Details**: Cached for 30 minutes
- **User Teams**: Cached for 5 minutes

### Rate Limiting & Ethics

- **Automatic throttling**: Maximum 60 requests per minute (configurable)
- **Respectful caching**: Minimizes API calls through intelligent caching
- **Error handling**: Graceful degradation when API is unavailable
- **No scraping**: Only uses official API endpoints

### Limitations

- **Public API**: Subject to change without notice
- **Rate limits**: May be throttled during high traffic periods
- **Data accuracy**: Dependent on official FPL data updates
- **Availability**: Service may be unavailable during maintenance

### Safe Usage Guidelines

1. **Use caching**: Don't disable the built-in caching mechanisms
2. **Respect limits**: Don't modify rate limiting configurations aggressively
3. **Handle errors**: Implement proper error handling for API failures
4. **Monitor usage**: Be aware of your request patterns
5. **Test responsibly**: Use sample data for development when possible

### Example Requests

```bash
# Get all midfielders under £10m
curl "http://localhost:8000/players?position=MID&max_cost=10.0"

# Compare players
curl -X POST "http://localhost:8000/compare" \
  -H "Content-Type: application/json" \
  -d '{"player_ids": [1, 2, 3], "horizon_gameweeks": 5}'

# Get team advice
curl -X POST "http://localhost:8000/advisor" \
  -H "Content-Type: application/json" \
  -d '{
    "player_ids": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
    "budget": 2.5,
    "free_transfers": 1
  }'
```

## Mobile Access

The API is optimized for mobile applications:

### Network Setup
```bash
# Start server accessible on local network
fpl-toolkit serve --host 0.0.0.0 --port 8000

# Access from phone using computer's IP
# Example: http://192.168.1.100:8000
```

### Mobile-Friendly Features
- **Compact JSON responses** for reduced bandwidth
- **CORS enabled** for web app integration
- **Responsive Streamlit interface** that works on mobile browsers
- **Efficient caching** to minimize API calls

### iPhone Usage
1. Start the server on your computer
2. Find your computer's IP address (`ipconfig` on Windows, `ifconfig` on Mac/Linux)
3. Access `http://YOUR_IP:8000` from your iPhone browser
4. Bookmark for quick access

## AI Tools

### Heuristic Rules
The AI advisor uses proven FPL strategies:
- **Value Detection**: Identify underperforming premium players
- **Form Analysis**: Flag players with poor recent form
- **Fixture Awareness**: Consider upcoming match difficulty
- **Injury Monitoring**: Track player availability
- **Ownership Analysis**: Find differential picks

### Optional ML Enhancement
```bash
# Install sentence-transformers for enhanced summarization
pip install "fpl-toolkit[ai]"
```

The advisor gracefully falls back to template-based summaries if ML models aren't available.

### Customization
```python
from fpl_toolkit.ai.advisor import FPLAdvisor

advisor = FPLAdvisor()

# Detect underperformers with custom thresholds
underperformers = advisor.detect_underperformers(
    team_players, 
    points_threshold=4.0,  # Minimum PPG
    cost_threshold=9.0     # Premium player threshold
)

# Find differential picks
differentials = advisor.highlight_differentials(
    ownership_threshold=8.0,  # Max ownership %
    min_points=3.5           # Minimum PPG
)
```

## Configuration

### Environment Variables

Create a `.env` file:
```bash
# Copy example configuration
cp .env.example .env

# Edit as needed
DATABASE_URL=postgresql://user:password@localhost:5432/fpl_toolkit
AI_MODEL=all-MiniLM-L6-v2
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
CACHE_TTL_SECONDS=3600
RATE_LIMIT_PER_MINUTE=60
```

### Rate Limiting & Caching

The toolkit implements respectful rate limiting:
- **Automatic caching** of FPL API responses (1 hour default)
- **Request throttling** to avoid overwhelming FPL servers
- **Configurable cache TTL** via environment variables

## Development

### Setup
```bash
git clone https://github.com/AmberMaze/Fpl-toolkit.git
cd Fpl-toolkit
pip install -e ".[dev,db,web,ai]"
```

### Testing
```bash
# Run all tests
pytest

# With coverage
pytest --cov=src/fpl_toolkit

# Lint code
ruff check src tests
ruff format src tests

# Type checking
mypy src/fpl_toolkit
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Disclaimers

- **Data Source**: Uses the official FPL API
- **Rate Limiting**: Please use responsibly to avoid overwhelming FPL servers
- **Accuracy**: Projections are estimates and should not be the sole basis for decisions
- **Liability**: No guarantee of accuracy or performance

## Support

- 📚 **Documentation**: See `/docs` folder for detailed guides
- 🐛 **Issues**: Report bugs on GitHub Issues
- 💬 **Discussions**: Join GitHub Discussions for questions

---

Built with ❤️ for the FPL community