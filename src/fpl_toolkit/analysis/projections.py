"""Player projection utilities."""
from typing import List, Dict, Any, Optional
from ..api.client import FPLClient
from .fixtures import compute_fixture_difficulty
from .advanced_metrics import default_metrics_engine


def calculate_player_projection(player_id: int, gameweek: int, client: Optional[FPLClient] = None) -> Dict[str, Any]:
    """
    Calculate projection for a player in a specific gameweek.
    
    Args:
        player_id: FPL player ID
        gameweek: Target gameweek for projection
        client: Optional FPL client instance
    
    Returns:
        Projection data including expected points and confidence
    """
    if client is None:
        client = FPLClient()
    
    try:
        # Get player data
        players = client.get_players()
        player_details = client.get_player_details(player_id)
        
        # Find player in players list
        player_data = None
        for player in players:
            if player["id"] == player_id:
                player_data = player
                break
        
        if not player_data:
            return {"error": f"Player {player_id} not found"}
        
        # Get recent form data
        history = player_details.get("history", [])
        recent_history = history[-5:] if len(history) >= 5 else history
        
        # Calculate base projection using recent form
        if recent_history:
            recent_points = [h.get("total_points", 0) for h in recent_history]
            recent_minutes = [h.get("minutes", 0) for h in recent_history]
            avg_points = sum(recent_points) / len(recent_points)
            avg_minutes = sum(recent_minutes) / len(recent_minutes)
        else:
            # Fallback to season averages
            avg_points = player_data.get("points_per_game", 0)
            avg_minutes = 90 if player_data.get("status") == "a" else 45
        
        # Get fixture difficulty for player's team
        team_id = player_data.get("team")
        fixture_data = compute_fixture_difficulty(team_id, 1, client) if team_id else None
        
        # Calculate fixture multiplier
        if fixture_data and fixture_data["fixtures"]:
            fixture = fixture_data["fixtures"][0]
            difficulty = fixture.get("difficulty", 3.0)
            is_home = fixture.get("is_home", False)
            
            # Convert difficulty to multiplier (easier fixtures = higher multiplier)
            if difficulty <= 2.0:
                fixture_multiplier = 1.3  # Easy fixture
            elif difficulty <= 3.0:
                fixture_multiplier = 1.1  # Average fixture
            elif difficulty <= 4.0:
                fixture_multiplier = 0.9  # Difficult fixture
            else:
                fixture_multiplier = 0.7  # Very difficult fixture
            
            # Home advantage
            if is_home:
                fixture_multiplier *= 1.1
        else:
            fixture_multiplier = 1.0
        
        # Apply position-specific adjustments
        position = player_data.get("element_type")
        if position == 1:  # Goalkeeper
            base_projection = avg_points * 0.9  # GKs more consistent
        elif position == 2:  # Defender
            base_projection = avg_points * 0.95
        elif position == 3:  # Midfielder
            base_projection = avg_points * 1.0
        else:  # Forward
            base_projection = avg_points * 1.05  # Forwards more variable
        
        # Calculate final projection
        projected_points = base_projection * fixture_multiplier
        
        # Apply advanced metrics enhancements
        position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
        player_position = position_map.get(position, "MID")
        opponent_id = fixture_data["fixtures"][0].get("opponent_id") if fixture_data and fixture_data["fixtures"] else None
        
        # Get enhanced projection with xG/xA and zone weakness
        if default_metrics_engine.is_data_available()["xgxa_available"] or default_metrics_engine.is_data_available()["zone_weakness_available"]:
            enhanced = default_metrics_engine.get_enhanced_projection(
                player_id=player_id,
                base_projection=projected_points,
                opponent_team_id=opponent_id,
                player_position=player_position,
                minutes_played=int(avg_minutes),
                attack_style="balanced"
            )
            projected_points = enhanced["final_projection"]
            # Store enhancement data for later use
            enhancement_data = enhanced
        else:
            enhancement_data = {"base_projection": projected_points, "final_projection": projected_points}
        
        # Adjust for player status
        status = player_data.get("status", "a")
        chance_of_playing = player_data.get("chance_of_playing_this_round")
        
        if status != "a":  # Not available
            projected_points *= 0.3
            confidence = 0.2
        elif chance_of_playing is not None:
            if chance_of_playing <= 25:
                projected_points *= 0.4
                confidence = 0.3
            elif chance_of_playing <= 50:
                projected_points *= 0.7
                confidence = 0.5
            elif chance_of_playing <= 75:
                projected_points *= 0.9
                confidence = 0.7
            else:
                confidence = 0.8
        else:
            confidence = 0.75
        
        # Calculate projected minutes
        if status != "a" or (chance_of_playing and chance_of_playing <= 25):
            projected_minutes = int(avg_minutes * 0.3)
        elif chance_of_playing and chance_of_playing <= 50:
            projected_minutes = int(avg_minutes * 0.7)
        else:
            projected_minutes = int(avg_minutes)
        
        return {
            "player_id": player_id,
            "gameweek": gameweek,
            "projected_points": round(projected_points, 2),
            "projected_minutes": projected_minutes,
            "confidence_score": round(confidence, 2),
            "fixture_difficulty": fixture_data["fixtures"][0].get("difficulty", 3.0) if fixture_data and fixture_data["fixtures"] else 3.0,
            "form_factor": round(avg_points, 2),
            "home_advantage": fixture_data["fixtures"][0].get("is_home", False) if fixture_data and fixture_data["fixtures"] else False,
            "opponent_team_id": fixture_data["fixtures"][0].get("opponent_id") if fixture_data and fixture_data["fixtures"] else None,
            "status": status,
            "chance_of_playing": chance_of_playing,
            # Advanced metrics data
            "advanced_metrics": enhancement_data,
            "has_advanced_metrics": default_metrics_engine.is_data_available()
        }
    
    finally:
        if client and hasattr(client, '_created_locally'):
            client.close()


