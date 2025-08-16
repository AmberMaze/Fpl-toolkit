# Quick Start Guide

Get up and running with the FPL Toolkit in minutes.

## ⚡ Fastest Setup

### 1-Command Installation

```bash
# Clone and setup everything automatically
git clone https://github.com/AmberMaze/Fpl-toolkit.git
cd Fpl-toolkit
chmod +x scripts/setup.sh && ./scripts/setup.sh
```

**What this does:**
- ✅ Creates Python virtual environment  
- ✅ Installs all dependencies (AI features if available)
- ✅ Sets up database and configuration
- ✅ Runs verification tests
- ✅ Provides next steps

### 2. Start Using

```bash
# Activate environment
source venv/bin/activate

# Start API server
fpl-toolkit serve --reload

# Start Streamlit dashboard (new terminal)
fpl-toolkit streamlit

# Start frontend (if Node.js available)
cd frontend && npm run dev
```

**Access Points:**
- 🌐 **API**: http://localhost:8000/docs
- 📊 **Dashboard**: http://localhost:8501  
- 💻 **Frontend**: http://localhost:3000

## 🎯 First Steps Tutorial

### Get Team Analysis

**Using CLI:**
```bash
# Analyze your team (replace with your team ID)
fpl-toolkit team-advisor 123456

# Get player projections
fpl-toolkit projections 123 --gameweeks 5

# Compare players
fpl-toolkit compare 123 456 789
```

**Using API:**
```bash
# Get team advice automatically
curl http://localhost:8000/team/123456/advisor

# Get detailed team summary
curl http://localhost:8000/team/123456/summary

# Find transfer targets
curl http://localhost:8000/transfer-targets/123
```

**Using Streamlit:**
1. Go to http://localhost:8501
2. Enter your team ID in the sidebar
3. Explore AI recommendations and visualizations
4. Use comparison tools for player analysis

### Analyze Transfer Scenarios

**CLI Example:**
```bash
# Should I transfer out Haaland (123) for Kane (456)?
fpl-toolkit transfer-scenario 123 456 --horizon 5

# Find the best replacements for a player
fpl-toolkit transfer-targets 123 --budget 2.5
```

**API Example:**
```bash
curl -X POST http://localhost:8000/transfer-scenario \
  -H "Content-Type: application/json" \
  -d '{
    "player_out_id": 123,
    "player_in_id": 456,
    "horizon_gameweeks": 5
  }'
```

### Get Player Insights

**Find Top Performers:**
```bash
# Top projected players by position
fpl-toolkit players --position MID --sort projected_points --limit 10

# Undervalued players (value picks)
fpl-toolkit players --max-cost 8.0 --min-form 5.0
```

**Compare Options:**
```bash
# Compare three midfielders
fpl-toolkit compare 234 345 456

# Get detailed player breakdown
fpl-toolkit player-details 234
```

## 🎮 Common Workflows

### Weekly Team Check

```bash
# 1. Get your team's status
fpl-toolkit team-advisor $YOUR_TEAM_ID

# 2. Check for urgent transfers
fpl-toolkit team-summary $YOUR_TEAM_ID --highlight-issues

# 3. Review upcoming fixtures
fpl-toolkit fixtures --weeks 3
```

### Transfer Planning

```bash
# 1. Identify weak players
fpl-toolkit team-analysis $YOUR_TEAM_ID --show-underperformers

# 2. Find replacement targets
fpl-toolkit transfer-targets $WEAK_PLAYER_ID --budget $AVAILABLE_BUDGET

# 3. Analyze specific transfers
fpl-toolkit transfer-scenario $OUT_PLAYER $IN_PLAYER
```

### Captain Selection

```bash
# 1. Get top captain options
fpl-toolkit captain-picks --gameweek next

# 2. Compare captain candidates
fpl-toolkit compare $CAPTAIN_OPTION_1 $CAPTAIN_OPTION_2 $CAPTAIN_OPTION_3

# 3. Check fixture difficulty
fpl-toolkit fixtures $TEAM_ID --weeks 1
```

## 📱 Interface Overview

### Streamlit Dashboard

**Main Features:**
- **Team Analysis**: Comprehensive squad evaluation
- **Player Comparison**: Side-by-side player stats
- **Transfer Planner**: What-if scenario analysis
- **Fixture Calendar**: Upcoming match difficulty

