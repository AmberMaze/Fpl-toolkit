# CLI Reference

Complete command-line interface reference for the FPL Toolkit.

## 🎯 Overview

The FPL Toolkit provides a rich command-line interface with emoji-enhanced output, colored formatting, and comprehensive functionality for Fantasy Premier League analysis.

**Installation Check:**
```bash
fpl-toolkit --version  # Check if installed correctly
fpl-toolkit --help     # Show all available commands
```

## 🚀 Server Commands

### Start API Server

```bash
fpl-toolkit serve [OPTIONS]
```

**Options:**
- `--host TEXT`: Host to bind to (default: 127.0.0.1)
- `--port INTEGER`: Port to bind to (default: 8000)
- `--reload`: Enable auto-reload for development
- `--workers INTEGER`: Number of worker processes
- `--cors-allow-all`: Enable CORS for all origins
- `--debug`: Enable debug mode

**Examples:**
```bash
# Development server with auto-reload
fpl-toolkit serve --reload

# Production server
fpl-toolkit serve --host 0.0.0.0 --port 8000 --workers 4

# Server with CORS enabled
fpl-toolkit serve --cors-allow-all

# Debug mode
fpl-toolkit serve --debug --reload
```

### Start Streamlit Dashboard

```bash
fpl-toolkit streamlit [OPTIONS]
```

**Options:**
- `--port INTEGER`: Port for Streamlit (default: 8501)
- `--host TEXT`: Host to bind to (default: localhost)

**Examples:**
```bash
# Start dashboard
fpl-toolkit streamlit

# Custom port
fpl-toolkit streamlit --port 8502

# External access
fpl-toolkit streamlit --host 0.0.0.0
```

## 🗄️ Database Commands

### Initialize Database

```bash
fpl-toolkit init [OPTIONS]
```

**Options:**
- `--reset`: Drop existing tables and recreate
- `--sample-data`: Load sample data for testing

**Examples:**
```bash
# Initialize database
fpl-toolkit init

# Reset and recreate
fpl-toolkit init --reset

# Initialize with sample data
fpl-toolkit init --sample-data
```

### Database Management

```bash
# Check database status
fpl-toolkit db-status

# Backup database
fpl-toolkit db-backup --output backup.db

# Restore database
fpl-toolkit db-restore --input backup.db

# Migrate database schema
fpl-toolkit db-migrate
```

## 👥 Team Analysis Commands

### Team Advisor

```bash
fpl-toolkit team-advisor TEAM_ID [OPTIONS]
```

**Arguments:**
- `TEAM_ID`: FPL team ID (required)

**Options:**
- `--horizon INTEGER`: Analysis horizon in gameweeks (default: 5)
- `--free-transfers INTEGER`: Number of free transfers (default: 1)
- `--budget FLOAT`: Available budget in millions (default: auto-detect)
- `--format [json|table|summary]`: Output format (default: summary)

**Examples:**
```bash
# Basic team analysis
fpl-toolkit team-advisor 123456

# Extended horizon analysis
fpl-toolkit team-advisor 123456 --horizon 8

# With specific transfer budget
fpl-toolkit team-advisor 123456 --budget 2.5 --free-transfers 2

# JSON output for scripting
fpl-toolkit team-advisor 123456 --format json
```

### Team Summary

```bash
fpl-toolkit team-summary TEAM_ID [OPTIONS]
```

**Options:**
- `--horizon INTEGER`: Analysis horizon (default: 5)
- `--show-bench`: Include bench players in analysis
- `--highlight-issues`: Highlight problematic players
- `--export TEXT`: Export to file (CSV, JSON)

**Examples:**
```bash
# Detailed team summary
fpl-toolkit team-summary 123456 --show-bench

# Export team analysis
fpl-toolkit team-summary 123456 --export team_analysis.csv

# Focus on issues
fpl-toolkit team-summary 123456 --highlight-issues
```

### Team Picks

```bash
fpl-toolkit team-picks TEAM_ID [OPTIONS]
```

**Options:**
- `--gameweek INTEGER`: Specific gameweek (default: current)
- `--format [table|json|lineup]`: Output format

**Examples:**
```bash
# Current gameweek picks
fpl-toolkit team-picks 123456

# Specific gameweek
fpl-toolkit team-picks 123456 --gameweek 25

# Lineup format
fpl-toolkit team-picks 123456 --format lineup
```

## 🎯 Player Analysis Commands

### Player Details

