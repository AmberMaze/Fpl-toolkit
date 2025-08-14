"""Team-centric API endpoints for FPL toolkit."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from ..api.client import FPLClient
from ..ai.advisor import FPLAdvisor
from ..analysis.projections import calculate_horizon_projection
from ..analysis.advanced_metrics import enhance_breakdown_with_advanced_metrics, _simple_event_breakdown


# Create router for team endpoints
team_router = APIRouter(prefix="/team", tags=["team"])


def get_fpl_client():
    """Dependency to get FPL client."""
    client = FPLClient()
    try:
        yield client
    finally:
        client.close()


def get_fpl_advisor():
    """Dependency to get FPL advisor."""
    advisor = FPLAdvisor()
    try:
        yield advisor
    finally:
        advisor.close()


def _simple_minutes_projection(player_data: Dict[str, Any], recent_history: List[Dict[str, Any]]) -> int:
    """
    Estimate expected minutes from recent matches.
    
    Args:
        player_data: Player static data
        recent_history: Recent match history (last 3 matches)
    
    Returns:
        Expected minutes (capped between 15-90)
    """
    if not recent_history:
        # Fallback based on player status
        if player_data.get("status") == "a":  # Available
            return 75  # Default expectation for available players
        else:
            return 30  # Reduced expectation for unavailable/doubtful players
    
    # Calculate average from recent 3 matches
    recent_3 = recent_history[-3:] if len(recent_history) >= 3 else recent_history
    minutes_list = [h.get("minutes", 0) for h in recent_3]
    avg_minutes = sum(minutes_list) / len(minutes_list) if minutes_list else 0
    
    # Cap between 15 and 90
    return max(15, min(90, int(avg_minutes)))


def _simple_event_breakdown_for_projection(projected_points: float, player_data: Dict[str, Any], expected_minutes: int) -> Dict[str, float]:
    """
    Decompose projected points into categories using position-specific weights.
    
    Args:
        projected_points: Total projected points for next GW
        player_data: Player static data including position
        expected_minutes: Expected minutes for the match
    
    Returns:
        Breakdown dictionary with appearance, goals, assists, cs, bonus, misc, total
    """
    position = player_data.get("element_type", 3)  # Default to MID
    
    # Position-specific weights (approximate distribution of points)
    if position == 1:  # GK
        weights = {
            "appearance": 0.25,  # 2 points for playing
            "goals": 0.10,       # Rare but high value
            "assists": 0.05,     # Very rare
            "cs": 0.35,          # Main source of points
            "bonus": 0.15,       # Bonus points
            "misc": 0.10         # Saves, penalties saved, etc.
        }
    elif position == 2:  # DEF
        weights = {
            "appearance": 0.20,
            "goals": 0.15,       # Less frequent but high value
            "assists": 0.20,     # Good source of points
            "cs": 0.25,          # Important for defenders
            "bonus": 0.15,
            "misc": 0.05         # Cards, own goals (negative)
        }
    elif position == 3:  # MID
        weights = {
            "appearance": 0.15,
            "goals": 0.25,       # Main source
            "assists": 0.25,     # Main source
            "cs": 0.10,          # Only if clean sheet
            "bonus": 0.20,
            "misc": 0.05
        }
    else:  # FWD (position == 4)
        weights = {
            "appearance": 0.15,
            "goals": 0.40,       # Primary source
            "assists": 0.15,
            "cs": 0.05,          # Rare
            "bonus": 0.20,
            "misc": 0.05
        }
    
    # Apply form scaling based on recent performance
    form = float(player_data.get("form", "0") or "0")
    form_multiplier = 0.8 + (form / 10.0) * 0.4  # Scale between 0.8-1.2 based on form
    
    # Apply minutes scaling (if less than 60 minutes expected, reduce non-appearance points)
    minutes_multiplier = min(1.0, expected_minutes / 60.0)
    
    # Calculate breakdown
    breakdown = {}
    remaining_points = projected_points
    
    # Appearance points (base 2 for playing, scaled by minutes probability)
    appearance_base = 2.0 if expected_minutes >= 60 else (2.0 * expected_minutes / 90.0)
    breakdown["appearance"] = min(remaining_points, appearance_base)
    remaining_points -= breakdown["appearance"]
    
    # Distribute remaining points according to position weights
    for category in ["goals", "assists", "cs", "bonus", "misc"]:
        if remaining_points <= 0:
            breakdown[category] = 0.0
        else:
            base_allocation = remaining_points * weights[category] / sum(weights[cat] for cat in ["goals", "assists", "cs", "bonus", "misc"])
            
            # Apply form and minutes scaling to non-appearance categories
            if category != "appearance":
                scaled_allocation = base_allocation * form_multiplier * minutes_multiplier
            else:
                scaled_allocation = base_allocation
            
            breakdown[category] = round(min(remaining_points, scaled_allocation), 2)
    
    # Ensure total matches projected points
    breakdown["total"] = round(projected_points, 2)
    
    return breakdown


@team_router.get("/{team_id}/picks")
async def get_team_picks(
    team_id: int,
    gameweek: Optional[int] = Query(None, description="Specific gameweek (default: current)"),
    client: FPLClient = Depends(get_fpl_client)
):
    """
    Get raw picks data from the FPL API for a team.
    
    Returns team picks including bank, event transfers, captain flags, etc.
    """
    try:
        picks_data = client.get_team_picks(team_id, gameweek)
        
        # Also get team info for additional context
        team_info = client.get_user_team(team_id)
        
        response = {
            "team_id": team_id,
            "team_name": team_info.get("name", "Unknown"),
            "manager_name": f"{team_info.get('player_first_name', '')} {team_info.get('player_last_name', '')}".strip(),
            "gameweek": picks_data.get("entry_history", {}).get("event"),
            "picks": picks_data.get("picks", []),
            "bank": picks_data.get("entry_history", {}).get("bank", 0) / 10.0,  # Convert to millions
            "total_transfers": picks_data.get("entry_history", {}).get("event_transfers", 0),
            "transfer_cost": picks_data.get("entry_history", {}).get("event_transfers_cost", 0),
            "points": picks_data.get("entry_history", {}).get("points", 0),
            "overall_rank": picks_data.get("entry_history", {}).get("overall_rank"),
            "raw_picks_data": picks_data  # Include full raw data for completeness
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching team picks: {str(e)}")


@team_router.get("/{team_id}/advisor")
async def get_team_advisor(
    team_id: int,
    horizon: Optional[int] = Query(5, description="Analysis horizon in gameweeks"),
    free_transfers: Optional[int] = Query(1, description="Number of free transfers available"),
    client: FPLClient = Depends(get_fpl_client),
    advisor: FPLAdvisor = Depends(get_fpl_advisor)
):
    """
    Get AI-powered team advice by automatically deriving player IDs from current picks.
    
    Auto-derives player_ids from current picks then invokes existing advisor logic.
    """
    try:
        # Get current team picks to derive player IDs
        picks_data = client.get_team_picks(team_id)
        picks = picks_data.get("picks", [])
        
        if not picks:
            raise HTTPException(status_code=404, detail="No picks found for this team")
        
        # Extract player IDs from picks
        player_ids = [pick.get("element") for pick in picks if pick.get("element")]
        
        if len(player_ids) != 15:
            raise HTTPException(status_code=400, detail=f"Expected 15 players, found {len(player_ids)}")
        
        # Get bank amount for budget calculation
        bank = picks_data.get("entry_history", {}).get("bank", 0) / 10.0
        
        # Prepare team state for advisor
        team_state = {
            "player_ids": player_ids,
            "budget": bank,
            "free_transfers": free_transfers,
            "horizon_gameweeks": horizon
        }
        
        # Get advice from existing advisor
        advice = advisor.advise_team(team_state)
        
        # Return trimmed response as specified
        return {
            "team_id": team_id,
            "summary": advice.get("summary", ""),
            "top_differentials": advice.get("top_differentials", [])[:5],
            "recommendations": advice.get("recommendations", []),
            "underperformers": advice.get("underperformers", [])[:3],
            "horizon_gameweeks": horizon,
            "current_player_ids": player_ids,
            "bank": bank,
            "free_transfers": free_transfers
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating team advice: {str(e)}")


@team_router.get("/{team_id}/summary")
async def get_team_summary(
    team_id: int,
    horizon: Optional[int] = Query(5, description="Analysis horizon in gameweeks"),
    client: FPLClient = Depends(get_fpl_client)
):
    """
    Get team summary with per-player next GW projections and enhanced breakdown.
    
    Returns per-player next GW projection, total horizon points, confidence, 
    fixture difficulty, captain/vice, bank, transfer count with breakdown.
    Enhanced with advanced metrics and zone adjustments when available.
    """
    try:
        # Get current team picks
        picks_data = client.get_team_picks(team_id)
        picks = picks_data.get("picks", [])
        
        if not picks:
            raise HTTPException(status_code=404, detail="No picks found for this team")
        
        # Get all players data for lookup
        all_players = client.get_players()
        player_lookup = {p["id"]: p for p in all_players}
        
        # Find captain and vice captain info
        captain_id = None
        vice_captain_id = None
        captain_name = None
        vice_captain_name = None
        
        for pick in picks:
            player_id = pick.get("element")
            if pick.get("is_captain") and player_id in player_lookup:
                captain_id = player_id
                player_data = player_lookup[player_id]
                captain_name = f"{player_data.get('first_name', '')} {player_data.get('second_name', '')}".strip()
            elif pick.get("is_vice_captain") and player_id in player_lookup:
                vice_captain_id = player_id
                player_data = player_lookup[player_id]
                vice_captain_name = f"{player_data.get('first_name', '')} {player_data.get('second_name', '')}".strip()
        
        # Process each player in the squad
        squad_projections = []
        
        for pick in picks:
            player_id = pick.get("element")
            if not player_id or player_id not in player_lookup:
                continue
                
            player_data = player_lookup[player_id]
            
            # Get player details for recent history
            try:
                player_details = client.get_player_details(player_id)
                recent_history = player_details.get("history", [])
            except:
                recent_history = []
            
            # Calculate next GW projection
            next_gw_projection = calculate_horizon_projection(player_id, 1, client)
            
            if "error" in next_gw_projection or not next_gw_projection.get("projections"):
                # Fallback projection if calculation fails
                next_gw_points = float(player_data.get("form", "0") or "0") * 1.2
                confidence = 0.5
                fixture_difficulty = 3.0
                projected_minutes = 60
            else:
                proj_data = next_gw_projection["projections"][0]
                next_gw_points = proj_data.get("projected_points", 0)
                confidence = proj_data.get("confidence_score", 0.5)
                fixture_difficulty = proj_data.get("fixture_difficulty", 3.0)
                projected_minutes = proj_data.get("projected_minutes", 60)
            
            # Calculate horizon projection
            horizon_projection = calculate_horizon_projection(player_id, horizon, client)
            total_horizon_points = horizon_projection.get("total_projected_points", 0)
            
            # Estimate expected minutes for breakdown
            expected_minutes = _simple_minutes_projection(player_data, recent_history)
            
            # Generate heuristic breakdown first
            breakdown = _simple_event_breakdown_for_projection(next_gw_points, player_data, expected_minutes)
            
            # ENHANCED: Apply advanced metrics and zone adjustments
            enhanced_breakdown = enhance_breakdown_with_advanced_metrics(
                breakdown, player_data, next_gw_points, opponent_team_id, player_id
            )
            
            # Player summary
            position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
            player_summary = {
                "player_id": player_id,
                "name": f"{player_data.get('first_name', '')} {player_data.get('second_name', '')}".strip(),
                "position": position_map.get(player_data.get("element_type"), "Unknown"),
                "team_id": player_data.get("team", 0),
                "cost": player_data.get("now_cost", 0) / 10.0,
                "is_captain": pick.get("is_captain", False),
                "is_vice_captain": pick.get("is_vice_captain", False),
                "is_bench": pick.get("position", 1) > 11,
                "squad_position": pick.get("position", 1),
                "next_gw_points": round(next_gw_points, 2),
                "total_horizon_points": round(total_horizon_points, 2),
                "confidence": round(confidence, 2),
                "fixture_difficulty": round(fixture_difficulty, 1),
                "expected_minutes": expected_minutes,
                "breakdown": enhanced_breakdown  # Using enhanced breakdown
            }
            
            squad_projections.append(player_summary)
        
        # Sort by next GW points descending
        squad_projections.sort(key=lambda x: x["next_gw_points"], reverse=True)
        
        # Calculate team totals
        total_next_gw = sum(p["next_gw_points"] for p in squad_projections if not p["is_bench"])
        total_horizon = sum(p["total_horizon_points"] for p in squad_projections if not p["is_bench"])
        avg_confidence = sum(p["confidence"] for p in squad_projections if not p["is_bench"]) / 11
        
        return {
            "team_id": team_id,
            "horizon_gameweeks": horizon,
            "captain_name": captain_name,  # ENHANCED: Captain name resolution
            "vice_captain_name": vice_captain_name,  # ENHANCED: Vice captain name resolution
            "bank": picks_data.get("entry_history", {}).get("bank", 0) / 10.0,
            "transfers_made": picks_data.get("entry_history", {}).get("event_transfers", 0),
            "squad_projections": squad_projections,
            "team_totals": {
                "next_gw_points": round(total_next_gw, 2),
                "total_horizon_points": round(total_horizon, 2),
                "average_confidence": round(avg_confidence, 2)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating team summary: {str(e)}")


@team_router.get("/{team_id}/projections")
async def get_team_projections(
    team_id: int,
    horizon: Optional[int] = Query(5, description="Analysis horizon in gameweeks"),
    client: FPLClient = Depends(get_fpl_client)
):
    """
    Get aggregated horizon points and average projected GW points for each squad player.
    
    Returns aggregated horizon points totals for the squad.
    """
    try:
        # Get current team picks
        picks_data = client.get_team_picks(team_id)
        picks = picks_data.get("picks", [])
        
        if not picks:
            raise HTTPException(status_code=404, detail="No picks found for this team")
        
        # Get all players data for lookup
        all_players = client.get_players()
        player_lookup = {p["id"]: p for p in all_players}
        
        # Calculate projections for each player
        player_projections = []
        
        for pick in picks:
            player_id = pick.get("element")
            if not player_id or player_id not in player_lookup:
                continue
                
            player_data = player_lookup[player_id]
            
            # Calculate horizon projection
            projection = calculate_horizon_projection(player_id, horizon, client)
            
            if "error" in projection:
                # Fallback calculation
                total_points = float(player_data.get("form", "0") or "0") * horizon * 1.2
                avg_points = total_points / horizon if horizon > 0 else 0
            else:
                total_points = projection.get("total_projected_points", 0)
                avg_points = projection.get("average_projected_points", 0)
            
            position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
            player_projection = {
                "player_id": player_id,
                "name": f"{player_data.get('first_name', '')} {player_data.get('second_name', '')}".strip(),
                "position": position_map.get(player_data.get("element_type"), "Unknown"),
                "is_bench": pick.get("position", 1) > 11,
                "squad_position": pick.get("position", 1),
                "total_horizon_points": round(total_points, 2),
                "average_gw_points": round(avg_points, 2)
            }
            
            player_projections.append(player_projection)
        
        # Sort by total horizon points descending
        player_projections.sort(key=lambda x: x["total_horizon_points"], reverse=True)
        
        # Calculate team aggregates
        starting_xi = [p for p in player_projections if not p["is_bench"]]
        bench = [p for p in player_projections if p["is_bench"]]
        
        starting_xi_total = sum(p["total_horizon_points"] for p in starting_xi)
        bench_total = sum(p["total_horizon_points"] for p in bench)
        squad_total = starting_xi_total + bench_total
        
        return {
            "team_id": team_id,
            "horizon_gameweeks": horizon,
            "player_projections": player_projections,
            "aggregates": {
                "starting_xi_total": round(starting_xi_total, 2),
                "bench_total": round(bench_total, 2),
                "squad_total": round(squad_total, 2),
                "starting_xi_average": round(starting_xi_total / len(starting_xi), 2) if starting_xi else 0,
                "squad_average": round(squad_total / len(player_projections), 2) if player_projections else 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating team projections: {str(e)}")