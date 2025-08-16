# AI Tools Documentation

This document describes the AI-powered features of the FPL Toolkit, including heuristic rules, optional ML integration, and advisor functionality.

## FPL Advisor Overview

The `FPLAdvisor` class combines rule-based heuristics with optional machine learning models to provide intelligent FPL decision support.

```python
from fpl_toolkit.ai.advisor import FPLAdvisor

# Initialize advisor (automatically attempts to load ML model)
advisor = FPLAdvisor()

# Get comprehensive team advice
advice = advisor.advise_team(team_state)
```

## Heuristic Rules Engine

### Underperformer Detection

The advisor identifies players who may need replacing based on multiple criteria:

```python
def detect_underperformers(team_players, points_threshold=3.0, cost_threshold=8.0):
    """
    Detect underperforming players.
    
    Criteria:
    - Overall PPG below threshold
    - Premium players (£8m+) with PPG < 6.0  
    - Recent form below 2.0
    - Injury/suspension status
    """
```

#### Detection Rules
1. **Low Average Performance**
   - Players with PPG < 3.0 (default threshold)
   - Configurable based on user expectations

2. **Premium Underperformance**
   - Expensive players (≥£8.0m) with PPG < 6.0
   - Higher expectations for premium assets

3. **Poor Recent Form**
   - Form rating < 2.0 indicates recent struggles
   - Based on last 4-6 gameweeks

4. **Availability Issues**
   - Injured, suspended, or doubtful players
   - Status != "available"

#### Priority Scoring
```python
def calculate_priority(player, issues):
    """
    Priority = number of issues + premium bonus
    
    Premium bonus: +1 if cost >= £8m (expensive mistakes hurt more)
    """
    priority = len(issues)
    if player.cost >= 8.0:
        priority += 1
    return priority
```

### Fixture Swing Detection

Identifies teams with significant changes in fixture difficulty:

```python
def detect_fixture_swings(team_ids, horizon_gameweeks=5):
    """
    Find teams with improving or worsening fixtures.
    
    Categories:
    - "getting_easier": Later fixtures 0.5+ easier than early ones
    - "getting_harder": Later fixtures 0.5+ harder than early ones
    - "neutral": No significant trend
    """
```

#### Trend Classification
- **Minimum fixtures**: Requires ≥3 fixtures for trend analysis
- **Significance threshold**: 0.5 difficulty point difference
- **Comparison method**: Average of first 2 vs last 2 fixtures

### Differential Highlighting

Finds low-ownership players with good potential:

```python
def highlight_differentials(ownership_threshold=10.0, min_points=4.0):
    """
    Find differential picks.
    
    Criteria:
    - Ownership ≤ threshold (default 10%)
    - PPG ≥ minimum (default 4.0)
    - Currently available (status == "a")
    
    Scoring: PPG / max(ownership, 1.0) for differential value
    """
```

#### Use Cases
1. **Template Avoidance**: Avoid highly owned players
2. **Rank Climbing**: Differentials can boost rank if successful
3. **Budget Optimization**: Often cheaper than template options

### Cost Efficiency Analysis

Calculates value for money across players:

```python
def calculate_cost_efficiency(players):
    """
    Efficiency = Points Per Game / Cost
    
    Helps identify:
    - Budget options with good returns
    - Overpriced players to avoid
    - Value picks in each position
    """
```

## AI Model Integration

### Optional Sentence Transformers

The advisor can optionally use sentence-transformers for enhanced text generation:

```python
def _try_load_model(self):
    """
    Attempt to load sentence-transformers model.
    
    Model: all-MiniLM-L6-v2 (lightweight, good performance)
    Fallback: Template-based summaries if import fails
    """
    try:
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
    except ImportError:
        self.model = None
```

### Graceful Fallback

The system works fully without ML dependencies:

```python
def generate_team_summary(self, team_analysis):
    """
    Generate summary using available method:
    
    1. AI model (if available): Enhanced natural language generation
    2. Template fallback: Rule-based summary construction
    """
    if self.model:
        return self._generate_ai_summary(team_analysis)
    else:
        return self._generate_template_summary(team_analysis)
```

## Template Summary Generation

### Structure
```python
def _generate_template_summary(self, team_analysis):
    """
    Template-based summary with structured information:
    
    1. Team overview (total/average projected points)
    2. Problem assessment (number of concerning players)
    3. Top recommendation (highest priority transfer)
    """
```

