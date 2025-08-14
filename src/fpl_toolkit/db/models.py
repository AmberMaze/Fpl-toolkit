"""SQLAlchemy models for FPL data."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from .engine import Base


class Player(Base):
    """Player model for storing FPL player data."""
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    fpl_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    team_id = Column(Integer, nullable=False)
    position = Column(String(20), nullable=False)  # GK, DEF, MID, FWD
    cost = Column(Float, nullable=False)  # Cost in millions
    total_points = Column(Integer, default=0)
    selected_by_percent = Column(Float, default=0.0)
    form = Column(Float, default=0.0)
    points_per_game = Column(Float, default=0.0)
    minutes = Column(Integer, default=0)
    goals_scored = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    clean_sheets = Column(Integer, default=0)
    goals_conceded = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    bonus = Column(Integer, default=0)
    bps = Column(Integer, default=0)  # Bonus Points System
    influence = Column(Float, default=0.0)
    creativity = Column(Float, default=0.0)
    threat = Column(Float, default=0.0)
    ict_index = Column(Float, default=0.0)
    status = Column(String(20), default="a")  # a=available, i=injured, s=suspended, etc.
    news = Column(Text, default="")
    chance_of_playing_this_round = Column(Integer, nullable=True)
    chance_of_playing_next_round = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    gameweek_history = relationship("GameweekHistory", back_populates="player", cascade="all, delete-orphan")
    projections = relationship("Projection", back_populates="player", cascade="all, delete-orphan")


class GameweekHistory(Base):
    """Gameweek history for players."""
    __tablename__ = "gameweek_history"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    gameweek = Column(Integer, nullable=False)
    total_points = Column(Integer, default=0)
    minutes = Column(Integer, default=0)
    goals_scored = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    clean_sheets = Column(Integer, default=0)
    goals_conceded = Column(Integer, default=0)
    own_goals = Column(Integer, default=0)
    penalties_saved = Column(Integer, default=0)
    penalties_missed = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    bonus = Column(Integer, default=0)
    bps = Column(Integer, default=0)
    influence = Column(Float, default=0.0)
    creativity = Column(Float, default=0.0)
    threat = Column(Float, default=0.0)
    ict_index = Column(Float, default=0.0)
    value = Column(Float, default=0.0)
    transfers_balance = Column(Integer, default=0)
    selected = Column(Integer, default=0)
    transfers_in = Column(Integer, default=0)
    transfers_out = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    player = relationship("Player", back_populates="gameweek_history")


class Projection(Base):
    """Player projections for future gameweeks."""
    __tablename__ = "projections"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    gameweek = Column(Integer, nullable=False)
    projected_points = Column(Float, nullable=False)
    projected_minutes = Column(Integer, default=0)
    confidence_score = Column(Float, default=0.5)  # 0-1 confidence in prediction
    fixture_difficulty = Column(Float, default=3.0)  # 1=easy, 5=difficult
    form_factor = Column(Float, default=1.0)
    home_advantage = Column(Boolean, default=False)
    opponent_team_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    player = relationship("Player", back_populates="projections")


class DecisionScenario(Base):
    """Transfer decision scenarios and analysis."""
    __tablename__ = "decision_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_name = Column(String(200), nullable=False)
    player_out_id = Column(Integer, nullable=True)  # Player being transferred out
    player_in_id = Column(Integer, nullable=True)   # Player being transferred in
    cost_change = Column(Float, default=0.0)        # Net cost difference
    projected_points_gain = Column(Float, default=0.0)  # Expected points gain over horizon
    horizon_gameweeks = Column(Integer, default=5)   # Number of gameweeks to analyze
    confidence_score = Column(Float, default=0.5)
    risk_score = Column(Float, default=0.5)         # Higher = more risky
    reasoning = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)