"""Transfer decision support and scenario analysis."""
from typing import List, Dict, Any, Optional, Tuple
from ..api.client import FPLClient
from .projections import calculate_horizon_projection


def analyze_transfer_scenario(player_out_id: int, player_in_id: int, horizon_gameweeks: int = 5, 
                            client: Optional[FPLClient] = None) -> Dict[str, Any]:
    """
    Analyze a transfer scenario between two players.
    
    Args:
        player_out_id: ID of player to transfer out
        player_in_id: ID of player to transfer in
        horizon_gameweeks: Number of gameweeks to analyze
        client: Optional FPL client instance
    
    Returns:
        Transfer scenario analysis
    """
    if client is None:
        client = FPLClient()
    
    try:
        players = client.get_players()
        player_lookup = {p["id"]: p for p in players}
        
        player_out = player_lookup.get(player_out_id)
        player_in = player_lookup.get(player_in_id)
        
        if not player_out or not player_in:
            return {"error": "One or both players not found"}
        
        # Get projections for both players
        out_projection = calculate_horizon_projection(player_out_id, horizon_gameweeks, client)
        in_projection = calculate_horizon_projection(player_in_id, horizon_gameweeks, client)
        
        if "error" in out_projection or "error" in in_projection:
            return {"error": "Could not calculate projections"}
        
        # Calculate cost difference
        cost_out = player_out.get("now_cost", 0) / 10.0
        cost_in = player_in.get("now_cost", 0) / 10.0
        cost_change = cost_in - cost_out
        
        # Calculate projected points difference
        points_out = out_projection.get("total_projected_points", 0)
        points_in = in_projection.get("total_projected_points", 0)
        points_gain = points_in - points_out
        
        # Calculate confidence and risk scores
        conf_out = out_projection.get("average_confidence", 0.5)
        conf_in = in_projection.get("average_confidence", 0.5)
        confidence_score = (conf_out + conf_in) / 2
        
        # Risk assessment
        risk_factors = []
        risk_score = 0.0
        
        # Cost risk - higher cost change increases risk
        if cost_change > 1.0:
            risk_factors.append("High cost increase")
            risk_score += 0.2
        elif cost_change > 0.5:
            risk_factors.append("Moderate cost increase")
            risk_score += 0.1
        
        # Form risk - check recent form
        out_form = float(player_out.get("form", "0") or "0")
        in_form = float(player_in.get("form", "0") or "0")
        
        if in_form < 3.0:
            risk_factors.append("New player poor recent form")
            risk_score += 0.2
        elif out_form > 5.0:
            risk_factors.append("Transferring out in-form player")
            risk_score += 0.15
        
        # Ownership risk
        out_ownership = float(player_out.get("selected_by_percent", "0") or "0")
        in_ownership = float(player_in.get("selected_by_percent", "0") or "0")
        
        if out_ownership > 20.0 and in_ownership < 5.0:
            risk_factors.append("Moving from popular to differential pick")
            risk_score += 0.1
        
        # Injury risk
        if player_in.get("status") != "a":
            risk_factors.append("New player injury concerns")
            risk_score += 0.3
        
        # Cap risk score
        risk_score = min(1.0, risk_score)
        
        # Generate reasoning
        reasoning_parts = []
        
        if points_gain > 2.0:
            reasoning_parts.append(f"Strong projected gain of {points_gain:.1f} points over {horizon_gameweeks} gameweeks")
        elif points_gain > 0.5:
            reasoning_parts.append(f"Modest projected gain of {points_gain:.1f} points")
        elif points_gain < -1.0:
            reasoning_parts.append(f"Projected loss of {abs(points_gain):.1f} points - not recommended")
        else:
            reasoning_parts.append("Minimal projected points difference")
        
        if cost_change > 0:
            reasoning_parts.append(f"Costs £{cost_change:.1f}m more")
        elif cost_change < -0.5:
            reasoning_parts.append(f"Frees up £{abs(cost_change):.1f}m in budget")
        
        if risk_factors:
            reasoning_parts.append(f"Risk factors: {', '.join(risk_factors)}")
        
        # Recommendation
        if points_gain > 1.0 and risk_score < 0.5:
            recommendation = "Strongly Recommended"
        elif points_gain > 0.5 and risk_score < 0.7:
            recommendation = "Recommended"
        elif points_gain > 0 and risk_score < 0.3:
            recommendation = "Consider"
        elif abs(points_gain) <= 0.5:
            recommendation = "Neutral"
        else:
            recommendation = "Not Recommended"
        
        return {
            "player_out_id": player_out_id,
            "player_in_id": player_in_id,
            "player_out_name": f"{player_out.get('first_name', '')} {player_out.get('second_name', '')}".strip(),
            "player_in_name": f"{player_in.get('first_name', '')} {player_in.get('second_name', '')}".strip(),
            "cost_change": round(cost_change, 1),
            "projected_points_gain": round(points_gain, 2),
            "horizon_gameweeks": horizon_gameweeks,
            "confidence_score": round(confidence_score, 2),
            "risk_score": round(risk_score, 2),
            "risk_factors": risk_factors,
            "reasoning": ". ".join(reasoning_parts),
            "recommendation": recommendation,
            "player_out_projection": out_projection,
            "player_in_projection": in_projection
        }
    
    finally:
        if client and hasattr(client, '_created_locally'):
            client.close()


