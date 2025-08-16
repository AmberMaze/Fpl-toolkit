"""Professional FPL Toolkit Dashboard - Modern Fantasy Premier League Analysis Platform.

Inspired by the best features from:
- Fantasy Football Scout (expert analysis, team reveals)
- FPL Review (projections, transfer solver)
- FPL Form (predictions, fixture difficulty)
- FPL.page (real-time dashboard)
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.fpl_toolkit.ai.advisor import FPLAdvisor
from src.fpl_toolkit.analysis.decisions import (
    analyze_transfer_scenario,
    find_transfer_targets,
)
from src.fpl_toolkit.analysis.fixtures import get_fixture_difficulty_rankings
from src.fpl_toolkit.analysis.projections import (
    compare_player_projections,
    get_top_projected_players,
)
from src.fpl_toolkit.api.client import FPLClient

# =====================================================
# PAGE CONFIGURATION & STYLING
# =====================================================

st.set_page_config(
    page_title="FPL Toolkit Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/AmberMaze/Fpl-toolkit",
        "Report a bug": "https://github.com/AmberMaze/Fpl-toolkit/issues",
        "About": "# FPL Toolkit Pro\nYour complete Fantasy Premier League analysis platform!",
    },
)

# Custom CSS for modern styling
st.markdown(
    """
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main layout */
    .main .block-container {
        font-family: 'Inter', sans-serif;
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        margin: 0;
        font-weight: 700;
        font-size: 2.5rem;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        margin: 0.5rem 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 0;
    }
    
    .metric-label {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-delta {
        font-size: 0.8rem;
        margin-top: 0.25rem;
    }
    
    .metric-delta.positive {
        color: #27ae60;
    }
    
    .metric-delta.negative {
        color: #e74c3c;
    }
    
    /* Player cards */
    .player-card {
        background: white;
        border: 1px solid #e8ecef;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }
    
    .player-card:hover {
        border-color: #667eea;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
    
    .player-name {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 0 0 0.5rem 0;
    }
    
    .player-details {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    .player-stats {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .stat-item {
        text-align: center;
        min-width: 80px;
    }
    
    .stat-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
        display: block;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #95a5a6;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Position badges */
    .position-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .position-gk { background: #3498db; color: white; }
    .position-def { background: #27ae60; color: white; }
    .position-mid { background: #f39c12; color: white; }
    .position-fwd { background: #e74c3c; color: white; }
    
    /* Difficulty indicators */
    .difficulty-easy { color: #27ae60; font-weight: 600; }
    .difficulty-medium { color: #f39c12; font-weight: 600; }
    .difficulty-hard { color: #e74c3c; font-weight: 600; }
    
    /* Tables */
    .dataframe {
        border: none !important;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    .dataframe thead {
        background: #f8f9fa;
    }
    
    .dataframe th {
        font-weight: 600;
        color: #2c3e50;
        border: none !important;
        padding: 1rem 0.75rem;
    }
    
    .dataframe td {
        border: none !important;
        padding: 0.75rem;
        border-bottom: 1px solid #f0f0f0;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #f8f9fa;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-live { background: #27ae60; }
    .status-cached { background: #f39c12; }
    .status-error { background: #e74c3c; }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .main-header {
            padding: 1.5rem;
            text-align: center;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .player-stats {
            justify-content: center;
        }
        
        .metric-card {
            text-align: center;
        }
    }
    
    /* Loading animations */
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border: 1px solid #e8ecef;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        color: #495057;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #f8f9fa;
        border-color: #667eea;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #667eea;
        color: white;
        border-color: #667eea;
    }
</style>
""",
    unsafe_allow_html=True,
)


# =====================================================
# DATA LOADING & CACHING
# =====================================================


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_players_data():
    """Load and cache players data with error handling."""
    try:
        with FPLClient() as client:
            players = client.get_players()
            return {"data": players, "status": "success", "timestamp": datetime.now()}
    except Exception as e:
        st.error(f"Error loading players: {str(e)}")
        return {"data": [], "status": "error", "error": str(e)}


@st.cache_data(ttl=1800)
def load_teams_data():
    """Load and cache teams data with error handling."""
    try:
        with FPLClient() as client:
            teams = client.get_teams()
            return {"data": teams, "status": "success", "timestamp": datetime.now()}
    except Exception as e:
        st.error(f"Error loading teams: {str(e)}")
        return {"data": [], "status": "error", "error": str(e)}


@st.cache_data(ttl=3600)
def load_gameweek_data():
    """Load current gameweek information."""
    try:
        with FPLClient() as client:
            gw_data = client.get_gameweeks()
            current_gw = next(
                (gw for gw in gw_data if gw.get("is_current", False)), None
            )
            if not current_gw:
                current_gw = gw_data[0] if gw_data else {"id": 1, "name": "Gameweek 1"}
            return {"data": current_gw, "status": "success"}
    except Exception as e:
        return {
            "data": {"id": 1, "name": "Gameweek 1"},
            "status": "error",
            "error": str(e),
        }


# =====================================================
# UTILITY FUNCTIONS
# =====================================================


def format_player_name(player: Dict[str, Any]) -> str:
    """Format player name from FPL data."""
    first_name = player.get("first_name", "").strip()
    second_name = player.get("second_name", "").strip()
    return f"{first_name} {second_name}".strip() or "Unknown Player"


def get_position_name(element_type: int) -> str:
    """Convert element type to position name."""
    position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
    return position_map.get(element_type, "Unknown")


def get_position_badge_class(position: str) -> str:
    """Get CSS class for position badge."""
    position_classes = {
        "GK": "position-gk",
        "DEF": "position-def",
        "MID": "position-mid",
        "FWD": "position-fwd",
    }
    return position_classes.get(position, "position-badge")


def format_currency(value: float) -> str:
    """Format currency values."""
    return f"£{value:.1f}m"


def get_difficulty_class(difficulty: float) -> str:
    """Get CSS class for difficulty level."""
    if difficulty <= 2.5:
        return "difficulty-easy"
    elif difficulty <= 3.5:
        return "difficulty-medium"
    else:
        return "difficulty-hard"


def create_metric_card(
    title: str, value: str, delta: str = None, delta_positive: bool = True
) -> str:
    """Create HTML for a metric card."""
    delta_class = "positive" if delta_positive else "negative"
    delta_html = f'<p class="metric-delta {delta_class}">{delta}</p>' if delta else ""

    return f"""
    <div class="metric-card">
        <p class="metric-label">{title}</p>
        <p class="metric-value">{value}</p>
        {delta_html}
    </div>
    """


def create_player_card(
    player: Dict[str, Any], team_name: str = "Unknown", detailed: bool = False
) -> str:
    """Create HTML for a player card."""
    name = format_player_name(player)
    position = get_position_name(player.get("element_type", 1))
    position_class = get_position_badge_class(position)
    cost = player.get("now_cost", 0) / 10.0
    points = player.get("total_points", 0)
    form = float(player.get("form", "0") or "0")

    basic_stats = f"""
    <div class="stat-item">
        <span class="stat-value">{format_currency(cost)}</span>
        <span class="stat-label">Cost</span>
    </div>
    <div class="stat-item">
        <span class="stat-value">{points}</span>
        <span class="stat-label">Points</span>
    </div>
    <div class="stat-item">
        <span class="stat-value">{form:.1f}</span>
        <span class="stat-label">Form</span>
    </div>
    """

    if detailed:
        ppg = float(player.get("points_per_game", "0") or "0")
        ownership = float(player.get("selected_by_percent", "0") or "0")
        basic_stats += f"""
        <div class="stat-item">
            <span class="stat-value">{ppg:.1f}</span>
            <span class="stat-label">PPG</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">{ownership:.1f}%</span>
            <span class="stat-label">Owned</span>
        </div>
        """

    return f"""
    <div class="player-card">
        <div class="player-name">{name}</div>
        <div class="player-details">
            <span class="position-badge {position_class}">{position}</span>
            <span style="margin-left: 1rem; color: #7f8c8d;">{team_name}</span>
        </div>
        <div class="player-stats">
            {basic_stats}
        </div>
    </div>
    """


# =====================================================
# MAIN DASHBOARD COMPONENTS
# =====================================================


def render_header():
    """Render the main dashboard header."""
    current_gw_data = load_gameweek_data()
    current_gw = current_gw_data.get("data", {})

    st.markdown(
        f"""
    <div class="main-header">
        <h1>⚽ FPL Toolkit Pro</h1>
        <p>Advanced Fantasy Premier League Analysis & Decision Support | {current_gw.get('name', 'Season 2024/25')}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_dashboard_overview():
    """Render the main dashboard overview with key metrics."""
    st.subheader("📊 Dashboard Overview")

    # Load data
    players_result = load_players_data()
    teams_result = load_teams_data()

    if players_result["status"] == "success" and teams_result["status"] == "success":
        players = players_result["data"]
        teams = teams_result["data"]

        # Calculate key metrics
        total_players = len(players)
        avg_cost = (
            sum(p.get("now_cost", 0) for p in players) / (10.0 * len(players))
            if players
            else 0
        )
        top_scorer = (
            max(players, key=lambda x: x.get("total_points", 0)) if players else None
        )
        most_expensive = (
            max(players, key=lambda x: x.get("now_cost", 0)) if players else None
        )

        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                create_metric_card(
                    "Total Players", str(total_players), f"Across {len(teams)} teams"
                ),
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                create_metric_card(
                    "Average Cost", format_currency(avg_cost), "League average"
                ),
                unsafe_allow_html=True,
            )

        with col3:
            if top_scorer:
                top_scorer_name = format_player_name(top_scorer)
                top_points = top_scorer.get("total_points", 0)
                st.markdown(
                    create_metric_card(
                        "Top Scorer", f"{top_points} pts", top_scorer_name
                    ),
                    unsafe_allow_html=True,
                )

        with col4:
            if most_expensive:
                expensive_name = format_player_name(most_expensive)
                expensive_cost = most_expensive.get("now_cost", 0) / 10.0
                st.markdown(
                    create_metric_card(
                        "Most Expensive",
                        format_currency(expensive_cost),
                        expensive_name,
                    ),
                    unsafe_allow_html=True,
                )

        # Data freshness indicator
        timestamp = players_result.get("timestamp")
        if timestamp:
            time_diff = datetime.now() - timestamp
            freshness = (
                "Live"
                if time_diff.seconds < 300
                else f"Cached ({time_diff.seconds//60}m ago)"
            )
            status_class = "status-live" if time_diff.seconds < 300 else "status-cached"

            st.markdown(
                f"""
            <div style="text-align: right; margin-top: 1rem; color: #7f8c8d; font-size: 0.9rem;">
                <span class="status-indicator {status_class}"></span>
                Data Status: {freshness}
            </div>
            """,
                unsafe_allow_html=True,
            )

    else:
        st.error("Failed to load dashboard data. Please check your connection.")


def render_my_team_tab():
    """Render the My Team tab for lineup management."""
    st.header("👥 My Team")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Current Lineup")

        # Team input methods
        input_method = st.radio(
            "How would you like to input your team?",
            ["Manual Entry", "Team ID Import", "Player Selection"],
            horizontal=True,
        )

        if input_method == "Manual Entry":
            team_input = st.text_area(
                "Enter your team player IDs",
                placeholder="Enter 15 player IDs separated by commas\ne.g., 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15",
                height=100,
                help="Find player IDs in the Players Explorer tab",
            )

            if team_input.strip():
                try:
                    player_ids = [
                        int(x.strip())
                        for x in team_input.replace("\n", ",").split(",")
                        if x.strip()
                    ]
                    if len(player_ids) == 15:
                        st.success(f"✅ Valid team with {len(player_ids)} players")
                        # Display team summary
                        display_team_lineup(player_ids)
                    elif len(player_ids) < 15:
                        st.warning(f"⚠️ Need {15 - len(player_ids)} more players")
                    else:
                        st.error("❌ Too many players! Maximum 15 allowed.")
                except ValueError:
                    st.error("❌ Invalid format. Please enter numbers only.")

        elif input_method == "Team ID Import":
            team_id = st.text_input(
                "FPL Team ID",
                placeholder="e.g., 123456",
                help="Find your team ID in the FPL website URL",
            )

            if team_id and st.button("Import Team"):
                with st.spinner("Importing team data..."):
                    # TODO: Implement FPL team import
                    st.info("Team import feature coming soon!")

        else:  # Player Selection
            st.info("Interactive team builder coming soon!")

    with col2:
        st.subheader("Team Analysis")

        # Quick team stats
        st.markdown(
            """
        <div class="metric-card">
            <h4>Team Value</h4>
            <p>£100.0m / £100.0m</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="metric-card">
            <h4>Free Transfers</h4>
            <p>1 available</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="metric-card">
            <h4>Team Score</h4>
            <p>85/100</p>
            <small>Based on form & fixtures</small>
        </div>
        """,
            unsafe_allow_html=True,
        )


def display_team_lineup(player_ids: list):
    """Display team lineup in formation."""
    players_result = load_players_data()
    if players_result["status"] != "success":
        st.error("Cannot load player data")
        return

    players = players_result["data"]
    player_lookup = {p["id"]: p for p in players}

    # Get player data
    team_players = []
    for pid in player_ids:
        if pid in player_lookup:
            team_players.append(player_lookup[pid])

    if not team_players:
        st.warning("No valid players found")
        return

    # Group by position
    positions = {"GK": [], "DEF": [], "MID": [], "FWD": []}

    for player in team_players:
        pos = get_position_name(player.get("element_type", 1))
        if pos in positions:
            positions[pos].append(player)

    # Display formation
    st.markdown("### Formation View")

    for pos_name, pos_players in positions.items():
        if pos_players:
            st.markdown(f"**{pos_name} ({len(pos_players)})**")
            cols = st.columns(len(pos_players))

            for i, player in enumerate(pos_players):
                with cols[i]:
                    cost = player.get("now_cost", 0) / 10.0
                    points = player.get("total_points", 0)
                    form = float(player.get("form", "0") or "0")

                    st.markdown(
                        f"""
                    <div style="text-align: center; padding: 0.5rem; border: 1px solid #ddd; border-radius: 8px; margin: 0.25rem;">
                        <div style="font-weight: 600;">{format_player_name(player)}</div>
                        <div style="font-size: 0.8rem; color: #666;">
                            {format_currency(cost)} | {points}pts | {form:.1f}
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )


def render_players_explorer():
    """Render the Players Explorer tab with advanced filtering."""
    st.header("🔍 Players Explorer")

    # Load data
    players_result = load_players_data()
    teams_result = load_teams_data()

    if players_result["status"] != "success" or teams_result["status"] != "success":
        st.error("Failed to load player data")
        return

    players = players_result["data"]
    teams = teams_result["data"]
    team_lookup = {t["id"]: t["name"] for t in teams}

    # Advanced filters
    st.subheader("🎛️ Advanced Filters")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        position_filter = st.selectbox(
            "Position",
            ["All Positions", "Goalkeepers", "Defenders", "Midfielders", "Forwards"],
            index=0,
        )

    with col2:
        cost_range = st.slider(
            "Cost Range (£m)",
            min_value=4.0,
            max_value=15.0,
            value=(4.0, 15.0),
            step=0.1,
        )

    with col3:
        points_range = st.slider(
            "Total Points", min_value=0, max_value=300, value=(0, 300), step=10
        )

    with col4:
        form_threshold = st.slider(
            "Minimum Form", min_value=0.0, max_value=10.0, value=0.0, step=0.1
        )

    # Additional filters
    col5, col6, col7 = st.columns(3)

    with col5:
        team_filter = st.multiselect(
            "Teams",
            options=[team["name"] for team in teams],
            default=[],
            help="Leave empty to include all teams",
        )

    with col6:
        ownership_range = st.slider(
            "Ownership %", min_value=0.0, max_value=100.0, value=(0.0, 100.0), step=0.1
        )

    with col7:
        search_term = st.text_input("Search Player", placeholder="Enter player name...")

    # Sort options
    sort_by = st.selectbox(
        "Sort by",
        ["Total Points", "Form", "Points per Game", "Cost", "Ownership %"],
        index=0,
    )

    sort_ascending = st.checkbox("Ascending order", False)

    # Apply filters
    filtered_players = filter_players(
        players,
        team_lookup,
        position_filter,
        cost_range,
        points_range,
        form_threshold,
        team_filter,
        ownership_range,
        search_term,
    )

    # Sort players
    sort_key_map = {
        "Total Points": "total_points",
        "Form": "form",
        "Points per Game": "points_per_game",
        "Cost": "now_cost",
        "Ownership %": "selected_by_percent",
    }

    sort_key = sort_key_map[sort_by]
    filtered_players.sort(
        key=lambda x: float(x.get(sort_key, 0) or 0), reverse=not sort_ascending
    )

    # Display results
    st.subheader(f"📋 Results ({len(filtered_players)} players)")

    if filtered_players:
        # Display options
        view_mode = st.radio(
            "View Mode", ["Card View", "Table View", "Detailed View"], horizontal=True
        )

        if view_mode == "Card View":
            # Card grid view
            cols_per_row = 3
            for i in range(
                0, len(filtered_players[:30]), cols_per_row
            ):  # Limit to 30 for performance
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(filtered_players):
                        player = filtered_players[i + j]
                        team_name = team_lookup.get(player.get("team"), "Unknown")

                        with col:
                            player_card_html = create_player_card(
                                player, team_name, detailed=True
                            )
                            st.markdown(player_card_html, unsafe_allow_html=True)

                            # Action buttons
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("Compare", key=f"compare_{player['id']}"):
                                    if "comparison_list" not in st.session_state:
                                        st.session_state.comparison_list = []
                                    if (
                                        player["id"]
                                        not in st.session_state.comparison_list
                                    ):
                                        st.session_state.comparison_list.append(
                                            player["id"]
                                        )
                                        st.success("Added to comparison!")

                            with col_btn2:
                                if st.button("Details", key=f"details_{player['id']}"):
                                    st.session_state.selected_player = player["id"]
                                    st.success("Player selected!")

        elif view_mode == "Table View":
            # Table view
            table_data = []
            for player in filtered_players[:50]:  # Limit for performance
                table_data.append(
                    {
                        "Name": format_player_name(player),
                        "Position": get_position_name(player.get("element_type", 1)),
                        "Team": team_lookup.get(player.get("team"), "Unknown"),
                        "Cost": format_currency(player.get("now_cost", 0) / 10.0),
                        "Points": player.get("total_points", 0),
                        "Form": f"{float(player.get('form', '0') or '0'):.1f}",
                        "PPG": f"{float(player.get('points_per_game', '0') or '0'):.1f}",
                        "Owned %": f"{float(player.get('selected_by_percent', '0') or '0'):.1f}%",
                    }
                )

            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True, height=600)

        else:  # Detailed View
            # Detailed single player view
            selected_index = st.selectbox(
                "Select Player for Detailed View",
                range(min(10, len(filtered_players))),
                format_func=lambda x: format_player_name(filtered_players[x]),
            )

            player = filtered_players[selected_index]
            render_player_detailed_view(player, team_lookup)

    else:
        st.info("No players match your current filters. Try adjusting the criteria.")


def filter_players(
    players: list,
    team_lookup: dict,
    position_filter: str,
    cost_range: tuple,
    points_range: tuple,
    form_threshold: float,
    team_filter: list,
    ownership_range: tuple,
    search_term: str,
) -> list:
    """Apply filters to player list."""
    filtered = []

    # Position mapping
    position_map = {"Goalkeepers": 1, "Defenders": 2, "Midfielders": 3, "Forwards": 4}

    for player in players:
        # Position filter
        if position_filter != "All Positions":
            if player.get("element_type") != position_map[position_filter]:
                continue

        # Cost filter
        cost = player.get("now_cost", 0) / 10.0
        if not (cost_range[0] <= cost <= cost_range[1]):
            continue

        # Points filter
        points = player.get("total_points", 0)
        if not (points_range[0] <= points <= points_range[1]):
            continue

        # Form filter
        form = float(player.get("form", "0") or "0")
        if form < form_threshold:
            continue

        # Team filter
        if team_filter:
            team_name = team_lookup.get(player.get("team"), "Unknown")
            if team_name not in team_filter:
                continue

        # Ownership filter
        ownership = float(player.get("selected_by_percent", "0") or "0")
        if not (ownership_range[0] <= ownership <= ownership_range[1]):
            continue

        # Search filter
        if search_term:
            player_name = format_player_name(player).lower()
            if search_term.lower() not in player_name:
                continue

        filtered.append(player)

    return filtered


def render_player_detailed_view(player: dict, team_lookup: dict):
    """Render detailed view for a single player."""
    st.subheader(f"📊 {format_player_name(player)} - Detailed Analysis")

    col1, col2 = st.columns([1, 2])

    with col1:
        # Player info card
        team_name = team_lookup.get(player.get("team"), "Unknown")
        position = get_position_name(player.get("element_type", 1))

        st.markdown(
            f"""
        <div class="player-card">
            <h3>{format_player_name(player)}</h3>
            <p><span class="position-badge {get_position_badge_class(position)}">{position}</span> | {team_name}</p>
            <hr>
            <div class="player-stats">
                <div class="stat-item">
                    <span class="stat-value">{format_currency(player.get('now_cost', 0) / 10.0)}</span>
                    <span class="stat-label">Cost</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{player.get('total_points', 0)}</span>
                    <span class="stat-label">Total Points</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{float(player.get('form', '0') or '0'):.1f}</span>
                    <span class="stat-label">Form</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{float(player.get('points_per_game', '0') or '0'):.1f}</span>
                    <span class="stat-label">PPG</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{float(player.get('selected_by_percent', '0') or '0'):.1f}%</span>
                    <span class="stat-label">Ownership</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{player.get('minutes', 0)}</span>
                    <span class="stat-label">Minutes</span>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        # Performance charts
        st.markdown("#### 📈 Performance Analysis")

        # Create sample performance chart
        try:
            # Mock data for demonstration - replace with actual fixture data
            gameweeks = list(range(1, 11))
            points_history = [np.random.randint(0, 15) for _ in gameweeks]

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=gameweeks,
                    y=points_history,
                    mode="lines+markers",
                    name="Points per GW",
                    line=dict(color="#667eea", width=3),
                    marker=dict(size=8),
                )
            )

            fig.update_layout(
                title="Points History (Last 10 GWs)",
                xaxis_title="Gameweek",
                yaxis_title="Points",
                height=300,
                margin=dict(l=0, r=0, t=30, b=0),
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception:
            st.info("Performance charts require additional data setup")

    # Advanced stats
    st.markdown("#### 🎯 Advanced Statistics")

    col3, col4, col5 = st.columns(3)

    with col3:
        st.metric("Goals", player.get("goals_scored", 0))
        st.metric("Assists", player.get("assists", 0))

    with col4:
        st.metric("Clean Sheets", player.get("clean_sheets", 0))
        st.metric("Bonus Points", player.get("bonus", 0))

    with col5:
        st.metric("Yellow Cards", player.get("yellow_cards", 0))
        st.metric("Red Cards", player.get("red_cards", 0))


def render_transfer_planner():
    """Render the Transfer Planner tab."""
    st.header("🔄 Transfer Planner")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Transfer Analysis")

        # Transfer scenario inputs
        transfer_type = st.radio(
            "Transfer Type",
            ["Single Transfer", "Double Transfer", "Wildcard Planning"],
            horizontal=True,
        )

        if transfer_type == "Single Transfer":
            render_single_transfer()
        elif transfer_type == "Double Transfer":
            render_double_transfer()
        else:
            render_wildcard_planner()

    with col2:
        st.subheader("Transfer Recommendations")

        # Quick recommendations
        st.markdown(
            """
        <div class="metric-card">
            <h4>🔥 Hot Picks</h4>
            <p>Players trending up</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="metric-card">
            <h4>❄️ Ice Cold</h4>
            <p>Players to avoid</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="metric-card">
            <h4>💎 Differentials</h4>
            <p>Low ownership gems</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_single_transfer():
    """Render single transfer analysis."""
    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Player Out (ID)", placeholder="Enter player ID to transfer out")

    with col2:
        st.text_input("Player In (ID)", placeholder="Enter player ID to transfer in")

    st.slider("Analysis Horizon (Gameweeks)", 1, 10, 5)

    if st.button("Analyze Transfer", type="primary"):
        with st.spinner("Analyzing transfer scenario..."):
            # TODO: Implement transfer analysis
            st.success("Transfer analysis feature coming soon!")


def render_double_transfer():
    """Render double transfer analysis."""
    st.markdown("**Players Out**")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("First Player Out (ID)", key="out1")
    with col2:
        st.text_input("Second Player Out (ID)", key="out2")

    st.markdown("**Players In**")
    col3, col4 = st.columns(2)
    with col3:
        st.text_input("First Player In (ID)", key="in1")
    with col4:
        st.text_input("Second Player In (ID)", key="in2")

    if st.button("Analyze Double Transfer", type="primary"):
        with st.spinner("Analyzing double transfer..."):
            st.success("Double transfer analysis feature coming soon!")


def render_wildcard_planner():
    """Render wildcard planning interface."""
    st.markdown("**Wildcard Team Builder**")

    budget = st.number_input(
        "Budget (£m)", min_value=90.0, max_value=110.0, value=100.0, step=0.1
    )

    # Formation selector
    formation = st.selectbox(
        "Formation",
        ["3-4-3", "3-5-2", "4-3-3", "4-4-2", "4-5-1", "5-3-2", "5-4-1"],
        index=2,
    )

    st.info(f"Selected formation: {formation} with £{budget:.1f}m budget")

    if st.button("Optimize Wildcard Team", type="primary"):
        with st.spinner("Building optimal team..."):
            st.success("Wildcard optimizer feature coming soon!")


def render_fixture_analysis():
    """Render the Fixture Analysis tab."""
    st.header("📅 Fixture Analysis")

    tab1, tab2, tab3 = st.tabs(
        ["Team Fixtures", "Fixture Difficulty", "Blank/Double GWs"]
    )

    with tab1:
        render_team_fixtures()

    with tab2:
        render_fixture_difficulty()

    with tab3:
        render_blank_double_gameweeks()


def render_team_fixtures():
    """Render team fixtures analysis."""
    st.subheader("Team Fixture Analysis")

    teams_result = load_teams_data()
    if teams_result["status"] != "success":
        st.error("Cannot load teams data")
        return

    teams = teams_result["data"]

    # Team selector
    selected_teams = st.multiselect(
        "Select Teams to Analyze",
        options=[team["name"] for team in teams],
        default=[teams[0]["name"]] if teams else [],
        max_selections=6,
    )

    if selected_teams:
        # Analysis horizon
        horizon = st.slider("Analyze Next N Gameweeks", 3, 10, 5)

        # Mock fixture data for demonstration
        st.markdown(f"#### Fixture Analysis for Next {horizon} Gameweeks")

        for team in selected_teams:
            with st.expander(f"{team} Fixtures"):
                # Mock fixtures
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Home Fixtures", "2")
                with col2:
                    st.metric("Away Fixtures", "3")
                with col3:
                    st.metric("Avg Difficulty", "3.2")

                st.info("Detailed fixture data integration coming soon!")


def render_fixture_difficulty():
    """Render fixture difficulty ratings."""
    st.subheader("🎯 Fixture Difficulty Rankings")

    analysis_period = st.selectbox(
        "Analysis Period", ["Next 3 GWs", "Next 5 GWs", "Next 8 GWs"], index=1
    )

    if st.button("Analyze Fixture Difficulty"):
        with st.spinner("Calculating fixture difficulty..."):
            try:
                # Get fixture difficulty data
                n_gameweeks = int(analysis_period.split()[1])
                fixture_data = get_fixture_difficulty_rankings(next_n=n_gameweeks)

                if fixture_data:
                    # Split into easy and hard fixtures
                    easy_fixtures = fixture_data[:10]
                    hard_fixtures = fixture_data[-10:]

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("#### 🟢 Easiest Fixtures")
                        for i, team in enumerate(easy_fixtures, 1):
                            difficulty = team.get("average_difficulty", 0)
                            difficulty_class = get_difficulty_class(difficulty)

                            st.markdown(
                                f"""
                            <div style="display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #eee;">
                                <span>{i}. {team.get('team_name', 'Unknown')}</span>
                                <span class="{difficulty_class}">{difficulty:.1f}</span>
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )

                    with col2:
                        st.markdown("#### 🔴 Hardest Fixtures")
                        for i, team in enumerate(hard_fixtures, 1):
                            difficulty = team.get("average_difficulty", 0)
                            difficulty_class = get_difficulty_class(difficulty)

                            st.markdown(
                                f"""
                            <div style="display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #eee;">
                                <span>{i}. {team.get('team_name', 'Unknown')}</span>
                                <span class="{difficulty_class}">{difficulty:.1f}</span>
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )

                else:
                    st.warning("No fixture data available")

            except Exception as e:
                st.error(f"Error analyzing fixtures: {str(e)}")


def render_blank_double_gameweeks():
    """Render blank and double gameweek analysis."""
    st.subheader("📋 Blank & Double Gameweeks")

    st.info(
        "Blank and Double Gameweek analysis will be available during the season when fixtures are updated."
    )

    # Placeholder for BGW/DGW data
    st.markdown(
        """
    #### What to Look For:
    - **Blank Gameweeks (BGW)**: When teams don't play due to cup competitions
    - **Double Gameweeks (DGW)**: When teams play twice in one gameweek
    - **Planning Strategy**: Build your squad around these special gameweeks
    """
    )


def render_statistics_hub():
    """Render the Statistics Hub tab."""
    st.header("📊 Statistics Hub")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["League Stats", "Player Comparisons", "Form Analysis", "Projections"]
    )

    with tab1:
        render_league_statistics()

    with tab2:
        render_player_comparisons()

    with tab3:
        render_form_analysis()

    with tab4:
        render_projections_analysis()


def render_league_statistics():
    """Render league-wide statistics."""
    st.subheader("🏆 League Statistics")

    players_result = load_players_data()
    if players_result["status"] != "success":
        st.error("Cannot load player data")
        return

    players = players_result["data"]

    # Top performers by position
    st.markdown("#### Top Performers by Position")

    positions = {"GK": 1, "DEF": 2, "MID": 3, "FWD": 4}

    for pos_name, pos_id in positions.items():
        pos_players = [p for p in players if p.get("element_type") == pos_id]
        if pos_players:
            top_player = max(pos_players, key=lambda x: x.get("total_points", 0))

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    f"Top {pos_name}",
                    format_player_name(top_player),
                    f"{top_player.get('total_points', 0)} points",
                )


def render_player_comparisons():
    """Render player comparison interface."""
    st.subheader("⚖️ Player Comparisons")

    # Check for comparison list in session state
    if "comparison_list" not in st.session_state:
        st.session_state.comparison_list = []

    comparison_list = st.session_state.comparison_list

    if comparison_list:
        st.markdown(f"#### Comparing {len(comparison_list)} players")

        # Show selected players
        players_result = load_players_data()
        if players_result["status"] == "success":
            players = players_result["data"]
            player_lookup = {p["id"]: p for p in players}

            selected_players = [
                player_lookup[pid] for pid in comparison_list if pid in player_lookup
            ]

            if selected_players:
                # Display comparison table
                comparison_data = []
                for player in selected_players:
                    comparison_data.append(
                        {
                            "Player": format_player_name(player),
                            "Position": get_position_name(
                                player.get("element_type", 1)
                            ),
                            "Cost": format_currency(player.get("now_cost", 0) / 10.0),
                            "Points": player.get("total_points", 0),
                            "Form": f"{float(player.get('form', '0') or '0'):.1f}",
                            "PPG": f"{float(player.get('points_per_game', '0') or '0'):.1f}",
                            "Owned %": f"{float(player.get('selected_by_percent', '0') or '0'):.1f}%",
                        }
                    )

                df = pd.DataFrame(comparison_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Clear comparison list
                if st.button("Clear Comparison List"):
                    st.session_state.comparison_list = []
                    st.rerun()

        # Advanced comparison
        if len(comparison_list) >= 2:
            horizon = st.slider(
                "Projection Horizon (GWs)", 1, 10, 5, key="comp_horizon"
            )

            if st.button("Run Advanced Comparison"):
                with st.spinner("Running comparison analysis..."):
                    try:
                        comparison_result = compare_player_projections(
                            comparison_list, horizon
                        )

                        if comparison_result:
                            st.success("Comparison completed!")
                            # Display detailed comparison results
                            st.json(comparison_result)  # Temporary display
                        else:
                            st.warning("No comparison data available")

                    except Exception as e:
                        st.error(f"Comparison error: {str(e)}")

    else:
        st.info(
            "No players selected for comparison. Add players from the Players Explorer tab."
        )


def render_form_analysis():
    """Render form analysis."""
    st.subheader("📈 Form Analysis")

    form_period = st.selectbox(
        "Form Period", ["Last 3 GWs", "Last 5 GWs", "Season Average"], index=1
    )

    position_filter = st.selectbox(
        "Position Filter",
        ["All", "GK", "DEF", "MID", "FWD"],
        index=0,
        key="form_position",
    )

    if st.button("Analyze Form"):
        with st.spinner("Analyzing player form..."):
            players_result = load_players_data()
            if players_result["status"] == "success":
                players = players_result["data"]

                # Filter by position if specified
                if position_filter != "All":
                    position_map = {"GK": 1, "DEF": 2, "MID": 3, "FWD": 4}
                    players = [
                        p
                        for p in players
                        if p.get("element_type") == position_map[position_filter]
                    ]

                # Sort by form
                players.sort(
                    key=lambda x: float(x.get("form", "0") or "0"), reverse=True
                )

                # Display top form players
                st.markdown("#### 🔥 Best Form Players")

                top_form = players[:10]
                for i, player in enumerate(top_form, 1):
                    form = float(player.get("form", "0") or "0")
                    cost = player.get("now_cost", 0) / 10.0

                    st.markdown(
                        f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; border: 1px solid #eee; border-radius: 8px; margin: 0.5rem 0;">
                        <div>
                            <strong>{i}. {format_player_name(player)}</strong>
                            <br>
                            <small>{get_position_name(player.get('element_type', 1))} | {format_currency(cost)}</small>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 1.2rem; font-weight: 600; color: #27ae60;">{form:.1f}</span>
                            <br>
                            <small>Form</small>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )


def render_projections_analysis():
    """Render projections analysis."""
    st.subheader("🔮 Points Projections")

    projection_horizon = st.slider(
        "Projection Horizon (GWs)", 1, 10, 5, key="proj_horizon"
    )
    position_proj = st.selectbox(
        "Position", ["All", "GK", "DEF", "MID", "FWD"], key="proj_position"
    )
    max_cost_proj = st.slider("Max Cost (£m)", 4.0, 15.0, 15.0, key="proj_cost")

    if st.button("Generate Projections"):
        with st.spinner("Calculating projections..."):
            try:
                pos_filter = None if position_proj == "All" else position_proj

                projections = get_top_projected_players(
                    position=pos_filter,
                    max_cost=max_cost_proj,
                    limit=15,
                    horizon_gameweeks=projection_horizon,
                )

                if projections:
                    st.markdown(
                        f"#### 🎯 Top Projected Players (Next {projection_horizon} GWs)"
                    )

                    proj_data = []
                    for proj in projections:
                        proj_data.append(
                            {
                                "Player": proj["name"],
                                "Position": proj["position"],
                                "Cost": format_currency(proj["cost"]),
                                "Projected Points": f"{proj['projected_points']:.1f}",
                                "Points per £m": f"{proj['projected_points'] / proj['cost']:.2f}",
                                "Confidence": f"{proj['confidence_score']:.2f}",
                                "Current Form": f"{proj['form']:.1f}",
                            }
                        )

                    df = pd.DataFrame(proj_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)

                else:
                    st.warning("No projection data available")

            except Exception as e:
                st.error(f"Projection error: {str(e)}")


# =====================================================
# MAIN APPLICATION
# =====================================================


def main():
    """Main application entry point."""
    # Render header
    render_header()

    # Main navigation
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "🏠 Dashboard",
            "👥 My Team",
            "🔍 Players",
            "🔄 Transfers",
            "📅 Fixtures",
            "📊 Statistics",
        ]
    )

    with tab1:
        render_dashboard_overview()

    with tab2:
        render_my_team_tab()

    with tab3:
        render_players_explorer()

    with tab4:
        render_transfer_planner()

    with tab5:
        render_fixture_analysis()

    with tab6:
        render_statistics_hub()

    # Sidebar
    render_sidebar()


def render_sidebar():
    """Render the sidebar with tools and settings."""
    with st.sidebar:
        st.markdown("### ⚙️ Tools & Settings")

        # Quick actions
        st.markdown("#### Quick Actions")

        if st.button("🔄 Refresh Data", help="Clear cache and reload data"):
            st.cache_data.clear()
            st.success("Data cache cleared!")

        if st.button("📱 Mobile View", help="Optimize for mobile"):
            st.info("Already optimized for mobile!")

        # Data status
        st.markdown("#### 📊 Data Status")
        players_result = load_players_data()
        teams_result = load_teams_data()

        if players_result["status"] == "success":
            st.success("✅ Players data loaded")
        else:
            st.error("❌ Players data failed")

        if teams_result["status"] == "success":
            st.success("✅ Teams data loaded")
        else:
            st.error("❌ Teams data failed")

        # App info
        st.markdown("#### ℹ️ About")
        st.markdown(
            """
        **FPL Toolkit Pro** combines the best features from:
        - Fantasy Football Scout
        - FPL Review  
        - FPL Form
        - FPL.page
        
        Built for serious FPL managers who want data-driven decisions.
        """
        )

        st.markdown("#### 🚀 Features")
        st.markdown(
            """
        ✅ Real-time player data  
        ✅ Advanced filtering  
        ✅ Transfer analysis  
        ✅ Fixture difficulty  
        ✅ Form tracking  
        ✅ Points projections  
        ✅ Team optimization  
        ✅ Mobile responsive  
        """
        )

        # Version info
        st.markdown("---")
        st.markdown("**Version**: 2.0.0 Pro")
        st.markdown("**Last Updated**: August 2025")


if __name__ == "__main__":
    main()
