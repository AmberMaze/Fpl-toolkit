# FPL Toolkit

A comprehensive Fantasy Premier League (FPL) analysis and decision support toolkit with AI-powered recommendations, mobile-friendly APIs, and advanced analytics.

## Features

- 🤖 **AI-Powered Advisor**: Intelligent team analysis and transfer recommendations
- 📊 **Advanced Analytics**: Fixture difficulty, player projections, and performance metrics
- 📈 **Advanced Metrics**: Expected goals (xG/xA) and zone weakness adjustments for enhanced projections
- 📱 **Mobile-Friendly API**: RESTful endpoints optimized for mobile access
- 🗄️ **Database Integration**: SQLite fallback with optional PostgreSQL support
- 🌐 **Modern Frontend**: Next.js web application optimized for Vercel deployment
- 🖥️ **Streamlit Interface**: Alternative web interface with responsive design
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

## Frontend (Next.js)

A modern React frontend is available in the `frontend/` directory, optimized for Vercel deployment.

### Quick Start

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Features

- 🎨 **Modern UI** with Tailwind CSS and FPL-themed design
- 📱 **Responsive Design** optimized for mobile and desktop
- 🤖 **AI Integration** with the Python backend API
- ⚡ **Fast Performance** with Next.js 14 and App Router
- 🚀 **Vercel Ready** with optimized deployment configuration

### Deployment to Vercel

1. **Connect Repository to Vercel**
2. **Set Environment Variable**: `NEXT_PUBLIC_API_URL=https://your-backend-api.render.com`
3. **Auto-Deploy**: Pushes to main branch automatically deploy

See `frontend/README.md` for detailed setup and deployment instructions.

### Key Endpoints

- `GET /health` - Health check
- `GET /players` - List players with filters
- `GET /player/{id}` - Player details
- `POST /compare` - Compare multiple players
- `POST /advisor` - Get AI team advice
- `GET /projections/{id}` - Player projections
- `POST /transfer-scenario` - Analyze transfers
- `GET /fixtures/{team_id}` - Fixture difficulty
- `GET /team/{team_id}/picks` - Get team picks and lineup
- `GET /team/{team_id}/advisor` - Get automatic team advice
- `GET /team/{team_id}/summary` - Get team summary with projections
- `GET /team/{team_id}/projections` - Get team projection aggregates

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

# Get team picks (new team-centric endpoint)
curl "http://localhost:8000/team/123456/picks"

# Get automatic team advice (new team-centric endpoint)
curl "http://localhost:8000/team/123456/advisor?horizon=5&free_transfers=1"

# Get team summary with breakdown (new team-centric endpoint)
curl "http://localhost:8000/team/123456/summary?horizon=5"
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

### Advanced Metrics Configuration

The toolkit supports enhanced projections using advanced metrics:

```bash
# Enable/disable advanced metrics
ENABLE_ADVANCED_METRICS=true
ENABLE_ZONE_WEAKNESS=true

# Data file paths (sample data included)
XGXA_DATA_FILE=data/xgxa_sample.json
ZONE_WEAKNESS_DATA_FILE=data/zone_weakness_sample.json

# Fallback behavior when data unavailable
ADVANCED_METRICS_FALLBACK=sample_data
```

**Advanced Metrics Features:**
- **xG/xA Integration**: Expected goals and assists data enhances projection accuracy
- **Zone Weakness Analysis**: Team-specific defensive vulnerabilities by attack zone
- **Position-Based Adjustments**: Different attack patterns for forwards, midfielders, defenders
- **Sample Data Included**: Development-ready with realistic sample datasets
- **Graceful Fallback**: Works seamlessly when advanced data is unavailable

## Deployment

### Docker Deployment

Build and run with Docker:

```bash
# Build the Docker image
docker build -t fpl-toolkit .

# Run the container
docker run -p 8000:8000 fpl-toolkit

# Access the API at http://localhost:8000
```

### Render Deployment

For easy deployment to Render:

1. Fork this repository
2. Connect your GitHub repo to Render
3. Create a new Web Service with these settings:
   - **Build Command**: `pip install '.[web]'`
   - **Start Command**: `python -m fpl_toolkit.cli serve --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11

### Other Cloud Platforms

The included Dockerfile works with any container-based hosting:
- Heroku (using heroku.yml)
- Google Cloud Run  
- AWS ECS/Fargate
- Azure Container Instances

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

## Support & Documentation

### 📖 Complete Documentation
Comprehensive guides available in the `Documentation/` directory:

- **[🚀 Quick Start](Documentation/Quick-Start.md)** - Get up and running in minutes
- **[⚙️ Setup & Installation](Documentation/Setup-Installation.md)** - Complete setup guide
- **[🎯 Features Overview](Documentation/Features.md)** - All available functionality
- **[🛠️ API Reference](Documentation/API-Reference.md)** - REST API documentation
- **[💻 CLI Reference](Documentation/CLI-Reference.md)** - Command-line tools
- **[🏗️ Technical Stack](Documentation/Technical-Stack.md)** - Architecture overview
- **[🚀 Deployment Guide](Documentation/Deployment.md)** - Production deployment
- **[📋 Best Practices](Documentation/Best-Practices.md)** - Development guidelines
- **[🔧 Troubleshooting](Documentation/Troubleshooting.md)** - Common issues & solutions

> **📋 Documentation Index**: [Documentation/README.md](Documentation/README.md)

### 🆘 Getting Help
- 🐛 **Issues**: Report bugs on [GitHub Issues](https://github.com/AmberMaze/Fpl-toolkit/issues)
- 💬 **Discussions**: Ask questions in [GitHub Discussions](https://github.com/AmberMaze/Fpl-toolkit/discussions)
- 📧 **Contact**: Create an issue for direct support

---

Built with ❤️ for the FPL community