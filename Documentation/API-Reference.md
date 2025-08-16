# API Reference

Complete documentation for the FPL Toolkit REST API endpoints.

## 🌐 Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-api-domain.com`

## 📊 Core Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### Players

#### Get All Players

```http
GET /players
```

**Query Parameters:**
- `position` (optional): Filter by position (GK, DEF, MID, FWD)
- `team` (optional): Filter by team ID
- `min_price` (optional): Minimum price in millions
- `max_price` (optional): Maximum price in millions
- `limit` (optional): Limit results (default: 50)

**Response:**
```json
{
  "players": [
    {
      "id": 1,
      "name": "Erling Haaland",
      "team": "Manchester City",
      "position": "FWD",
      "price": 14.0,
      "total_points": 250,
      "form": "8.5",
      "selected_by_percent": "45.2"
    }
  ],
  "total": 100,
  "page": 1
}
```

#### Get Player Details

```http
GET /players/{player_id}
```

**Response:**
```json
{
  "id": 1,
  "name": "Erling Haaland",
  "team": "Manchester City",
  "position": "FWD",
  "price": 14.0,
  "total_points": 250,
  "form": "8.5",
  "selected_by_percent": "45.2",
  "history": [
    {
      "gameweek": 1,
      "points": 12,
      "goals": 2,
      "assists": 0,
      "minutes": 90
    }
  ],
  "projections": {
    "next_5_gameweeks": {
      "expected_points": 45.2,
      "confidence": 0.85
    }
  }
}
```

### Teams

#### Get All Teams

```http
GET /teams
```

**Response:**
```json
{
  "teams": [
    {
      "id": 1,
      "name": "Arsenal",
      "short_name": "ARS",
      "strength": 5,
      "strength_overall_home": 1320,
      "strength_overall_away": 1285
    }
  ]
}
```

#### Get Team Details

```http
GET /teams/{team_id}
```

**Response:**
```json
{
  "id": 1,
  "name": "Arsenal",
  "short_name": "ARS",
  "strength": 5,
  "fixtures": [
    {
      "gameweek": 15,
      "opponent": "Chelsea",
      "is_home": true,
      "difficulty": 4
    }
  ],
  "players": [
    {
      "id": 10,
      "name": "Bukayo Saka",
      "position": "MID",
      "price": 8.5
    }
  ]
}
```

### Analysis Endpoints

#### Player Projections

```http
GET /analysis/projections/players
```

**Query Parameters:**
- `position` (optional): Filter by position
- `horizon` (optional): Projection horizon in gameweeks (default: 5)
- `limit` (optional): Limit results (default: 20)

**Response:**
```json
{
  "projections": [
    {
      "player_id": 1,
      "name": "Erling Haaland",
      "expected_points": 45.2,
      "confidence": 0.85,
      "horizon_gameweeks": 5,
      "breakdown": {
        "goals": 3.2,
        "assists": 1.1,
        "clean_sheets": 0.5,
        "bonus": 2.1
      }
    }
  ]
}
```

#### Transfer Analysis

```http
POST /analysis/transfers
```

**Request Body:**
```json
{
  "player_out": 123,
  "player_in": 456,
  "gameweeks_horizon": 5,
  "budget_remaining": 2.5
}
```

**Response:**
```json
{
  "recommendation": "proceed",
  "confidence": 0.78,
  "expected_points_gain": 8.5,
  "analysis": {
    "player_out": {
      "name": "Player A",
      "expected_points": 20.5
    },
    "player_in": {
      "name": "Player B", 
      "expected_points": 29.0
    },
    "net_gain": 8.5,
    "risk_factors": ["injury_prone", "rotation_risk"]
  }
}
```

#### Fixture Difficulty

```http
GET /analysis/fixtures
```

**Query Parameters:**
- `team_id` (optional): Specific team
- `gameweeks` (optional): Number of gameweeks to analyze (default: 5)

**Response:**
```json
{
  "fixtures": [
    {
      "team_id": 1,
      "team_name": "Arsenal", 
      "next_5_fixtures": [
        {
          "gameweek": 15,
          "opponent": "Chelsea",
          "difficulty": 4,
          "is_home": true
        }
      ],
      "average_difficulty": 3.2,
      "attacking_potential": 0.85,
      "defensive_potential": 0.72
    }
  ]
}
```

## 🤖 AI Advisor Endpoints

### Team Analysis

```http
POST /ai/analyze-team
```

**Request Body:**
```json
{
  "team_id": 12345,
  "budget": 100.0,
  "gameweeks_horizon": 5,
  "strategy": "aggressive"
}
```

**Response:**
```json
{
  "overall_score": 8.2,
  "recommendations": [
    {
      "type": "transfer",
      "priority": "high",
      "description": "Consider transferring out Player X for Player Y",
      "expected_gain": 5.2,
      "confidence": 0.82
    }
  ],
  "team_analysis": {
    "strengths": ["Strong midfield", "Good fixture run"],
    "weaknesses": ["Weak defense", "Price-locked forwards"],
    "suggestions": ["Upgrade defense", "Monitor rotation"]
  }
}
```

### Player Recommendations

```http
GET /ai/recommendations/players
```

**Query Parameters:**
- `position`: Required position (GK, DEF, MID, FWD)
- `max_price`: Maximum price
- `exclude_teams`: Comma-separated team IDs to exclude
- `strategy`: Investment strategy (conservative, balanced, aggressive)

**Response:**
```json
{
  "recommendations": [
    {
      "player_id": 123,
      "name": "Player Name",
      "team": "Team Name",
      "price": 8.5,
      "recommendation_score": 9.2,
      "reasoning": [
        "Excellent fixture run",
        "High expected goals",
        "Good value for money"
      ],
      "risk_level": "low",
      "confidence": 0.89
    }
  ]
}
```

## 🔐 Authentication

Currently, the API is open and doesn't require authentication. For production deployments, consider implementing:

- API key authentication
- Rate limiting
- CORS configuration

## ⚡ Rate Limiting

- **Development**: No limits
- **Production**: 100 requests per minute per IP

## 📱 Mobile Optimization

All endpoints are optimized for mobile consumption:
- Limited array sizes (3-5 items by default)
- Compressed response format
- Essential data prioritization

## 🔄 Caching

The API implements intelligent caching:
- **Player data**: 1 hour TTL
- **Live data**: 15 minutes TTL
- **Static data**: 24 hours TTL

## 📊 Response Format

All API responses follow a consistent format:

### Success Response

```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456",
    "cache_hit": true
  }
}
```

### Error Response

```json
{
  "error": {
    "code": "PLAYER_NOT_FOUND",
    "message": "Player with ID 999 not found",
    "details": {}
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456"
  }
}
```

## 🔧 Development

### Testing Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get players
curl "http://localhost:8000/players?position=FWD&limit=5"

# Player details
curl http://localhost:8000/players/123

# Transfer analysis
curl -X POST http://localhost:8000/analysis/transfers \
  -H "Content-Type: application/json" \
  -d '{"player_out": 123, "player_in": 456, "gameweeks_horizon": 5}'
```

### Interactive Documentation

When running locally, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🎯 Best Practices

1. **Always handle errors** - Check response status codes
2. **Respect rate limits** - Implement client-side throttling
3. **Cache responses** - Avoid redundant requests
4. **Use query parameters** - Filter data efficiently
5. **Monitor performance** - Track response times

---

*For implementation examples, see the [User Guide](./User-Guide.md) or explore the [TypeScript client](../frontend/src/lib/api.ts).*