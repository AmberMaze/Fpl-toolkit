"""Enhanced SQLAlchemy models for advanced FPL features."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .engine import Base


class UserTeam(Base):
    """User's FPL team data."""

    __tablename__ = "user_teams"

    id = Column(Integer, primary_key=True, index=True)
    fpl_team_id = Column(Integer, unique=True, index=True, nullable=False)
    team_name = Column(String(100), nullable=False)
    manager_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)  # For authenticated users
    current_gameweek = Column(Integer, default=1)
    total_points = Column(Integer, default=0)
    overall_rank = Column(Integer, nullable=True)
    bank = Column(Float, default=0.0)  # Money in bank
    team_value = Column(Float, default=100.0)  # Total team value
    free_transfers = Column(Integer, default=1)
    transfers_made = Column(Integer, default=0)
    points_on_bench = Column(Integer, default=0)
    favourite_team = Column(Integer, nullable=True)  # FPL team ID
    started_event = Column(Integer, default=1)
    player_first_name = Column(String(100), nullable=True)
    player_last_name = Column(String(100), nullable=True)
    player_region_id = Column(Integer, nullable=True)
    player_region_name = Column(String(100), nullable=True)
    summary_overall_points = Column(Integer, default=0)
    summary_overall_rank = Column(Integer, nullable=True)
    summary_event_points = Column(Integer, default=0)
    summary_event_rank = Column(Integer, nullable=True)
    current_chips_data = Column(JSON, nullable=True)  # Store chips usage
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team_picks = relationship(
        "TeamPick", back_populates="team", cascade="all, delete-orphan"
    )
    transfers = relationship(
        "Transfer", back_populates="team", cascade="all, delete-orphan"
    )
    league_memberships = relationship(
        "LeagueMembership", back_populates="team", cascade="all, delete-orphan"
    )
    watchlist_players = relationship(
        "WatchlistPlayer", back_populates="team", cascade="all, delete-orphan"
    )


class TeamPick(Base):
    """User's team picks for specific gameweeks."""

    __tablename__ = "team_picks"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("user_teams.id"), nullable=False)
    gameweek = Column(Integer, nullable=False)
    player_fpl_id = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False)  # 1-15 (starting XI + bench)
    is_captain = Column(Boolean, default=False)
    is_vice_captain = Column(Boolean, default=False)
    multiplier = Column(Integer, default=1)  # 1=normal, 2=captain, 3=triple captain
    selling_price = Column(Float, nullable=True)
    purchase_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    team = relationship("UserTeam", back_populates="team_picks")


class Transfer(Base):
    """Transfer history for user teams."""

    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("user_teams.id"), nullable=False)
    gameweek = Column(Integer, nullable=False)
    player_in_fpl_id = Column(Integer, nullable=False)
    player_out_fpl_id = Column(Integer, nullable=False)
    cost = Column(Float, default=0.0)  # Transfer cost (hits)
    time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    team = relationship("UserTeam", back_populates="transfers")


class League(Base):
    """FPL leagues data."""

    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)
    fpl_league_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    league_type = Column(String(50), nullable=False)  # 'classic' or 'h2h'
    admin_entry = Column(Integer, nullable=True)
    closed = Column(Boolean, default=False)
    max_entries = Column(Integer, nullable=True)
    min_entries = Column(Integer, nullable=True)
    rank = Column(Integer, nullable=True)
    size = Column(Integer, default=0)
    league_code = Column(String(20), nullable=True)
    created = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    memberships = relationship(
        "LeagueMembership", back_populates="league", cascade="all, delete-orphan"
    )


class LeagueMembership(Base):
    """User team membership in leagues."""

    __tablename__ = "league_memberships"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("user_teams.id"), nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    rank = Column(Integer, nullable=True)
    last_rank = Column(Integer, nullable=True)
    rank_sort = Column(Integer, nullable=True)
    total = Column(Integer, default=0)  # Total points
    event_total = Column(Integer, default=0)  # Current gameweek points
    joined_time = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("UserTeam", back_populates="league_memberships")
    league = relationship("League", back_populates="memberships")


class WatchlistPlayer(Base):
    """Player watchlist for users."""

    __tablename__ = "watchlist_players"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("user_teams.id"), nullable=False)
    player_fpl_id = Column(Integer, nullable=False)
    list_type = Column(String(20), nullable=False)  # 'target', 'avoid', 'monitor'
    notes = Column(Text, nullable=True)
    priority = Column(Integer, default=1)  # 1=high, 2=medium, 3=low
    target_gameweek = Column(Integer, nullable=True)  # When to target this player
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("UserTeam", back_populates="watchlist_players")


