"""FastAPI service for mobile-friendly FPL toolkit endpoints."""
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ..api.client import FPLClient
from ..ai.advisor import FPLAdvisor
from ..analysis.projections import calculate_horizon_projection, compare_player_projections
from ..analysis.decisions import analyze_transfer_scenario, find_transfer_targets
from ..analysis.fixtures import compute_fixture_difficulty


# Pydantic models for request/response
class PlayerResponse(BaseModel):
    id: int
    name: str
    team_id: int
    position: str
    cost: float
    total_points: int
    form: float
    selected_by_percent: float
    status: str


class ProjectionResponse(BaseModel):
    player_id: int
    gameweek: int
    projected_points: float
    projected_minutes: int
    confidence_score: float
    fixture_difficulty: float


class ComparisonRequest(BaseModel):
    player_ids: List[int]
    horizon_gameweeks: Optional[int] = 5


class AdvisorRequest(BaseModel):
    player_ids: List[int]
    budget: Optional[float] = 100.0
    free_transfers: Optional[int] = 1
    horizon_gameweeks: Optional[int] = 5


class TransferScenarioRequest(BaseModel):
    player_out_id: int
    player_in_id: int
    horizon_gameweeks: Optional[int] = 5


# FastAPI app
app = FastAPI(
    title="FPL Toolkit API",
    description="Mobile-friendly API for Fantasy Premier League analysis and decision support",
    version="0.1.0"
)

# Add CORS middleware for mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get FPL client
def get_fpl_client():
    client = FPLClient()
    try:
        yield client
    finally:
        client.close()


# Dependency to get FPL advisor
def get_fpl_advisor():
    advisor = FPLAdvisor()
    try:
        yield advisor
    finally:
        advisor.close()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "FPL Toolkit API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "players": "/players",
            "player_detail": "/player/{id}",
            "compare": "/compare",
            "advisor": "/advisor",
            "projections": "/projections/{id}",
            "transfer_scenario": "/transfer-scenario",
            "fixture_difficulty": "/fixtures/{team_id}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "fpl-toolkit-api"}


@app.get("/players", response_model=List[PlayerResponse])
async def get_players(
    position: Optional[str] = Query(None, description="Filter by position (GK, DEF, MID, FWD)"),
    max_cost: Optional[float] = Query(None, description="Maximum cost filter"),
    min_points: Optional[int] = Query(None, description="Minimum total points filter"),
    limit: Optional[int] = Query(50, description="Limit number of results"),
    client: FPLClient = Depends(get_fpl_client)
):
    """Get players list with optional filters."""
    try:
        players = client.get_players()
        
        # Position mapping
        position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
        
        filtered_players = []
        for player in players:
            # Apply filters
            if position and position_map.get(player.get("element_type")) != position:
                continue
            
            if max_cost and player.get("now_cost", 0) / 10.0 > max_cost:
                continue
            
            if min_points and player.get("total_points", 0) < min_points:
                continue
            
            # Format response
            player_response = PlayerResponse(
                id=player["id"],
                name=f"{player.get('first_name', '')} {player.get('second_name', '')}".strip(),
                team_id=player.get("team", 0),
                position=position_map.get(player.get("element_type"), "Unknown"),
                cost=player.get("now_cost", 0) / 10.0,
                total_points=player.get("total_points", 0),
                form=float(player.get("form", "0") or "0"),
                selected_by_percent=float(player.get("selected_by_percent", "0") or "0"),
                status=player.get("status", "a")
            )
            filtered_players.append(player_response)
        
        # Sort by total points and limit
        filtered_players.sort(key=lambda x: x.total_points, reverse=True)
        return filtered_players[:limit]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching players: {str(e)}")


@app.get("/player/{player_id}")
async def get_player_details(
    player_id: int,
    client: FPLClient = Depends(get_fpl_client)
):
    """Get detailed player information."""
    try:
        players = client.get_players()
        player_details = client.get_player_details(player_id)
        
        # Find player in main list
        player_data = None
        for player in players:
            if player["id"] == player_id:
                player_data = player
                break
        
        if not player_data:
            raise HTTPException(status_code=404, detail="Player not found")
        
        position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
        
        # Format response
        response = {
            "id": player_data["id"],
            "name": f"{player_data.get('first_name', '')} {player_data.get('second_name', '')}".strip(),
            "team_id": player_data.get("team", 0),
            "position": position_map.get(player_data.get("element_type"), "Unknown"),
            "cost": player_data.get("now_cost", 0) / 10.0,
            "total_points": player_data.get("total_points", 0),
            "form": float(player_data.get("form", "0") or "0"),
            "selected_by_percent": float(player_data.get("selected_by_percent", "0") or "0"),
            "status": player_data.get("status", "a"),
            "points_per_game": float(player_data.get("points_per_game", "0") or "0"),
            "minutes": player_data.get("minutes", 0),
            "goals_scored": player_data.get("goals_scored", 0),
            "assists": player_data.get("assists", 0),
            "clean_sheets": player_data.get("clean_sheets", 0),
            "recent_history": player_details.get("history", [])[-5:],  # Last 5 gameweeks
            "upcoming_fixtures": player_details.get("fixtures", [])[:5]  # Next 5 fixtures
        }
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching player details: {str(e)}")


