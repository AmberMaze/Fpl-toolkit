"""Advanced FPL analysis functions for enhanced features."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

try:
    import numpy as np
except ImportError:
    # Create a minimal numpy substitute for basic operations
    class NumpySubstitute:
        @staticmethod
        def var(data):
            if not data:
                return 0
            mean = sum(data) / len(data)
            return sum((x - mean) ** 2 for x in data) / len(data)
        
        @staticmethod
        def mean(data):
            return sum(data) / len(data) if data else 0
            
        @staticmethod
        def std(data):
            return (NumpySubstitute.var(data)) ** 0.5
    
    np = NumpySubstitute()

from ..api.client import FPLClient
from ..db.enhanced_models import (
    CustomProjection,
    EffectiveOwnership,
    GameweekAnalysis,
    UserTeam,
    WatchlistPlayer,
)


def calculate_effective_ownership(
    client: FPLClient, gameweek: Optional[int] = None
) -> Dict[str, Any]:
    """Calculate effective ownership including captaincy effects."""
    if not gameweek:
        current_gw = client.get_current_gameweek()
        gameweek = current_gw.get("id") if current_gw else 1

    players = client.get_players()
    live_data = client.get_live_gameweek(gameweek)

    effective_ownership = {}

    for player in players:
        player_id = player["id"]
        ownership = float(player.get("selected_by_percent", "0") or "0")

        # Get captain data from live gameweek (simplified estimation)
        # In reality, this would need more complex analysis
        captain_percentage = ownership * 0.15  # Rough estimation
        vice_captain_percentage = ownership * 0.10

        # Calculate effective ownership
        # Formula: EO = ownership + (captain% * ownership) + (vice_captain% * ownership * 0.1)
        effective_ownership_value = (
            ownership
            + (captain_percentage * ownership / 100)
            + (vice_captain_percentage * ownership / 100 * 0.1)
        )

        effective_ownership[player_id] = {
            "player_name": f"{player.get('first_name', '')} {player.get('second_name', '')}".strip(),
            "regular_ownership": ownership,
            "effective_ownership": round(effective_ownership_value, 2),
            "captain_percentage": round(captain_percentage, 2),
            "vice_captain_percentage": round(vice_captain_percentage, 2),
            "ownership_diff": round(effective_ownership_value - ownership, 2),
        }

    # Sort by effective ownership
    sorted_ownership = dict(
        sorted(
            effective_ownership.items(),
            key=lambda x: x[1]["effective_ownership"],
            reverse=True,
        )
    )

    return {
        "gameweek": gameweek,
        "players": sorted_ownership,
        "top_effective_ownership": dict(list(sorted_ownership.items())[:20]),
        "highest_captain_targets": sorted(
            effective_ownership.items(),
            key=lambda x: x[1]["captain_percentage"],
            reverse=True,
        )[:10],
    }


def analyze_zonal_strengths_weaknesses(
    client: FPLClient, gameweek: Optional[int] = None
) -> Dict[str, Any]:
    """Analyze team zonal strengths and weaknesses for a gameweek."""
    if not gameweek:
        current_gw = client.get_current_gameweek()
        gameweek = current_gw.get("id") if current_gw else 1

    fixtures = client.get_fixtures(gameweek)
    teams = client.get_teams()
    players = client.get_players()

    team_lookup = {t["id"]: t for t in teams}

    zonal_analysis = {
        "gameweek": gameweek,
        "defensive_zones": {},
        "attacking_zones": {},
        "fixture_analysis": [],
        "best_defensive_assets": [],
        "best_attacking_assets": [],
        "worst_defensive_matchups": [],
        "avoid_assets": [],
    }

    # Analyze each fixture
    for fixture in fixtures:
        if fixture.get("finished", False):
            continue

        home_team_id = fixture.get("team_h")
        away_team_id = fixture.get("team_a")

        home_team = team_lookup.get(home_team_id)
        away_team = team_lookup.get(away_team_id)

        if not home_team or not away_team:
            continue

        # Team strength analysis
        home_att_strength = home_team.get("strength_attack_home", 1000)
        home_def_strength = home_team.get("strength_defence_home", 1000)
        away_att_strength = away_team.get("strength_attack_away", 1000)
        away_def_strength = away_team.get("strength_defence_away", 1000)

        # Calculate fixture difficulty from team perspective
        home_fixture_difficulty = (away_def_strength / 1000) * 5
        away_fixture_difficulty = (home_def_strength / 1000) * 5

        fixture_analysis = {
            "fixture_id": fixture.get("id"),
            "home_team": home_team["name"],
            "away_team": away_team["name"],
            "home_attack_rating": home_att_strength,
            "home_defense_rating": home_def_strength,
            "away_attack_rating": away_att_strength,
            "away_defense_rating": away_def_strength,
            "home_fixture_difficulty": round(home_fixture_difficulty, 1),
            "away_fixture_difficulty": round(away_fixture_difficulty, 1),
            "clean_sheet_probability": {
                "home": max(
                    0, min(1, (home_def_strength - away_att_strength) / 500 + 0.3)
                ),
                "away": max(
                    0, min(1, (away_def_strength - home_att_strength) / 500 + 0.2)
                ),
            },
        }

        zonal_analysis["fixture_analysis"].append(fixture_analysis)

        # Zone strength analysis
        zonal_analysis["defensive_zones"][home_team["name"]] = {
            "strength_rating": home_def_strength,
            "clean_sheet_probability": fixture_analysis["clean_sheet_probability"][
                "home"
            ],
            "opponent": away_team["name"],
            "opponent_attack_strength": away_att_strength,
        }

        zonal_analysis["attacking_zones"][home_team["name"]] = {
            "strength_rating": home_att_strength,
            "opponent_defense": away_def_strength,
            "fixture_difficulty": home_fixture_difficulty,
            "goal_probability": max(
                0, min(3, (home_att_strength - away_def_strength) / 200 + 1.5)
            ),
        }

        zonal_analysis["defensive_zones"][away_team["name"]] = {
            "strength_rating": away_def_strength,
            "clean_sheet_probability": fixture_analysis["clean_sheet_probability"][
                "away"
            ],
            "opponent": home_team["name"],
            "opponent_attack_strength": home_att_strength,
        }

        zonal_analysis["attacking_zones"][away_team["name"]] = {
            "strength_rating": away_att_strength,
            "opponent_defense": home_def_strength,
            "fixture_difficulty": away_fixture_difficulty,
            "goal_probability": max(
                0, min(3, (away_att_strength - home_def_strength) / 200 + 1.2)
            ),
        }

    # Find best assets based on analysis
    team_players = {}
    for player in players:
        team_id = player.get("team")
        if team_id not in team_players:
            team_players[team_id] = []
        team_players[team_id].append(player)

    # Best defensive assets (defenders + GKs from teams with good clean sheet odds)
    for team_name, zone_data in zonal_analysis["defensive_zones"].items():
        if zone_data["clean_sheet_probability"] > 0.4:  # 40%+ clean sheet chance
            team_id = next((t["id"] for t in teams if t["name"] == team_name), None)
            if team_id in team_players:
                defenders = [
                    p for p in team_players[team_id] if p.get("element_type") in [1, 2]
                ]  # GK, DEF
                for defender in defenders:
                    if (
                        float(defender.get("selected_by_percent", "0") or "0") < 30
                    ):  # Under 30% owned
                        zonal_analysis["best_defensive_assets"].append(
                            {
                                "player_name": f"{defender.get('first_name', '')} {defender.get('second_name', '')}".strip(),
                                "team": team_name,
                                "position": (
                                    "GK" if defender.get("element_type") == 1 else "DEF"
                                ),
                                "cost": defender.get("now_cost", 0) / 10.0,
                                "clean_sheet_probability": zone_data[
                                    "clean_sheet_probability"
                                ],
                                "ownership": float(
                                    defender.get("selected_by_percent", "0") or "0"
                                ),
                            }
                        )

    # Best attacking assets (mids + forwards from teams with good goal probability)
    for team_name, zone_data in zonal_analysis["attacking_zones"].items():
        if zone_data["goal_probability"] > 1.8:  # Above average goal expectation
            team_id = next((t["id"] for t in teams if t["name"] == team_name), None)
            if team_id in team_players:
                attackers = [
                    p for p in team_players[team_id] if p.get("element_type") in [3, 4]
                ]  # MID, FWD
                for attacker in attackers:
                    if float(attacker.get("form", "0") or "0") > 4.0:  # Good form
                        zonal_analysis["best_attacking_assets"].append(
                            {
                                "player_name": f"{attacker.get('first_name', '')} {attacker.get('second_name', '')}".strip(),
                                "team": team_name,
                                "position": (
                                    "MID"
                                    if attacker.get("element_type") == 3
                                    else "FWD"
                                ),
                                "cost": attacker.get("now_cost", 0) / 10.0,
                                "goal_probability": zone_data["goal_probability"],
                                "form": float(attacker.get("form", "0") or "0"),
                                "fixture_difficulty": zone_data["fixture_difficulty"],
                            }
                        )

    # Sort recommendations
    zonal_analysis["best_defensive_assets"].sort(
        key=lambda x: x["clean_sheet_probability"], reverse=True
    )
    zonal_analysis["best_attacking_assets"].sort(
        key=lambda x: x["goal_probability"], reverse=True
    )

    return zonal_analysis


def generate_custom_gameweek_projections(
    client: FPLClient,
    start_gw: int,
    end_gw: int,
    player_ids: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """Generate custom projections for a specific gameweek range."""
    players = client.get_players()

    if player_ids:
        players = [p for p in players if p["id"] in player_ids]

    projections = {}

    for player in players:
        player_id = player["id"]

        # Get player's fixtures for the range
        try:
            player_details = client.get_player_details(player_id)
            fixtures = player_details.get("fixtures", [])
            history = player_details.get("history", [])

            range_fixtures = [
                f for f in fixtures if start_gw <= f.get("event", 0) <= end_gw
            ]

            if not range_fixtures:
                continue

            # Calculate projection metrics
            form = float(player.get("form", "0") or "0")
            ppg = float(player.get("points_per_game", "0") or "0")

            # Advanced projection calculation
            projected_points = 0
            projected_goals = 0
            projected_assists = 0
            projected_clean_sheets = 0
            projected_bonus = 0

            total_difficulty = 0

            for fixture in range_fixtures:
                difficulty = fixture.get("difficulty", 3)
                is_home = fixture.get("is_home", False)

                # Base projection from form and PPG
                base_points = (form + ppg) / 2

                # Adjust for fixture difficulty
                difficulty_multiplier = (
                    6 - difficulty
                ) / 3  # 1.67 for easy, 1.0 for average, 0.33 for hard

                # Home advantage
                if is_home:
                    base_points *= 1.1

                game_projection = base_points * difficulty_multiplier
                projected_points += max(0, game_projection)
                total_difficulty += difficulty

                # Position-specific projections
                position = player.get("element_type", 1)

                if position == 4:  # Forward
                    projected_goals += max(0, (form / 10) * difficulty_multiplier)
                    projected_assists += max(0, (form / 20) * difficulty_multiplier)
                elif position == 3:  # Midfielder
                    projected_goals += max(0, (form / 15) * difficulty_multiplier)
                    projected_assists += max(0, (form / 12) * difficulty_multiplier)
                elif position == 2:  # Defender
                    projected_assists += max(0, (form / 25) * difficulty_multiplier)
                    if difficulty <= 2:  # Easy fixture
                        projected_clean_sheets += 0.6
                    elif difficulty == 3:
                        projected_clean_sheets += 0.3
                elif position == 1:  # Goalkeeper
                    if difficulty <= 2:
                        projected_clean_sheets += 0.7
                    elif difficulty == 3:
                        projected_clean_sheets += 0.4

            # Bonus points estimation
            projected_bonus = min(
                projected_points / 6, len(range_fixtures) * 2
            )  # Conservative bonus estimate

            # Calculate confidence based on form consistency
            if len(history) >= 3:
                recent_points = [h.get("total_points", 0) for h in history[-3:]]
                point_variance = np.var(recent_points) if recent_points else 0
                confidence = max(
                    0.3, min(1.0, 1 - (point_variance / 100))
                )  # Higher variance = lower confidence
            else:
                confidence = 0.5

            avg_difficulty = (
                total_difficulty / len(range_fixtures) if range_fixtures else 3
            )

            projections[player_id] = {
                "player_name": f"{player.get('first_name', '')} {player.get('second_name', '')}".strip(),
                "team_id": player.get("team"),
                "position": ["", "GK", "DEF", "MID", "FWD"][
                    player.get("element_type", 1)
                ],
                "cost": player.get("now_cost", 0) / 10.0,
                "fixtures_count": len(range_fixtures),
                "avg_difficulty": round(avg_difficulty, 1),
                "current_form": form,
                "projected_points": round(projected_points, 1),
                "projected_goals": round(projected_goals, 1),
                "projected_assists": round(projected_assists, 1),
                "projected_clean_sheets": round(projected_clean_sheets, 1),
                "projected_bonus": round(projected_bonus, 1),
                "confidence_score": round(confidence, 2),
                "value_rating": round(
                    projected_points / max(player.get("now_cost", 50) / 10.0, 4.0), 2
                ),
                "form_trend": _calculate_form_trend(history),
                "injury_risk": _assess_injury_risk(player),
                "rotation_risk": _assess_rotation_risk(player, history),
            }

        except Exception as e:
            # If we can't get player details, skip
            continue

    # Sort by projected points
    sorted_projections = dict(
        sorted(
            projections.items(), key=lambda x: x[1]["projected_points"], reverse=True
        )
    )

    return {
        "gameweek_range": f"GW{start_gw}-{end_gw}",
        "total_players": len(sorted_projections),
        "projections": sorted_projections,
        "top_projections": dict(list(sorted_projections.items())[:25]),
        "best_value": sorted(
            projections.items(), key=lambda x: x[1]["value_rating"], reverse=True
        )[:15],
        "summary": {
            "highest_projected": (
                max(projections.values(), key=lambda x: x["projected_points"])
                if projections
                else None
            ),
            "best_value": (
                max(projections.values(), key=lambda x: x["value_rating"])
                if projections
                else None
            ),
            "average_confidence": (
                round(
                    sum(p["confidence_score"] for p in projections.values())
                    / len(projections),
                    2,
                )
                if projections
                else 0
            ),
        },
    }


def predict_league_standings(
    client: FPLClient, league_id: int, target_gameweek: int
) -> Dict[str, Any]:
    """Predict league standings based on current form and fixtures."""
    try:
        # Get current league standings
        league_data = client.get_league_standings(league_id)
        current_gw = client.get_current_gameweek()
        current_gw_id = current_gw.get("id") if current_gw else 1

        if target_gameweek <= current_gw_id:
            return {"error": "Target gameweek must be in the future"}

        standings = league_data.get("standings", {}).get("results", [])

        predictions = []

        for entry in standings:
            team_id = entry.get("entry")
            current_points = entry.get("total", 0)

            # Get team's recent performance
            try:
                team_picks = client.get_team_picks(team_id)
                recent_performance = _analyze_recent_team_performance(
                    client, team_id, current_gw_id
                )

                # Project points gain from current gameweek to target
                gameweeks_to_predict = target_gameweek - current_gw_id
                avg_weekly_points = recent_performance.get("avg_points", 45)

                # Add some variance based on team quality
                projected_gain = avg_weekly_points * gameweeks_to_predict
                predicted_total = current_points + projected_gain

                predictions.append(
                    {
                        "entry": team_id,
                        "entry_name": entry.get("entry_name", ""),
                        "player_name": entry.get("player_name", ""),
                        "current_total": current_points,
                        "current_rank": entry.get("rank", 0),
                        "projected_gain": round(projected_gain, 1),
                        "predicted_total": round(predicted_total, 1),
                        "avg_weekly_points": round(avg_weekly_points, 1),
                        "form_trend": recent_performance.get("trend", "stable"),
                        "confidence": recent_performance.get("confidence", 0.5),
                    }
                )

            except Exception:
                # If we can't analyze a team, use conservative projection
                projected_gain = 45 * (
                    target_gameweek - current_gw_id
                )  # Average points
                predictions.append(
                    {
                        "entry": team_id,
                        "entry_name": entry.get("entry_name", ""),
                        "player_name": entry.get("player_name", ""),
                        "current_total": current_points,
                        "current_rank": entry.get("rank", 0),
                        "projected_gain": round(projected_gain, 1),
                        "predicted_total": round(current_points + projected_gain, 1),
                        "avg_weekly_points": 45,
                        "form_trend": "unknown",
                        "confidence": 0.3,
                    }
                )

        # Sort by predicted total
        predictions.sort(key=lambda x: x["predicted_total"], reverse=True)

        # Add predicted ranks
        for i, prediction in enumerate(predictions, 1):
            prediction["predicted_rank"] = i
            prediction["rank_change"] = prediction["current_rank"] - i

        return {
            "league_id": league_id,
            "current_gameweek": current_gw_id,
            "target_gameweek": target_gameweek,
            "predictions": predictions,
            "summary": {
                "biggest_climber": (
                    max(predictions, key=lambda x: x["rank_change"])
                    if predictions
                    else None
                ),
                "biggest_faller": (
                    min(predictions, key=lambda x: x["rank_change"])
                    if predictions
                    else None
                ),
                "predicted_winner": predictions[0] if predictions else None,
                "avg_confidence": (
                    round(
                        sum(p["confidence"] for p in predictions) / len(predictions), 2
                    )
                    if predictions
                    else 0
                ),
            },
        }

    except Exception as e:
        return {"error": f"Failed to predict league standings: {str(e)}"}


def _calculate_form_trend(history: List[Dict]) -> str:
    """Calculate form trend from recent history."""
    if len(history) < 4:
        return "insufficient_data"

    recent_points = [h.get("total_points", 0) for h in history[-4:]]
    earlier_points = (
        [h.get("total_points", 0) for h in history[-8:-4]] if len(history) >= 8 else []
    )

    if not earlier_points:
        return "insufficient_data"

    recent_avg = sum(recent_points) / len(recent_points)
    earlier_avg = sum(earlier_points) / len(earlier_points)

    diff = recent_avg - earlier_avg

    if diff > 1.5:
        return "improving"
    elif diff < -1.5:
        return "declining"
    else:
        return "stable"


def _assess_injury_risk(player: Dict) -> float:
    """Assess injury risk based on player status."""
    status = player.get("status", "a")
    chance_playing = player.get("chance_of_playing_this_round")

    if status in ["i", "s", "u"]:  # injured, suspended, unavailable
        return 1.0
    elif chance_playing is not None:
        return 1.0 - (chance_playing / 100)
    else:
        return 0.1  # Low default risk


def _assess_rotation_risk(player: Dict, history: List[Dict]) -> float:
    """Assess rotation risk based on recent minutes."""
    if len(history) < 3:
        return 0.5

    recent_minutes = [h.get("minutes", 0) for h in history[-3:]]
    avg_minutes = sum(recent_minutes) / len(recent_minutes)

    if avg_minutes >= 80:
        return 0.1  # Low rotation risk
    elif avg_minutes >= 60:
        return 0.3  # Medium risk
    elif avg_minutes >= 30:
        return 0.6  # High risk
    else:
        return 0.9  # Very high risk


def _analyze_recent_team_performance(
    client: FPLClient, team_id: int, current_gw: int
) -> Dict[str, Any]:
    """Analyze recent team performance for predictions."""
    try:
        # Get last 3 gameweeks of data
        recent_scores = []

        for gw in range(max(1, current_gw - 3), current_gw):
            try:
                picks_data = client.get_team_picks(team_id, gw)
                entry_history = picks_data.get("entry_history", {})
                points = entry_history.get("points", 0)
                recent_scores.append(points)
            except:
                continue

        if not recent_scores:
            return {"avg_points": 45, "trend": "unknown", "confidence": 0.3}

        avg_points = sum(recent_scores) / len(recent_scores)

        # Calculate trend
        if len(recent_scores) >= 2:
            if recent_scores[-1] > recent_scores[0]:
                trend = "improving"
            elif recent_scores[-1] < recent_scores[0]:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "unknown"

        # Calculate confidence based on consistency
        if len(recent_scores) >= 3:
            variance = np.var(recent_scores)
            confidence = max(0.3, min(1.0, 1 - (variance / 1000)))
        else:
            confidence = 0.5

        return {
            "avg_points": avg_points,
            "trend": trend,
            "confidence": confidence,
            "recent_scores": recent_scores,
        }

    except Exception:
        return {"avg_points": 45, "trend": "unknown", "confidence": 0.3}
