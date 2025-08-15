"""Enhanced FPL Toolkit with Advanced Features - Your Complete Fantasy Premier League Management System.

🌟 NEW FEATURES:
- 👥 My Team Management with Football Pitch Lineup
- 🏆 League Analysis & Predictions
- 📊 Advanced Analytics (Effective Ownership, Zonal Analysis)
- 🔮 Custom Gameweek Projections
- 📋 Player Watchlists & Transfer Planning
- 🎯 Head-to-Head Records
- 💡 AI-Powered Insights
"""

from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from src.fpl_toolkit.analysis.advanced_analysis import predict_league_standings
from src.fpl_toolkit.api.client import FPLClient
from src.fpl_toolkit.ui.pitch_components import (
    create_team_stats_overview,
    render_team_lineup_pitch,
    render_team_stats_cards,
)

# Configure page with enhanced styling
st.set_page_config(
    page_title="FPL Toolkit Pro - Advanced",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/AmberMaze/Fpl-toolkit",
        "Report a bug": "https://github.com/AmberMaze/Fpl-toolkit/issues",
        "About": "FPL Toolkit Pro - Your complete Fantasy Premier League management system with advanced analytics!",
    },
)

# Enhanced CSS for the new features
st.markdown(
    """
<style>
    /* Enhanced modern styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .main .block-container {
        font-family: 'Inter', sans-serif;
        padding-top: 1.5rem;
        max-width: 100%;
    }
    
    /* Main header with gradient */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 2.5rem;
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
        font-size: 3rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        margin: 1rem 0 0 0;
        opacity: 0.95;
        font-size: 1.2rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* Enhanced metric cards */
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
    
    /* Enhanced player cards */
    .player-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e8ecef;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .player-card:hover {
        border-color: #667eea;
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
        transform: translateY(-4px);
    }
    
    .player-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .player-card:hover::before {
        transform: scaleX(1);
    }
    
    /* Position badges with enhanced styling */
    .position-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-right: 0.75rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .position-gk { 
        background: linear-gradient(135deg, #3498db, #2980b9); 
        color: white; 
    }
    .position-def { 
        background: linear-gradient(135deg, #27ae60, #229954); 
        color: white; 
    }
    .position-mid { 
        background: linear-gradient(135deg, #f39c12, #e67e22); 
        color: white; 
    }
    .position-fwd { 
        background: linear-gradient(135deg, #e74c3c, #c0392b); 
        color: white; 
    }
    
    /* Enhanced tables */
    .dataframe {
        border: none !important;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        background: white;
    }
    
    /* Status indicators with glow effect */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 0.75rem;
        box-shadow: 0 0 8px currentColor;
    }
    
    .status-live { 
        background: #27ae60; 
        animation: pulse 2s infinite;
    }
    .status-cached { background: #f39c12; }
    .status-error { background: #e74c3c; }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 8px #27ae60; }
        50% { box-shadow: 0 0 20px #27ae60; }
        100% { box-shadow: 0 0 8px #27ae60; }
    }
    
    /* Enhanced tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.75rem;
        background: transparent;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border: 1px solid #e8ecef;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-weight: 600;
        color: #495057;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-color: #667eea;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
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
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .main-header {
            padding: 2rem 1.5rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-card {
            margin: 0.5rem 0;
            padding: 1.5rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
    }
    
    /* Loading animation */
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
    
    /* Success/Warning/Error styling */
    .stSuccess {
        background: linear-gradient(145deg, #d4edda, #c3e6cb);
        border-left: 4px solid #28a745;
        border-radius: 8px;
    }
    
    .stWarning {
        background: linear-gradient(145deg, #fff3cd, #ffeaa7);
        border-left: 4px solid #ffc107;
        border-radius: 8px;
    }
    
    .stError {
        background: linear-gradient(145deg, #f8d7da, #f5c6cb);
        border-left: 4px solid #dc3545;
        border-radius: 8px;
    }
</style>
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


@st.cache_data(ttl=900)  # 15 minutes cache for team data
def load_user_team_data(team_id: int):
    """Load user team data."""
    try:
        with FPLClient() as client:
            team_data = client.get_user_team(team_id)
            return {"data": team_data, "status": "success"}
    except Exception as e:
        return {"data": {}, "status": "error", "error": str(e)}


@st.cache_data(ttl=600)  # 10 minutes cache for picks
def load_team_picks_data(team_id: int, gameweek: int):
    """Load team picks for specific gameweek."""
    try:
        with FPLClient() as client:
            picks_data = client.get_team_picks(team_id, gameweek)
            return {"data": picks_data, "status": "success"}
    except Exception as e:
        return {"data": {}, "status": "error", "error": str(e)}


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


def create_metric_card(
    title: str, value: str, subtitle: str = "", icon: str = ""
) -> str:
    """Create enhanced HTML for a metric card."""
    icon_html = f'<div class="feature-icon">{icon}</div>' if icon else ""
    subtitle_html = f'<p class="metric-subtitle">{subtitle}</p>' if subtitle else ""

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
        <h1>⚽ FPL Toolkit Pro - Advanced</h1>
        <p>🚀 Complete Fantasy Premier League Management System | Season 2024/25</p>
        <p style="font-size: 1rem; margin-top: 1rem; opacity: 0.9;">
            ✨ New: Team Lineup Pitch View | League Predictions | Advanced Analytics | Custom Projections
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


# =====================================================
# MAIN APPLICATION SECTIONS
# =====================================================


def render_my_team_advanced():
    """Render advanced My Team section with authentication and pitch view."""
    st.header("👥 My Team - Advanced Management")

    # Team ID input with authentication option
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

        # Demo section
        st.markdown("---")
        st.markdown("### 🎯 Demo: Sample Team Analysis")

        demo_col1, demo_col2, demo_col3 = st.columns(3)

        with demo_col1:
            st.markdown(
                create_metric_card("Team Value", "£99.7m", "£0.3m remaining", "💰"),
                unsafe_allow_html=True,
            )

        with demo_col2:
            st.markdown(
                create_metric_card("Total Points", "1,247", "Rank: 234,567", "🏆"),
                unsafe_allow_html=True,
            )

        with demo_col3:
            st.markdown(
                create_metric_card(
                    "Free Transfers", "1", "Next deadline: Sat 19:00", "🔄"
                ),
                unsafe_allow_html=True,
            )

        return

    try:
        team_id = int(team_id_input)
    except ValueError:
        st.error("❌ Please enter a valid numeric Team ID")
        return

    # Load team data
    with st.spinner("🔄 Loading your team data..."):
        team_result = load_user_team_data(team_id)
        players_result = load_players_data()
        teams_result = load_teams_data()
        gameweeks_result = load_gameweeks_data()

    if team_result["status"] != "success":
        st.error(
            f"❌ Could not load team data: {team_result.get('error', 'Unknown error')}"
        )
        return

    if players_result["status"] != "success" or teams_result["status"] != "success":
        st.error("❌ Could not load FPL data")
        return

    team_data = team_result["data"]
    players = players_result["data"]
    teams = teams_result["data"]
    gameweeks = gameweeks_result["data"]

    # Display team info header
    st.success(
        f"✅ Successfully loaded team: **{team_data.get('name', 'Unknown')}** (Manager: {team_data.get('player_first_name', '')} {team_data.get('player_last_name', '')})"
    )

    # Current gameweek
    current_gw = next(
        (gw for gw in gameweeks if gw.get("is_current", False)),
        gameweeks[0] if gameweeks else None,
    )
    current_gw_id = current_gw.get("id") if current_gw else 1

    # Load current picks
    picks_result = load_team_picks_data(team_id, current_gw_id)

    if picks_result["status"] != "success":
        st.error("❌ Could not load team picks")
        return

    picks_data = picks_result["data"]
    picks = picks_data.get("picks", [])

    # Get player details for the team
    player_lookup = {p["id"]: p for p in players}
    team_players = []

    for pick in picks:
        player_id = pick.get("element")
        if player_id in player_lookup:
            player = player_lookup[player_id].copy()
            player["pick_info"] = pick
            team_players.append(player)

    # Sort by position (starting XI first, then bench)
    team_players.sort(key=lambda x: x["pick_info"].get("position", 15))

    # Team overview metrics
    st.markdown("### 📊 Team Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        team_value = sum(p.get("now_cost", 0) for p in team_players) / 10.0
        bank = picks_data.get("entry_history", {}).get("bank", 0) / 10.0
        st.markdown(
            create_metric_card(
                "Team Value", f"£{team_value:.1f}m", f"Bank: £{bank:.1f}m", "💰"
            ),
            unsafe_allow_html=True,
        )

    with col2:
        total_points = picks_data.get("entry_history", {}).get("total_points", 0)
        gw_points = picks_data.get("entry_history", {}).get("points", 0)
        st.markdown(
            create_metric_card(
                "Total Points", f"{total_points:,}", f"This GW: {gw_points}", "🏆"
            ),
            unsafe_allow_html=True,
        )

    with col3:
        overall_rank = picks_data.get("entry_history", {}).get("overall_rank")
        rank_text = f"{overall_rank:,}" if overall_rank else "N/A"
        st.markdown(
            create_metric_card(
                "Overall Rank", rank_text, f"Gameweek {current_gw_id}", "📈"
            ),
            unsafe_allow_html=True,
        )

    with col4:
        transfers_cost = picks_data.get("entry_history", {}).get(
            "event_transfers_cost", 0
        )
        transfers_made = picks_data.get("entry_history", {}).get("event_transfers", 0)
        st.markdown(
            create_metric_card(
                "Transfers",
                f"{transfers_made} made",
                f"Cost: {transfers_cost} pts",
                "🔄",
            ),
            unsafe_allow_html=True,
        )

    # Main team analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["⚽ Pitch View", "📊 Team Stats", "📈 Performance", "🔄 Transfers"]
    )

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
        st.markdown("### 📊 Detailed Team Statistics")

        # Player performance table
        if team_players:
            table_data = []
            for player in team_players:
                pick_info = player.get("pick_info", {})
                team_info = next(
                    (t for t in teams if t["id"] == player.get("team")), {}
                )

                table_data.append(
                    {
                        "Position": pick_info.get("position", 0),
                        "Player": format_player_name(player),
                        "Team": team_info.get("short_name", ""),
                        "Pos": get_position_name(player.get("element_type", 1)),
                        "Cost": f"£{player.get('now_cost', 0) / 10.0:.1f}m",
                        "Points": player.get("total_points", 0),
                        "Form": f"{float(player.get('form', '0') or '0'):.1f}",
                        "PPG": f"{float(player.get('points_per_game', '0') or '0'):.1f}",
                        "Captain": (
                            "🔴"
                            if pick_info.get("is_captain")
                            else "🔵" if pick_info.get("is_vice_captain") else ""
                        ),
                        "Status": "⚽" if pick_info.get("position", 15) <= 11 else "🪑",
                    }
                )

            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

        # Position analysis
        st.markdown("#### 📊 Position Analysis")

        if team_players:
            position_stats = {"GK": [], "DEF": [], "MID": [], "FWD": []}

            for player in team_players:
                pos = get_position_name(player.get("element_type", 1))
                if pos in position_stats:
                    position_stats[pos].append(player)

            pos_col1, pos_col2, pos_col3, pos_col4 = st.columns(4)

            for i, (pos, players_in_pos) in enumerate(position_stats.items()):
                col = [pos_col1, pos_col2, pos_col3, pos_col4][i]

                with col:
                    if players_in_pos:
                        total_cost = (
                            sum(p.get("now_cost", 0) for p in players_in_pos) / 10.0
                        )
                        total_points = sum(
                            p.get("total_points", 0) for p in players_in_pos
                        )
                        avg_form = sum(
                            float(p.get("form", "0") or "0") for p in players_in_pos
                        ) / len(players_in_pos)

                        st.markdown(f"**{pos} ({len(players_in_pos)})**")
                        st.write(f"💰 Cost: £{total_cost:.1f}m")
                        st.write(f"🏆 Points: {total_points}")
                        st.write(f"📈 Avg Form: {avg_form:.1f}")

    with tab3:
        st.markdown("### 📈 Performance Analysis")

        # Load recent performance data
        st.info(
            "🚧 Performance tracking will show your team's points progression, rank changes, and key metrics over time."
        )

        # Placeholder for performance charts
        st.markdown("#### 📊 Recent Gameweek Performance")
        st.write("- Points progression chart")
        st.write("- Rank movement tracker")
        st.write("- Captain performance analysis")
        st.write("- Transfer efficiency metrics")

    with tab4:
        st.markdown("### 🔄 Transfer Analysis")

        st.info(
            "🚧 Transfer analysis will show your transfer history, efficiency, and suggested moves."
        )

        # Transfer suggestions placeholder
        st.markdown("#### 💡 Transfer Suggestions")
        st.write("- Players to consider transferring out")
        st.write("- High-value transfer targets")
        st.write("- Optimal transfer timing")
        st.write("- Captain recommendations")


def render_league_analysis():
    """Render league analysis and predictions."""
    st.header("🏆 League Analysis & Predictions")

    # League ID input
    league_id_input = st.text_input(
        "🆔 Enter League ID",
        placeholder="e.g., 314",
        help="Find league ID in the URL when viewing a league",
    )

    if not league_id_input:
        st.info(
            "👆 Enter a League ID to analyze league standings and make predictions!"
        )

        # Demo section
        st.markdown("---")
        st.markdown("### 🎯 League Analysis Features")

        feature_col1, feature_col2, feature_col3 = st.columns(3)

        with feature_col1:
            st.markdown(
                """
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h4>Current Standings</h4>
                    <p>View detailed league table with ranks, points, and recent form</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with feature_col2:
            st.markdown(
                """
                <div class="feature-card">
                    <div class="feature-icon">🔮</div>
                    <h4>Predictions</h4>
                    <p>AI-powered predictions for final league standings based on current form</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with feature_col3:
            st.markdown(
                """
                <div class="feature-card">
                    <div class="feature-icon">👥</div>
                    <h4>Head-to-Head</h4>
                    <p>Compare teams directly and track historical matchups</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        return

    try:
        league_id = int(league_id_input)
    except ValueError:
        st.error("❌ Please enter a valid numeric League ID")
        return

    # Load league data
    with st.spinner("🔄 Loading league data..."):
        try:
            with FPLClient() as client:
                league_data = client.get_league_standings(league_id)
        except Exception as e:
            st.error(f"❌ Could not load league data: {str(e)}")
            return

    if not league_data or "standings" not in league_data:
        st.error("❌ Invalid league ID or no data available")
        return

    league_info = league_data.get("league", {})
    standings = league_data.get("standings", {}).get("results", [])

    # League header
    st.success(
        f"✅ League: **{league_info.get('name', 'Unknown League')}** ({len(standings)} teams)"
    )

    # League analysis tabs
    tab1, tab2, tab3 = st.tabs(
        ["📊 Current Standings", "🔮 Predictions", "⚔️ Head-to-Head"]
    )

    with tab1:
        st.markdown("### 📊 Current League Standings")

        if standings:
            # Create standings table
            standings_data = []
            for entry in standings[:20]:  # Top 20
                standings_data.append(
                    {
                        "Rank": entry.get("rank", 0),
                        "Team": entry.get("entry_name", ""),
                        "Manager": entry.get("player_name", ""),
                        "GW Points": entry.get("event_total", 0),
                        "Total Points": f"{entry.get('total', 0):,}",
                        "Last Rank": entry.get("last_rank", 0),
                        "Change": (
                            entry.get("rank", 0) - entry.get("last_rank", 0)
                            if entry.get("last_rank")
                            else 0
                        ),
                    }
                )

            df = pd.DataFrame(standings_data)

            # Add rank change indicators
            def format_change(change):
                if change > 0:
                    return f"📈 +{change}"
                elif change < 0:
                    return f"📉 {change}"
                else:
                    return "➡️ 0"

            if not df.empty:
                df["Rank Change"] = df["Change"].apply(format_change)
                df = df.drop("Change", axis=1)

                st.dataframe(df, use_container_width=True, hide_index=True)

            # League stats
            st.markdown("#### 📈 League Statistics")

            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

            with stat_col1:
                avg_points = sum(s.get("total", 0) for s in standings) / len(standings)
                st.markdown(
                    create_metric_card(
                        "Average Points", f"{avg_points:,.0f}", "League average", "📊"
                    ),
                    unsafe_allow_html=True,
                )

            with stat_col2:
                leader_points = standings[0].get("total", 0) if standings else 0
                st.markdown(
                    create_metric_card(
                        "Leader Points",
                        f"{leader_points:,}",
                        standings[0].get("entry_name", "") if standings else "",
                        "🏆",
                    ),
                    unsafe_allow_html=True,
                )

            with stat_col3:
                gw_high = max((s.get("event_total", 0) for s in standings), default=0)
                st.markdown(
                    create_metric_card(
                        "GW High Score", f"{gw_high}", "This gameweek", "🔥"
                    ),
                    unsafe_allow_html=True,
                )

            with stat_col4:
                point_gap = (
                    leader_points - standings[-1].get("total", 0)
                    if len(standings) > 1
                    else 0
                )
                st.markdown(
                    create_metric_card(
                        "Leader Gap", f"{point_gap:,}", "First to last", "📏"
                    ),
                    unsafe_allow_html=True,
                )

    with tab2:
        st.markdown("### 🔮 League Predictions")

        # Prediction controls
        col1, col2 = st.columns([1, 1])

        with col1:
            target_gameweek = st.selectbox(
                "Predict standings for Gameweek:",
                options=[25, 30, 35, 38],  # Common prediction targets
                index=3,
                help="Select which gameweek to predict final standings for",
            )

        with col2:
            if st.button("🔮 Generate Predictions", type="primary"):
                with st.spinner("🤖 Generating predictions..."):
                    try:
                        predictions = predict_league_standings(
                            FPLClient(), league_id, target_gameweek
                        )

                        if "error" in predictions:
                            st.error(f"❌ {predictions['error']}")
                        else:
                            st.success("✅ Predictions generated successfully!")

                            # Display predictions
                            pred_data = []
                            for pred in predictions["predictions"][:10]:
                                pred_data.append(
                                    {
                                        "Predicted Rank": pred["predicted_rank"],
                                        "Team": pred["entry_name"],
                                        "Manager": pred["player_name"],
                                        "Current Points": f"{pred['current_total']:,}",
                                        "Predicted Total": f"{pred['predicted_total']:,}",
                                        "Expected Gain": f"+{pred['projected_gain']:.0f}",
                                        "Rank Change": (
                                            f"{pred['rank_change']:+d}"
                                            if pred["rank_change"] != 0
                                            else "0"
                                        ),
                                        "Form": pred["form_trend"].title(),
                                    }
                                )

                            pred_df = pd.DataFrame(pred_data)
                            st.dataframe(
                                pred_df, use_container_width=True, hide_index=True
                            )

                            # Prediction insights
                            summary = predictions.get("summary", {})
                            if summary:
                                st.markdown("#### 🎯 Prediction Insights")

                                insight_col1, insight_col2 = st.columns(2)

                                with insight_col1:
                                    biggest_climber = summary.get("biggest_climber")
                                    if biggest_climber:
                                        st.success(
                                            f"📈 **Biggest Climber**: {biggest_climber['player_name']} (+{biggest_climber['rank_change']} positions)"
                                        )

                                with insight_col2:
                                    biggest_faller = summary.get("biggest_faller")
                                    if biggest_faller:
                                        st.error(
                                            f"📉 **Biggest Faller**: {biggest_faller['player_name']} ({biggest_faller['rank_change']} positions)"
                                        )

                    except Exception as e:
                        st.error(f"❌ Prediction failed: {str(e)}")

        st.info(
            "💡 Predictions are based on recent form, team strength, and fixture difficulty. Results may vary!"
        )

    with tab3:
        st.markdown("### ⚔️ Head-to-Head Analysis")

        st.info("🚧 Head-to-head records and team comparisons coming soon!")

        # Placeholder for H2H features
        st.markdown("#### 🔜 Coming Features:")
        st.write("- Compare any two teams in the league")
        st.write("- Historical head-to-head records")
        st.write("- Team strength analysis")
        st.write("- Transfer strategies comparison")


def main():
    """Main application entry point with enhanced features."""
    # Render main header
    render_main_header()

    # Main navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "🏠 Dashboard",
            "👥 My Team",
            "🏆 Leagues",
            "🔍 Players",
            "📊 Analytics",
            "🔮 Projections",
            "📋 Watchlist",
        ]
    )

    with tab1:
        # Enhanced dashboard with new features
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
                    <h4>League Predictions</h4>
                    <p>Analyze league standings and predict final positions using AI</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with quick_col3:
            st.markdown(
                """
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h4>Advanced Analytics</h4>
                    <p>Effective ownership, zonal analysis, and custom gameweek projections</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Data overview
        st.markdown("---")
        st.subheader("📊 FPL Data Overview")

        players_result = load_players_data()
        teams_result = load_teams_data()

        if (
            players_result["status"] == "success"
            and teams_result["status"] == "success"
        ):
            players = players_result["data"]
            teams = teams_result["data"]

            overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

            with overview_col1:
                st.markdown(
                    create_metric_card(
                        "Total Players", str(len(players)), f"{len(teams)} teams", "⚽"
                    ),
                    unsafe_allow_html=True,
                )

            with overview_col2:
                avg_cost = (
                    sum(p.get("now_cost", 0) for p in players) / (10.0 * len(players))
                    if players
                    else 0
                )
                st.markdown(
                    create_metric_card(
                        "Avg Player Cost", f"£{avg_cost:.1f}m", "Market average", "💰"
                    ),
                    unsafe_allow_html=True,
                )

            with overview_col3:
                top_scorer = (
                    max(players, key=lambda x: x.get("total_points", 0))
                    if players
                    else None
                )
                top_points = top_scorer.get("total_points", 0) if top_scorer else 0
                top_name = format_player_name(top_scorer) if top_scorer else "N/A"
                st.markdown(
                    create_metric_card(
                        "Top Scorer", f"{top_points} pts", top_name, "🏆"
                    ),
                    unsafe_allow_html=True,
                )

            with overview_col4:
                timestamp = players_result.get("timestamp", datetime.now())
                time_diff = datetime.now() - timestamp
                update_text = f"{int(time_diff.total_seconds() / 60)} min ago"
                st.markdown(
                    create_metric_card(
                        "Data Updated", update_text, "Real-time FPL data", "🔄"
                    ),
                    unsafe_allow_html=True,
                )

    with tab2:
        render_my_team_advanced()

    with tab3:
        render_league_analysis()

    with tab4:
        st.header("🔍 Advanced Player Explorer")
        st.info(
            "🚧 Enhanced player explorer with advanced filtering, comparison tools, and watchlist management coming soon!"
        )

    with tab5:
        st.header("📊 Advanced Analytics")
        st.info(
            "🚧 Effective ownership, zonal analysis, and advanced metrics coming soon!"
        )

    with tab6:
        st.header("🔮 Custom Projections")
        st.info(
            "🚧 Custom gameweek range projections and scenario planning coming soon!"
        )

    with tab7:
        st.header("📋 Player Watchlist")
        st.info("🚧 Player watchlist, target lists, and avoid lists coming soon!")

    # Enhanced sidebar
    render_enhanced_sidebar()


def render_enhanced_sidebar():
    """Render enhanced sidebar with new features."""
    with st.sidebar:
        st.markdown("### ⚙️ FPL Toolkit Pro")

        # Quick stats
        st.markdown("#### 📊 System Status")

        players_result = load_players_data()
        teams_result = load_teams_data()

        # Status indicators with enhanced styling
        if players_result["status"] == "success":
            st.markdown(
                '<span class="status-indicator status-live"></span>✅ Players data loaded',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="status-indicator status-error"></span>❌ Players data failed',
                unsafe_allow_html=True,
            )

        if teams_result["status"] == "success":
            st.markdown(
                '<span class="status-indicator status-live"></span>✅ Teams data loaded',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="status-indicator status-error"></span>❌ Teams data failed',
                unsafe_allow_html=True,
            )

        # Quick actions
        st.markdown("#### ⚡ Quick Actions")

        if st.button("🔄 Refresh All Data", help="Clear cache and reload all data"):
            st.cache_data.clear()
            st.success("✅ Data refreshed!")
            st.rerun()

        # Feature roadmap
        st.markdown("#### 🚀 New Features")
        st.markdown(
            """
        - ✅ Football pitch lineup view
        - ✅ League predictions
        - 🚧 Effective ownership analysis
        - 🚧 Zonal strength/weakness
        - 🚧 Custom projections
        - 🚧 Player watchlists
        - 🚧 Transfer optimization
        - 🚧 Mobile app integration
        """
        )

        # App info
        st.markdown("#### ℹ️ About")
        st.markdown(
            """
        **FPL Toolkit Pro - Advanced** brings professional-grade FPL management tools to your fingertips.
        
        **New Features:**
        - 👥 Team management with pitch view
        - 🏆 League analysis & predictions
        - 📊 Advanced analytics dashboard
        - 🔮 Custom projections engine
        """
        )

        st.markdown("---")
        st.markdown("**Version**: 3.0.0 Advanced  \n**Updated**: August 2025")


if __name__ == "__main__":
    main()
