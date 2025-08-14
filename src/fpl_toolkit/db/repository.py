"""Repository layer for database operations."""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from .models import Player, GameweekHistory, Projection, DecisionScenario
from .engine import get_session


class PlayerRepository:
    """Repository for Player operations."""
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()
    
    def get_by_id(self, player_id: int) -> Optional[Player]:
        """Get player by ID."""
        return self.session.query(Player).filter(Player.id == player_id).first()
    
    def get_by_fpl_id(self, fpl_id: int) -> Optional[Player]:
        """Get player by FPL ID."""
        return self.session.query(Player).filter(Player.fpl_id == fpl_id).first()
    
    def get_all(self, limit: Optional[int] = None) -> List[Player]:
        """Get all players."""
        query = self.session.query(Player)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def get_by_position(self, position: str) -> List[Player]:
        """Get players by position."""
        return self.session.query(Player).filter(Player.position == position).all()
    
    def get_by_team(self, team_id: int) -> List[Player]:
        """Get players by team."""
        return self.session.query(Player).filter(Player.team_id == team_id).all()
    
    def upsert(self, player_data: Dict[str, Any]) -> Player:
        """Insert or update player."""
        fpl_id = player_data.get("fpl_id")
        if not fpl_id:
            raise ValueError("fpl_id is required")
        
        player = self.get_by_fpl_id(fpl_id)
        if player:
            # Update existing player
            for key, value in player_data.items():
                if hasattr(player, key):
                    setattr(player, key, value)
        else:
            # Create new player
            player = Player(**player_data)
            self.session.add(player)
        
        self.session.commit()
        self.session.refresh(player)
        return player
    
    def search(self, name_query: str, limit: int = 10) -> List[Player]:
        """Search players by name."""
        return (
            self.session.query(Player)
            .filter(Player.name.ilike(f"%{name_query}%"))
            .limit(limit)
            .all()
        )


class GameweekHistoryRepository:
    """Repository for GameweekHistory operations."""
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()
    
    def store_history(self, player_id: int, gameweek: int, history_data: Dict[str, Any]) -> GameweekHistory:
        """Store gameweek history for a player."""
        # Check if record already exists
        existing = (
            self.session.query(GameweekHistory)
            .filter(
                and_(
                    GameweekHistory.player_id == player_id,
                    GameweekHistory.gameweek == gameweek
                )
            )
            .first()
        )
        
        if existing:
            # Update existing record
            for key, value in history_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            history = existing
        else:
            # Create new record
            history_data.update({"player_id": player_id, "gameweek": gameweek})
            history = GameweekHistory(**history_data)
            self.session.add(history)
        
        self.session.commit()
        self.session.refresh(history)
        return history
    
    def get_player_history(self, player_id: int, limit: int = 10) -> List[GameweekHistory]:
        """Get recent history for a player."""
        return (
            self.session.query(GameweekHistory)
            .filter(GameweekHistory.player_id == player_id)
            .order_by(desc(GameweekHistory.gameweek))
            .limit(limit)
            .all()
        )
    
    def get_gameweek_data(self, gameweek: int) -> List[GameweekHistory]:
        """Get all player data for a specific gameweek."""
        return (
            self.session.query(GameweekHistory)
            .filter(GameweekHistory.gameweek == gameweek)
            .all()
        )


class ProjectionRepository:
    """Repository for Projection operations."""
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()
    
    def store_projection(self, player_id: int, gameweek: int, projection_data: Dict[str, Any]) -> Projection:
        """Store projection for a player and gameweek."""
        # Check if projection already exists
        existing = (
            self.session.query(Projection)
            .filter(
                and_(
                    Projection.player_id == player_id,
                    Projection.gameweek == gameweek
                )
            )
            .first()
        )
        
        if existing:
            # Update existing projection
            for key, value in projection_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            projection = existing
        else:
            # Create new projection
            projection_data.update({"player_id": player_id, "gameweek": gameweek})
            projection = Projection(**projection_data)
            self.session.add(projection)
        
        self.session.commit()
        self.session.refresh(projection)
        return projection
    
    def get_projections(self, player_id: int, gameweeks: Optional[List[int]] = None) -> List[Projection]:
        """Get projections for a player."""
        query = self.session.query(Projection).filter(Projection.player_id == player_id)
        
        if gameweeks:
            query = query.filter(Projection.gameweek.in_(gameweeks))
        
        return query.order_by(Projection.gameweek).all()
    
    def get_gameweek_projections(self, gameweek: int) -> List[Projection]:
        """Get all projections for a specific gameweek."""
        return (
            self.session.query(Projection)
            .filter(Projection.gameweek == gameweek)
            .order_by(desc(Projection.projected_points))
            .all()
        )


class DecisionRepository:
    """Repository for DecisionScenario operations."""
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()
    
    def create_scenario(self, scenario_data: Dict[str, Any]) -> DecisionScenario:
        """Create a new decision scenario."""
        scenario = DecisionScenario(**scenario_data)
        self.session.add(scenario)
        self.session.commit()
        self.session.refresh(scenario)
        return scenario
    
    def get_scenarios(self, limit: int = 10) -> List[DecisionScenario]:
        """Get recent decision scenarios."""
        return (
            self.session.query(DecisionScenario)
            .order_by(desc(DecisionScenario.created_at))
            .limit(limit)
            .all()
        )
    
    def get_by_id(self, scenario_id: int) -> Optional[DecisionScenario]:
        """Get scenario by ID."""
        return self.session.query(DecisionScenario).filter(DecisionScenario.id == scenario_id).first()