"""Advanced scenario planning for FPL gameweeks."""
from typing import List, Dict, Any, Optional, Tuple
import itertools
from datetime import datetime, timedelta
from ..api.client import FPLClient
from ..analysis.fixtures import compute_fixture_difficulty
from ..analysis.projections import calculate_horizon_projection
from ..analysis.decisions import analyze_transfer_scenario


class ScenarioPlanner:
    """Advanced scenario planning for FPL gameweeks and transfers."""
    
    def __init__(self, client: Optional[FPLClient] = None):
        self.client = client or FPLClient()
    
    def plan_gameweek_scenarios(self, team_state: Dict[str, Any], 
                               scenario_count: int = 5) -> List[Dict[str, Any]]:
        """
        Plan multiple scenarios for upcoming gameweeks.
        
        Args:
            team_state: Current team state with player_ids, budget, transfers
            scenario_count: Number of scenarios to generate
        
        Returns:
            List of optimized scenarios
        """
        current_team_ids = team_state.get("player_ids", [])
        budget = team_state.get("budget", 100.0)
        free_transfers = team_state.get("free_transfers", 1)
        horizon_gws = team_state.get("horizon_gameweeks", 5)
        
        scenarios = []
        
        # Scenario 1: Conservative (no transfers)
        conservative_scenario = self._plan_conservative_scenario(
            current_team_ids, horizon_gws
        )
        scenarios.append(conservative_scenario)
        
        # Scenario 2: Single transfer (best value)
        if free_transfers >= 1:
            single_transfer_scenario = self._plan_single_transfer_scenario(
                current_team_ids, budget, horizon_gws
            )
            scenarios.append(single_transfer_scenario)
        
        # Scenario 3: Double transfer (if available)
        if free_transfers >= 2:
            double_transfer_scenario = self._plan_double_transfer_scenario(
                current_team_ids, budget, horizon_gws
            )
            scenarios.append(double_transfer_scenario)
        
        # Scenario 4: Aggressive (hit for key transfers)
        aggressive_scenario = self._plan_aggressive_scenario(
            current_team_ids, budget, horizon_gws
        )
        scenarios.append(aggressive_scenario)
        
        # Scenario 5: Fixture-based (optimize for next 3 GWs)
        fixture_scenario = self._plan_fixture_based_scenario(
            current_team_ids, budget, horizon_gws
        )
        scenarios.append(fixture_scenario)
        
        # Rank scenarios by expected points
        scenarios.sort(key=lambda x: x["expected_points"], reverse=True)
        
        return scenarios[:scenario_count]
    
    def _plan_conservative_scenario(self, team_ids: List[int], 
                                  horizon_gws: int) -> Dict[str, Any]:
        """Plan conservative scenario with no transfers."""
        total_projected = 0
        player_projections = []
        
        for player_id in team_ids:
            projection = calculate_horizon_projection(player_id, horizon_gws, self.client)
            total_projected += projection.get("total_projected_points", 0)
            player_projections.append(projection)
        
        return {
            "name": "Conservative (No Transfers)",
            "description": "Keep current team, no transfers used",
            "transfers": [],
            "transfer_cost": 0,
            "expected_points": total_projected,
            "net_points": total_projected,  # No transfer hits
            "risk_level": "Low",
            "player_projections": player_projections,
            "reasoning": "Safest option - rely on current players without taking risks"
        }
    
    def _plan_single_transfer_scenario(self, team_ids: List[int], budget: float,
                                     horizon_gws: int) -> Dict[str, Any]:
        """Plan best single transfer scenario."""
        players = self.client.get_players()
        player_lookup = {p["id"]: p for p in players}
        current_players = [player_lookup[pid] for pid in team_ids if pid in player_lookup]
        
        best_transfer = None
        best_gain = 0
        
        # Find best single transfer
        for out_player in current_players:
            out_id = out_player["id"]
            out_cost = out_player.get("now_cost", 0) / 10.0
            out_position = out_player.get("element_type")
            
            # Find best replacements
            available_budget = budget + out_cost
            candidates = [
                p for p in players 
                if (p.get("element_type") == out_position and 
                    p.get("now_cost", 0) / 10.0 <= available_budget and
                    p["id"] not in team_ids and
                    p.get("status") == "a")
            ]
            
            for in_player in candidates[:20]:  # Limit to top candidates
                in_id = in_player["id"]
                
                # Calculate point gain
                out_projection = calculate_horizon_projection(out_id, horizon_gws, self.client)
                in_projection = calculate_horizon_projection(in_id, horizon_gws, self.client)
                
                point_gain = (in_projection.get("total_projected_points", 0) - 
                            out_projection.get("total_projected_points", 0))
                
                if point_gain > best_gain:
                    best_gain = point_gain
                    best_transfer = {
                        "out": out_player,
                        "in": in_player,
                        "cost_change": in_player.get("now_cost", 0) / 10.0 - out_cost,
                        "point_gain": point_gain
                    }
        
        if best_transfer:
            # Calculate total expected points with transfer
            baseline_points = sum(
                calculate_horizon_projection(pid, horizon_gws, self.client).get("total_projected_points", 0)
                for pid in team_ids
            )
            expected_points = baseline_points + best_transfer["point_gain"]
            
            return {
                "name": "Single Transfer",
                "description": f"Transfer {best_transfer['out'].get('second_name')} → {best_transfer['in'].get('second_name')}",
                "transfers": [best_transfer],
                "transfer_cost": 0,  # Free transfer
                "expected_points": expected_points,
                "net_points": expected_points,
                "risk_level": "Medium",
                "reasoning": f"Best single transfer gains {best_transfer['point_gain']:.1f} points over {horizon_gws} gameweeks"
            }
        else:
            return self._plan_conservative_scenario(team_ids, horizon_gws)
    
    def _plan_double_transfer_scenario(self, team_ids: List[int], budget: float,
                                     horizon_gws: int) -> Dict[str, Any]:
        """Plan best double transfer scenario."""
        # This is a simplified version - full optimization would be computationally expensive
        single_scenario = self._plan_single_transfer_scenario(team_ids, budget, horizon_gws)
        
        if not single_scenario.get("transfers"):
            return single_scenario
        
        # For now, return single transfer with note about double potential
        scenario = single_scenario.copy()
        scenario["name"] = "Double Transfer"
        scenario["description"] += " + consider second transfer"
        scenario["reasoning"] += ". Second transfer could add more value."
        scenario["risk_level"] = "Medium-High"
        
        return scenario
    
    def _plan_aggressive_scenario(self, team_ids: List[int], budget: float,
                                horizon_gws: int) -> Dict[str, Any]:
        """Plan aggressive scenario with potential hits."""
        single_scenario = self._plan_single_transfer_scenario(team_ids, budget, horizon_gws)
        
        if not single_scenario.get("transfers"):
            return single_scenario
        
        # Consider taking a -4 hit for high-gain transfers
        best_transfer = single_scenario["transfers"][0]
        expected_gain = best_transfer.get("point_gain", 0)
        
        if expected_gain > 6:  # Worth a -4 hit
            scenario = single_scenario.copy()
            scenario["name"] = "Aggressive (-4 Hit)"
            scenario["description"] = f"Take -4 hit for {best_transfer['in'].get('second_name')}"
            scenario["transfer_cost"] = 4
            scenario["net_points"] = scenario["expected_points"] - 4
            scenario["risk_level"] = "High"
            scenario["reasoning"] = f"High expected gain ({expected_gain:.1f}) justifies -4 hit"
        else:
            scenario = single_scenario.copy()
            scenario["name"] = "Aggressive (Free Transfer)"
            scenario["risk_level"] = "Medium-High"
        
        return scenario
    
    def _plan_fixture_based_scenario(self, team_ids: List[int], budget: float,
                                   horizon_gws: int) -> Dict[str, Any]:
        """Plan scenario optimized for next 3 gameweeks fixtures."""
        players = self.client.get_players()
        player_lookup = {p["id"]: p for p in players}
        
        # Get teams with best fixtures
        teams = self.client.get_teams()
        team_fixtures = {}
        
        for team in teams:
            team_id = team["id"]
            fixture_data = compute_fixture_difficulty(team_id, 3, self.client)  # Focus on next 3 GWs
            team_fixtures[team_id] = fixture_data.get("average_difficulty", 3.0)
        
        # Sort teams by fixture difficulty (lower is better)
        best_fixture_teams = sorted(team_fixtures.items(), key=lambda x: x[1])[:5]
        
        # Find best players from teams with good fixtures
        target_players = []
        for team_id, difficulty in best_fixture_teams:
            team_players = [p for p in players if p.get("team") == team_id and p.get("status") == "a"]
            # Sort by points per game
            team_players.sort(key=lambda p: float(p.get("points_per_game", "0") or "0"), reverse=True)
            target_players.extend(team_players[:3])  # Top 3 from each team
        
        # Find best transfer to fixture-friendly player
        current_players = [player_lookup[pid] for pid in team_ids if pid in player_lookup]
        best_transfer = None
        best_gain = 0
        
        for out_player in current_players:
            out_id = out_player["id"]
            out_cost = out_player.get("now_cost", 0) / 10.0
            out_position = out_player.get("element_type")
            available_budget = budget + out_cost
            
            candidates = [
                p for p in target_players
                if (p.get("element_type") == out_position and 
                    p.get("now_cost", 0) / 10.0 <= available_budget and
                    p["id"] not in team_ids)
            ]
            
            for in_player in candidates[:10]:
                in_id = in_player["id"]
                
                # Calculate short-term projection (3 GWs)
                out_projection = calculate_horizon_projection(out_id, 3, self.client)
                in_projection = calculate_horizon_projection(in_id, 3, self.client)
                
                point_gain = (in_projection.get("total_projected_points", 0) - 
                            out_projection.get("total_projected_points", 0))
                
                if point_gain > best_gain:
                    best_gain = point_gain
                    best_transfer = {
                        "out": out_player,
                        "in": in_player,
                        "cost_change": in_player.get("now_cost", 0) / 10.0 - out_cost,
                        "point_gain": point_gain,
                        "fixture_difficulty": team_fixtures.get(in_player.get("team"), 3.0)
                    }
        
        if best_transfer:
            baseline_points = sum(
                calculate_horizon_projection(pid, horizon_gws, self.client).get("total_projected_points", 0)
                for pid in team_ids
            )
            expected_points = baseline_points + best_transfer["point_gain"]
            
            return {
                "name": "Fixture Focus",
                "description": f"Target good fixtures: {best_transfer['in'].get('second_name')}",
                "transfers": [best_transfer],
                "transfer_cost": 0,
                "expected_points": expected_points,
                "net_points": expected_points,
                "risk_level": "Medium",
                "reasoning": f"Optimize for next 3 GWs with fixture difficulty {best_transfer['fixture_difficulty']:.1f}"
            }
        else:
            return self._plan_conservative_scenario(team_ids, horizon_gws)
    
    def compare_scenarios(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare and rank scenarios."""
        if not scenarios:
            return {"error": "No scenarios to compare"}
        
        # Sort by net points (after transfer costs)
        ranked_scenarios = sorted(scenarios, key=lambda x: x.get("net_points", 0), reverse=True)
        
        best_scenario = ranked_scenarios[0]
        worst_scenario = ranked_scenarios[-1]
        
        return {
            "best_scenario": best_scenario,
            "worst_scenario": worst_scenario,
            "point_range": best_scenario.get("net_points", 0) - worst_scenario.get("net_points", 0),
            "recommendation": self._generate_scenario_recommendation(ranked_scenarios),
            "ranked_scenarios": ranked_scenarios
        }
    
    def _generate_scenario_recommendation(self, ranked_scenarios: List[Dict[str, Any]]) -> str:
        """Generate recommendation based on scenario comparison."""
        if not ranked_scenarios:
            return "No scenarios available for recommendation."
        
        best = ranked_scenarios[0]
        best_name = best.get("name", "Unknown")
        best_points = best.get("net_points", 0)
        best_risk = best.get("risk_level", "Unknown")
        
        if len(ranked_scenarios) > 1:
            second_best = ranked_scenarios[1]
            point_diff = best_points - second_best.get("net_points", 0)
            
            if point_diff < 2:
                return f"Close choice: {best_name} edges out slightly (+{point_diff:.1f} pts) but consider risk level ({best_risk})"
            else:
                return f"Clear winner: {best_name} (+{point_diff:.1f} pts advantage, {best_risk} risk)"
        else:
            return f"Recommended: {best_name} ({best_points:.1f} expected points, {best_risk} risk)"
    
    def plan_weekly_strategy(self, team_state: Dict[str, Any], 
                           weeks_ahead: int = 4) -> Dict[str, Any]:
        """Plan strategy for multiple weeks ahead."""
        current_gw = self.client.get_current_gameweek()
        if not current_gw:
            return {"error": "Could not determine current gameweek"}
        
        current_gw_id = current_gw.get("id", 1)
        
        weekly_plans = {}
        cumulative_transfers = []
        
        for week_offset in range(weeks_ahead):
            target_gw = current_gw_id + week_offset
            
            # Plan for this specific week
            week_plan = self._plan_single_gameweek(team_state, target_gw, cumulative_transfers)
            weekly_plans[f"GW{target_gw}"] = week_plan
            
            # Update cumulative transfers
            if week_plan.get("recommended_transfers"):
                cumulative_transfers.extend(week_plan["recommended_transfers"])
        
        return {
            "current_gameweek": current_gw_id,
            "weeks_planned": weeks_ahead,
            "weekly_strategy": weekly_plans,
            "total_transfers_planned": len(cumulative_transfers),
            "summary": self._generate_weekly_summary(weekly_plans)
        }
    
    def _plan_single_gameweek(self, team_state: Dict[str, Any], target_gw: int,
                            existing_transfers: List[Dict]) -> Dict[str, Any]:
        """Plan strategy for a single gameweek."""
        current_team_ids = team_state.get("player_ids", [])
        
        # Analyze fixtures for this specific gameweek
        fixtures = self.client.get_fixtures(target_gw)
        gw_fixtures = {}
        
        for fixture in fixtures:
            home_team = fixture.get("team_h")
            away_team = fixture.get("team_a")
            difficulty = fixture.get("team_h_difficulty", 3) + fixture.get("team_a_difficulty", 3)
            
            gw_fixtures[home_team] = {"opponent": away_team, "home": True, "difficulty": fixture.get("team_h_difficulty", 3)}
            gw_fixtures[away_team] = {"opponent": home_team, "home": False, "difficulty": fixture.get("team_a_difficulty", 3)}
        
        # Analyze current team for this gameweek
        players = self.client.get_players()
        player_lookup = {p["id"]: p for p in players}
        
        team_analysis = []
        for player_id in current_team_ids:
            if player_id in player_lookup:
                player = player_lookup[player_id]
                team_id = player.get("team")
                fixture_info = gw_fixtures.get(team_id, {})
                
                team_analysis.append({
                    "player": player,
                    "fixture": fixture_info,
                    "projected_points": self._estimate_gw_points(player, fixture_info)
                })
        
        # Identify potential improvements
        recommended_transfers = []
        transfer_value = 0
        
        # Simple heuristic: look for players with difficult fixtures
        for analysis in team_analysis:
            fixture = analysis["fixture"]
            if fixture.get("difficulty", 3) >= 4:  # Difficult fixture
                # This is a simplified recommendation
                recommended_transfers.append({
                    "out": analysis["player"],
                    "reason": f"Difficult fixture (difficulty {fixture.get('difficulty')})",
                    "priority": "medium"
                })
        
        return {
            "gameweek": target_gw,
            "team_analysis": team_analysis,
            "recommended_transfers": recommended_transfers[:2],  # Max 2 per week
            "expected_points": sum(a["projected_points"] for a in team_analysis),
            "fixture_summary": f"{len([a for a in team_analysis if a['fixture'].get('difficulty', 3) <= 2])} easy fixtures"
        }
    
    def _estimate_gw_points(self, player: Dict[str, Any], fixture_info: Dict[str, Any]) -> float:
        """Estimate points for a single gameweek."""
        base_ppg = float(player.get("points_per_game", "0") or "0")
        
        # Adjust based on fixture difficulty
        difficulty = fixture_info.get("difficulty", 3)
        if difficulty <= 2:
            multiplier = 1.2  # Easy fixture
        elif difficulty >= 4:
            multiplier = 0.8  # Hard fixture
        else:
            multiplier = 1.0  # Average fixture
        
        # Home/away adjustment
        if fixture_info.get("home"):
            multiplier *= 1.1  # Home advantage
        
        return base_ppg * multiplier
    
    def _generate_weekly_summary(self, weekly_plans: Dict[str, Any]) -> str:
        """Generate summary of weekly strategy."""
        total_transfers = sum(
            len(plan.get("recommended_transfers", [])) 
            for plan in weekly_plans.values()
        )
        
        total_expected = sum(
            plan.get("expected_points", 0) 
            for plan in weekly_plans.values()
        )
        
        return f"Weekly strategy: {total_expected:.1f} expected points over {len(weekly_plans)} gameweeks, {total_transfers} transfers recommended"