class EffectiveOwnership(Base):
    """Effective ownership data by gameweek."""

    __tablename__ = "effective_ownership"

    id = Column(Integer, primary_key=True, index=True)
    gameweek = Column(Integer, nullable=False)
    player_fpl_id = Column(Integer, nullable=False)
    regular_ownership = Column(Float, default=0.0)  # Regular ownership percentage
    effective_ownership = Column(Float, default=0.0)  # Including captaincy effect
    captain_percentage = Column(Float, default=0.0)  # Percentage captained
    vice_captain_percentage = Column(Float, default=0.0)  # Percentage vice captained
    top10k_ownership = Column(Float, nullable=True)  # Ownership in top 10k
    top10k_captain = Column(Float, nullable=True)  # Captaincy in top 10k
    created_at = Column(DateTime, default=datetime.utcnow)

    # Compound index for efficient querying
    __table_args__ = ({"mysql_engine": "InnoDB"},)


class GameweekAnalysis(Base):
    """Comprehensive gameweek analysis data."""

    __tablename__ = "gameweek_analysis"

    id = Column(Integer, primary_key=True, index=True)
    gameweek = Column(Integer, nullable=False)
    analysis_type = Column(
        String(50), nullable=False
    )  # 'zonal', 'team_strength', 'fixture_difficulty'
    team_id = Column(Integer, nullable=True)  # Specific team analysis
    analysis_data = Column(JSON, nullable=False)  # Store complex analysis results
    confidence_score = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CustomProjection(Base):
    """Custom player projections for gameweek ranges."""

    __tablename__ = "custom_projections"

    id = Column(Integer, primary_key=True, index=True)
    player_fpl_id = Column(Integer, nullable=False)
    start_gameweek = Column(Integer, nullable=False)
    end_gameweek = Column(Integer, nullable=False)
    projected_points = Column(Float, nullable=False)
    projected_goals = Column(Float, default=0.0)
    projected_assists = Column(Float, default=0.0)
    projected_clean_sheets = Column(Float, default=0.0)
    projected_bonus = Column(Float, default=0.0)
    fixture_difficulty_score = Column(Float, default=3.0)
    form_factor = Column(Float, default=1.0)
    injury_risk = Column(Float, default=0.0)  # 0-1 scale
    rotation_risk = Column(Float, default=0.0)  # 0-1 scale
    confidence_score = Column(Float, default=0.5)
    methodology = Column(String(100), nullable=True)  # How projection was calculated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChipUsage(Base):
    """Track chip usage across gameweeks."""

    __tablename__ = "chip_usage"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("user_teams.id"), nullable=False)
    chip_name = Column(
        String(50), nullable=False
    )  # 'wildcard', 'free_hit', 'bench_boost', 'triple_captain'
    gameweek_played = Column(Integer, nullable=True)  # When the chip was used
    is_available = Column(Boolean, default=True)
    times_played = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("UserTeam")


class HeadToHeadRecord(Base):
    """Head-to-head records between teams."""

    __tablename__ = "h2h_records"

    id = Column(Integer, primary_key=True, index=True)
    team1_id = Column(Integer, ForeignKey("user_teams.id"), nullable=False)
    team2_id = Column(Integer, ForeignKey("user_teams.id"), nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    gameweek = Column(Integer, nullable=False)
    team1_points = Column(Integer, default=0)
    team2_points = Column(Integer, default=0)
    winner_team_id = Column(Integer, nullable=True)  # NULL for draw
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    team1 = relationship("UserTeam", foreign_keys=[team1_id])
    team2 = relationship("UserTeam", foreign_keys=[team2_id])
    league = relationship("League")


class PredictedLineup(Base):
    """Predicted lineups for teams."""

    __tablename__ = "predicted_lineups"

    id = Column(Integer, primary_key=True, index=True)
    gameweek = Column(Integer, nullable=False)
    team_fpl_id = Column(Integer, nullable=False)  # Premier League team ID
    predicted_xi = Column(JSON, nullable=False)  # Array of player IDs
    predicted_bench = Column(JSON, nullable=True)  # Array of player IDs
    formation = Column(String(10), nullable=True)  # e.g., "4-3-3"
    confidence_score = Column(Float, default=0.5)
    prediction_source = Column(String(100), nullable=True)  # How prediction was made
    injury_updates = Column(JSON, nullable=True)  # Latest injury news
    suspension_updates = Column(JSON, nullable=True)  # Latest suspension news
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