```bash
fpl-toolkit player-details PLAYER_ID [OPTIONS]
```

**Arguments:**
- `PLAYER_ID`: FPL player ID (required)

**Options:**
- `--include-history`: Show recent gameweek history
- `--include-fixtures`: Show upcoming fixtures
- `--horizon INTEGER`: Projection horizon (default: 5)

**Examples:**
```bash
# Basic player details
fpl-toolkit player-details 123

# Comprehensive analysis
fpl-toolkit player-details 123 --include-history --include-fixtures

# Extended projection
fpl-toolkit player-details 123 --horizon 10
```

### Player Comparison

```bash
fpl-toolkit compare PLAYER_ID1 PLAYER_ID2 [PLAYER_ID3...] [OPTIONS]
```

**Arguments:**
- `PLAYER_ID1, PLAYER_ID2, ...`: Player IDs to compare (2-10 players)

**Options:**
- `--horizon INTEGER`: Analysis horizon (default: 5)
- `--metrics [points|value|form|fixtures]`: Focus on specific metrics
- `--format [table|json|chart]`: Output format
- `--export TEXT`: Export comparison to file

**Examples:**
```bash
# Compare two players
fpl-toolkit compare 123 456

# Compare multiple players
fpl-toolkit compare 123 456 789 --horizon 8

# Focus on value metrics
fpl-toolkit compare 123 456 --metrics value

# Export comparison
fpl-toolkit compare 123 456 789 --export comparison.csv
```

### Player Search

```bash
fpl-toolkit players [OPTIONS]
```

**Options:**
- `--position [GK|DEF|MID|FWD]`: Filter by position
- `--team TEXT`: Filter by team name
- `--max-cost FLOAT`: Maximum cost in millions
- `--min-cost FLOAT`: Minimum cost in millions
- `--min-points INTEGER`: Minimum total points
- `--min-form FLOAT`: Minimum form rating
- `--sort [name|cost|points|form|value]`: Sort by field
- `--limit INTEGER`: Limit results (default: 20)
- `--format [table|json|list]`: Output format

**Examples:**
```bash
# All midfielders under £10m
fpl-toolkit players --position MID --max-cost 10.0

# High-form defenders
fpl-toolkit players --position DEF --min-form 5.0 --sort form

# Value picks
fpl-toolkit players --max-cost 8.0 --min-points 50 --sort value

# Export player list
fpl-toolkit players --position FWD --limit 50 --format json > forwards.json
```

## 🔄 Transfer Commands

### Transfer Scenario Analysis

```bash
fpl-toolkit transfer-scenario PLAYER_OUT_ID PLAYER_IN_ID [OPTIONS]
```

**Arguments:**
- `PLAYER_OUT_ID`: Player to transfer out
- `PLAYER_IN_ID`: Player to transfer in

**Options:**
- `--horizon INTEGER`: Analysis horizon (default: 5)
- `--cost-hit INTEGER`: Points hit for transfer (default: 0)
- `--format [summary|detailed|json]`: Output detail level

**Examples:**
```bash
# Basic transfer analysis
fpl-toolkit transfer-scenario 123 456

# With points hit consideration
fpl-toolkit transfer-scenario 123 456 --cost-hit 4

# Extended analysis
fpl-toolkit transfer-scenario 123 456 --horizon 8 --format detailed
```

### Transfer Targets

```bash
fpl-toolkit transfer-targets PLAYER_ID [OPTIONS]
```

**Arguments:**
- `PLAYER_ID`: Player to find replacements for

**Options:**
- `--budget FLOAT`: Additional budget available
- `--max-cost-increase FLOAT`: Maximum cost increase (default: 2.0)
- `--position [auto|GK|DEF|MID|FWD]`: Position filter (default: auto)
- `--limit INTEGER`: Number of suggestions (default: 10)
- `--sort [points|value|form]`: Sort criteria

**Examples:**
```bash
# Find replacement targets
fpl-toolkit transfer-targets 123

# With additional budget
fpl-toolkit transfer-targets 123 --budget 2.5

# Limit cost increase
fpl-toolkit transfer-targets 123 --max-cost-increase 1.0

# Best value targets
fpl-toolkit transfer-targets 123 --sort value --limit 5
```

### Wildcard Planner

```bash
fpl-toolkit wildcard-planner TEAM_ID [OPTIONS]
```

**Arguments:**
- `TEAM_ID`: Current team ID