**Quick Navigation:**
1. **Sidebar**: Team ID input and settings
2. **Main Tabs**: Analysis, Comparison, Planning
3. **Export**: Download charts and data

### Next.js Frontend

**Pages:**
- **Dashboard**: Overview with key metrics
- **Team Analysis**: AI-powered insights
- **Player Search**: Filter and compare players

**Mobile Features:**
- Responsive design for all devices
- Touch-optimized interactions
- Progressive Web App capabilities

### CLI Tools

**Essential Commands:**
```bash
fpl-toolkit --help                    # Show all commands
fpl-toolkit serve                     # Start API server
fpl-toolkit streamlit                 # Start dashboard
fpl-toolkit init                      # Setup database
fpl-toolkit team-advisor <id>         # Team analysis
fpl-toolkit compare <id1> <id2> <id3> # Player comparison
fpl-toolkit projections <id>          # Player projections
```

## 🔧 Configuration

### Basic Settings

Edit `.env` file for customization:
```bash
# Database (SQLite by default)
DATABASE_URL=sqlite:///fpl_toolkit.db

# Cache settings
CACHE_TTL_SECONDS=3600

# Features
ENABLE_ADVANCED_METRICS=true
DEBUG=false
```

### Advanced Configuration

**PostgreSQL Database:**
```bash
# Replace SQLite with PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost:5432/fpl_toolkit
```

**AI Features:**
```bash
# Install AI dependencies
pip install -e ".[ai]"

# Verify AI availability
python -c "from src.fpl_toolkit.ai.advisor import FPLAdvisor; print('AI Ready')"
```

**API Customization:**
```bash
# Custom port
fpl-toolkit serve --port 8080

# External access
fpl-toolkit serve --host 0.0.0.0
```

## 🎯 Example Workflows

### New User Onboarding

```bash
# 1. First setup
./scripts/setup.sh

# 2. Find your team ID from FPL website
# Visit: https://fantasy.premierleague.com/entry/YOUR_TEAM_ID/

# 3. Get instant team analysis
fpl-toolkit team-advisor YOUR_TEAM_ID

# 4. Explore Streamlit dashboard
fpl-toolkit streamlit
# Visit: http://localhost:8501
```

### Weekly Routine

```bash
# Monday: Review previous gameweek
fpl-toolkit team-summary $TEAM_ID --gameweek previous

# Wednesday: Plan transfers
fpl-toolkit team-advisor $TEAM_ID --free-transfers 1

# Friday: Final captain choice
fpl-toolkit captain-picks --gameweek next

# Saturday: Last-minute checks
fpl-toolkit team-status $TEAM_ID
```

### Transfer Window

```bash
# Evaluate current team
fpl-toolkit team-analysis $TEAM_ID --horizon 5

# Find best value players
fpl-toolkit players --sort value --position ALL --limit 20

# Plan multiple transfers
fpl-toolkit wildcard-planner $TEAM_ID --budget 100.0
```

## 🆘 Quick Troubleshooting

### Common Issues

**Installation Problems:**
```bash
# Clear and reinstall
rm -rf venv
./scripts/setup.sh

# Check Python version
python3 --version  # Should be 3.10+
```

**API Not Working:**
```bash
# Check if server is running
curl http://localhost:8000/health

# Restart with debug
fpl-toolkit serve --reload --debug
```

**Database Issues:**
```bash
# Reset database
rm fpl_toolkit.db
fpl-toolkit init
```

**AI Features Missing:**
```bash
# Install AI dependencies
pip install -e ".[ai]"

# Verify installation
python -c "import sentence_transformers; print('AI Ready')"
```

### Getting Help

- 📖 **Documentation**: Check `Documentation/` folder
- 🐛 **Issues**: https://github.com/AmberMaze/Fpl-toolkit/issues
- 💬 **Discussions**: GitHub Discussions tab
- 📧 **Contact**: Create an issue for support

## 🚀 Next Steps

After getting started:

1. 📖 **Read Features Guide**: Learn about all capabilities
2. 🔧 **Explore CLI**: Master command-line tools
3. 🎨 **Customize Dashboard**: Personalize your analysis
4. 🤖 **Try AI Features**: Experience ML-powered insights
5. 🌐 **Deploy Online**: Set up production deployment

---

*Ready to dive deeper? Check out the [Features Guide](./Features.md) for comprehensive capabilities or the [User Guide](./User-Guide.md) for detailed usage instructions.*