### Example Output
```
Team Analysis: Projected 75.5 points over next 5 gameweeks (avg: 5.0 per player). 
⚠️ 2 player(s) need attention. 
Top transfer priority: Problem Player -> consider Better Option for 3.2 point gain.
```

## Comprehensive Team Advice

### Input Structure
```python
team_state = {
    "player_ids": [1, 2, 3, ...],      # Current team
    "budget": 2.5,                      # Available funds (£m)
    "free_transfers": 1,                # Free transfers available
    "horizon_gameweeks": 5              # Analysis timeframe
}
```

### Analysis Pipeline
```python
def advise_team(self, team_state):
    """
    Comprehensive team analysis pipeline:
    
    1. Load player data and validate team
    2. Detect underperformers using heuristics
    3. Analyze fixture swings for team's clubs
    4. Find differential opportunities
    5. Calculate cost efficiency rankings
    6. Generate transfer suggestions
    7. Compile recommendations by priority
    8. Create natural language summary
    """
```

### Output Structure
```python
{
    "summary": "Natural language team overview",
    "underperformers": [
        {
            "player": {...},
            "issues": ["Poor form", "Injury concerns"],
            "priority": 3
        }
    ],
    "fixture_analysis": {
        "improving_fixtures": [...],
        "worsening_fixtures": [...]
    },
    "top_differentials": [...],
    "transfer_suggestions": [
        {
            "player_out": {...},
            "issues": [...],
            "suggestions": [...]  # Top 3 replacement options
        }
    ],
    "recommendations": [
        {
            "type": "transfer",
            "priority": "high",
            "message": "Consider transferring out X due to poor form"
        }
    ]
}
```

## Recommendation Prioritization

### Priority Levels
1. **High**: Urgent issues (injuries, terrible form, fixture swings)
2. **Medium**: Optimization opportunities (fixture improvements)  
3. **Low**: Fine-tuning (differentials, minor upgrades)

### Recommendation Types
```python
recommendation_types = {
    "transfer": "Player replacement suggestions",
    "fixtures": "Fixture-based opportunities", 
    "differential": "Low-ownership alternatives",
    "captain": "Captaincy recommendations",
    "bench": "Bench optimization advice"
}
```

## Configuration and Customization

### Threshold Configuration
```python
# Customize detection thresholds
underperformers = advisor.detect_underperformers(
    team_players,
    points_threshold=4.0,   # Stricter PPG requirement
    cost_threshold=9.0      # Higher premium threshold
)

# Adjust differential criteria
differentials = advisor.highlight_differentials(
    ownership_threshold=5.0,  # More exclusive differentials
    min_points=5.0           # Higher performance requirement
)
```

### Model Configuration
```python
# Use custom sentence-transformers model
class CustomAdvisor(FPLAdvisor):
    def _try_load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("custom-model-name")
        except ImportError:
            self.model = None
```

## Performance Considerations

### Computational Complexity
- **Heuristic rules**: O(n) where n = number of players
- **Fixture analysis**: O(t) where t = number of teams
- **Transfer suggestions**: O(n×m) where m = candidates per position

### Caching Strategy
```python
# API client automatically caches responses
client = FPLClient()  # 1-hour cache by default

# Advisor reuses client instance
advisor = FPLAdvisor(client=client)
```

### Memory Usage
- **Base advisor**: ~10MB (heuristics only)
- **With ML model**: ~100MB additional (sentence-transformers)
- **Per analysis**: ~1MB temporary data

## Validation and Testing

### Heuristic Validation
```python
def test_underperformer_detection():
    """
    Test cases:
    1. Injured player flagged
    2. Premium underperformer detected
    3. Good player not flagged
    4. Priority scoring correct
    """
```

### Integration Testing
```python
def test_full_advisor_workflow():
    """
    End-to-end test:
    1. Load test team
    2. Generate advice
    3. Validate output structure
    4. Check recommendation logic
    """
```

## Future Enhancements

### Advanced ML Integration
- **Player embeddings**: Vector representations of player styles
- **Sequence models**: LSTM/Transformer for time series prediction
- **Multi-task learning**: Joint prediction of points, minutes, cards

### Enhanced Heuristics
- **Rotation risk**: Predict when players might be rested
- **Price change prediction**: Anticipate player value changes
- **Captain optimization**: Specialized captaincy algorithms

### Personalization
- **User modeling**: Learn from user's historical decisions
- **Risk tolerance**: Adjust recommendations based on user preferences
- **League context**: Mini-league specific advice