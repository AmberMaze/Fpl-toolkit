# API Reference

This document provides comprehensive reference for the FPL Toolkit FastAPI endpoints.

## Base Information

- **Base URL**: `http://localhost:8000` (development)
- **Content-Type**: `application/json`
- **CORS**: Enabled for all origins (configure for production)

## Authentication

Currently no authentication required. All endpoints are public.

## Rate Limiting

- **Client-side caching**: 1 hour default TTL
- **Respectful usage**: Built-in delays to protect FPL API
- **Error handling**: Graceful degradation on API failures

## Core Endpoints

### Health Check

#### `GET /health`

Check API health status.

**Response:**
```json
{
  "status": "ok",
  "service": "fpl-toolkit-api"
}
```

**Status Codes:**
- `200`: Service healthy

---

### Root Information

#### `GET /`

Get API information and available endpoints.

**Response:**
```json
{
  "message": "FPL Toolkit API",
  "version": "0.1.0",
  "endpoints": {
    "health": "/health",
    "players": "/players",
    "player_detail": "/player/{id}",
    "compare": "/compare",
    "advisor": "/advisor",
    "projections": "/projections/{id}",
    "transfer_scenario": "/transfer-scenario",
    "fixture_difficulty": "/fixtures/{team_id}",
    "team_summary": "/team/{team_id}/summary"
  }
}
```

---

## Player Endpoints

### List Players

#### `GET /players`

Get filtered list of players.

**Query Parameters:**
- `position` (optional): Filter by position (`GK`, `DEF`, `MID`, `FWD`)
- `max_cost` (optional): Maximum cost in millions (float)
- `min_points` (optional): Minimum total points (integer)
- `limit` (optional): Maximum results to return (default: 50)

**Example Request:**
```bash
GET /players?position=MID&max_cost=10.0&limit=20
```

**Response:**
```json
[
  {
    "id": 123,
    "name": "Mohamed Salah",
    "team_id": 14,
    "position": "MID",
    "cost": 12.5,
    "total_points": 180,
    "form": 5.2,
    "selected_by_percent": 45.8,
    "status": "a"
  }
]
```

**Status Codes:**
- `200`: Success
- `500`: Server error

---

### Player Details

#### `GET /player/{player_id}`

Get detailed information for a specific player.

**Path Parameters:**
- `player_id` (required): FPL player ID (integer)

**Example Request:**
```bash
GET /player/123
```

