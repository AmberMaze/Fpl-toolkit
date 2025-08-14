"""Advanced metrics integration for FPL Toolkit.

This module provides optional integration with external metrics sources like
expected goals (xG) and expected assists (xA), as well as zone weakness
adjustments for more sophisticated player projections.
"""

import json
import os
from typing import Dict, Any, Optional, Tuple
from pathlib import Path


def get_player_expected_rates(player: Dict[str, Any], cache: Optional[Dict] = None) -> Dict[str, Optional[float]]:
    """Get expected goals and assists rates for a player.
    
    Args:
        player: Player data from FPL API
        cache: Optional cache for performance
        
    Returns:
        Dict with xg_per90 and xa_per90 keys, values can be None if not available
    """
    # Default response structure
    result = {"xg_per90": None, "xa_per90": None}
    
    # Check if external metrics are enabled
    if not os.getenv("ENABLE_UNDERSTAT", "0") == "1":
        # Use local sample data instead
        return _get_local_expected_rates(player)
    
    # If enabled, implement Understat integration here
    # For now, return None to maintain graceful fallback
    try:
        # TODO: Implement Understat API integration
        # This would require: pip install understat
        # and proper error handling for network calls
        pass
    except Exception:
        # Graceful fallback to local data
        return _get_local_expected_rates(player)
    
    return result