@app.post("/compare")
async def compare_players(
    request: ComparisonRequest,
    client: FPLClient = Depends(get_fpl_client)
):
    """Compare multiple players over a time horizon."""
    try:
        if len(request.player_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 players required for comparison")
        
        if len(request.player_ids) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 players allowed for comparison")
        
        comparison_data = compare_player_projections(request.player_ids, request.horizon_gameweeks)
        
        return {
            "comparisons": comparison_data["comparisons"],
            "best_projection": comparison_data["best_projection"],
            "horizon_gameweeks": request.horizon_gameweeks,
            "players_compared": len(request.player_ids)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing players: {str(e)}")


@app.post("/advisor")
async def get_team_advice(
    request: AdvisorRequest,
    advisor: FPLAdvisor = Depends(get_fpl_advisor)
):
    """Get AI-powered team advice."""
    try:
        team_state = {
            "player_ids": request.player_ids,
            "budget": request.budget,
            "free_transfers": request.free_transfers,
            "horizon_gameweeks": request.horizon_gameweeks
        }
        
        advice = advisor.advise_team(team_state)
        
        return {
            "summary": advice["summary"],
            "recommendations": advice["recommendations"],
            "underperformers": advice["underperformers"][:3],  # Top 3 for mobile
            "top_differentials": advice["top_differentials"][:5],  # Top 5 for mobile
            "transfer_suggestions": advice["transfer_suggestions"][:2],  # Top 2 for mobile
            "horizon_gameweeks": request.horizon_gameweeks
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating advice: {str(e)}")


@app.get("/projections/{player_id}", response_model=ProjectionResponse)
async def get_player_projection(
    player_id: int,
    gameweek: Optional[int] = Query(None, description="Target gameweek (default: next gameweek)"),
    client: FPLClient = Depends(get_fpl_client)
):
    """Get projection for a specific player and gameweek."""
    try:
        if gameweek is None:
            next_gw = client.get_next_gameweek()
            gameweek = next_gw.get("id") if next_gw else 1
        
        projection = calculate_horizon_projection(player_id, 1, client)
        
        if "error" in projection:
            raise HTTPException(status_code=404, detail=projection["error"])
        
        if not projection["projections"]:
            raise HTTPException(status_code=404, detail="No projection data available")
        
        proj_data = projection["projections"][0]
        
        return ProjectionResponse(
            player_id=proj_data["player_id"],
            gameweek=proj_data["gameweek"],
            projected_points=proj_data["projected_points"],
            projected_minutes=proj_data["projected_minutes"],
            confidence_score=proj_data["confidence_score"],
            fixture_difficulty=proj_data["fixture_difficulty"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating projection: {str(e)}")


@app.post("/transfer-scenario")
async def analyze_transfer(
    request: TransferScenarioRequest,
    client: FPLClient = Depends(get_fpl_client)
):
    """Analyze a transfer scenario."""
    try:
        scenario = analyze_transfer_scenario(
            request.player_out_id,
            request.player_in_id,
            request.horizon_gameweeks,
            client
        )
        
        if "error" in scenario:
            raise HTTPException(status_code=400, detail=scenario["error"])
        
        return {
            "player_out_name": scenario["player_out_name"],
            "player_in_name": scenario["player_in_name"],
            "cost_change": scenario["cost_change"],
            "projected_points_gain": scenario["projected_points_gain"],
            "confidence_score": scenario["confidence_score"],
            "risk_score": scenario["risk_score"],
            "recommendation": scenario["recommendation"],
            "reasoning": scenario["reasoning"],
            "horizon_gameweeks": request.horizon_gameweeks
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing transfer: {str(e)}")


@app.get("/fixtures/{team_id}")
async def get_fixture_difficulty(
    team_id: int,
    next_n: Optional[int] = Query(5, description="Number of fixtures to analyze"),
    client: FPLClient = Depends(get_fpl_client)
):
    """Get fixture difficulty analysis for a team."""
    try:
        fixture_data = compute_fixture_difficulty(team_id, next_n, client)
        
        return {
            "team_id": team_id,
            "average_difficulty": fixture_data["average_difficulty"],
            "difficulty_trend": fixture_data["difficulty_trend"],
            "fixtures": fixture_data["fixtures"],
            "home_fixtures": fixture_data["home_fixtures"],
            "away_fixtures": fixture_data["away_fixtures"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing fixtures: {str(e)}")


@app.get("/transfer-targets/{player_id}")
async def get_transfer_targets(
    player_id: int,
    max_cost_increase: Optional[float] = Query(2.0, description="Maximum cost increase allowed"),
    limit: Optional[int] = Query(5, description="Maximum number of suggestions"),
    client: FPLClient = Depends(get_fpl_client)
):
    """Get transfer target suggestions for a player."""
    try:
        targets = find_transfer_targets(player_id, max_cost_increase, limit=limit)
        
        # Format for mobile
        formatted_targets = []
        for target in targets:
            formatted_targets.append({
                "player_in_name": target["player_in_name"],
                "cost_change": target["cost_change"],
                "projected_points_gain": target["projected_points_gain"],
                "recommendation": target["recommendation"],
                "confidence_score": target["confidence_score"],
                "risk_score": target["risk_score"]
            })
        
        return {
            "player_id": player_id,
            "transfer_targets": formatted_targets,
            "max_cost_increase": max_cost_increase
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding transfer targets: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)