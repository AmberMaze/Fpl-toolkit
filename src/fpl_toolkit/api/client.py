"""FPL API client for fetching data."""
import httpx
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class FPLClient:
    """Client for Fantasy Premier League API."""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("FPL_BASE_URL", "https://fantasy.premierleague.com/api")
        self.session = httpx.Client(timeout=30.0)
        self._cache = {}
        self._cache_ttl = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    
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
        self._cache[key] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
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
            if (fixture.get("team_h") == team_id or fixture.get("team_a") == team_id):
                # Only include future fixtures
                if fixture.get("event", 0) >= current_gw_id and not fixture.get("finished", False):
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
            "fixtures": player_details.get("fixtures", [])
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
    
    def get_team_picks(self, team_id: int, gameweek: Optional[int] = None) -> Dict[str, Any]:
        """Get user's team picks for a specific gameweek."""
        if not gameweek:
            current_gw = self.get_current_gameweek()
            gameweek = current_gw.get("id") if current_gw else 1
        
        cache_key = f"picks_{team_id}_{gameweek}"
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data
        
        response = self.session.get(f"{self.base_url}/entry/{team_id}/event/{gameweek}/picks/")
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
        
        response = self.session.get(f"{self.base_url}/leagues-classic/{league_id}/standings/?page_standings={page}")
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
        self._cache[cache_key] = {
            "data": data,
            "timestamp": datetime.now()
        }
        return data
    
    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()