def _get_local_expected_rates(player: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """Get expected rates from local sample data file.
    
    Args:
        player: Player data from FPL API
        
    Returns:
        Dict with xg_per90 and xa_per90 keys, values can be None if not found
    """
    result = {"xg_per90": None, "xa_per90": None}
    
    try:
        # Get sample data file path
        sample_file_path = Path("data/xgxa_sample.json")
        if not sample_file_path.exists():
            # Try relative to module's parent directory
            current_dir = Path(__file__).parent.parent.parent
            sample_file_path = current_dir / "data" / "xgxa_sample.json"
        
        if not sample_file_path.exists():
            return result
            
        with open(sample_file_path, 'r') as f:
            xgxa_data = json.load(f)
        
        # Create player name for matching
        player_name = _normalize_player_name(player)
        
        # Simple fuzzy matching - look for player name in data
        for key, metrics in xgxa_data.items():
            if _names_match(player_name, key):
                result["xg_per90"] = metrics.get("xg_per90")
                result["xa_per90"] = metrics.get("xa_per90")
                break
                
    except Exception:
        # Silent failure - return None values
        pass
    
    return result


def _normalize_player_name(player: Dict[str, Any]) -> str:
    """Normalize player name for matching."""
    first_name = player.get("first_name", "").lower().strip()
    second_name = player.get("second_name", "").lower().strip()
    web_name = player.get("web_name", "").lower().strip()
    
    # Use web_name if available, otherwise combine first and second name
    if web_name:
        return web_name
    else:
        return f"{first_name} {second_name}".strip()


def _names_match(name1: str, name2: str) -> bool:
    """Simple fuzzy name matching using contains logic."""
    name1 = name1.lower().strip()
    name2 = name2.lower().strip()
    
    # Exact match
    if name1 == name2:
        return True
    
    # Check if either name contains the other
    if name1 in name2 or name2 in name1:
        return True
    
    # Check if last names match (for cases like "Haaland" vs "Erling Haaland")
    name1_parts = name1.split()
    name2_parts = name2.split()
    
    if name1_parts and name2_parts:
        if name1_parts[-1] == name2_parts[-1]:
            return True
    
    return False


def load_zone_weakness() -> Dict[str, Dict[str, float]]:
    """Load zone weakness data from configuration file.
    
    Returns:
        Dict mapping team_id to zone weakness indices
    """
    zone_data = {}
    
    try:
        # Get zone weakness file path from environment or use default
        zone_file = os.getenv("ZONE_WEAKNESS_FILE", "./data/zone_weakness.sample.json")
        
        # Handle relative paths from project root
        if not os.path.isabs(zone_file):
            # Try relative to current working directory first
            zone_file_path = Path(zone_file)
            if not zone_file_path.exists():
                # If not found, try relative to the module's parent directory
                current_dir = Path(__file__).parent.parent.parent
                zone_file_path = current_dir / zone_file
        else:
            zone_file_path = Path(zone_file)
        
        if not zone_file_path.exists():
            return zone_data
            
        with open(zone_file_path, 'r') as f:
            zone_data = json.load(f)
            
    except Exception:
        # Silent failure - return empty dict for graceful fallback
        pass
    
    return zone_data


def get_player_zone_side(player_id: int, position: Optional[str] = None) -> str:
    """Determine which zone side (left/center/right) a player typically plays.
    
    This is a simplified heuristic. In a full implementation, this could use
    positional data, team formation analysis, or historical positioning data.
    
    Args:
        player_id: Player ID
        position: Player position (GK, DEF, MID, FWD)
        
    Returns:
        One of: 'left', 'center', 'right'
    """
    # Simple static mapping for demonstration
    # In practice, this could be more sophisticated
    player_side_mapping = {
        # Example mappings - in reality this would be much more comprehensive
        7: "right",     # Sterling (typically right wing)
        233: "left",    # Rashford (typically left wing)
        283: "center",  # Haaland (center forward)
        254: "right",   # Salah (right wing)
        # Add more mappings as needed
    }
    
    # Return specific mapping if available
    if player_id in player_side_mapping:
        return player_side_mapping[player_id]
    
    # Default fallback to center for most players
    return "center"


def apply_zone_weakness_adjustment(
    base_attacking_points: float,
    opponent_team_id: int,
    player_zone_side: str,
    zone_weakness_data: Optional[Dict] = None
) -> Tuple[float, float]:
    """Apply zone weakness adjustment to attacking points.
    
    Args:
        base_attacking_points: Base attacking points (goals + assists)
        opponent_team_id: ID of the opposing team
        player_zone_side: Which zone the player attacks ('left', 'center', 'right')
        zone_weakness_data: Optional zone weakness data, loaded if None
        
    Returns:
        Tuple of (adjusted_points, zone_multiplier)
    """
    if zone_weakness_data is None:
        zone_weakness_data = load_zone_weakness()
    
    # Default multiplier if no data available
    zone_multiplier = 1.0
    
    # Get opponent team zone data
    team_data = zone_weakness_data.get(str(opponent_team_id))
    if team_data:
        zone_key = f"{player_zone_side}_conceded_index"
        zone_multiplier = team_data.get(zone_key, 1.0)
    
    # Apply adjustment
    adjusted_points = base_attacking_points * zone_multiplier
    
    return adjusted_points, zone_multiplier


def enhance_breakdown_with_advanced_metrics(
    base_breakdown: Dict[str, float],
    player: Dict[str, Any],
    opponent_team_id: Optional[int] = None,
    player_id: Optional[int] = None
) -> Dict[str, Any]:
    """Enhance a basic event breakdown with advanced metrics.
    
    Args:
        base_breakdown: Basic breakdown with appearance, goals, assists, etc.
        player: Player data from FPL API
        opponent_team_id: ID of opponent team for zone adjustment
        player_id: Player ID for zone side determination
        
    Returns:
        Enhanced breakdown with optional adjustments block
    """
    enhanced = base_breakdown.copy()
    adjustments = {}
    
    # Get advanced metrics
    expected_rates = get_player_expected_rates(player)
    xg_per90 = expected_rates.get("xg_per90")
    xa_per90 = expected_rates.get("xa_per90")
    
    # Apply xG/xA reweighting if available
    if xg_per90 is not None and xa_per90 is not None:
        original_goals = enhanced.get("goals", 0.0)
        original_assists = enhanced.get("assists", 0.0)
        original_attacking = original_goals + original_assists
        
        if original_attacking > 0 and (xg_per90 + xa_per90) > 0:
            # Reweight goals vs assists based on xG/xA ratio
            xg_xa_total = xg_per90 + xa_per90
            xg_proportion = xg_per90 / xg_xa_total
            xa_proportion = xa_per90 / xg_xa_total
            
            enhanced["goals"] = round(original_attacking * xg_proportion, 3)
            enhanced["assists"] = round(original_attacking * xa_proportion, 3)
            
            adjustments["xg_per90"] = xg_per90
            adjustments["xa_per90"] = xa_per90
    
    # Apply zone weakness adjustment
    zone_multiplier = 1.0
    if opponent_team_id and player_id:
        player_zone = get_player_zone_side(player_id, player.get("position"))
        attacking_points = enhanced.get("goals", 0.0) + enhanced.get("assists", 0.0)
        
        if attacking_points > 0:
            adjusted_attacking, zone_multiplier = apply_zone_weakness_adjustment(
                attacking_points, opponent_team_id, player_zone
            )
            
            # Redistribute the adjusted attacking points proportionally
            if attacking_points > 0:
                goals_proportion = enhanced.get("goals", 0.0) / attacking_points
                assists_proportion = enhanced.get("assists", 0.0) / attacking_points
                
                enhanced["goals"] = round(adjusted_attacking * goals_proportion, 3)
                enhanced["assists"] = round(adjusted_attacking * assists_proportion, 3)
            
            adjustments["zone_multiplier"] = round(zone_multiplier, 3)
    
    # Recalculate total
    enhanced["total"] = round(sum([
        enhanced.get("appearance", 0.0),
        enhanced.get("goals", 0.0),
        enhanced.get("assists", 0.0),
        enhanced.get("cs", 0.0),
        enhanced.get("bonus", 0.0),
        enhanced.get("misc", 0.0)
    ]), 3)
    
    # Add adjustments block if any adjustments were made
    if adjustments:
        enhanced["adjustments"] = adjustments
    
    return enhanced


# Simple event breakdown function for demonstration
def _simple_event_breakdown(projected_points: float, player_data: Dict[str, Any], minutes: int = 90) -> Dict[str, float]:
    """Create a simple event breakdown based on player's season stats.
    
    This is a basic implementation for demonstration. In practice, this would
    use more sophisticated projection algorithms.
    """
    # Get player's per-90 stats
    total_minutes = player_data.get("minutes", 1)
    if total_minutes == 0:
        total_minutes = 1  # Avoid division by zero
    
    per_90_factor = 90.0 / total_minutes if total_minutes >= 90 else 1.0
    
    # Basic breakdown
    breakdown = {
        "appearance": 2.0,  # Base appearance points
        "goals": round(player_data.get("goals_scored", 0) * per_90_factor * 0.3, 3),
        "assists": round(player_data.get("assists", 0) * per_90_factor * 0.4, 3),
        "cs": round(player_data.get("clean_sheets", 0) * per_90_factor * 0.2, 3),
        "bonus": round(player_data.get("bonus", 0) * per_90_factor * 0.15, 3),
        "misc": 0.5  # Miscellaneous points (saves, etc.)
    }
    
    breakdown["total"] = round(sum(breakdown.values()), 3)
    
    return breakdown