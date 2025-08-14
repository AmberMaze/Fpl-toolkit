"""Fixture difficulty analysis utilities."""
from typing import List, Dict, Any, Optional, Tuple
from ..api.client import FPLClient


def compute_fixture_difficulty(team_id: int, next_n: int = 5, client: Optional[FPLClient] = None) -> Dict[str, Any]:
    """
    Compute fixture difficulty for a team over the next N gameweeks.
    
    Args:
        team_id: FPL team ID
        next_n: Number of future fixtures to analyze
        client: Optional FPL client instance
    
    Returns:
        Dictionary with difficulty metrics and fixture details
    """
    if client is None:
        client = FPLClient()
    
    try:
        # Get team fixtures
        fixtures = client.get_team_fixtures(team_id, next_n)
        teams = client.get_teams()
        
        # Create team lookup for opponent strength
        team_lookup = {team["id"]: team for team in teams}
        
        if not fixtures:
            return {
                "team_id": team_id,
                "fixtures": [],
                "average_difficulty": 3.0,
                "total_difficulty": 0.0,
                "home_fixtures": 0,
                "away_fixtures": 0,
                "difficulty_trend": "neutral"
            }
        
        fixture_analysis = []
        total_difficulty = 0.0
        home_count = 0
        away_count = 0
        
        for fixture in fixtures:
            is_home = fixture.get("team_h") == team_id
            opponent_id = fixture.get("team_a") if is_home else fixture.get("team_h")
            
            # Get opponent team info
            opponent = team_lookup.get(opponent_id, {})
            opponent_name = opponent.get("name", "Unknown")
            
            # Calculate base difficulty using opponent's strength and form
            base_difficulty = calculate_opponent_difficulty(opponent)
            
            # Apply home/away modifier
            if is_home:
                difficulty = max(1.0, base_difficulty - 0.5)  # Home advantage
                home_count += 1
            else:
                difficulty = min(5.0, base_difficulty + 0.3)  # Away disadvantage
                away_count += 1
            
            fixture_info = {
                "gameweek": fixture.get("event"),
                "opponent_id": opponent_id,
                "opponent_name": opponent_name,
                "is_home": is_home,
                "difficulty": round(difficulty, 2),
                "kickoff_time": fixture.get("kickoff_time")
            }
            
            fixture_analysis.append(fixture_info)
            total_difficulty += difficulty
        
        average_difficulty = total_difficulty / len(fixtures) if fixtures else 3.0
        
        # Determine difficulty trend
        if len(fixtures) >= 3:
            early_avg = sum(f["difficulty"] for f in fixture_analysis[:2]) / 2
            late_avg = sum(f["difficulty"] for f in fixture_analysis[-2:]) / 2
            
            if late_avg > early_avg + 0.5:
                trend = "getting_harder"
            elif early_avg > late_avg + 0.5:
                trend = "getting_easier"
            else:
                trend = "neutral"
        else:
            trend = "neutral"
        
        return {
            "team_id": team_id,
            "fixtures": fixture_analysis,
            "average_difficulty": round(average_difficulty, 2),
            "total_difficulty": round(total_difficulty, 2),
            "home_fixtures": home_count,
            "away_fixtures": away_count,
            "difficulty_trend": trend,
            "analyzed_gameweeks": len(fixtures)
        }
    
    finally:
        if client and hasattr(client, '_created_locally'):
            client.close()


def calculate_opponent_difficulty(opponent_team: Dict[str, Any]) -> float:
    """
    Calculate base difficulty against an opponent team.
    
    Args:
        opponent_team: Team data from FPL API
    
    Returns:
        Difficulty score from 1.0 (easy) to 5.0 (very difficult)
    """
    # Default difficulty if no data
    if not opponent_team:
        return 3.0
    
    # Get team strength metrics (these are provided by FPL API)
    overall_home = opponent_team.get("strength_overall_home", 3)
    overall_away = opponent_team.get("strength_overall_away", 3)
    attack_home = opponent_team.get("strength_attack_home", 3)
    attack_away = opponent_team.get("strength_attack_away", 3)
    defence_home = opponent_team.get("strength_defence_home", 3)
    defence_away = opponent_team.get("strength_defence_away", 3)
    
    # Calculate average strength (FPL ratings are 1-5)
    avg_strength = (
        overall_home + overall_away +
        attack_home + attack_away +
        defence_home + defence_away
    ) / 6.0
    
    # Normalize to 1-5 scale
    return max(1.0, min(5.0, avg_strength))


def get_fixture_difficulty_rankings(teams: Optional[List[int]] = None, next_n: int = 5) -> List[Dict[str, Any]]:
    """
    Get fixture difficulty rankings for all teams or specified teams.
    
    Args:
        teams: Optional list of team IDs to analyze. If None, analyzes all teams.
        next_n: Number of fixtures to analyze per team
    
    Returns:
        List of teams sorted by fixture difficulty (easiest first)
    """
    with FPLClient() as client:
        all_teams = client.get_teams()
        
        if teams is None:
            teams = [team["id"] for team in all_teams]
        
        team_difficulties = []
        
        for team_id in teams:
            difficulty_data = compute_fixture_difficulty(team_id, next_n, client)
            
            # Find team name
            team_name = "Unknown"
            for team in all_teams:
                if team["id"] == team_id:
                    team_name = team["name"]
                    break
            
            team_difficulties.append({
                "team_id": team_id,
                "team_name": team_name,
                "average_difficulty": difficulty_data["average_difficulty"],
                "total_difficulty": difficulty_data["total_difficulty"],
                "fixtures_analyzed": difficulty_data["analyzed_gameweeks"],
                "difficulty_trend": difficulty_data["difficulty_trend"],
                "home_fixtures": difficulty_data["home_fixtures"],
                "away_fixtures": difficulty_data["away_fixtures"]
            })
        
        # Sort by average difficulty (easiest first)
        team_difficulties.sort(key=lambda x: x["average_difficulty"])
        
        return team_difficulties


def compare_team_fixtures(team_ids: List[int], next_n: int = 5) -> Dict[str, Any]:
    """
    Compare fixture difficulty between multiple teams.
    
    Args:
        team_ids: List of team IDs to compare
        next_n: Number of fixtures to analyze
    
    Returns:
        Comparison data with rankings and detailed analysis
    """
    with FPLClient() as client:
        comparisons = []
        
        for team_id in team_ids:
            difficulty_data = compute_fixture_difficulty(team_id, next_n, client)
            comparisons.append(difficulty_data)
        
        # Sort by average difficulty
        comparisons.sort(key=lambda x: x["average_difficulty"])
        
        return {
            "comparisons": comparisons,
            "easiest_fixtures": comparisons[0] if comparisons else None,
            "hardest_fixtures": comparisons[-1] if comparisons else None,
            "analyzed_gameweeks": next_n
        }