**Response:**
```json
{
  "id": 123,
  "name": "Mohamed Salah",
  "team_id": 14,
  "position": "MID",
  "cost": 12.5,
  "total_points": 180,
  "form": 5.2,
  "selected_by_percent": 45.8,
  "status": "a",
  "points_per_game": 7.2,
  "minutes": 2250,
  "goals_scored": 18,
  "assists": 12,
  "clean_sheets": 8,
  "recent_history": [
    {
      "round": 25,
      "total_points": 12
    }
  ],
  "upcoming_fixtures": [
    {
      "event": 26,
      "opponent_team": 6,
      "is_home": true
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `404`: Player not found
- `500`: Server error

---

## Analysis Endpoints

### Compare Players

#### `POST /compare`

Compare multiple players over a time horizon.

**Request Body:**
```json
{
  "player_ids": [123, 456, 789],
  "horizon_gameweeks": 5
}
```

**Request Schema:**
- `player_ids` (required): Array of player IDs (2-10 players)
- `horizon_gameweeks` (optional): Analysis timeframe (default: 5)

**Response:**
```json
{
  "comparisons": [
    {
      "name": "Mohamed Salah",
      "cost": 12.5,
      "current_points": 180,
      "total_projected_points": 42.5,
      "average_confidence": 0.85,
      "points_per_million": 3.4
    }
  ],
  "best_projection": {
    "name": "Mohamed Salah",
    "total_projected_points": 42.5
  },
  "horizon_gameweeks": 5,
  "players_compared": 3
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid request (wrong number of players)
- `500`: Server error

---

### Player Projections

#### `GET /projections/{player_id}`

Get projection for a specific player and gameweek.

**Path Parameters:**
- `player_id` (required): FPL player ID

**Query Parameters:**
- `gameweek` (optional): Target gameweek (default: next gameweek)

**Example Request:**
```bash
GET /projections/123?gameweek=26
```

**Response:**
```json
{
  "player_id": 123,
  "gameweek": 26,
  "projected_points": 8.5,
  "projected_minutes": 90,
  "confidence_score": 0.82,
  "fixture_difficulty": 3.0
}
```

**Status Codes:**
- `200`: Success
- `404`: Player not found or no projection data
- `500`: Server error

---

## Decision Support Endpoints

### AI Advisor

#### `POST /advisor`

Get AI-powered team advice and recommendations.

**Request Body:**
```json
{
  "player_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
  "budget": 2.5,
  "free_transfers": 1,
  "horizon_gameweeks": 5
}
```

**Request Schema:**
- `player_ids` (required): Array of current team player IDs
- `budget` (optional): Available budget in millions (default: 100.0)
- `free_transfers` (optional): Number of free transfers (default: 1)
- `horizon_gameweeks` (optional): Analysis timeframe (default: 5)

**Response:**
```json
{
  "summary": "Team looks solid with 75.5 projected points. 1 player needs attention.",
  "recommendations": [
    {
      "type": "transfer",
      "priority": "high",
      "message": "Consider transferring out Problem Player due to injury concerns"
    }
  ],
  "underperformers": [
    {
      "player": {
        "id": 456,
        "name": "Problem Player"
      },
      "issues": ["Injury concerns", "Poor form"],
      "priority": 3
    }
  ],
  "top_differentials": [
    {
      "name": "Differential Pick",
      "ownership": 3.2,
      "points_per_game": 5.1,
      "differential_score": 1.59
    }
  ],
  "transfer_suggestions": [
    {
      "player_out": {
        "name": "Problem Player"
      },
      "suggestions": [
        {
          "player_in_name": "Better Option",
          "projected_points_gain": 3.2,
          "recommendation": "Recommended"
        }
      ]
    }
  ],
  "horizon_gameweeks": 5
}
```

**Status Codes:**
- `200`: Success
- `500`: Server error

---

### Transfer Scenario Analysis

#### `POST /transfer-scenario`

Analyze a specific transfer scenario.

**Request Body:**
```json
{
  "player_out_id": 123,
  "player_in_id": 456,
  "horizon_gameweeks": 5
}
```

**Request Schema:**
- `player_out_id` (required): Player to transfer out
- `player_in_id` (required): Player to transfer in
- `horizon_gameweeks` (optional): Analysis timeframe (default: 5)

**Response:**
```json
{
  "player_out_name": "Current Player",
  "player_in_name": "Target Player",
  "cost_change": 1.5,
  "projected_points_gain": 5.2,
  "confidence_score": 0.75,
  "risk_score": 0.3,
  "recommendation": "Recommended",
  "reasoning": "Strong projected gain of 5.2 points over 5 gameweeks. Costs £1.5m more.",
  "horizon_gameweeks": 5
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid player IDs
- `500`: Server error

---

### Transfer Targets

#### `GET /transfer-targets/{player_id}`

Find suitable transfer targets for a given player.

**Path Parameters:**
- `player_id` (required): Player to replace

**Query Parameters:**
- `max_cost_increase` (optional): Maximum cost increase allowed (default: 2.0)
- `limit` (optional): Maximum suggestions (default: 5)

**Example Request:**
```bash
GET /transfer-targets/123?max_cost_increase=1.5&limit=3
```

**Response:**
```json
{
  "player_id": 123,
  "transfer_targets": [
    {
      "player_in_name": "Best Option",
      "cost_change": 0.5,
      "projected_points_gain": 4.2,
      "recommendation": "Strongly Recommended",
      "confidence_score": 0.85,
      "risk_score": 0.2
    }
  ],
  "max_cost_increase": 1.5
}
```

**Status Codes:**
- `200`: Success
- `500`: Server error

---

## Fixture Analysis Endpoints

### Fixture Difficulty

#### `GET /fixtures/{team_id}`

Get fixture difficulty analysis for a team.

**Path Parameters:**
- `team_id` (required): FPL team ID

**Query Parameters:**
- `next_n` (optional): Number of fixtures to analyze (default: 5)

**Example Request:**
```bash
GET /fixtures/14?next_n=8
```

**Response:**
```json
{
  "team_id": 14,
  "average_difficulty": 2.8,
  "difficulty_trend": "getting_easier",
  "fixtures": [
    {
      "gameweek": 26,
      "opponent_id": 6,
      "opponent_name": "Brighton",
      "is_home": true,
      "difficulty": 2.5,
      "kickoff_time": "2024-02-10T15:00:00Z"
    }
  ],
  "home_fixtures": 3,
  "away_fixtures": 2
}
```

**Status Codes:**
- `200`: Success
- `500`: Server error

---

## Team Management Endpoints

### Team Summary

#### `GET /team/{team_id}/summary`

Get comprehensive team summary including captain/vice captain names and enhanced player breakdowns with optional advanced metrics.

**Path Parameters:**
- `team_id` (required): FPL manager team ID

**Query Parameters:**
- `gameweek` (optional): Target gameweek (default: current gameweek)

**Example Request:**
```bash
GET /team/12345/summary?gameweek=10
```

**Response:**
```json
{
  "team_id": 12345,
  "team_name": "Amber's Arsenal",
  "manager_name": "Amber Bridgers",
  "total_points": 1847,
  "gameweek_points": 78,
  "overall_rank": 125000,
  "gameweek_rank": 89000,
  "captain": 283,
  "vice_captain": 254,
  "captain_name": "Erling Haaland",
  "vice_captain_name": "Mohamed Salah",
  "players": [
    {
      "id": 283,
      "name": "Erling Haaland",
      "position": "FWD",
      "team_id": 1,
      "cost": 13.0,
      "total_points": 267,
      "is_captain": true,
      "is_vice_captain": false,
      "multiplier": 2,
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
  ],
  "transfers_made": 1,
  "free_transfers": 1,
  "bank_balance": 1.5,
  "gameweek": 10
}
```

**Breakdown Fields:**
- `appearance`: Base appearance points
- `goals`: Projected goal points
- `assists`: Projected assist points  
- `cs`: Clean sheet points (defenders/goalkeepers)
- `bonus`: Bonus point projection
- `misc`: Miscellaneous points (saves, etc.)
- `total`: Sum of all breakdown components
- `adjustments` (optional): Advanced metrics applied
  - `xg_per90`: Expected goals per 90 minutes
  - `xa_per90`: Expected assists per 90 minutes  
  - `zone_multiplier`: Zone weakness adjustment factor

**Status Codes:**
- `200`: Success
- `404`: Team not found
- `500`: Server error

**Notes:**
- Captain and vice captain names are resolved from the player database
- Enhanced breakdowns include optional advanced metrics when available
- Zone adjustments consider opponent team weaknesses
- Graceful fallback when advanced metrics unavailable

---

## Error Handling

### Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common Error Codes

- **400 Bad Request**: Invalid input parameters
- **404 Not Found**: Resource not found (player, gameweek, etc.)
- **500 Internal Server Error**: Server-side error
- **503 Service Unavailable**: FPL API temporarily unavailable

### Example Error Responses

**400 Bad Request:**
```json
{
  "detail": "At least 2 players required for comparison"
}
```

**404 Not Found:**
```json
{
  "detail": "Player not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error fetching players: Connection timeout"
}
```

---

## Data Models

### PlayerResponse
```typescript
interface PlayerResponse {
  id: number;
  name: string;
  team_id: number;
  position: "GK" | "DEF" | "MID" | "FWD";
  cost: number;
  total_points: number;
  form: number;
  selected_by_percent: number;
  status: string;
}
```

### ProjectionResponse
```typescript
interface ProjectionResponse {
  player_id: number;
  gameweek: number;
  projected_points: number;
  projected_minutes: number;
  confidence_score: number;
  fixture_difficulty: number;
}
```

### ComparisonRequest
```typescript
interface ComparisonRequest {
  player_ids: number[];
  horizon_gameweeks?: number; // default: 5
}
```

### AdvisorRequest
```typescript
interface AdvisorRequest {
  player_ids: number[];
  budget?: number; // default: 100.0
  free_transfers?: number; // default: 1
  horizon_gameweeks?: number; // default: 5
}
```

### TransferScenarioRequest
```typescript
interface TransferScenarioRequest {
  player_out_id: number;
  player_in_id: number;
  horizon_gameweeks?: number; // default: 5
}
```

---

## Usage Examples

### JavaScript/Fetch
```javascript
// Get players
const players = await fetch('/players?position=MID&max_cost=10.0')
  .then(res => res.json());

// Compare players
const comparison = await fetch('/compare', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    player_ids: [123, 456, 789],
    horizon_gameweeks: 5
  })
}).then(res => res.json());

