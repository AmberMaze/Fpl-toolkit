"""AI-powered advisor for FPL decision making."""
from typing import List, Dict, Any, Optional
from ..api.client import FPLClient
from .fixtures import compute_fixture_difficulty
from .projections import calculate_horizon_projection
from .decisions import analyze_transfer_scenario, find_transfer_targets


class FPLAdvisor:
    """AI-powered FPL advisor combining heuristics with optional ML models."""
    
    def __init__(self, client: Optional[FPLClient] = None):
        self.client = client or FPLClient()
        self.model = None
        self._try_load_model()
    
    def _try_load_model(self):
        """Try to load sentence-transformers model if available."""
        try:
            from sentence_transformers import SentenceTransformer
            model_name = "all-MiniLM-L6-v2"  # Lightweight model
            self.model = SentenceTransformer(model_name)
        except ImportError:
            # Fallback to heuristic-only approach
            self.model = None
    
    def detect_underperformers(self, team_players: List[Dict[str, Any]], points_threshold: float = 3.0, 
                              cost_threshold: float = 8.0) -> List[Dict[str, Any]]:
        """
        Detect underperforming players based on points and cost.
        
        Args:
            team_players: List of player data
            points_threshold: Minimum points per game threshold
            cost_threshold: Cost threshold for premium players
        
        Returns:
            List of underperforming players with reasoning
        """
        underperformers = []
        
        for player in team_players:
            points_per_game = float(player.get("points_per_game", "0") or "0")
            cost = player.get("now_cost", 0) / 10.0
            form = float(player.get("form", "0") or "0")
            
            issues = []
            
            # Check overall performance
            if points_per_game < points_threshold:
                issues.append(f"Low average: {points_per_game:.1f} PPG")
            
            # Check premium player performance
            if cost >= cost_threshold and points_per_game < 6.0:
                issues.append(f"Premium underperformer at £{cost:.1f}m")
            
            # Check recent form
            if form < 2.0:
                issues.append(f"Poor recent form: {form:.1f}")
            
            # Check injury status
            if player.get("status") != "a":
                issues.append("Injury/suspension concerns")
            
            if issues:
                underperformers.append({
                    "player": player,
                    "issues": issues,
                    "priority": len(issues) + (1 if cost >= cost_threshold else 0)
                })
        
        # Sort by priority (most issues first)
        underperformers.sort(key=lambda x: x["priority"], reverse=True)
        return underperformers
    
    def detect_fixture_swings(self, team_ids: List[int], horizon_gameweeks: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect teams with significant fixture difficulty changes.
        
        Args:
            team_ids: List of team IDs to analyze
            horizon_gameweeks: Number of gameweeks to analyze
        
        Returns:
            Dictionary with improving and worsening fixture lists
        """
        improving_fixtures = []
        worsening_fixtures = []
        
        teams = self.client.get_teams()
        team_lookup = {t["id"]: t for t in teams}
        
        for team_id in team_ids:
            fixture_data = compute_fixture_difficulty(team_id, horizon_gameweeks, self.client)
            
            if fixture_data["analyzed_gameweeks"] >= 3:
                trend = fixture_data["difficulty_trend"]
                team_name = team_lookup.get(team_id, {}).get("name", f"Team {team_id}")
                
                fixture_info = {
                    "team_id": team_id,
                    "team_name": team_name,
                    "average_difficulty": fixture_data["average_difficulty"],
                    "trend": trend,
                    "fixtures": fixture_data["fixtures"]
                }
                
                if trend == "getting_easier":
                    improving_fixtures.append(fixture_info)
                elif trend == "getting_harder":
                    worsening_fixtures.append(fixture_info)
        
        return {
            "improving_fixtures": improving_fixtures,
            "worsening_fixtures": worsening_fixtures
        }
    
    def highlight_differentials(self, ownership_threshold: float = 10.0, min_points: float = 4.0) -> List[Dict[str, Any]]:
        """
        Highlight low-ownership players with good potential.
        
        Args:
            ownership_threshold: Maximum ownership percentage
            min_points: Minimum points per game threshold
        
        Returns:
            List of differential players
        """
        players = self.client.get_players()
        differentials = []
        
        for player in players:
            ownership = float(player.get("selected_by_percent", "0") or "0")
            points_per_game = float(player.get("points_per_game", "0") or "0")
            form = float(player.get("form", "0") or "0")
            
            if (ownership <= ownership_threshold and 
                points_per_game >= min_points and 
                player.get("status") == "a"):
                
                differential_score = points_per_game / max(ownership, 1.0)  # Avoid division by zero
                
                differentials.append({
                    "player": player,
                    "ownership": ownership,
                    "points_per_game": points_per_game,
                    "form": form,
                    "differential_score": round(differential_score, 2),
                    "name": f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()
                })
        
        # Sort by differential score
        differentials.sort(key=lambda x: x["differential_score"], reverse=True)
        return differentials[:20]  # Top 20 differentials
    
    def calculate_cost_efficiency(self, players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate cost efficiency for players.
        
        Args:
            players: List of player data
        
        Returns:
            List of players with efficiency metrics
        """
        efficiency_data = []
        
        for player in players:
            cost = player.get("now_cost", 0) / 10.0
            points_per_game = float(player.get("points_per_game", "0") or "0")
            
            if cost > 0:
                efficiency = points_per_game / cost
                
                efficiency_data.append({
                    "player": player,
                    "cost": cost,
                    "points_per_game": points_per_game,
                    "efficiency": round(efficiency, 3),
                    "name": f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()
                })
        
        # Sort by efficiency
        efficiency_data.sort(key=lambda x: x["efficiency"], reverse=True)
        return efficiency_data
    
    def generate_team_summary(self, team_analysis: Dict[str, Any]) -> str:
        """Generate a text summary using AI model or template."""
        if self.model:
            return self._generate_ai_summary(team_analysis)
        else:
            return self._generate_template_summary(team_analysis)
    
    def _generate_template_summary(self, team_analysis: Dict[str, Any]) -> str:
        """Generate summary using template approach."""
        summary_parts = []
        
        # Team overview
        total_points = team_analysis.get("total_projected_points", 0)
        avg_points = team_analysis.get("average_projected_points", 0)
        problem_count = len(team_analysis.get("problem_players", []))
        
        summary_parts.append(f"Team Analysis: Projected {total_points:.1f} points over next {team_analysis.get('horizon_gameweeks', 5)} gameweeks (avg: {avg_points:.1f} per player).")
        
        if problem_count > 0:
            summary_parts.append(f"⚠️ {problem_count} player(s) need attention.")
        else:
            summary_parts.append("✅ Team looks solid with no major concerns.")
        
        # Transfer suggestions
        suggestions = team_analysis.get("transfer_suggestions", [])
        if suggestions:
            summary_parts.append(f"Top transfer priority: {suggestions[0]['player_out']['name']} -> consider {suggestions[0]['suggestions'][0]['player_in_name']} for {suggestions[0]['suggestions'][0]['projected_points_gain']:.1f} point gain.")
        
        return " ".join(summary_parts)
    
    def _generate_ai_summary(self, team_analysis: Dict[str, Any]) -> str:
        """Generate summary using AI model (placeholder for actual implementation)."""
        # This would involve more sophisticated NLP processing
        # For now, fall back to template approach
        return self._generate_template_summary(team_analysis)
    
    def advise_team(self, team_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide comprehensive team advice.
        
        Args:
            team_state: Dictionary containing current team information
        
        Returns:
            Comprehensive advice with structured suggestions
        """
        current_team_ids = team_state.get("player_ids", [])
        budget = team_state.get("budget", 100.0)
        free_transfers = team_state.get("free_transfers", 1)
        horizon_gameweeks = team_state.get("horizon_gameweeks", 5)
        
        # Get player data
        players = self.client.get_players()
        player_lookup = {p["id"]: p for p in players}
        current_players = [player_lookup[pid] for pid in current_team_ids if pid in player_lookup]
        
        # Run various analyses
        underperformers = self.detect_underperformers(current_players)
        
        # Get team IDs for fixture analysis
        team_ids = list(set(p.get("team") for p in current_players if p.get("team")))
        fixture_swings = self.detect_fixture_swings(team_ids, horizon_gameweeks)
        
        differentials = self.highlight_differentials()
        efficiency_data = self.calculate_cost_efficiency(current_players)
        
        # Generate transfer suggestions
        transfer_suggestions = []
        if free_transfers > 0 and underperformers:
            for underperformer in underperformers[:free_transfers]:
                player_id = underperformer["player"]["id"]
                suggestions = find_transfer_targets(player_id, max_cost_increase=2.0, limit=3)
                
                if suggestions:
                    transfer_suggestions.append({
                        "player_out": underperformer["player"],
                        "issues": underperformer["issues"],
                        "suggestions": suggestions[:3]
                    })
        
        # Compile advice
        advice = {
            "summary": "",
            "underperformers": underperformers,
            "fixture_analysis": fixture_swings,
            "top_differentials": differentials[:10],
            "cost_efficiency": efficiency_data[:10],
            "transfer_suggestions": transfer_suggestions,
            "recommendations": []
        }
        
        # Generate recommendations
        recommendations = []
        
        if underperformers:
            recommendations.append({
                "type": "transfer",
                "priority": "high",
                "message": f"Consider transferring out {underperformers[0]['player'].get('second_name', 'player')} due to: {', '.join(underperformers[0]['issues'])}"
            })
        
        if fixture_swings["improving_fixtures"]:
            best_fixtures = fixture_swings["improving_fixtures"][0]
            recommendations.append({
                "type": "fixtures",
                "priority": "medium",
                "message": f"Target {best_fixtures['team_name']} players - fixtures improving (difficulty: {best_fixtures['average_difficulty']:.1f})"
            })
        
        if differentials:
            recommendations.append({
                "type": "differential",
                "priority": "low",
                "message": f"Consider differential pick: {differentials[0]['name']} ({differentials[0]['ownership']:.1f}% owned, {differentials[0]['points_per_game']:.1f} PPG)"
            })
        
        advice["recommendations"] = recommendations
        
        # Generate summary
        team_analysis_summary = {
            "total_projected_points": sum(calculate_horizon_projection(pid, horizon_gameweeks, self.client).get("total_projected_points", 0) for pid in current_team_ids),
            "problem_players": underperformers,
            "transfer_suggestions": transfer_suggestions,
            "horizon_gameweeks": horizon_gameweeks
        }
        
        advice["summary"] = self.generate_team_summary(team_analysis_summary)
        
        return advice
    
    def close(self):
        """Close the FPL client."""
        if self.client:
            self.client.close()