"""Enhanced FPL API client with authentication support."""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import httpx


class FPLClient:
    """Enhanced client for Fantasy Premier League API with authentication support."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.base_url = base_url or os.getenv(
            "FPL_BASE_URL", "https://fantasy.premierleague.com/api"
        )
        self.session = httpx.Client(timeout=30.0)
        self._cache = {}
        self._cache_ttl = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
        self._authenticated = False
        self._user_data = None

        # Authentication credentials
        self.email = email or os.getenv("FPL_EMAIL")
        self.password = password or os.getenv("FPL_PASSWORD")

    def authenticate(self) -> bool:
        """Authenticate with FPL using email and password."""
        if not self.email or not self.password:
            return False

        try:
            # Get login page to get CSRF token
            login_url = "https://users.premierleague.com/accounts/login/"
            response = self.session.get(login_url)

            # Extract CSRF token (simplified - in production you'd parse the HTML properly)
            csrf_token = None
            for line in response.text.split("\n"):
                if "csrfmiddlewaretoken" in line and "value=" in line:
                    csrf_token = line.split('value="')[1].split('"')[0]
                    break

            if not csrf_token:
                return False

            # Login data
            login_data = {
                "csrfmiddlewaretoken": csrf_token,
                "login": self.email,
                "password": self.password,
                "app": "plfpl-web",
                "redirect_uri": "https://fantasy.premierleague.com/a/login",
            }

            # Headers
            headers = {
                "Referer": login_url,
                "Content-Type": "application/x-www-form-urlencoded",
            }

            # Perform login
            login_response = self.session.post(
                login_url, data=login_data, headers=headers
            )

            # Check if login was successful by trying to access authenticated endpoint
            me_response = self.session.get(f"{self.base_url}/me/")

            if me_response.status_code == 200:
                self._authenticated = True
                self._user_data = me_response.json()
                return True

            return False

        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return False

    def is_authenticated(self) -> bool:
        """Check if client is authenticated."""
        return self._authenticated

    def get_my_team(self, team_id: int | None = None) -> dict[str, Any] | None:
        """Get authenticated user's team data (requires authentication)."""
        if not self.is_authenticated():
            return None

        if not team_id and self._user_data:
            team_id = self._user_data.get("entry")

        if not team_id:
            return None

        try:
            response = self.session.get(f"{self.base_url}/my-team/{team_id}/")
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def get_my_transfers(self, team_id: int | None = None) -> list[dict[str, Any]]:
        """Get authenticated user's transfer history (requires authentication)."""
        if not self.is_authenticated():
            return []

        if not team_id and self._user_data:
            team_id = self._user_data.get("entry")

        if not team_id:
            return []

        try:
            response = self.session.get(f"{self.base_url}/entry/{team_id}/transfers/")
            response.raise_for_status()
            return response.json()
        except Exception:
            return []

    def get_my_leagues(self, team_id: int | None = None) -> list[dict[str, Any]]:
        """Get authenticated user's leagues (requires authentication)."""
        if not self.is_authenticated():
            return []

        if not team_id and self._user_data:
            team_id = self._user_data.get("entry")

        if not team_id:
            return []

        user_data = self.get_user_team(team_id)
        if user_data:
            classic_leagues = user_data.get("leagues", {}).get("classic", [])
            h2h_leagues = user_data.get("leagues", {}).get("h2h", [])
            return classic_leagues + h2h_leagues

        return []

    def get_effective_ownership(self, gameweek: int | None = None) -> dict[str, Any]:
        """Calculate effective ownership data for players."""
        if not gameweek:
            current_gw = self.get_current_gameweek()
            gameweek = current_gw.get("id") if current_gw else 1

        players = self.get_players()
        ownership_data = {}

        for player in players:
            ownership = float(player.get("selected_by_percent", "0") or "0")
            # Effective ownership considers captaincy
            # This is a simplified calculation - real effective ownership is more complex
            effective_ownership = ownership * 1.1  # Rough approximation

            ownership_data[player["id"]] = {
                "regular_ownership": ownership,
                "effective_ownership": effective_ownership,
                "captain_percentage": ownership * 0.1,  # Simplified estimation
            }

        return ownership_data

    def get_advanced_player_metrics(self, player_id: int) -> dict[str, Any]:
        """Get advanced metrics for a player."""
        player_details = self.get_player_details(player_id)
        history = player_details.get("history", [])

        if not history:
            return {}

        # Calculate advanced metrics
        total_minutes = sum(h.get("minutes", 0) for h in history)
        total_points = sum(h.get("total_points", 0) for h in history)
        total_bonus = sum(h.get("bonus", 0) for h in history)
        total_bps = sum(h.get("bps", 0) for h in history)

        games_played = len([h for h in history if h.get("minutes", 0) > 0])

        metrics = {
            "games_played": games_played,
            "minutes_per_game": total_minutes / max(games_played, 1),
            "points_per_90": (
                (total_points / max(total_minutes, 1)) * 90 if total_minutes > 0 else 0
            ),
            "bonus_frequency": total_bonus / max(games_played, 1),
            "bps_per_game": total_bps / max(games_played, 1),
            "consistency_score": self._calculate_consistency_score(history),
            "form_trend": self._calculate_form_trend(history),
        }

        return metrics

    def _calculate_consistency_score(self, history: list[dict]) -> float:
        """Calculate player consistency score based on point variance."""
        if len(history) < 3:
            return 0.0

        points = [h.get("total_points", 0) for h in history[-10:]]  # Last 10 games
        if not points:
            return 0.0

        mean_points = sum(points) / len(points)
        variance = sum((p - mean_points) ** 2 for p in points) / len(points)

        # Higher consistency = lower variance relative to mean
        if mean_points > 0:
            consistency = max(0, 1 - (variance / (mean_points**2)))
        else:
            consistency = 0

        return min(1.0, consistency)

    def _calculate_form_trend(self, history: list[dict]) -> str:
        """Calculate form trend (improving/declining/stable)."""
        if len(history) < 6:
            return "insufficient_data"

        recent_points = [h.get("total_points", 0) for h in history[-3:]]
        earlier_points = [h.get("total_points", 0) for h in history[-6:-3]]

        recent_avg = sum(recent_points) / len(recent_points)
        earlier_avg = sum(earlier_points) / len(earlier_points)

        diff = recent_avg - earlier_avg

        if diff > 1:
            return "improving"
        elif diff < -1:
            return "declining"
        else:
            return "stable"

    def get_gameweek_projections(self, start_gw: int, end_gw: int) -> dict[str, Any]:
        """Get player projections for a custom gameweek range."""
        players = self.get_players()
        projections = {}

        for player in players:
            # Get player fixtures for the range
            fixtures = self.get_player_details(player["id"]).get("fixtures", [])

            range_fixtures = [
                f for f in fixtures if start_gw <= f.get("event", 0) <= end_gw
            ]

            if not range_fixtures:
                continue

            # Calculate projected points based on form, fixtures, and historical data
            form = float(player.get("form", "0") or "0")
            projected_points = 0

            for fixture in range_fixtures:
                difficulty = fixture.get("difficulty", 3)
                # Simple projection based on form and difficulty
                game_projection = form * (5 - difficulty) / 3
                projected_points += max(0, game_projection)

            projections[player["id"]] = {
                "player_name": f"{player.get('first_name', '')} {player.get('second_name', '')}".strip(),
                "projected_points": round(projected_points, 1),
                "fixtures_count": len(range_fixtures),
                "avg_difficulty": sum(f.get("difficulty", 3) for f in range_fixtures)
                / len(range_fixtures),
                "current_form": form,
            }

        return projections

    def get_zonal_analysis(self, gameweek: int | None = None) -> dict[str, Any]:
        """Get zonal strength and weakness analysis."""
        if not gameweek:
            current_gw = self.get_current_gameweek()
            gameweek = current_gw.get("id") if current_gw else 1

        # Get fixtures for the gameweek
        fixtures = self.get_fixtures(gameweek)
        teams = self.get_teams()
        team_lookup = {t["id"]: t for t in teams}

        zone_analysis = {
            "defensive_strength": {},
            "attacking_threat": {},
            "fixture_difficulty": {},
            "recommended_assets": {"attack": [], "defense": [], "avoid": []},
        }

        for fixture in fixtures:
            if fixture.get("finished", False):
                continue

            home_team = team_lookup.get(fixture.get("team_h"))
            away_team = team_lookup.get(fixture.get("team_a"))

            if home_team and away_team:
                # Simplified zonal analysis based on strength ratings
                home_strength = home_team.get("strength_overall_home", 1000)
                away_strength = away_team.get("strength_overall_away", 1000)

                zone_analysis["defensive_strength"][home_team["name"]] = home_team.get(
                    "strength_defence_home", 1000
                )
                zone_analysis["defensive_strength"][away_team["name"]] = away_team.get(
                    "strength_defence_away", 1000
                )

                zone_analysis["attacking_threat"][home_team["name"]] = home_team.get(
                    "strength_attack_home", 1000
                )
                zone_analysis["attacking_threat"][away_team["name"]] = away_team.get(
                    "strength_attack_away", 1000
                )

    def get_team_picks(
        self, team_id: int, gameweek: int | None = None
    ) -> dict[str, Any]:
        """Get user's team picks for a specific gameweek."""
        if not gameweek:
            current_gw = self.get_current_gameweek()
            gameweek = current_gw.get("id") if current_gw else 1

        cache_key = f"picks_{team_id}_{gameweek}"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        response = self.session.get(
            f"{self.base_url}/entry/{team_id}/event/{gameweek}/picks/"
        )
        response.raise_for_status()
        data = response.json()

        self._set_cache(cache_key, data)
        return data

    def get_team_transfers(self, team_id: int) -> list[dict[str, Any]]:
        """Get user's transfer history."""
        cache_key = f"transfers_{team_id}"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        response = self.session.get(f"{self.base_url}/entry/{team_id}/transfers/")
        response.raise_for_status()
        data = response.json()

        self._set_cache(cache_key, data)
        return data

    def get_league_standings(self, league_id: int, page: int = 1) -> dict[str, Any]:
        """Get league standings."""
        cache_key = f"league_{league_id}_{page}"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        response = self.session.get(
            f"{self.base_url}/leagues-classic/{league_id}/standings/?page_standings={page}"
        )
        response.raise_for_status()
        data = response.json()

        self._set_cache(cache_key, data)
        return data

    def get_dream_team(self, gameweek: int | None = None) -> dict[str, Any]:
        """Get dream team for a specific gameweek."""
        if not gameweek:
            current_gw = self.get_current_gameweek()
            gameweek = current_gw.get("id") if current_gw else 1

        cache_key = f"dream_team_{gameweek}"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        response = self.session.get(f"{self.base_url}/dream-team/{gameweek}/")
        response.raise_for_status()
        data = response.json()

        self._set_cache(cache_key, data)
        return data

    def get_live_gameweek(self, gameweek: int | None = None) -> dict[str, Any]:
        """Get live gameweek data with player scores."""
        if not gameweek:
            current_gw = self.get_current_gameweek()
            gameweek = current_gw.get("id") if current_gw else 1

        cache_key = f"live_{gameweek}"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        response = self.session.get(f"{self.base_url}/event/{gameweek}/live/")
        response.raise_for_status()
        data = response.json()

        # Shorter cache for live data
        self._cache[cache_key] = {"data": data, "timestamp": datetime.now()}
        return data

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self._cache:
            return False

        cache_entry = self._cache[key]
        cache_time = cache_entry.get("timestamp", datetime.min)
        return datetime.now() - cache_time < timedelta(seconds=self._cache_ttl)

    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached data if valid."""
        if self._is_cache_valid(key):
            return self._cache[key]["data"]
        return None

    def _set_cache(self, key: str, data: Any) -> None:
        """Set cache entry with timestamp."""
        self._cache[key] = {"data": data, "timestamp": datetime.now()}

    def get_bootstrap_static(self) -> Dict[str, Any]:
        """Get bootstrap static data (players, teams, gameweeks)."""
        cache_key = "bootstrap_static"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        response = self.session.get(f"{self.base_url}/bootstrap-static/")
        response.raise_for_status()
        data = response.json()

        self._set_cache(cache_key, data)
        return data

    def get_players(self) -> List[Dict[str, Any]]:
        """Get all players data."""
        bootstrap = self.get_bootstrap_static()
        return bootstrap.get("elements", [])

    def get_teams(self) -> List[Dict[str, Any]]:
        """Get all teams data."""
        bootstrap = self.get_bootstrap_static()
        return bootstrap.get("teams", [])

    def get_gameweeks(self) -> List[Dict[str, Any]]:
        """Get all gameweeks data."""
        bootstrap = self.get_bootstrap_static()
        return bootstrap.get("events", [])

    def get_current_gameweek(self) -> Optional[Dict[str, Any]]:
        """Get current gameweek information."""
        gameweeks = self.get_gameweeks()
        for gw in gameweeks:
            if gw.get("is_current", False):
                return gw
        return None

    def get_next_gameweek(self) -> Optional[Dict[str, Any]]:
        """Get next gameweek information."""
        gameweeks = self.get_gameweeks()
        for gw in gameweeks:
            if gw.get("is_next", False):
                return gw
        return None

    def get_player_details(self, player_id: int) -> Dict[str, Any]:
        """Get detailed player information."""
        cache_key = f"player_{player_id}"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        response = self.session.get(f"{self.base_url}/element-summary/{player_id}/")
        response.raise_for_status()
        data = response.json()

        self._set_cache(cache_key, data)
        return data

    def get_fixtures(self, gameweek: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get fixtures data."""
        cache_key = f"fixtures_{gameweek}" if gameweek else "fixtures_all"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        url = f"{self.base_url}/fixtures/"
        if gameweek:
            url += f"?event={gameweek}"

        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()

        self._set_cache(cache_key, data)
        return data

    def get_team_fixtures(self, team_id: int, next_n: int = 5) -> List[Dict[str, Any]]:
        """Get next N fixtures for a team."""
        all_fixtures = self.get_fixtures()
        team_fixtures = []

        current_gw = self.get_current_gameweek()
        current_gw_id = current_gw.get("id") if current_gw else 1

        for fixture in all_fixtures:
            if fixture.get("team_h") == team_id or fixture.get("team_a") == team_id:
                # Only include future fixtures
                if fixture.get("event", 0) >= current_gw_id and not fixture.get(
                    "finished", False
                ):
                    team_fixtures.append(fixture)
                    if len(team_fixtures) >= next_n:
                        break

        return team_fixtures

    def get_player_history(self, player_id: int) -> Dict[str, Any]:
        """Get player's gameweek history."""
        player_details = self.get_player_details(player_id)
        return {
            "history": player_details.get("history", []),
            "history_past": player_details.get("history_past", []),
            "fixtures": player_details.get("fixtures", []),
        }

    def get_user_team(self, team_id: int) -> Dict[str, Any]:
        """Get user's team information."""
        cache_key = f"entry_{team_id}"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        response = self.session.get(f"{self.base_url}/entry/{team_id}/")
        response.raise_for_status()
        data = response.json()

        self._set_cache(cache_key, data)
        return data

    def get_team_picks(
        self, team_id: int, gameweek: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get user's team picks for a specific gameweek."""
        if not gameweek:
            current_gw = self.get_current_gameweek()
            gameweek = current_gw.get("id") if current_gw else 1

        cache_key = f"picks_{team_id}_{gameweek}"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        response = self.session.get(
            f"{self.base_url}/entry/{team_id}/event/{gameweek}/picks/"
        )
        response.raise_for_status()
        data = response.json()

        self._set_cache(cache_key, data)
        return data

    def get_team_transfers(self, team_id: int) -> List[Dict[str, Any]]:
        """Get user's transfer history."""
        cache_key = f"transfers_{team_id}"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        response = self.session.get(f"{self.base_url}/entry/{team_id}/transfers/")
        response.raise_for_status()
        data = response.json()

        self._set_cache(cache_key, data)
        return data

    def get_league_standings(self, league_id: int, page: int = 1) -> Dict[str, Any]:
        """Get league standings."""
        cache_key = f"league_{league_id}_{page}"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        response = self.session.get(
            f"{self.base_url}/leagues-classic/{league_id}/standings/?page_standings={page}"
        )
        response.raise_for_status()
        data = response.json()

        self._set_cache(cache_key, data)
        return data

    def get_dream_team(self, gameweek: Optional[int] = None) -> Dict[str, Any]:
        """Get dream team for a specific gameweek."""
        if not gameweek:
            current_gw = self.get_current_gameweek()
            gameweek = current_gw.get("id") if current_gw else 1

        cache_key = f"dream_team_{gameweek}"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        response = self.session.get(f"{self.base_url}/dream-team/{gameweek}/")
        response.raise_for_status()
        data = response.json()

        self._set_cache(cache_key, data)
        return data

    def get_live_gameweek(self, gameweek: Optional[int] = None) -> Dict[str, Any]:
        """Get live gameweek data with player scores."""
        if not gameweek:
            current_gw = self.get_current_gameweek()
            gameweek = current_gw.get("id") if current_gw else 1

        cache_key = f"live_{gameweek}"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        response = self.session.get(f"{self.base_url}/event/{gameweek}/live/")
        response.raise_for_status()
        data = response.json()

        # Shorter cache for live data
        self._cache[cache_key] = {"data": data, "timestamp": datetime.now()}
        return data

    def get_entry_info(self, entry_id: int) -> Dict[str, Any]:
        """Get detailed entry information including leagues."""
        cache_key = f"entry_{entry_id}"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        response = self.session.get(f"{self.base_url}/entry/{entry_id}/")
        response.raise_for_status()
        data = response.json()

        self._set_cache(cache_key, data)
        return data

    def get_entry_leagues(self, entry_id: int) -> Dict[str, Any]:
        """Get all leagues for an entry."""
        entry_info = self.get_entry_info(entry_id)
        return {
            "classic": entry_info.get("leagues", {}).get("classic", []),
            "h2h": entry_info.get("leagues", {}).get("h2h", []),
            "cup": entry_info.get("leagues", {}).get("cup", [])
        }

    def search_player_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Search for players by name."""
        players = self.get_players()
        name_lower = name.lower()
        
        matches = []
        for player in players:
            player_name = f"{player.get('first_name', '')} {player.get('second_name', '')}".strip().lower()
            if name_lower in player_name:
                matches.append(player)
        
        return matches

    def get_player_by_id(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific player by ID."""
        players = self.get_players()
        for player in players:
            if player.get("id") == player_id:
                return player
        return None

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