// Get team advice
const advice = await fetch('/advisor', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    player_ids: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
    budget: 2.5,
    free_transfers: 1
  })
}).then(res => res.json());
```

### Python/Requests
```python
import requests

base_url = "http://localhost:8000"

# Get players
players = requests.get(f"{base_url}/players", params={
    "position": "MID",
    "max_cost": 10.0
}).json()

# Compare players
comparison = requests.post(f"{base_url}/compare", json={
    "player_ids": [123, 456, 789],
    "horizon_gameweeks": 5
}).json()

# Analyze transfer
scenario = requests.post(f"{base_url}/transfer-scenario", json={
    "player_out_id": 123,
    "player_in_id": 456
}).json()
```

### cURL Examples
```bash
# Get midfielders under £10m
curl "http://localhost:8000/players?position=MID&max_cost=10.0"

# Compare three players
curl -X POST "http://localhost:8000/compare" \
  -H "Content-Type: application/json" \
  -d '{"player_ids": [123, 456, 789]}'

# Get fixture difficulty
curl "http://localhost:8000/fixtures/14?next_n=5"

# Analyze transfer scenario
curl -X POST "http://localhost:8000/transfer-scenario" \
  -H "Content-Type: application/json" \
  -d '{"player_out_id": 123, "player_in_id": 456}'
```

---

## Performance Notes

- **Caching**: Responses are cached for 1 hour by default
- **Async Processing**: All endpoints are async for better concurrency
- **Database**: SQLite for development, PostgreSQL recommended for production
- **Memory Usage**: Typical response times <500ms for cached data

## Security Notes

- **CORS**: Currently allows all origins (configure for production)
- **Rate Limiting**: Built-in client-side caching reduces API load
- **Input Validation**: All inputs are validated using Pydantic models
- **SQL Injection**: Protected by SQLAlchemy ORM