def calculate_horizon_projection(player_id: int, horizon_gameweeks: int = 5, client: Optional[FPLClient] = None) -> Dict[str, Any]:
    """
    Calculate projection for a player over multiple gameweeks.
    
    Args:
        player_id: FPL player ID
        horizon_gameweeks: Number of gameweeks to project
        client: Optional FPL client instance
    
    Returns:
        Multi-gameweek projection data
    """
    if client is None:
        client = FPLClient()
    
    try:
        current_gw = client.get_current_gameweek()
        if not current_gw:
            return {"error": "Could not determine current gameweek"}
        
        current_gw_id = current_gw.get("id", 1)
        projections = []
        total_projected_points = 0
        
        for i in range(horizon_gameweeks):
            gw = current_gw_id + i
            projection = calculate_player_projection(player_id, gw, client)
            
            if "error" not in projection:
                projections.append(projection)
                total_projected_points += projection.get("projected_points", 0)
        
        avg_confidence = sum(p.get("confidence_score", 0) for p in projections) / len(projections) if projections else 0
        
        return {
            "player_id": player_id,
            "horizon_gameweeks": horizon_gameweeks,
            "projections": projections,
            "total_projected_points": round(total_projected_points, 2),
            "average_projected_points": round(total_projected_points / len(projections), 2) if projections else 0,
            "average_confidence": round(avg_confidence, 2)
        }
    
    finally:
        if client and hasattr(client, '_created_locally'):
            client.close()


def get_top_projected_players(position: Optional[str] = None, max_cost: Optional[float] = None, 
                             gameweek: Optional[int] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get top projected players for a gameweek.
    
    Args:
        position: Filter by position (GK, DEF, MID, FWD)
        max_cost: Maximum player cost filter
        gameweek: Target gameweek (defaults to next gameweek)
        limit: Maximum number of players to return
    
    Returns:
        List of top projected players
    """
    with FPLClient() as client:
        if gameweek is None:
            next_gw = client.get_next_gameweek()
            gameweek = next_gw.get("id") if next_gw else 1
        
        players = client.get_players()
        position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
        
        player_projections = []
        
        for player in players:
            # Apply filters
            if position and position_map.get(player.get("element_type")) != position:
                continue
            
            if max_cost and player.get("now_cost", 0) / 10.0 > max_cost:
                continue
            
            # Skip unavailable players
            if player.get("status") != "a":
                continue
            
            # Calculate projection
            projection = calculate_player_projection(player["id"], gameweek, client)
            
            if "error" not in projection:
                projection.update({
                    "name": f"{player.get('first_name', '')} {player.get('second_name', '')}".strip(),
                    "cost": player.get("now_cost", 0) / 10.0,
                    "position": position_map.get(player.get("element_type"), "Unknown"),
                    "total_points": player.get("total_points", 0),
                    "form": player.get("form", 0),
                    "selected_by_percent": player.get("selected_by_percent", 0)
                })
                player_projections.append(projection)
        
        # Sort by projected points and return top players
        player_projections.sort(key=lambda x: x.get("projected_points", 0), reverse=True)
        return player_projections[:limit]


def compare_player_projections(player_ids: List[int], horizon_gameweeks: int = 5) -> Dict[str, Any]:
    """
    Compare projections between multiple players.
    
    Args:
        player_ids: List of player IDs to compare
        horizon_gameweeks: Number of gameweeks to analyze
    
    Returns:
        Comparison data with relative performance metrics
    """
    with FPLClient() as client:
        players = client.get_players()
        player_lookup = {p["id"]: p for p in players}
        
        comparisons = []
        
        for player_id in player_ids:
            player_data = player_lookup.get(player_id)
            if not player_data:
                continue
            
            projection = calculate_horizon_projection(player_id, horizon_gameweeks, client)
            
            if "error" not in projection:
                projection.update({
                    "name": f"{player_data.get('first_name', '')} {player_data.get('second_name', '')}".strip(),
                    "cost": player_data.get("now_cost", 0) / 10.0,
                    "current_points": player_data.get("total_points", 0),
                    "points_per_million": round(
                        projection.get("total_projected_points", 0) / (player_data.get("now_cost", 1) / 10.0), 2
                    )
                })
                comparisons.append(projection)
        
        # Sort by total projected points
        comparisons.sort(key=lambda x: x.get("total_projected_points", 0), reverse=True)
        
        return {
            "comparisons": comparisons,
            "best_projection": comparisons[0] if comparisons else None,
            "horizon_gameweeks": horizon_gameweeks
        }