def find_transfer_targets(player_out_id: int, max_cost_increase: float = 2.0, 
                         same_position_only: bool = True, horizon_gameweeks: int = 5,
                         limit: int = 10) -> List[Dict[str, Any]]:
    """
    Find suitable transfer targets for a given player.
    
    Args:
        player_out_id: ID of player to transfer out
        max_cost_increase: Maximum cost increase allowed
        same_position_only: Whether to only consider same position
        horizon_gameweeks: Number of gameweeks to analyze
        limit: Maximum number of suggestions
    
    Returns:
        List of transfer suggestions sorted by projected gain
    """
    with FPLClient() as client:
        players = client.get_players()
        player_lookup = {p["id"]: p for p in players}
        
        player_out = player_lookup.get(player_out_id)
        if not player_out:
            return []
        
        player_out_cost = player_out.get("now_cost", 0) / 10.0
        player_out_position = player_out.get("element_type")
        max_cost = player_out_cost + max_cost_increase
        
        candidates = []
        
        for player in players:
            # Skip the same player
            if player["id"] == player_out_id:
                continue
            
            # Position filter
            if same_position_only and player.get("element_type") != player_out_position:
                continue
            
            # Cost filter
            player_cost = player.get("now_cost", 0) / 10.0
            if player_cost > max_cost:
                continue
            
            # Availability filter
            if player.get("status") != "a":
                continue
            
            candidates.append(player)
        
        # Analyze transfer scenarios for all candidates
        transfer_scenarios = []
        
        for candidate in candidates:
            scenario = analyze_transfer_scenario(
                player_out_id, candidate["id"], horizon_gameweeks, client
            )
            
            if "error" not in scenario:
                transfer_scenarios.append(scenario)
        
        # Sort by projected points gain
        transfer_scenarios.sort(key=lambda x: x.get("projected_points_gain", 0), reverse=True)
        
        return transfer_scenarios[:limit]


