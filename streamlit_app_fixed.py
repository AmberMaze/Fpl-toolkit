"""Enhanced FPL Toolkit with Advanced Features - Your Complete Fantasy Premier League Management System.

🌟 ENHANCED FEATURES for @AmberMaze:
- 👥 My Team Management with Football Pitch Lineup
- 🏆 League Analysis with User Leagues Detection
- 📊 Team Builder for Pre-Season with 5-Week Planning
- 🔧 Working Tab Navigation
- 💡 Better Error Handling
- 💾 Persistent Manager ID Storage
- 🔮 Comprehensive Projected Points (Goals, Assists, Clean Sheets, Bonus)
- 📱 Mobile-Optimized Interface
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

# Enhanced session state initialization for persistent data
if "manager_id" not in st.session_state:
    st.session_state.manager_id = ""
if "selected_team" not in st.session_state:
    st.session_state.selected_team = {
        "GK": [],
        "DEF": [],
        "MID": [],
        "FWD": []
    }
if "gameweek_plans" not in st.session_state:
    st.session_state.gameweek_plans = {}
if "user_preferences" not in st.session_state:
    st.session_state.user_preferences = {
        "planning_horizon": 5,
        "risk_tolerance": "medium",
        "budget_allocation": "balanced"
    }

from src.fpl_toolkit.analysis.advanced_analysis import predict_league_standings
from src.fpl_toolkit.api.client import FPLClient
from src.fpl_toolkit.ui.pitch_components import (
    create_team_stats_overview,
    render_team_lineup_pitch,
    render_team_stats_cards,
)

# Configure page with enhanced styling optimized for mobile
st.set_page_config(
    page_title="FPL Toolkit Pro - Enhanced",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/AmberMaze/Fpl-toolkit",
        "Report a bug": "https://github.com/AmberMaze/Fpl-toolkit/issues",
        "About": "FPL Toolkit Pro - Your complete Fantasy Premier League management system with mobile optimization and 5-week planning!",
    },
)

# Enhanced CSS for the new features with mobile optimization
st.markdown(
    """
