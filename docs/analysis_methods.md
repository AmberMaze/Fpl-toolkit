# Analysis Methods

This document outlines the analytical methods used in the FPL Toolkit for player evaluation, fixture difficulty assessment, and decision support.

## Fixture Difficulty Analysis

### Overview
Fixture difficulty scoring helps identify periods when players are likely to perform well or poorly based on their upcoming opponents.

### Methodology

#### Base Difficulty Calculation
```python
def calculate_opponent_difficulty(opponent_team):
    """
    Calculate base difficulty using FPL's team strength ratings.
    
    Inputs:
    - strength_overall_home/away (1-5)
    - strength_attack_home/away (1-5) 
    - strength_defence_home/away (1-5)
    
    Output: Average strength rating (1.0-5.0)
    """
    avg_strength = (
        overall_home + overall_away +
        attack_home + attack_away +
        defence_home + defence_away
    ) / 6.0
    
    return max(1.0, min(5.0, avg_strength))
```

#### Home/Away Adjustments
- **Home fixtures**: -0.5 difficulty (easier)
- **Away fixtures**: +0.3 difficulty (harder)
- **Bounds**: Final difficulty clamped to 1.0-5.0 range

#### Trend Analysis
```python
def analyze_trend(fixtures):
    """
    Determine if fixtures are getting easier or harder.
    
    Method:
    - Compare average difficulty of first 2 vs last 2 fixtures
    - Threshold: 0.5 difference required for trend classification
    """
    if len(fixtures) >= 3:
        early_avg = avg(fixtures[:2])
        late_avg = avg(fixtures[-2:])
        
        if late_avg > early_avg + 0.5:
            return "getting_harder"
        elif early_avg > late_avg + 0.5:
            return "getting_easier"
    
    return "neutral"
```

### Use Cases
1. **Transfer Planning**: Target players with improving fixtures
2. **Captain Selection**: Avoid players facing difficult opponents
3. **Bench Strategy**: Consider fixture difficulty for rotation

## Player Projections

### Overview
Player projections estimate future performance using recent form, fixture difficulty, and player-specific factors.

### Core Projection Formula
```python
def calculate_projection(player, fixture_data):
    """
    Base projection calculation.
    """
    # Step 1: Recent form baseline
    recent_points = player.recent_gameweeks(5)
    avg_points = sum(recent_points) / len(recent_points)
    
    # Step 2: Fixture multiplier
    fixture_multiplier = get_fixture_multiplier(fixture_data)
    
    # Step 3: Position adjustment
    position_multiplier = get_position_multiplier(player.position)
    
    # Step 4: Status adjustment
    status_multiplier = get_status_multiplier(player.status, player.chance_of_playing)
    
    return avg_points * fixture_multiplier * position_multiplier * status_multiplier
```

### Fixture Multipliers
- **Difficulty 1-2**: 1.3x multiplier (easy fixtures)
- **Difficulty 2-3**: 1.1x multiplier (average fixtures)
- **Difficulty 3-4**: 0.9x multiplier (difficult fixtures)
- **Difficulty 4-5**: 0.7x multiplier (very difficult fixtures)
- **Home advantage**: +10% bonus

### Position Adjustments
- **Goalkeepers**: 0.9x (more consistent, lower variance)
- **Defenders**: 0.95x (moderate consistency)
- **Midfielders**: 1.0x (baseline)
- **Forwards**: 1.05x (higher variance, explosive potential)

### Status Adjustments
```python
def get_status_multiplier(status, chance_of_playing):
    """
    Adjust for injury/availability concerns.
    """
    if status != "available":
        return 0.3  # Injured/suspended
    
    if chance_of_playing is not None:
        if chance_of_playing <= 25:
            return 0.4  # Very doubtful
        elif chance_of_playing <= 50:
            return 0.7  # Doubtful
        elif chance_of_playing <= 75:
            return 0.9  # Probable
    
    return 1.0  # Fully available
```

### Confidence Scoring
Confidence represents how reliable the projection is:

```python
def calculate_confidence(player, projection_factors):
    """
    Calculate projection confidence (0.0-1.0).
    """
    base_confidence = 0.75
    
    # Reduce confidence for injured players
    if player.status != "available":
        base_confidence *= 0.3
    
    # Reduce confidence for inconsistent recent form
    recent_variance = calculate_variance(player.recent_points)
    if recent_variance > threshold:
        base_confidence *= 0.8
    
    # Reduce confidence for new players (limited data)
    if player.games_played < 5:
        base_confidence *= 0.6
    
    return min(1.0, base_confidence)
```

## Decision Support Logic

### Transfer Scenario Analysis

#### Points Gain Calculation
```python
def analyze_transfer_points(player_out, player_in, horizon):
    """
    Calculate expected points difference over time horizon.
    """
    out_projection = project_player(player_out, horizon)
    in_projection = project_player(player_in, horizon)
    
    return in_projection.total_points - out_projection.total_points
```

#### Risk Assessment
Multiple factors contribute to transfer risk:

1. **Cost Risk**
   - High cost increase (>£1.0m): +0.2 risk
   - Moderate increase (>£0.5m): +0.1 risk

2. **Form Risk**
   - New player poor form (<3.0): +0.2 risk
   - Transferring out in-form player (>5.0): +0.15 risk

3. **Ownership Risk**
   - Moving from popular (>20%) to differential (<5%): +0.1 risk

4. **Injury Risk**
   - New player injury concerns: +0.3 risk

#### Recommendation Algorithm
```python
def generate_recommendation(points_gain, risk_score):
    """
    Generate transfer recommendation based on points gain and risk.
    """
    if points_gain > 1.0 and risk_score < 0.5:
        return "Strongly Recommended"
    elif points_gain > 0.5 and risk_score < 0.7:
        return "Recommended" 
    elif points_gain > 0 and risk_score < 0.3:
        return "Consider"
    elif abs(points_gain) <= 0.5:
        return "Neutral"
    else:
        return "Not Recommended"
```

### Target Finding Algorithm

```python
def find_transfer_targets(player_out, constraints):
    """
    Find suitable replacement players.
    
    Filtering:
    1. Position match (if same_position_only=True)
    2. Cost constraint (player_cost <= current_cost + max_increase)
    3. Availability (status == "available")
    
    Ranking:
    - Sort by projected points gain (descending)
    - Apply risk assessment
    - Return top N candidates
    """
```

## Validation and Limitations

### Data Sources
- **FPL Official API**: Primary data source for all player and fixture information
- **Update Frequency**: Data cached for 1 hour to balance freshness with API respect
- **Rate Limiting**: Implemented to avoid overwhelming FPL servers

### Projection Accuracy
- **Historical Validation**: Projections should be validated against actual outcomes
- **Seasonal Variance**: Performance patterns may change throughout the season
- **Unexpected Events**: Cannot predict injuries, cards, or tactical changes

### Risk Factors
- **Model Assumptions**: Based on historical patterns that may not persist
- **Sample Size**: Limited recent form data can affect projection quality
- **External Factors**: Weather, team news, and motivation not considered

### Recommended Usage
1. **Use as guidance**: Projections supplement, not replace, human judgment
2. **Consider context**: Watch team news, press conferences, and tactical changes
3. **Diversify strategy**: Don't rely solely on algorithmic recommendations
4. **Monitor performance**: Track actual vs projected performance

## Future Enhancements

### Advanced Modeling
- **Machine Learning**: Integration of ML models for pattern recognition
- **Ensemble Methods**: Combining multiple prediction approaches
- **Feature Engineering**: Additional factors like weather, team motivation

### Data Enhancement
- **Expected Goals (xG)**: Incorporate underlying performance metrics
- **Player Tracking**: Physical performance and fatigue indicators
- **Market Sentiment**: Price change momentum and community sentiment

### Contextual Factors
- **Team Tactics**: Formation and playing style impact
- **Opposition Analysis**: Detailed opponent strength by position
- **Match Importance**: Cup games, relegation battles, title races