**Options:**
- `--budget FLOAT`: Total budget (default: 100.0)
- `--formation [3-4-3|3-5-2|4-3-3|4-4-2|4-5-1|5-3-2|5-4-1]`: Formation
- `--horizon INTEGER`: Planning horizon (default: 10)
- `--risk-level [conservative|balanced|aggressive]`: Risk preference

**Examples:**
```bash
# Plan wildcard team
fpl-toolkit wildcard-planner 123456

# Specific formation and budget
fpl-toolkit wildcard-planner 123456 --formation 3-5-2 --budget 99.5

# Aggressive strategy
fpl-toolkit wildcard-planner 123456 --risk-level aggressive
```

## 📊 Analysis Commands

### Player Projections

```bash
fpl-toolkit projections PLAYER_ID [OPTIONS]
```

**Arguments:**
- `PLAYER_ID`: Player to project

**Options:**
- `--gameweeks INTEGER`: Number of gameweeks (default: 5)
- `--include-breakdown`: Show points breakdown
- `--confidence-threshold FLOAT`: Minimum confidence (0-1)
- `--format [table|json|chart]`: Output format

**Examples:**
```bash
# 5-gameweek projection
fpl-toolkit projections 123

# Detailed breakdown
fpl-toolkit projections 123 --include-breakdown

# High-confidence projections only
fpl-toolkit projections 123 --confidence-threshold 0.7
```

### Fixture Analysis

```bash
fpl-toolkit fixtures [OPTIONS]
```

**Options:**
- `--team TEXT`: Specific team name
- `--team-id INTEGER`: Specific team ID
- `--weeks INTEGER`: Number of weeks ahead (default: 5)
- `--difficulty-threshold INTEGER`: Show fixtures above difficulty (1-5)
- `--format [table|calendar|json]`: Output format

**Examples:**
```bash
# All fixtures next 5 weeks
fpl-toolkit fixtures

# Arsenal's fixtures
fpl-toolkit fixtures --team Arsenal

# Difficult fixtures only
fpl-toolkit fixtures --difficulty-threshold 4

# Calendar view
fpl-toolkit fixtures --format calendar --weeks 8
```

### Captain Recommendations

```bash
fpl-toolkit captain-picks [OPTIONS]
```

**Options:**
- `--gameweek [current|next|INTEGER]`: Target gameweek
- `--team-id INTEGER`: Consider only players in team
- `--risk-level [safe|balanced|differential]`: Captain strategy
- `--limit INTEGER`: Number of suggestions (default: 5)

**Examples:**
```bash
# Next gameweek captain picks
fpl-toolkit captain-picks

# Safe captain options
fpl-toolkit captain-picks --risk-level safe

# Differential captains
fpl-toolkit captain-picks --risk-level differential --limit 10
```

## 🤖 AI Commands

### AI Analysis

```bash
fpl-toolkit ai-analyze TEAM_ID [OPTIONS]
```

**Arguments:**
- `TEAM_ID`: Team to analyze

**Options:**
- `--depth [quick|standard|deep]`: Analysis depth
- `--include-sentiment`: Include sentiment analysis
- `--confidence-threshold FLOAT`: Minimum AI confidence (default: 0.6)

**Examples:**
```bash
# AI team analysis
fpl-toolkit ai-analyze 123456

# Deep analysis with sentiment
fpl-toolkit ai-analyze 123456 --depth deep --include-sentiment
```

### Similar Players

```bash
fpl-toolkit similar-players PLAYER_ID [OPTIONS]
```

**Arguments:**
- `PLAYER_ID`: Reference player

**Options:**
- `--similarity-threshold FLOAT`: Minimum similarity (default: 0.7)
- `--exclude-same-team`: Exclude players from same team
- `--limit INTEGER`: Number of suggestions (default: 10)

**Examples:**
```bash
# Find similar players
fpl-toolkit similar-players 123

# High similarity only
fpl-toolkit similar-players 123 --similarity-threshold 0.8

# Exclude same team
fpl-toolkit similar-players 123 --exclude-same-team
```

## 🔧 Utility Commands

### Cache Management

```bash
# Check cache status
fpl-toolkit cache-status

# Clear all caches
fpl-toolkit cache-clear

# Refresh specific data
fpl-toolkit cache-refresh [players|teams|fixtures]

# Set cache TTL
fpl-toolkit cache-config --ttl 7200  # 2 hours
```

### Data Sync