def analyze_multiple_transfers(transfer_pairs: List[Tuple[int, int]], horizon_gameweeks: int = 5) -> Dict[str, Any]:
    """
    Analyze multiple transfer scenarios together.
    
    Args:
        transfer_pairs: List of (player_out_id, player_in_id) tuples
        horizon_gameweeks: Number of gameweeks to analyze
    
    Returns:
        Combined analysis of all transfers
    """
    with FPLClient() as client:
        scenarios = []
        total_cost_change = 0.0
        total_points_gain = 0.0
        
        for player_out_id, player_in_id in transfer_pairs:
            scenario = analyze_transfer_scenario(player_out_id, player_in_id, horizon_gameweeks, client)
            
            if "error" not in scenario:
                scenarios.append(scenario)
                total_cost_change += scenario.get("cost_change", 0)
                total_points_gain += scenario.get("projected_points_gain", 0)
        
        # Calculate combined metrics
        avg_confidence = sum(s.get("confidence_score", 0) for s in scenarios) / len(scenarios) if scenarios else 0
        avg_risk = sum(s.get("risk_score", 0) for s in scenarios) / len(scenarios) if scenarios else 0
        
        # Overall recommendation
        if total_points_gain > len(scenarios) * 1.5 and avg_risk < 0.5:
            overall_recommendation = "Strongly Recommended"
        elif total_points_gain > len(scenarios) * 0.5 and avg_risk < 0.7:
            overall_recommendation = "Recommended"
        elif total_points_gain > 0 and avg_risk < 0.6:
            overall_recommendation = "Consider"
        else:
            overall_recommendation = "Not Recommended"
        
        return {
            "scenarios": scenarios,
            "total_cost_change": round(total_cost_change, 1),
            "total_projected_points_gain": round(total_points_gain, 2),
            "average_confidence": round(avg_confidence, 2),
            "average_risk_score": round(avg_risk, 2),
            "horizon_gameweeks": horizon_gameweeks,
            "overall_recommendation": overall_recommendation,
            "transfer_count": len(scenarios)
        }


def evaluate_team_decisions(current_team_ids: List[int], budget: float = 100.0, 
                          free_transfers: int = 1, horizon_gameweeks: int = 5) -> Dict[str, Any]:
    """
    Evaluate potential decisions for an entire team.
    
    Args:
        current_team_ids: List of current team player IDs
        budget: Available budget
        free_transfers: Number of free transfers available
        horizon_gameweeks: Number of gameweeks to analyze
    
    Returns:
        Team-wide decision analysis and recommendations
    """
    with FPLClient() as client:
        players = client.get_players()
        player_lookup = {p["id"]: p for p in players}
        
        # Analyze current team
        team_analysis = []
        total_projected_points = 0
        problem_players = []
        
        for player_id in current_team_ids:
            player = player_lookup.get(player_id)
            if not player:
                continue
            
            projection = calculate_horizon_projection(player_id, horizon_gameweeks, client)
            
            if "error" not in projection:
                player_info = {
                    "player_id": player_id,
                    "name": f"{player.get('first_name', '')} {player.get('second_name', '')}".strip(),
                    "cost": player.get("now_cost", 0) / 10.0,
                    "projection": projection,
                    "status": player.get("status", "a"),
                    "form": float(player.get("form", "0") or "0")
                }
                
                team_analysis.append(player_info)
                total_projected_points += projection.get("total_projected_points", 0)
                
                # Identify problem players
                if (player.get("status") != "a" or 
                    projection.get("total_projected_points", 0) < horizon_gameweeks * 2 or
                    float(player.get("form", "0") or "0") < 2.0):
                    problem_players.append(player_info)
        
        # Generate transfer suggestions
        transfer_suggestions = []
        
        if free_transfers > 0 and problem_players:
            # Sort problem players by worst projected points
            problem_players.sort(key=lambda x: x["projection"].get("total_projected_points", 0))
            
            for i, problem_player in enumerate(problem_players[:free_transfers]):
                suggestions = find_transfer_targets(
                    problem_player["player_id"], 
                    max_cost_increase=2.0, 
                    horizon_gameweeks=horizon_gameweeks, 
                    limit=3
                )
                
                if suggestions:
                    transfer_suggestions.append({
                        "priority": i + 1,
                        "player_out": problem_player,
                        "suggestions": suggestions[:3]
                    })
        
        return {
            "team_analysis": team_analysis,
            "total_projected_points": round(total_projected_points, 2),
            "average_projected_points": round(total_projected_points / len(team_analysis), 2) if team_analysis else 0,
            "problem_players": problem_players,
            "transfer_suggestions": transfer_suggestions,
            "free_transfers": free_transfers,
            "budget": budget,
            "horizon_gameweeks": horizon_gameweeks
        }