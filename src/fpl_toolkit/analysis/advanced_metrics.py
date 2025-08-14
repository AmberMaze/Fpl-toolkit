"""Advanced metrics support for xG/xA and zone weakness adjustments."""
import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


class AdvancedMetricsEngine:
    """Engine for handling advanced metrics (xG/xA) and zone weakness adjustments."""
    
    def __init__(self, enable_advanced_metrics: bool = True, enable_zone_weakness: bool = True):
        """
        Initialize the advanced metrics engine.
        
        Args:
            enable_advanced_metrics: Whether to use xG/xA data
            enable_zone_weakness: Whether to apply zone weakness adjustments
        """
        self.enable_advanced_metrics = enable_advanced_metrics
        self.enable_zone_weakness = enable_zone_weakness
        self._xgxa_data = None
        self._zone_weakness_data = None
        
        # Load data files
        self._load_data_files()
    
    def _load_data_files(self):
        """Load xG/xA and zone weakness data from files."""
        try:
            # Get paths from environment or use defaults
            xgxa_file = os.getenv("XGXA_DATA_FILE", "data/xgxa_sample.json")
            zone_weakness_file = os.getenv("ZONE_WEAKNESS_DATA_FILE", "data/zone_weakness_sample.json")
            
            # Load xG/xA data
            if self.enable_advanced_metrics:
                xgxa_path = Path(xgxa_file)
                if xgxa_path.exists():
                    with open(xgxa_path, 'r') as f:
                        self._xgxa_data = json.load(f)
                
            # Load zone weakness data
            if self.enable_zone_weakness:
                zone_path = Path(zone_weakness_file)
                if zone_path.exists():
                    with open(zone_path, 'r') as f:
                        self._zone_weakness_data = json.load(f)
                        
        except Exception as e:
            print(f"Warning: Could not load advanced metrics data: {e}")
            self._xgxa_data = None
            self._zone_weakness_data = None
    
    def get_player_xg_xa(self, player_id: int) -> Dict[str, float]:
        """
        Get xG and xA data for a specific player.
        
        Args:
            player_id: FPL player ID
            
        Returns:
            Dictionary with xG/xA metrics or defaults
        """
        if not self.enable_advanced_metrics or not self._xgxa_data:
            return {
                "xg": 0.0,
                "xa": 0.0,
                "xg_per_90": 0.0,
                "xa_per_90": 0.0,
                "total_xg": 0.0,
                "total_xa": 0.0
            }
        
        # Find player in xG/xA data
        for player in self._xgxa_data.get("players", []):
            if player.get("player_id") == player_id:
                return {
                    "xg": player.get("xg", 0.0),
                    "xa": player.get("xa", 0.0),
                    "xg_per_90": player.get("xg_per_90", 0.0),
                    "xa_per_90": player.get("xa_per_90", 0.0),
                    "total_xg": player.get("total_xg", 0.0),
                    "total_xa": player.get("total_xa", 0.0)
                }
        
        # Return defaults if player not found
        return {
            "xg": 0.0,
            "xa": 0.0,
            "xg_per_90": 0.0,
            "xa_per_90": 0.0,
            "total_xg": 0.0,
            "total_xa": 0.0
        }
    
    def get_zone_weakness_multiplier(self, opponent_team_id: int, attack_zone: str = "central") -> float:
        """
        Get zone weakness multiplier for attacking against a specific team.
        
        Args:
            opponent_team_id: ID of the defending team
            attack_zone: Zone of attack (left_wing, right_wing, central, box_left, etc.)
            
        Returns:
            Multiplier for projection adjustment (1.0 = average, >1.0 = easier, <1.0 = harder)
        """
        if not self.enable_zone_weakness or not self._zone_weakness_data:
            return 1.0
        
        # Find team in zone weakness data
        for team in self._zone_weakness_data.get("teams", []):
            if team.get("team_id") == opponent_team_id:
                zone_weaknesses = team.get("zone_weaknesses", {})
                return zone_weaknesses.get(attack_zone, 1.0)
        
        # Return neutral multiplier if team not found
        return 1.0
    
    def get_position_attack_zones(self, position: str) -> List[str]:
        """
        Get relevant attack zones for a player position.
        
        Args:
            position: Player position (GK, DEF, MID, FWD)
            
        Returns:
            List of relevant attack zones for the position
        """
        position_zones = {
            "GK": [],  # Goalkeepers don't typically attack
            "DEF": ["set_pieces"],  # Defenders mainly from set pieces
            "MID": ["central", "left_wing", "right_wing", "set_pieces"],
            "FWD": ["box_left", "box_right", "box_central", "set_pieces"]
        }
        
        return position_zones.get(position, ["central"])
    
    def calculate_xg_based_projection(self, player_id: int, base_points: float, minutes_played: int = 90) -> float:
        """
        Calculate enhanced projection using xG/xA data.
        
        Args:
            player_id: FPL player ID
            base_points: Base projection without xG/xA
            minutes_played: Expected minutes for the player
            
        Returns:
            Enhanced projection incorporating xG/xA metrics
        """
        if not self.enable_advanced_metrics:
            return base_points
        
        xg_data = self.get_player_xg_xa(player_id)
        
        # Calculate xG/xA contribution (simplified model)
        # Goals from xG: assume 5 points per goal on average
        # Assists from xA: assume 3 points per assist on average  
        xg_points = (xg_data["xg_per_90"] * minutes_played / 90) * 5.0
        xa_points = (xg_data["xa_per_90"] * minutes_played / 90) * 3.0
        
        # Blend with base projection (70% base, 30% xG/xA)
        xg_enhanced = xg_points + xa_points
        return (base_points * 0.7) + (xg_enhanced * 0.3)
    
    def apply_zone_weakness_adjustment(self, base_projection: float, opponent_team_id: int, 
                                     player_position: str, attack_style: str = "balanced") -> float:
        """
        Apply zone weakness adjustments to projection.
        
        Args:
            base_projection: Base projection before zone adjustment
            opponent_team_id: ID of the opposing team
            player_position: Position of the attacking player
            attack_style: Style of attack (balanced, wing_heavy, central, set_piece)
            
        Returns:
            Adjusted projection incorporating zone weaknesses
        """
        if not self.enable_zone_weakness:
            return base_projection
        
        # Get relevant zones for the position
        attack_zones = self.get_position_attack_zones(player_position)
        
        if not attack_zones:
            return base_projection
        
        # Calculate weighted average of zone multipliers
        total_multiplier = 0.0
        zone_weights = {
            "balanced": {"central": 0.4, "left_wing": 0.15, "right_wing": 0.15, "box_central": 0.2, "set_pieces": 0.1},
            "wing_heavy": {"left_wing": 0.3, "right_wing": 0.3, "central": 0.2, "box_left": 0.1, "box_right": 0.1},
            "central": {"central": 0.5, "box_central": 0.3, "set_pieces": 0.2},
            "set_piece": {"set_pieces": 0.8, "box_central": 0.2}
        }
        
        weights = zone_weights.get(attack_style, zone_weights["balanced"])
        
        for zone in attack_zones:
            if zone in weights:
                zone_multiplier = self.get_zone_weakness_multiplier(opponent_team_id, zone)
                total_multiplier += zone_multiplier * weights[zone]
        
        # Normalize if we don't have full weight coverage
        weight_sum = sum(weights.get(zone, 0) for zone in attack_zones)
        if weight_sum > 0:
            total_multiplier = total_multiplier / weight_sum
        else:
            total_multiplier = 1.0
        
        return base_projection * total_multiplier
    
    def get_enhanced_projection(self, player_id: int, base_projection: float, 
                               opponent_team_id: Optional[int] = None,
                               player_position: str = "MID", minutes_played: int = 90,
                               attack_style: str = "balanced") -> Dict[str, Any]:
        """
        Get fully enhanced projection with both xG/xA and zone weakness adjustments.
        
        Args:
            player_id: FPL player ID
            base_projection: Original projection
            opponent_team_id: ID of opponent team (for zone weakness)
            player_position: Player position
            minutes_played: Expected minutes
            attack_style: Style of attack
            
        Returns:
            Enhanced projection with breakdown
        """
        # Start with base projection
        current_projection = base_projection
        
        # Apply xG/xA enhancement
        xg_enhanced = self.calculate_xg_based_projection(player_id, current_projection, minutes_played)
        xg_adjustment = xg_enhanced - current_projection
        
        # Apply zone weakness adjustment
        if opponent_team_id:
            zone_enhanced = self.apply_zone_weakness_adjustment(xg_enhanced, opponent_team_id, player_position, attack_style)
            zone_adjustment = zone_enhanced - xg_enhanced
        else:
            zone_enhanced = xg_enhanced
            zone_adjustment = 0.0
        
        return {
            "base_projection": round(base_projection, 2),
            "xg_enhanced_projection": round(xg_enhanced, 2),
            "final_projection": round(zone_enhanced, 2),
            "xg_adjustment": round(xg_adjustment, 2),
            "zone_adjustment": round(zone_adjustment, 2),
            "total_enhancement": round(zone_enhanced - base_projection, 2),
            "xg_data": self.get_player_xg_xa(player_id),
            "zone_multiplier": self.get_zone_weakness_multiplier(opponent_team_id or 0, "central") if opponent_team_id else 1.0
        }
    
    def is_data_available(self) -> Dict[str, bool]:
        """Check if advanced metrics data is available."""
        return {
            "xgxa_available": self._xgxa_data is not None,
            "zone_weakness_available": self._zone_weakness_data is not None,
            "advanced_metrics_enabled": self.enable_advanced_metrics,
            "zone_weakness_enabled": self.enable_zone_weakness
        }


# Create a default instance that can be imported
default_metrics_engine = AdvancedMetricsEngine(
    enable_advanced_metrics=os.getenv("ENABLE_ADVANCED_METRICS", "true").lower() == "true",
    enable_zone_weakness=os.getenv("ENABLE_ZONE_WEAKNESS", "true").lower() == "true"
)