<style>
    /* Enhanced modern styling with mobile-first approach */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .main .block-container {
        font-family: 'Inter', sans-serif;
        padding-top: 1rem;
        max-width: 100%;
    }
    
    /* Manager ID persistent header */
    .manager-header {
        background: linear-gradient(135deg, #38ef7d 0%, #11998e 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1.5rem;
        text-align: center;
        position: sticky;
        top: 0;
        z-index: 100;
        box-shadow: 0 8px 32px rgba(17, 153, 142, 0.4);
    }
    
    .manager-header h3 {
        margin: 0;
        font-weight: 700;
        font-size: 1.5rem;
    }
    
    .manager-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
        font-size: 1rem;
    }
    
    /* Main header with gradient */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 25%, transparent 25%, transparent 75%, rgba(255,255,255,0.1) 75%);
        background-size: 20px 20px;
        animation: move 20s linear infinite;
    }
    
    @keyframes move {
        0% { background-position: 0 0; }
        100% { background-position: 20px 20px; }
    }
    
    .main-header h1 {
        margin: 0;
        font-weight: 800;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        margin: 1rem 0 0 0;
        opacity: 0.95;
        font-size: 1.1rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* Enhanced metric cards for mobile */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.2);
        margin: 0.75rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #2c3e50;
        margin: 0.5rem 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .metric-label {
        color: #7f8c8d;
        font-size: 0.95rem;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    .metric-subtitle {
        color: #95a5a6;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        font-style: italic;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border: 1px solid #e8ecef;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.1));
    }
    
    /* Planning cards for 5-week planning */
    .plan-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
    }
    
    .plan-card h4 {
        margin: 0 0 1rem 0;
        font-weight: 700;
    }
    
    .plan-card p {
        margin: 0.5rem 0;
        opacity: 0.95;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem;
        }
        
        .main-header {
            padding: 1.5rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
        
        .manager-header {
            padding: 1rem;
        }
        
        .manager-header h3 {
            font-size: 1.2rem;
        }
        
        .metric-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .metric-value {
            font-size: 2rem;
        }
        
        .feature-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .plan-card {
            padding: 1rem;
        }
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================
# ENHANCED PROJECTION FUNCTIONS
# =====================================================

def calculate_comprehensive_projection(player: Dict[str, Any], gameweeks: int = 1) -> Dict[str, Any]:
    """Calculate comprehensive FPL projection including all scoring aspects.
    
    Includes: Minutes, Goals, Assists, Clean Sheets, Bonus Points, Saves, Cards
    """
    try:
        # Base stats per 90 minutes
        total_minutes = player.get("minutes", 0)
        minutes_per_game = (total_minutes / 38) if total_minutes > 0 else 60  # Average minutes per game
        
        # Scoring rates per 90 minutes
        goals_per_90 = (player.get("goals_scored", 0) / total_minutes * 90) if total_minutes > 0 else 0
        assists_per_90 = (player.get("assists", 0) / total_minutes * 90) if total_minutes > 0 else 0
        
        # Position-specific scoring rules
        element_type = player.get("element_type", 3)
        position_multipliers = {
            1: {"goals": 6, "assists": 3, "clean_sheet": 4, "save": 0.33, "bonus_factor": 1.0},  # GK
            2: {"goals": 6, "assists": 3, "clean_sheet": 4, "save": 0, "bonus_factor": 1.1},     # DEF  
            3: {"goals": 5, "assists": 3, "clean_sheet": 1, "save": 0, "bonus_factor": 1.0},     # MID
            4: {"goals": 4, "assists": 3, "clean_sheet": 0, "save": 0, "bonus_factor": 0.9}      # FWD
        }
        
        multiplier = position_multipliers.get(element_type, position_multipliers[3])
        
        # Project performance per gameweek
        minutes_adjustment = min(minutes_per_game / 90, 1.0)  # Cap at 90 minutes
        projected_goals = goals_per_90 * minutes_adjustment
        projected_assists = assists_per_90 * minutes_adjustment
        
        # Clean sheet probability based on position and team defensive record
        if element_type in [1, 2]:  # GK and DEF
            # Use historical clean sheet rate
            clean_sheets = player.get("clean_sheets", 0)
            cs_rate = clean_sheets / 38 if clean_sheets > 0 else 0.3  # Default 30%
            projected_clean_sheets = cs_rate
        else:
            projected_clean_sheets = 0
        
        # Bonus points estimation based on historical performance
        bonus_points = player.get("bonus", 0)
        avg_bonus_per_game = (bonus_points / 38) if bonus_points > 0 else 1.0
        projected_bonus = avg_bonus_per_game * multiplier["bonus_factor"]
        
        # Save points for goalkeepers
        if element_type == 1:
            # Estimate saves based on team defensive pressure
            estimated_saves_per_game = 3.0  # Average GK makes 3 saves per game
            projected_saves = estimated_saves_per_game * multiplier["save"]
        else:
            projected_saves = 0
        
        # Calculate points breakdown per gameweek
        points_breakdown = {
            "minutes_points": 2 if minutes_per_game >= 60 else (1 if minutes_per_game >= 1 else 0),
            "goal_points": projected_goals * multiplier["goals"],
            "assist_points": projected_assists * multiplier["assists"],
            "clean_sheet_points": projected_clean_sheets * multiplier["clean_sheet"],
            "bonus_points": projected_bonus,
            "save_points": projected_saves,
            "yellow_card_penalty": -0.3,  # Average yellow card penalty
            "red_card_penalty": -0.1       # Average red card penalty
        }
        
        # Total projected points per gameweek
        total_per_gw = sum(points_breakdown.values())
        total_for_horizon = total_per_gw * gameweeks
        
        # Confidence score based on minutes played and consistency
        games_played = total_minutes / 90 if total_minutes > 0 else 1
        consistency_score = min(games_played / 25, 1.0)  # Higher if played more games
        form_factor = min(float(player.get("form", "5.0")) / 10.0, 1.0)  # Current form
        confidence_score = (consistency_score + form_factor) / 2
        
        return {
            "player_id": player.get("id"),
            "player_name": format_player_name(player),
            "position": get_position_name(element_type),
            "projected_points_per_gw": round(total_per_gw, 2),
            "projected_points_total": round(total_for_horizon, 2),
            "points_breakdown": {k: round(v, 2) for k, v in points_breakdown.items()},
            "confidence_score": round(confidence_score, 2),
            "gameweeks_analyzed": gameweeks,
            "form": player.get("form", "5.0"),
            "value_score": round(total_per_gw / (player.get("now_cost", 50) / 10), 2)  # Points per £
        }
        
    except Exception as e:
        # Fallback projection if calculation fails
        return {
            "player_id": player.get("id"),
            "player_name": format_player_name(player),
            "position": get_position_name(player.get("element_type", 3)),
            "projected_points_per_gw": 5.0,
            "projected_points_total": 5.0 * gameweeks,
            "points_breakdown": {"error": "Calculation failed"},
            "confidence_score": 0.5,
            "gameweeks_analyzed": gameweeks,
            "form": "5.0",
            "value_score": 1.0,
            "error": str(e)
        }

def render_manager_header():
    """Render persistent manager ID header."""
    if st.session_state.manager_id:
        st.markdown(
            f"""
            <div class="manager-header">
                <h3>⚽ Manager ID: {st.session_state.manager_id}</h3>
                <p>📱 Ready for Season 2024/25 | 🎯 5-Week Planning Active | 🚀 Mobile Optimized</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="manager-header">
                <h3>⚽ Welcome to FPL Toolkit Enhanced</h3>
                <p>📱 Set your Manager ID below to unlock personalized features!</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# =====================================================
# DATA LOADING & CACHING FUNCTIONS
# =====================================================

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_players_data():
    """Load and cache players data with error handling."""
    try:
        with FPLClient() as client:
            players = client.get_players()
            return {"data": players, "status": "success", "timestamp": datetime.now()}
    except Exception as e:
        return {"data": [], "status": "error", "error": str(e)}

@st.cache_data(ttl=1800)
def load_teams_data():
    """Load and cache teams data with error handling."""
    try:
        with FPLClient() as client:
            teams = client.get_teams()
            return {"data": teams, "status": "success", "timestamp": datetime.now()}
    except Exception as e:
        return {"data": [], "status": "error", "error": str(e)}

@st.cache_data(ttl=1800)
def load_gameweeks_data():
    """Load and cache gameweeks data."""
    try:
        with FPLClient() as client:
            gameweeks = client.get_gameweeks()
            return {"data": gameweeks, "status": "success", "timestamp": datetime.now()}
    except Exception as e:
        return {"data": [], "status": "error", "error": str(e)}

# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def format_player_name(player: dict[str, Any]) -> str:
    """Format player name from FPL data."""
    first_name = player.get("first_name", "").strip()
    second_name = player.get("second_name", "").strip()
    return f"{first_name} {second_name}".strip() or "Unknown Player"

def get_position_name(element_type: int) -> str:
    """Convert element type to position name."""
    position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
    return position_map.get(element_type, "Unknown")

def create_metric_card(title: str, value: str, subtitle: str = "", icon: str = "") -> str:
    """Create enhanced HTML for a metric card."""
    icon_html = f'<div class="feature-icon">{icon}</div>' if icon else ""
    subtitle_html = (
        f'<p class="metric-subtitle">{subtitle}</p>' if subtitle else ""
    )

    return f"""
    <div class="metric-card">
        {icon_html}
        <p class="metric-label">{title}</p>
        <p class="metric-value">{value}</p>
        {subtitle_html}
    </div>
    """

def render_main_header():
    """Render the enhanced main dashboard header."""
    st.markdown(
        """
    <div class="main-header">
        <h1>⚽ FPL Toolkit Pro - Enhanced</h1>
        <p>🚀 Complete Fantasy Premier League Management System | Season 2024/25</p>
        <p style="font-size: 1rem; margin-top: 1rem; opacity: 0.9;">
            ✨ NEW: Persistent Manager ID | 🏗️ Enhanced Team Builder | 📅 5-Week Planning | 🔮 Comprehensive Projections | 📱 Mobile Optimized
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

# =====================================================
# MAIN APPLICATION SECTIONS
# =====================================================

def render_my_team_advanced():
    """Render advanced My Team section with team builder for pre-season."""
    st.header("👥 My Team - Advanced Management")

    # Team ID input
    col1, col2 = st.columns([2, 1])

    with col1:
        team_id_input = st.text_input(
            "🆔 Enter your FPL Team ID",
            placeholder="e.g., 4076192",
            help="Find your team ID in the URL when viewing your team on the FPL website",
        )

    with col2:
        st.markdown("#### 🔍 How to find your Team ID")
        st.markdown(
            """
            1. Go to [fantasy.premierleague.com](https://fantasy.premierleague.com)
            2. Navigate to 'Pick Team' or 'Points'
            3. Your Team ID is in the URL: `/entry/{TEAM_ID}/`
            """
        )

    if not team_id_input:
        st.info("👆 Enter your FPL Team ID above to view your team analysis!")
        render_team_builder_demo()
        return

    try:
        team_id = int(team_id_input)
    except ValueError:
        st.error("❌ Please enter a valid numeric Team ID")
        return

    # Load team data
    with st.spinner("🔄 Loading your team data..."):
        try:
            with FPLClient() as client:
                entry_info = client.get_entry_info(team_id)
                players_result = load_players_data()
                teams_result = load_teams_data()
                gameweeks_result = load_gameweeks_data()
        except Exception as e:
            st.error(f"❌ Could not load team data: {str(e)}")
            return

    if players_result["status"] != "success" or teams_result["status"] != "success":
        st.error("❌ Could not load FPL data")
        return

    players = players_result["data"]
    teams = teams_result["data"]
    gameweeks = gameweeks_result["data"]

    # Display team info header
    manager_name = f"{entry_info.get('player_first_name', '')} {entry_info.get('player_last_name', '')}".strip()
    team_name = entry_info.get("name", "Unknown Team")
    st.success(f"✅ Successfully loaded team: **{team_name}** (Manager: {manager_name})")

    # Try to get current picks
    picks_data = None
    team_players = []
    
    try:
        # Current gameweek
        current_gw = next((gw for gw in gameweeks if gw.get("is_current", False)), None)
        if not current_gw:
            current_gw = next((gw for gw in gameweeks if gw.get("is_next", False)), None)
        
        current_gw_id = current_gw.get("id") if current_gw else 1

        with FPLClient() as client:
            picks_result = client.get_team_picks(team_id, current_gw_id)
            if picks_result:
                picks_data = picks_result
                picks = picks_data.get("picks", [])
                
                # Get player details for the team
                player_lookup = {p["id"]: p for p in players}
                for pick in picks:
                    player_id = pick.get("element")
                    if player_id in player_lookup:
                        player = player_lookup[player_id].copy()
                        player["pick_info"] = pick
                        team_players.append(player)
                
                # Sort by position (starting XI first, then bench)
                team_players.sort(key=lambda x: x["pick_info"].get("position", 15))
    except Exception as e:
        st.warning(f"⚠️ Could not load current team picks: {str(e)}")
        st.info("💡 This might be because the season hasn't started yet or picks aren't available.")

    # Team overview metrics
    st.markdown("### 📊 Team Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if picks_data:
            team_value = sum(p.get("now_cost", 0) for p in team_players) / 10.0
            bank = picks_data.get("entry_history", {}).get("bank", 0) / 10.0
        else:
            team_value = 100.0  # Default
            bank = 0.0
        st.markdown(
            create_metric_card(
                "Team Value", f"£{team_value:.1f}m", f"Bank: £{bank:.1f}m", "💰"
            ),
            unsafe_allow_html=True
        )

    with col2:
        if picks_data:
            total_points = picks_data.get("entry_history", {}).get("total_points", 0)
            gw_points = picks_data.get("entry_history", {}).get("points", 0)
        else:
            total_points = entry_info.get("summary_overall_points", 0)
            gw_points = 0
        st.markdown(
            create_metric_card(
                "Total Points", f"{total_points:,}", f"This GW: {gw_points}", "🏆"
            ),
            unsafe_allow_html=True
        )

    with col3:
        overall_rank = entry_info.get("summary_overall_rank")
        rank_text = f"{overall_rank:,}" if overall_rank else "N/A"
        current_gw_id = current_gw.get("id") if current_gw else 1
        st.markdown(
            create_metric_card(
                "Overall Rank", rank_text, f"Gameweek {current_gw_id}", "📈"
            ),
            unsafe_allow_html=True
        )

    with col4:
        if picks_data:
            transfers_cost = picks_data.get("entry_history", {}).get("event_transfers_cost", 0)
            transfers_made = picks_data.get("entry_history", {}).get("event_transfers", 0)
        else:
            transfers_cost = 0
            transfers_made = 0
        st.markdown(
            create_metric_card(
                "Transfers", f"{transfers_made} made", f"Cost: {transfers_cost} pts", "🔄"
            ),
            unsafe_allow_html=True
        )

    # Team management tabs
    if team_players:
        render_team_with_picks(team_players, teams, picks_data)
    else:
        render_team_builder(players, teams)


def render_team_with_picks(team_players, teams, picks_data):
    """Render team analysis when picks are available."""
    tab1, tab2, tab3 = st.tabs([
        "⚽ Pitch View", 
        "📊 Team Stats", 
        "📈 Performance"
    ])
    
    with tab1:
        st.markdown("### ⚽ Football Pitch Lineup")
        
        if len(team_players) >= 11:
            # Render the football pitch lineup
            render_team_lineup_pitch(team_players, teams, "4-4-2")
            
            # Team stats overview
            team_stats = create_team_stats_overview(team_players)
            render_team_stats_cards(team_stats)
        else:
            st.warning("⚠️ Incomplete team data for pitch view")
    
    with tab2:
        render_detailed_team_stats(team_players, teams)
    
    with tab3:
        st.markdown("### 📈 Performance Analysis")
        st.info("🚧 Performance tracking will show your team's points progression, rank changes, and key metrics over time.")


def render_team_builder(players, teams):
    """Render team builder when picks aren't available."""
    st.markdown("### 🏗️ Team Builder")
    st.info("📝 Since team picks aren't available, you can build and analyze a custom team here!")
    
    # Initialize session state for team builder
    if "custom_team" not in st.session_state:
        st.session_state.custom_team = {
            "GK": [],
            "DEF": [],
            "MID": [], 
            "FWD": []
        }
    
    tab1, tab2 = st.tabs(["🔧 Build Team", "⚽ View Pitch"])
    
    with tab1:
        render_position_selector(players, teams)
    
    with tab2:
        render_custom_team_pitch()


def render_position_selector(players, teams):
    """Render position-wise player selection."""
    st.markdown("#### 🎯 Select Players by Position")
    
    # Create team lookup
    team_lookup = {t["id"]: t for t in teams}
    
    # Position requirements
    position_limits = {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}
    position_names = {"GK": "Goalkeepers", "DEF": "Defenders", "MID": "Midfielders", "FWD": "Forwards"}
    
    for pos_code, limit in position_limits.items():
        st.markdown(f"##### {position_names[pos_code]} ({len(st.session_state.custom_team[pos_code])}/{limit})")
        
        # Filter players by position
        element_type_map = {"GK": 1, "DEF": 2, "MID": 3, "FWD": 4}
        pos_players = [p for p in players if p.get("element_type") == element_type_map[pos_code]]
        
        # Sort by points
        pos_players.sort(key=lambda x: x.get("total_points", 0), reverse=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Player selection
            selected_players = st.multiselect(
                f"Choose {position_names[pos_code]}",
                options=pos_players[:50],  # Top 50 players
                format_func=lambda p: f"{format_player_name(p)} ({team_lookup.get(p.get('team'), {}).get('short_name', 'UNK')}) - £{p.get('now_cost', 0)/10.0:.1f}m - {p.get('total_points', 0)} pts",
                default=st.session_state.custom_team[pos_code],
                max_selections=limit,
                key=f"select_{pos_code}"
            )
            
            st.session_state.custom_team[pos_code] = selected_players
        
        with col2:
            if st.session_state.custom_team[pos_code]:
                total_cost = sum(p.get("now_cost", 0) for p in st.session_state.custom_team[pos_code]) / 10.0
                total_points = sum(p.get("total_points", 0) for p in st.session_state.custom_team[pos_code])
                st.metric(f"{pos_code} Cost", f"£{total_cost:.1f}m")
                st.metric(f"{pos_code} Points", f"{total_points}")
    
    # Team summary
    all_players = []
    for pos_players in st.session_state.custom_team.values():
        all_players.extend(pos_players)
    
    if len(all_players) == 15:
        total_cost = sum(p.get("now_cost", 0) for p in all_players) / 10.0
        total_points = sum(p.get("total_points", 0) for p in all_players)
        
        st.success(f"✅ Complete team! Total cost: £{total_cost:.1f}m | Total points: {total_points}")
        
        if total_cost > 100.0:
            st.error(f"❌ Team over budget by £{total_cost - 100.0:.1f}m")
    else:
        remaining = 15 - len(all_players)
        st.info(f"📝 Select {remaining} more players to complete your team")


def render_custom_team_pitch():
    """Render custom team in pitch format."""
    all_players = []
    for pos_players in st.session_state.custom_team.values():
        all_players.extend(pos_players)
    
    if len(all_players) >= 11:
        st.markdown("### ⚽ Your Custom Team")
        
        # Add position info for rendering
        for i, player in enumerate(all_players[:11]):  # Starting XI
            player["pick_info"] = {"position": i + 1}
        
        teams_result = load_teams_data()
        if teams_result["status"] == "success":
            render_team_lineup_pitch(all_players[:11], teams_result["data"], "4-4-2")
        
        # Show bench
        if len(all_players) > 11:
            st.markdown("#### 🪑 Bench")
            bench_players = all_players[11:]
            for i, player in enumerate(bench_players):
                st.write(f"{i+1}. {format_player_name(player)} - £{player.get('now_cost', 0)/10.0:.1f}m")
    else:
        st.info("📝 Select at least 11 players to view pitch lineup")


def render_team_builder_demo():
    """Render demo team builder."""
    st.markdown("---")
    st.markdown("### 🎯 Demo: Team Builder")
    
    demo_col1, demo_col2, demo_col3 = st.columns(3)
    
    with demo_col1:
        st.markdown(
            create_metric_card(
                "Team Value", "£99.7m", "£0.3m remaining", "💰"
            ),
            unsafe_allow_html=True
        )
    
    with demo_col2:
        st.markdown(
            create_metric_card(
                "Total Points", "1,247", "Rank: 234,567", "🏆"
            ),
            unsafe_allow_html=True
        )
    
    with demo_col3:
        st.markdown(
            create_metric_card(
                "Free Transfers", "1", "Next deadline: Sat 19:00", "🔄"
            ),
            unsafe_allow_html=True
        )


def render_detailed_team_stats(team_players, teams):
    """Render detailed team statistics."""
    st.markdown("### 📊 Detailed Team Statistics")
    
    # Player performance table
    if team_players:
        table_data = []
        for player in team_players:
            pick_info = player.get("pick_info", {})
            team_info = next((t for t in teams if t["id"] == player.get("team")), {})
            
            table_data.append({
                "Position": pick_info.get("position", 0),
                "Player": format_player_name(player),
                "Team": team_info.get("short_name", ""),
                "Pos": get_position_name(player.get("element_type", 1)),
                "Cost": f"£{player.get('now_cost', 0) / 10.0:.1f}m",
                "Points": player.get("total_points", 0),
                "Form": f"{float(player.get('form', '0') or '0'):.1f}",
                "PPG": f"{float(player.get('points_per_game', '0') or '0'):.1f}",
                "Captain": "🔴" if pick_info.get("is_captain") else "🔵" if pick_info.get("is_vice_captain") else "",
                "Status": "⚽" if pick_info.get("position", 15) <= 11 else "🪑"
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def render_league_analysis():
    """Render league analysis and management."""
    st.header("🏆 League Analysis & Management")
    
    # Manager ID for league access
    col1, col2 = st.columns([2, 1])
    
    with col1:
        manager_id_input = st.text_input(
            "🆔 Enter your Manager ID to see your leagues",
            placeholder="e.g., 4076192",
            help="Your manager ID is the same as your team ID"
        )
    
    with col2:
        st.markdown("#### 🎯 Your Leagues")
        st.markdown("Enter your manager ID to see all leagues you're participating in")
    
    if manager_id_input:
        try:
            manager_id = int(manager_id_input)
            render_user_leagues(manager_id)
        except ValueError:
            st.error("❌ Please enter a valid numeric Manager ID")
    else:
        render_league_demo()


def render_user_leagues(manager_id):
    """Render user's leagues."""
    with st.spinner("🔄 Loading your leagues..."):
        try:
            with FPLClient() as client:
                leagues_data = client.get_entry_leagues(manager_id)
                entry_info = client.get_entry_info(manager_id)
        except Exception as e:
            st.error(f"❌ Could not load league data: {str(e)}")
            return
    
    manager_name = f"{entry_info.get('player_first_name', '')} {entry_info.get('player_last_name', '')}".strip()
    st.success(f"✅ Loaded leagues for: **{manager_name}**")
    
    # Display leagues
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Classic Leagues")
        classic_leagues = leagues_data.get("classic", [])
        
        if classic_leagues:
            for league in classic_leagues[:10]:  # Show top 10
                with st.expander(f"🏆 {league.get('name', 'Unknown League')}"):
                    st.write(f"**League ID:** {league.get('id')}")
                    st.write(f"**Your Rank:** {league.get('entry_rank', 'N/A')}")
                    
                    if st.button(f"Analyze League {league.get('id')}", key=f"classic_{league.get('id')}"):
                        render_specific_league_analysis(league.get('id'))
        else:
            st.info("No classic leagues found")
    
    with col2:
        st.markdown("### ⚔️ Head-to-Head Leagues")
        h2h_leagues = leagues_data.get("h2h", [])
        
        if h2h_leagues:
            for league in h2h_leagues[:10]:
                with st.expander(f"⚔️ {league.get('name', 'Unknown League')}"):
                    st.write(f"**League ID:** {league.get('id')}")
                    st.write(f"**Your Rank:** {league.get('entry_rank', 'N/A')}")
                    
                    if st.button(f"Analyze League {league.get('id')}", key=f"h2h_{league.get('id')}"):
                        render_specific_league_analysis(league.get('id'))
        else:
            st.info("No head-to-head leagues found")


def render_specific_league_analysis(league_id):
    """Render analysis for a specific league."""
    with st.spinner(f"🔄 Loading league {league_id} data..."):
        try:
            with FPLClient() as client:
                league_data = client.get_league_standings(league_id)
        except Exception as e:
            st.error(f"❌ Could not load league data: {str(e)}")
            return
    
    league_info = league_data.get("league", {})
    standings = league_data.get("standings", {}).get("results", [])
    
    st.markdown(f"### 🏆 {league_info.get('name', 'League Analysis')}")
    
    if standings:
        standings_data = []
        for entry in standings[:20]:  # Top 20
            standings_data.append({
                "Rank": entry.get("rank", 0),
                "Team": entry.get("entry_name", ""),
                "Manager": entry.get("player_name", ""),
                "GW Points": entry.get("event_total", 0),
                "Total Points": f"{entry.get('total', 0):,}",
            })
        
        df = pd.DataFrame(standings_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("No standings data available")


def render_league_demo():
    """Render league demo."""
    st.info("👆 Enter your Manager ID above to see all your leagues and analyze them!")
    
    # Demo section
    st.markdown("---")
    st.markdown("### 🎯 League Features")
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h4>Your Leagues</h4>
                <p>View all classic and H2H leagues you're participating in</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with feature_col2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🔮</div>
                <h4>League Analysis</h4>
                <p>Detailed standings and performance analysis for each league</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with feature_col3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">👥</div>
                <h4>Team Comparison</h4>
                <p>Compare teams and track performance across gameweeks</p>
            </div>
            """,
            unsafe_allow_html=True
        )


def main():
    """Main application entry point with enhanced features."""
    # Render persistent manager header
    render_manager_header()
    
    # Enhanced sidebar with manager status
    st.sidebar.title("🧭 Navigation")
    
    # Manager ID section in sidebar
    if not st.session_state.manager_id:
        with st.sidebar.expander("🆔 Set Manager ID", expanded=True):
            manager_input = st.text_input(
                "Enter Manager ID:",
                placeholder="e.g., 4076192",
                key="sidebar_manager_id"
            )
            if st.button("💾 Save", key="save_manager_sidebar"):
                if manager_input.isdigit():
                    st.session_state.manager_id = manager_input
                    st.rerun()
                else:
                    st.error("Please enter a valid numeric ID")
    else:
        st.sidebar.success(f"✅ Manager: {st.session_state.manager_id}")
        if st.sidebar.button("🔄 Change Manager ID"):
            st.session_state.manager_id = ""
            st.rerun()
    
    # Navigation using selectbox instead of tabs (fixes tab navigation issue)
    selected_page = st.sidebar.selectbox(
        "Choose a section:",
        [
            "🏠 Homepage",
            "👥 My Team",
            "🏗️ Team Builder",
            "📅 5-Week Planning",
            "🏆 Leagues",
            "🔍 Players",
            "📊 Analytics",
            "🔮 Projections",
            "📋 Watchlist",
        ]
    )

    # Render selected page
    if selected_page == "🏠 Homepage":
        render_enhanced_homepage()
    elif selected_page == "👥 My Team":
        render_my_team_advanced()
    elif selected_page == "🏗️ Team Builder":
        render_enhanced_team_builder()
    elif selected_page == "📅 5-Week Planning":
        render_five_week_planning()
    elif selected_page == "🏆 Leagues":
        render_league_analysis()
    elif selected_page == "🔍 Players":
        render_players_section()
    elif selected_page == "📊 Analytics":
        render_analytics_section()
    elif selected_page == "🔮 Projections":
        render_projections_section()
    elif selected_page == "📋 Watchlist":
        render_watchlist_section()
    
    # Mobile-friendly footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📱 Mobile Ready")
    st.sidebar.markdown("✅ Touch-friendly interface")
    st.sidebar.markdown("✅ Persistent preferences")
    st.sidebar.markdown("✅ 5-week planning")
    st.sidebar.markdown("✅ Comprehensive projections")


def render_enhanced_homepage():
    """Enhanced homepage with manager ID setup and quick actions."""
    render_main_header()
    
    # Manager ID Setup Section
    st.markdown("### 👤 Manager Setup")
    
    if not st.session_state.manager_id:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            manager_id_input = st.text_input(
                "🆔 Enter your FPL Manager ID",
                value="",
                placeholder="e.g., 4076192",
                help="Your manager ID is the number in your FPL team URL",
                key="homepage_manager_id"
            )
            
            if st.button("💾 Save Manager ID", type="primary", key="save_homepage"):
                if manager_id_input.isdigit():
                    st.session_state.manager_id = manager_id_input
                    st.success(f"✅ Manager ID saved: {manager_id_input}")
                    st.rerun()
                else:
                    st.error("❌ Please enter a valid numeric Manager ID")
        
        with col2:
            st.markdown("#### 🔍 Finding Your Manager ID")
            st.markdown(
                """
                1. Go to [fantasy.premierleague.com](https://fantasy.premierleague.com)
                2. Navigate to your team
                3. Copy the number from URL: `/entry/{YOUR_ID}/`
                """
            )
    else:
        st.success(f"✅ Manager ID: {st.session_state.manager_id} is saved!")
        
        # Quick Actions for existing users
        st.markdown("### 🎯 Quick Actions")
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            st.markdown(
                """
                <div class="feature-card">
                    <h4>🏗️ Build GW1 Team</h4>
                    <p>Select your starting team for Gameweek 1 with manual selection</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        with action_col2:
            st.markdown(
                """
                <div class="feature-card">
                    <h4>📅 5-Week Planning</h4>
                    <p>Plan your strategy for the next 5 gameweeks with comprehensive projections</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        with action_col3:
            st.markdown(
                """
                <div class="feature-card">
                    <h4>🎯 Get Alternatives</h4>
                    <p>Find the best player alternatives based on value and projections</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

def render_enhanced_team_builder():
    """Enhanced team builder with comprehensive features."""
    st.title("🏗️ Enhanced Team Builder")
    
    if not st.session_state.manager_id:
        st.warning("⚠️ Please set your Manager ID on the homepage first!")
        st.info("💡 The team builder works great for pre-season planning when current picks aren't available.")
        
    # Team building tabs
    tab1, tab2, tab3 = st.tabs(["🔧 Build Team", "📊 Analysis", "🎯 Alternatives"])
    
    with tab1:
        render_enhanced_position_builder()
    
    with tab2:
        render_comprehensive_team_analysis()
    
    with tab3:
        render_smart_alternatives()

def render_enhanced_position_builder():
    """Enhanced position-based team builder with better UX."""
    st.markdown("### 🎯 Build Your Perfect Team")
    st.info("💡 Since the season hasn't started, use manual selection to plan your GW1 team!")
    
    # Load data with error handling
    players_result = load_players_data()
    teams_result = load_teams_data()
    
    if players_result["status"] != "success" or teams_result["status"] != "success":
        st.error("❌ Could not load FPL data. Please try again later.")
        return
    
    players = players_result["data"]
    teams = teams_result["data"]
    team_lookup = {t["id"]: t for t in teams}
    
    # Position requirements and current selection
    position_limits = {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}
    position_names = {"GK": "Goalkeepers", "DEF": "Defenders", "MID": "Midfielders", "FWD": "Forwards"}
    element_type_map = {"GK": 1, "DEF": 2, "MID": 3, "FWD": 4}
    
    total_cost = 0
    total_players = 0
    
    # Team summary at top
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    for pos_players in st.session_state.selected_team.values():
        total_players += len(pos_players)
        total_cost += sum(p.get("now_cost", 0) for p in pos_players) / 10
    
    with summary_col1:
        st.metric("👥 Players", f"{total_players}/15", delta=f"{15-total_players} needed" if total_players < 15 else "Complete!")
    with summary_col2:
        st.metric("💰 Cost", f"£{total_cost:.1f}m", delta=f"£{100-total_cost:.1f}m left")
    with summary_col3:
        if total_players > 0:
            avg_projection = sum(calculate_comprehensive_projection(p, 5)["projected_points_total"] for pos_players in st.session_state.selected_team.values() for p in pos_players) / total_players
            st.metric("🔮 Avg 5GW", f"{avg_projection:.1f} pts")
        else:
            st.metric("🔮 Avg 5GW", "0 pts")
    with summary_col4:
        if total_players == 15:
            if total_cost <= 100:
                st.success("✅ Valid Team!")
            else:
                st.error("❌ Over Budget!")
        else:
            st.info("📝 Building...")
    
    # Position-by-position selection
    for pos_code, limit in position_limits.items():
        with st.expander(f"🎯 {position_names[pos_code]} ({len(st.session_state.selected_team[pos_code])}/{limit})", expanded=True):
            
            # Filter players by position
            pos_players = [p for p in players if p.get("element_type") == element_type_map[pos_code]]
            
            # Sort by total points
            pos_players.sort(key=lambda x: x.get("total_points", 0), reverse=True)
            
            # Current selection display
            if st.session_state.selected_team[pos_code]:
                st.markdown("##### 👥 Currently Selected:")
                for player in st.session_state.selected_team[pos_code]:
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        st.write(f"⚽ {format_player_name(player)}")
                    with col2:
                        st.write(f"£{player.get('now_cost', 0)/10:.1f}m")
                    with col3:
                        proj = calculate_comprehensive_projection(player, 5)
                        st.write(f"🔮 {proj['projected_points_total']:.1f}")
                    with col4:
                        if st.button("🗑️", key=f"remove_{player['id']}", help="Remove player"):
                            st.session_state.selected_team[pos_code].remove(player)
                            st.rerun()
            
            # Add new players
            if len(st.session_state.selected_team[pos_code]) < limit:
                st.markdown("##### ➕ Available Players (Top Options):")
                
                for player in pos_players[:15]:  # Top 15 players
                    if player not in st.session_state.selected_team[pos_code]:
                        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                        
                        with col1:
                            team_name = team_lookup.get(player.get("team"), {}).get("short_name", "UNK")
                            st.write(f"⚽ {format_player_name(player)} ({team_name})")
                        with col2:
                            st.write(f"£{player.get('now_cost', 0)/10:.1f}m")
                        with col3:
                            st.write(f"{player.get('total_points', 0)} pts")
                        with col4:
                            proj = calculate_comprehensive_projection(player, 5)
                            st.write(f"🔮 {proj['projected_points_total']:.1f}")
                        with col5:
                            if st.button("➕", key=f"add_{player['id']}", help="Add player"):
                                if len(st.session_state.selected_team[pos_code]) < limit:
                                    st.session_state.selected_team[pos_code].append(player)
                                    st.rerun()

def render_comprehensive_team_analysis():
    """Render comprehensive team analysis with 5-week projections."""
    st.markdown("### 📊 Comprehensive Team Analysis")
    
    all_players = []
    for pos_players in st.session_state.selected_team.values():
        all_players.extend(pos_players)
    
    if len(all_players) < 11:
        st.warning("⚠️ Select at least 11 players to see detailed analysis")
        return
    
    # 5-Gameweek projections with comprehensive scoring
    st.markdown("#### 🔮 5-Gameweek Comprehensive Projections")
    st.info("📊 Projections include: Minutes, Goals, Assists, Clean Sheets, Bonus Points, Saves, and Card Penalties")
    
    projections = []
    for player in all_players:
        proj = calculate_comprehensive_projection(player, gameweeks=5)
        projections.append(proj)
    
    # Create enhanced projections dataframe
    proj_df = pd.DataFrame([
        {
            "Player": proj["player_name"],
            "Pos": proj["position"],
            "Per GW": proj["projected_points_per_gw"],
            "5 GW Total": proj["projected_points_total"],
            "Value Score": proj["value_score"],
            "Confidence": f"{proj['confidence_score']*100:.0f}%",
            "Form": proj["form"]
        }
        for proj in projections
    ])
    
    st.dataframe(proj_df, use_container_width=True)
    
    # Enhanced team metrics
    st.markdown("#### 📈 Team Performance Metrics")
    
    total_projected = sum(p["projected_points_total"] for p in projections)
    avg_per_gw = total_projected / 5
    avg_confidence = sum(p["confidence_score"] for p in projections) / len(projections)
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("📊 5-Week Total", f"{total_projected:.1f} pts")
    with metric_col2:
        st.metric("📅 Avg per GW", f"{avg_per_gw:.1f} pts")
    with metric_col3:
        st.metric("🎯 Avg Confidence", f"{avg_confidence*100:.0f}%")
    with metric_col4:
        top_10k_avg = 65 * 5  # Estimate
        performance_vs_avg = ((avg_per_gw - 65) / 65) * 100
        st.metric("📈 vs Top 10k", f"{performance_vs_avg:+.1f}%")
    
    # Detailed breakdown for top performers
    st.markdown("#### 🔍 Top Performers Breakdown")
    
    # Sort by projected points
    top_performers = sorted(projections, key=lambda x: x["projected_points_total"], reverse=True)
    
    for proj in top_performers[:5]:  # Show top 5 players
        with st.expander(f"📊 {proj['player_name']} - {proj['projected_points_per_gw']:.1f} pts/GW (Total: {proj['projected_points_total']:.1f})"):
            if "error" not in proj["points_breakdown"]:
                breakdown = proj["points_breakdown"]
                
                breakdown_col1, breakdown_col2, breakdown_col3 = st.columns(3)
                
                with breakdown_col1:
                    st.write(f"⏱️ **Minutes:** {breakdown['minutes_points']:.1f} pts")
                    st.write(f"⚽ **Goals:** {breakdown['goal_points']:.1f} pts")
                    st.write(f"🎯 **Assists:** {breakdown['assist_points']:.1f} pts")
                with breakdown_col2:
                    st.write(f"🛡️ **Clean Sheets:** {breakdown['clean_sheet_points']:.1f} pts")
                    st.write(f"⭐ **Bonus:** {breakdown['bonus_points']:.1f} pts")
                    st.write(f"🥅 **Saves:** {breakdown['save_points']:.1f} pts")
                with breakdown_col3:
                    st.write(f"🟨 **Yellow Cards:** {breakdown['yellow_card_penalty']:.1f} pts")
                    st.write(f"🟥 **Red Cards:** {breakdown['red_card_penalty']:.1f} pts")
                    st.write(f"💎 **Value Score:** {proj['value_score']:.2f}")

def render_smart_alternatives():
    """Render smart alternatives with enhanced recommendations."""
    st.markdown("### 🎯 Smart Player Alternatives & Recommendations")
    
    all_players = []
    for pos_players in st.session_state.selected_team.values():
        all_players.extend(pos_players)
    
    if not all_players:
        st.info("📝 Select some players first to see smart alternatives and recommendations")
        return
    
    players_result = load_players_data()
    if players_result["status"] != "success":
        st.error("❌ Could not load player data for alternatives")
        return
    
    all_available_players = players_result["data"]
    
    st.markdown("#### 🔄 Position-Based Alternatives")
    
    # Find alternatives for each position
    for pos_code, pos_players in st.session_state.selected_team.items():
        if pos_players:
            st.markdown(f"##### 🎯 {pos_code} Alternatives")
            
            element_type_map = {"GK": 1, "DEF": 2, "MID": 3, "FWD": 4}
            element_type = element_type_map[pos_code]
            
            # Find similar players not in team
            alternatives = [
                p for p in all_available_players 
                if p.get("element_type") == element_type and p not in pos_players
            ]
            
            # Calculate value scores and sort
            alt_with_scores = []
            for alt in alternatives:
                proj = calculate_comprehensive_projection(alt, gameweeks=5)
                alt_with_scores.append({
                    "player": alt,
                    "projection": proj,
                    "value_score": proj["value_score"]
                })
            
            # Sort by value score
            alt_with_scores.sort(key=lambda x: x["value_score"], reverse=True)
            
            for alt_data in alt_with_scores[:5]:  # Top 5 alternatives
                alt = alt_data["player"]
                proj = alt_data["projection"]
                
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"⚽ {format_player_name(alt)}")
                with col2:
                    st.write(f"£{alt.get('now_cost', 0)/10:.1f}m")
                with col3:
                    st.write(f"💎 {proj['value_score']:.2f}")
                with col4:
                    st.write(f"🔮 {proj['projected_points_total']:.1f}")
                with col5:
                    st.write(f"📊 {proj['confidence_score']*100:.0f}%")

def render_five_week_planning():
    """Render enhanced 5-gameweek planning interface."""
    st.title("📅 Strategic 5-Gameweek Planning")
    
    if not st.session_state.manager_id:
        st.warning("⚠️ Please set your Manager ID on the homepage first!")
        return
    
    st.markdown("### 🎯 Comprehensive Planning for Next 5 Gameweeks")
    st.info("🚀 Plan your team strategy with fixtures, transfers, and projected points for optimal performance!")
    
    # Planning overview cards
    plan_col1, plan_col2 = st.columns(2)
    
    with plan_col1:
        st.markdown(
            """
            <div class="plan-card">
                <h4>📊 Strategic Focus</h4>
                <p>📈 Target high-value fixtures</p>
                <p>🔄 Plan 2-3 strategic transfers</p>
                <p>🎯 Aim for 400+ points over 5 GWs</p>
                <p>💎 Find differential opportunities</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with plan_col2:
        st.markdown(
            """
            <div class="plan-card">
                <h4>⚽ Gameweek Strategy</h4>
                <p>🏠 GW1: Solid foundation picks</p>
                <p>🔥 GW2-3: Form-based selections</p>
                <p>💡 GW4-5: Fixture rotation</p>
                <p>📊 Monitor price movements</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Gameweek-by-gameweek breakdown
    st.markdown("### 📅 Detailed Gameweek Breakdown")
    
    for gw in range(1, 6):
        with st.expander(f"🏁 Gameweek {gw} Strategy & Analysis", expanded=(gw == 1)):
            gw_col1, gw_col2, gw_col3 = st.columns(3)
            
            with gw_col1:
                st.markdown(f"#### 🎯 GW{gw} Focus Areas")
                if gw == 1:
                    st.write("🏗️ **Foundation:** Strong, reliable players")
                    st.write("⚽ **Strategy:** Proven point scorers")
                    st.write("💰 **Budget:** Conservative approach")
                elif gw <= 3:
                    st.write("🔥 **Form:** Target in-form players")
                    st.write("📈 **Momentum:** Monitor price rises")
                    st.write("🔄 **Transfers:** 1-2 strategic moves")
                else:
                    st.write("🎲 **Rotation:** Fixture-based picks")
                    st.write("💎 **Differentials:** Find unique options")
                    st.write("📊 **Data:** Advanced metrics focus")
            
            with gw_col2:
                st.markdown(f"#### 💰 Transfer Strategy")
                st.write(f"💵 **Free Transfers:** 1")
                st.write(f"💸 **Hit Cost:** -4 pts each extra")
                st.write(f"🎯 **Recommended:** 1-2 total")
                if gw > 2:
                    st.write(f"🔄 **Bank Transfers:** Consider saving")
            
            with gw_col3:
                st.markdown(f"#### 📊 Points Targets")
                base_points = 70 - (gw * 2)  # Decreasing as difficulty increases
                st.write(f"🎯 **Target:** {base_points}+ points")
                st.write(f"📈 **Top 10k Avg:** ~{base_points - 5}")
                st.write(f"🏆 **Elite Target:** {base_points + 10}+")
                st.write(f"📊 **Confidence:** {max(90 - gw*5, 70)}%")
    
    # Team analysis if user has selected players
    all_players = []
    for pos_players in st.session_state.selected_team.values():
        all_players.extend(pos_players)
    
    if len(all_players) >= 11:
        st.markdown("### 📊 Your Team's 5-Week Projection")
        
        total_projection = 0
        for player in all_players:
            proj = calculate_comprehensive_projection(player, gameweeks=5)
            total_projection += proj["projected_points_total"]
        
        avg_per_gw = total_projection / 5
        
        projection_col1, projection_col2, projection_col3 = st.columns(3)
        
        with projection_col1:
            st.metric("🔮 Total 5-Week Projection", f"{total_projection:.1f} pts")
        with projection_col2:
            st.metric("📅 Average per Gameweek", f"{avg_per_gw:.1f} pts")
        with projection_col3:
            target_total = 350  # Conservative target
            vs_target = ((total_projection - target_total) / target_total) * 100
            st.metric("🎯 vs Target (350 pts)", f"{vs_target:+.1f}%")


def render_dashboard():
    """Render the main dashboard."""
    st.subheader("🎯 Quick Access")

    quick_col1, quick_col2, quick_col3 = st.columns(3)

    with quick_col1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">👥</div>
                <h4>My Team Manager</h4>
                <p>View your lineup in football pitch format, analyze performance, and plan transfers</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with quick_col2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🏆</div>
                <h4>League Analysis</h4>
                <p>Analyze league standings and see all your leagues in one place</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with quick_col3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h4>Team Builder</h4>
                <p>Build custom teams and analyze formations when picks aren't available</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Data overview
    st.markdown("---")
    st.subheader("📊 FPL Data Overview")

    players_result = load_players_data()
    teams_result = load_teams_data()

    if players_result["status"] == "success" and teams_result["status"] == "success":
        players = players_result["data"]
        teams = teams_result["data"]

        overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

        with overview_col1:
            st.markdown(
                create_metric_card(
                    "Total Players", str(len(players)), f"{len(teams)} teams", "⚽"
                ),
                unsafe_allow_html=True
            )

        with overview_col2:
            avg_cost = sum(p.get("now_cost", 0) for p in players) / (10.0 * len(players)) if players else 0
            st.markdown(
                create_metric_card(
                    "Avg Player Cost", f"£{avg_cost:.1f}m", "Market average", "💰"
                ),
                unsafe_allow_html=True
            )

        with overview_col3:
            top_scorer = max(players, key=lambda x: x.get("total_points", 0)) if players else None
            top_points = top_scorer.get("total_points", 0) if top_scorer else 0
            top_name = format_player_name(top_scorer) if top_scorer else "N/A"
            st.markdown(
                create_metric_card(
                    "Top Scorer", f"{top_points} pts", top_name, "🏆"
                ),
                unsafe_allow_html=True
            )

        with overview_col4:
            timestamp = players_result.get("timestamp", datetime.now())
            time_diff = datetime.now() - timestamp
            update_text = f"{int(time_diff.total_seconds() / 60)} min ago"
            st.markdown(
                create_metric_card(
                    "Data Updated", update_text, "Real-time FPL data", "🔄"
                ),
                unsafe_allow_html=True
            )


def render_players_section():
    """Render players section."""
    st.header("🔍 Advanced Player Explorer")
    st.info("🚧 Enhanced player explorer with advanced filtering, comparison tools, and watchlist management coming soon!")


def render_analytics_section():
    """Render analytics section."""
    st.header("📊 Advanced Analytics")
    st.info("🚧 Effective ownership, zonal analysis, and advanced metrics coming soon!")


def render_projections_section():
    """Render projections section."""
    st.header("🔮 Custom Projections")
    st.info("🚧 Custom gameweek range projections and scenario planning coming soon!")


def render_watchlist_section():
    """Render watchlist section."""
    st.header("📋 Player Watchlist")
    st.info("🚧 Player watchlist, target lists, and avoid lists coming soon!")


if __name__ == "__main__":
    main()
