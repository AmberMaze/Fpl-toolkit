"""Enhanced FPL Toolkit with Advanced Features - Your Complete Fantasy Premier League Management System.

🌟 FIXED FEATURES:
- 👥 My Team Management with Football Pitch Lineup
- 🏆 League Analysis with User Leagues Detection
- 📊 Team Builder for Pre-Season
- 🔧 Working Tab Navigation
- 💡 Better Error Handling
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
    page_title="FPL Toolkit Pro - Fixed",
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
        <h1>⚽ FPL Toolkit Pro - Fixed</h1>
        <p>🚀 Complete Fantasy Premier League Management System | Season 2024/25</p>
        <p style="font-size: 1rem; margin-top: 1rem; opacity: 0.9;">
            ✨ Fixed: Working Tabs | Team Builder | League Detection | Better Error Handling
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
    # Render main header
    render_main_header()

    # Navigation using selectbox instead of tabs (fixes tab navigation issue)
    st.sidebar.title("🧭 Navigation")
    selected_page = st.sidebar.selectbox(
        "Choose a section:",
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

    # Render selected page
    if selected_page == "🏠 Dashboard":
        render_dashboard()
    elif selected_page == "👥 My Team":
        render_my_team_advanced()
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