```bash
# Sync player data
fpl-toolkit sync-players

# Sync team data
fpl-toolkit sync-teams

# Sync gameweek data
fpl-toolkit sync-gameweeks

# Full data sync
fpl-toolkit sync-all
```

### Configuration

```bash
# Show current configuration
fpl-toolkit config-show

# Set configuration values
fpl-toolkit config-set --key CACHE_TTL_SECONDS --value 3600

# Reset to defaults
fpl-toolkit config-reset
```

## 📊 Output Formats

### Table Format (Default)

```bash
fpl-toolkit players --position FWD --limit 5
```

```
┌─────┬─────────────────┬──────┬─────────┬────────┬──────┐
│ ID  │ Name            │ Team │ Cost    │ Points │ Form │
├─────┼─────────────────┼──────┼─────────┼────────┼──────┤
│ 123 │ Erling Haaland  │ MCI  │ £14.0m  │ 250    │ 8.5  │
│ 456 │ Harry Kane      │ BAY  │ £12.5m  │ 220    │ 7.8  │
│ 789 │ Mohamed Salah   │ LIV  │ £13.0m  │ 240    │ 8.2  │
└─────┴─────────────────┴──────┴─────────┴────────┴──────┘
```

### JSON Format

```bash
fpl-toolkit team-advisor 123456 --format json
```

```json
{
  "team_id": 123456,
  "summary": "Team looks solid with 75.5 projected points",
  "recommendations": [
    {
      "type": "transfer",
      "priority": "high",
      "message": "Consider transferring out Player X"
    }
  ],
  "projected_points": 75.5,
  "confidence": 0.82
}
```

### Summary Format

```bash
fpl-toolkit team-advisor 123456 --format summary
```

```
🎯 FPL Team Analysis - Team ID: 123456
═══════════════════════════════════════════

📊 Overall Assessment: GOOD
🔮 Projected Points (5 GWs): 75.5 ± 8.2
💰 Budget Available: £2.5m
🔄 Free Transfers: 1

🚨 Priority Actions:
  1. Consider transferring out Player X (injury concerns)
  2. Captain Player Y for next gameweek

✨ Top Differentials:
  • Player Z (3.2% ownership) - High potential

💡 Recommendations:
  • Hold current formation
  • Use free transfer on Player X → Player A
  • Bank transfer if no urgent issues
```

## 🎨 Output Customization

### Color Output

```bash
# Enable/disable colors
export FPL_TOOLKIT_COLORS=true   # Enable colors
export FPL_TOOLKIT_COLORS=false  # Disable colors

# Or use flag
fpl-toolkit players --no-color
```

### Verbose Output

```bash
# Verbose mode
fpl-toolkit team-advisor 123456 --verbose

# Quiet mode (errors only)
fpl-toolkit team-advisor 123456 --quiet

# Debug mode
fpl-toolkit team-advisor 123456 --debug
```

## 🔍 Advanced Usage

### Piping and Scripting

```bash
# Chain commands
fpl-toolkit players --position FWD --format json | \
  jq '.[] | select(.form > 7.0)' | \
  fpl-toolkit compare --stdin

# Export and process
fpl-toolkit team-summary 123456 --export team.csv
python analyze_team.py team.csv

# Batch processing
for team_id in $(cat team_ids.txt); do
  fpl-toolkit team-advisor $team_id --format json >> analysis.jsonl
done
```

### Configuration Files

```bash
# Use configuration file
fpl-toolkit --config config.yaml team-advisor 123456

# Global configuration
export FPL_TOOLKIT_CONFIG=~/.fpl-toolkit.yaml
```

**config.yaml example:**
```yaml
api:
  cache_ttl: 3600
  timeout: 30

analysis:
  default_horizon: 5
  confidence_threshold: 0.7

output:
  format: table
  colors: true
  verbose: false
```

## 📋 Command Completion

### Bash Completion

```bash
# Install completion
fpl-toolkit --install-completion bash

# Or add to .bashrc
eval "$(_FPL_TOOLKIT_COMPLETE=bash_source fpl-toolkit)"
```

### Zsh Completion

```bash
# Install completion
fpl-toolkit --install-completion zsh

# Or add to .zshrc
eval "$(_FPL_TOOLKIT_COMPLETE=zsh_source fpl-toolkit)"
```

---

*For more examples and advanced usage patterns, see the [User Guide](./User-Guide.md) and [Quick Start Guide](./Quick-Start.md).*