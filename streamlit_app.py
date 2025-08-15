"""Enhanced FPL Toolkit Dashboard - Your Fantasy Premier League Command Center.

Inspired by the best features from top FPL websites:
- Fantasy Football Scout (expert analysis, community insights)
- FPL Review (projections, optimization)
- FPL Form (predictions, fixture difficulty)
- FPL.page (real-time dashboard)
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

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

# Configure page with modern styling
st.set_page_config(
    page_title="FPL Toolkit Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/AmberMaze/Fpl-toolkit",
        "Report a bug": "https://github.com/AmberMaze/Fpl-toolkit/issues",
        "About": "FPL Toolkit Pro - Your complete Fantasy Premier League analysis platform!",
    },
)

# Enhanced CSS for professional styling
st.markdown(
    """
<style>
    /* Modern styling inspired by top FPL sites */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main .block-container {
        font-family: 'Inter', sans-serif;
        padding-top: 2rem;
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
        text-align: center;
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
    
    /* Enhanced metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        margin: 0.5rem 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        text-align: center;
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
    
    /* Position badges */
    .position-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-right: 0.5rem;
    }
    
    .position-gk { background: #3498db; color: white; }
    .position-def { background: #27ae60; color: white; }
    .position-mid { background: #f39c12; color: white; }
    .position-fwd { background: #e74c3c; color: white; }
    
    /* Difficulty indicators */
    .difficulty-easy { color: #27ae60; font-weight: 600; }
    .difficulty-medium { color: #f39c12; font-weight: 600; }
    .difficulty-hard { color: #e74c3c; font-weight: 600; }
    
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
    
    /* Enhanced tables */
    .dataframe {
        border: none !important;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .main-header {
            padding: 1.5rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-card {
            margin: 0.25rem 0;
        }
    }
    
    /* Tab styling */
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


# Configure page
st.set_page_config(
    page_title="FPL Toolkit",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for mobile responsiveness
st.markdown(
    """
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 0.9rem;
            padding: 0.5rem;
        }
    }
    
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


# =====================================================
# PLOTLY VISUALIZATION FUNCTIONS
# =====================================================


def create_form_chart(players_data: List[dict], limit: int = 10) -> go.Figure:
    """Create an interactive form chart showing player form trends."""
    try:
        # Get top players by form
        top_players = sorted(
            players_data, key=lambda x: float(x.get("form", "0") or "0"), reverse=True
        )[:limit]

        fig = go.Figure()

        for player in top_players:
            form = float(player.get("form", "0") or "0")
            points = player.get("total_points", 0)
            cost = player.get("now_cost", 0) / 10.0

            fig.add_trace(
                go.Scatter(
                    x=[cost],
                    y=[form],
                    mode="markers+text",
                    marker=dict(
                        size=max(
                            points / 10, 8
                        ),  # Size based on total points, minimum 8
                        color=form,
                        colorscale="RdYlGn",
                        colorbar=dict(title="Form"),
                        line=dict(width=2, color="DarkSlateGrey"),
                    ),
                    text=format_player_name(player),
                    textposition="top center",
                    name=format_player_name(player),
                    hovertemplate="<b>%{text}</b><br>"
                    + "Cost: £%{x:.1f}m<br>"
                    + "Form: %{y:.1f}<br>"
                    + f"Points: {points}<br>"
                    + "<extra></extra>",
                )
            )

        fig.update_layout(
            title="Player Form vs Cost Analysis",
            xaxis_title="Cost (£m)",
            yaxis_title="Form",
            template="plotly_white",
            height=500,
            showlegend=False,
        )

        return fig

    except Exception as e:
        st.error(f"Error creating form chart: {str(e)}")
        return go.Figure()


def create_position_distribution_chart(players_data: List[dict]) -> go.Figure:
    """Create a pie chart showing player distribution by position."""
    try:
        position_counts = {"GK": 0, "DEF": 0, "MID": 0, "FWD": 0}
        position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}

        for player in players_data:
            pos = position_map.get(player.get("element_type", 1), "GK")
            position_counts[pos] += 1

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=list(position_counts.keys()),
                    values=list(position_counts.values()),
                    hole=0.3,
                    marker_colors=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"],
                )
            ]
        )

        fig.update_layout(
            title="Player Distribution by Position", template="plotly_white", height=400
        )

        return fig

    except Exception as e:
        st.error(f"Error creating position chart: {str(e)}")
        return go.Figure()


def create_value_analysis_chart(players_data: List[dict], limit: int = 20) -> go.Figure:
    """Create a scatter plot analyzing player value (points per million)."""
    try:
        # Calculate value for each player
        value_players = []
        for player in players_data:
            cost = player.get("now_cost", 0) / 10.0
            points = player.get("total_points", 0)
            if cost > 0 and points > 0:
                value = points / cost
                value_players.append(
                    {"player": player, "value": value, "cost": cost, "points": points}
                )

        # Sort by value and take top players
        value_players.sort(key=lambda x: x["value"], reverse=True)
        top_value = value_players[:limit]

        fig = go.Figure()

        position_colors = {1: "#FF6B6B", 2: "#4ECDC4", 3: "#45B7D1", 4: "#96CEB4"}
        position_names = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}

        for pos_id, color in position_colors.items():
            pos_players = [
                p for p in top_value if p["player"].get("element_type") == pos_id
            ]

            if pos_players:
                fig.add_trace(
                    go.Scatter(
                        x=[p["cost"] for p in pos_players],
                        y=[p["value"] for p in pos_players],
                        mode="markers+text",
                        marker=dict(
                            size=[max(p["points"] / 5, 8) for p in pos_players],
                            color=color,
                            line=dict(width=2, color="white"),
                            opacity=0.8,
                        ),
                        text=[format_player_name(p["player"]) for p in pos_players],
                        textposition="top center",
                        name=position_names[pos_id],
                        hovertemplate="<b>%{text}</b><br>"
                        + "Cost: £%{x:.1f}m<br>"
                        + "Value: %{y:.1f} pts/£m<br>"
                        + "<extra></extra>",
                    )
                )

        fig.update_layout(
            title="Player Value Analysis (Points per Million)",
            xaxis_title="Cost (£m)",
            yaxis_title="Value (Points per £m)",
            template="plotly_white",
            height=600,
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        )

        return fig

    except Exception as e:
        st.error(f"Error creating value chart: {str(e)}")
        return go.Figure()


def create_team_performance_chart(
    teams_data: List[dict], players_data: List[dict]
) -> go.Figure:
    """Create a bar chart showing team performance metrics."""
    try:
        team_stats = {}

        # Initialize team stats
        for team in teams_data:
            team_stats[team["id"]] = {
                "name": team["name"],
                "total_points": 0,
                "player_count": 0,
                "avg_cost": 0,
                "total_cost": 0,
            }

        # Aggregate player stats by team
        for player in players_data:
            team_id = player.get("team")
            if team_id in team_stats:
                team_stats[team_id]["total_points"] += player.get("total_points", 0)
                team_stats[team_id]["player_count"] += 1
                team_stats[team_id]["total_cost"] += player.get("now_cost", 0) / 10.0

        # Calculate averages
        for team_id in team_stats:
            if team_stats[team_id]["player_count"] > 0:
                team_stats[team_id]["avg_cost"] = (
                    team_stats[team_id]["total_cost"]
                    / team_stats[team_id]["player_count"]
                )

        # Sort teams by total points
        sorted_teams = sorted(
            team_stats.values(), key=lambda x: x["total_points"], reverse=True
        )[:10]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=[team["name"] for team in sorted_teams],
                y=[team["total_points"] for team in sorted_teams],
                marker_color="#667eea",
                text=[f"{team['total_points']}" for team in sorted_teams],
                textposition="outside",
            )
        )

        fig.update_layout(
            title="Top 10 Teams by Total Player Points",
            xaxis_title="Team",
            yaxis_title="Total Points",
            template="plotly_white",
            height=500,
            xaxis_tickangle=-45,
        )

        return fig

    except Exception as e:
        st.error(f"Error creating team performance chart: {str(e)}")
        return go.Figure()


# =====================================================
# DATA LOADING & UTILITY FUNCTIONS
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


def render_main_header():
    """Render the main dashboard header."""
    st.markdown(
        """
    <div class="main-header">
        <h1>⚽ FPL Toolkit Pro</h1>
        <p>Advanced Fantasy Premier League Analysis & Decision Support | Season 2024/25</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def create_metric_card(title: str, value: str, subtitle: str = "") -> str:
    """Create HTML for a metric card."""
    subtitle_html = (
        f'<p style="margin: 0; color: #7f8c8d; font-size: 0.8rem;">{subtitle}</p>'
        if subtitle
        else ""
    )

    return f"""
    <div class="metric-card">
        <p class="metric-label">{title}</p>
        <p class="metric-value">{value}</p>
        {subtitle_html}
    </div>
    """


def display_player_card(
    player: Dict[str, Any], team_name: str = "Unknown", show_detailed: bool = False
):
    """Display a player card with key information."""
    position = get_position_name(player.get("element_type", 1))
    position_class = get_position_badge_class(position)

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(
            f"""
        <div>
            <strong style="font-size: 1.1rem;">{format_player_name(player)}</strong><br>
            <span class="{position_class} position-badge">{position}</span>
            <span style="margin-left: 0.5rem; color: #7f8c8d;">{team_name}</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        cost = player.get("now_cost", 0) / 10.0
        st.metric("Cost", format_currency(cost))

    with col3:
        points = player.get("total_points", 0)
        st.metric("Points", f"{points}")

    if show_detailed:
        col4, col5, col6 = st.columns(3)

        with col4:
            form = float(player.get("form", "0") or "0")
            st.metric("Form", f"{form:.1f}")

        with col5:
            ppg = float(player.get("points_per_game", "0") or "0")
            st.metric("PPG", f"{ppg:.1f}")

        with col6:
            ownership = float(player.get("selected_by_percent", "0") or "0")
            st.metric("Owned", f"{ownership:.1f}%")


def render_dashboard_overview():
    """Render the main dashboard overview with key metrics and interactive charts."""
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
                    "Average Cost", format_currency(avg_cost), "Current market average"
                ),
                unsafe_allow_html=True,
            )

        with col3:
            if top_scorer:
                st.markdown(
                    create_metric_card(
                        "Top Scorer",
                        format_player_name(top_scorer),
                        f"{top_scorer.get('total_points', 0)} points",
                    ),
                    unsafe_allow_html=True,
                )

        with col4:
            if most_expensive:
                st.markdown(
                    create_metric_card(
                        "Most Expensive",
                        format_player_name(most_expensive),
                        format_currency(most_expensive.get("now_cost", 0) / 10.0),
                    ),
                    unsafe_allow_html=True,
                )

        # Interactive Charts Section
        st.markdown("---")
        st.subheader("📈 Interactive Analytics")

        # Chart tabs
        chart_tab1, chart_tab2, chart_tab3, chart_tab4 = st.tabs(
            [
                "🎯 Form Analysis",
                "📊 Position Split",
                "💎 Value Analysis",
                "🏆 Team Performance",
            ]
        )

        with chart_tab1:
            st.markdown("#### Top Players by Form vs Cost")
            try:
                form_chart = create_form_chart(players, limit=15)
                st.plotly_chart(form_chart, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading form chart: {str(e)}")
                st.info("Form analysis chart will show player performance trends.")

        with chart_tab2:
            st.markdown("#### Player Distribution by Position")
            try:
                position_chart = create_position_distribution_chart(players)
                col_chart, col_info = st.columns([2, 1])

                with col_chart:
                    st.plotly_chart(position_chart, use_container_width=True)

                with col_info:
                    st.markdown("**Position Breakdown:**")
                    position_counts = {"GK": 0, "DEF": 0, "MID": 0, "FWD": 0}
                    position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}

                    for player in players:
                        pos = position_map.get(player.get("element_type", 1), "GK")
                        position_counts[pos] += 1

                    for pos, count in position_counts.items():
                        percentage = (
                            (count / total_players) * 100 if total_players > 0 else 0
                        )
                        st.write(f"**{pos}**: {count} ({percentage:.1f}%)")

            except Exception as e:
                st.error(f"Error loading position chart: {str(e)}")

        with chart_tab3:
            st.markdown("#### Best Value Players (Points per Million)")
            try:
                value_chart = create_value_analysis_chart(players, limit=25)
                st.plotly_chart(value_chart, use_container_width=True)

                st.markdown(
                    "**💡 Tip:** Look for players in the top-right area for high value and reasonable cost."
                )

            except Exception as e:
                st.error(f"Error loading value chart: {str(e)}")

        with chart_tab4:
            st.markdown("#### Team Performance Analysis")
            try:
                team_chart = create_team_performance_chart(teams, players)
                st.plotly_chart(team_chart, use_container_width=True)

                # Additional team insights
                st.markdown("**📋 Team Insights:**")
                team_stats = {}
                for team in teams:
                    team_stats[team["id"]] = {
                        "name": team["name"],
                        "total_points": 0,
                        "player_count": 0,
                    }

                for player in players:
                    team_id = player.get("team")
                    if team_id in team_stats:
                        team_stats[team_id]["total_points"] += player.get(
                            "total_points", 0
                        )
                        team_stats[team_id]["player_count"] += 1

                best_team = max(team_stats.values(), key=lambda x: x["total_points"])
                st.success(
                    f"🏆 **Best Performing Team**: {best_team['name']} ({best_team['total_points']} total points)"
                )

            except Exception as e:
                st.error(f"Error loading team chart: {str(e)}")

    else:
        st.error("Failed to load data for dashboard overview")


def render_my_team_section():
    """Render My Team section for lineup management."""
    st.header("👥 My Team & Lineup")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Team Builder")

        # Team input
        team_input = st.text_area(
            "Enter your team player IDs (comma-separated)",
            placeholder="e.g., 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15",
            height=100,
            help="Enter exactly 15 player IDs. Find IDs in the Players Explorer.",
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
                    display_team_formation(player_ids)
                elif len(player_ids) < 15:
                    st.warning(f"⚠️ Need {15 - len(player_ids)} more players")
                else:
                    st.error("❌ Too many players! Maximum 15 allowed.")

            except ValueError:
                st.error("❌ Invalid format. Please enter numbers only.")

    with col2:
        st.subheader("Team Analysis")

        # Quick team stats
        st.markdown(
            create_metric_card("Team Value", "£100.0m", "Budget used"),
            unsafe_allow_html=True,
        )
        st.markdown(
            create_metric_card("Free Transfers", "1", "Available"),
            unsafe_allow_html=True,
        )
        st.markdown(
            create_metric_card("Team Score", "85/100", "Form & fixtures"),
            unsafe_allow_html=True,
        )


def display_team_formation(player_ids: list):
    """Display team in formation view."""
    players_result = load_players_data()
    if players_result["status"] != "success":
        st.error("Cannot load player data")
        return

    players = players_result["data"]
    player_lookup = {p["id"]: p for p in players}

    # Get valid players
    team_players = [player_lookup[pid] for pid in player_ids if pid in player_lookup]

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
    st.markdown("#### Formation View")

    for pos_name, pos_players in positions.items():
        if pos_players:
            st.markdown(f"**{pos_name} ({len(pos_players)})**")

            if len(pos_players) <= 5:  # Display in columns for reasonable numbers
                cols = st.columns(len(pos_players))

                for i, player in enumerate(pos_players):
                    with cols[i]:
                        cost = player.get("now_cost", 0) / 10.0
                        points = player.get("total_points", 0)
                        form = float(player.get("form", "0") or "0")

                        st.markdown(
                            f"""
                        <div style="text-align: center; padding: 0.75rem; border: 1px solid #ddd; border-radius: 8px; margin: 0.25rem; background: white;">
                            <div style="font-weight: 600; font-size: 0.9rem;">{format_player_name(player)}</div>
                            <div style="font-size: 0.8rem; color: #666; margin-top: 0.25rem;">
                                {format_currency(cost)} | {points}pts | {form:.1f}
                            </div>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )
            else:
                # For many players, show as list
                for player in pos_players:
                    cost = player.get("now_cost", 0) / 10.0
                    points = player.get("total_points", 0)
                    st.write(
                        f"• {format_player_name(player)} - {format_currency(cost)} - {points}pts"
                    )


# =====================================================
# MAIN APPLICATION FUNCTIONS
# =====================================================


def main():
    """Main application entry point with modern FPL dashboard."""
    # Render main header
    render_main_header()

    # Main navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "🏠 Dashboard",
            "👥 My Team",
            "🔍 Players Explorer",
            "🔄 Transfer Planner",
            "📅 Fixture Analysis",
            "📊 Statistics Hub",
        ]
    )

    with tab1:
        render_dashboard_overview()

        # Quick insights section
        st.markdown("---")
        st.subheader("🔥 Quick Insights")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📈 Top Form Players")
            try:
                players_result = load_players_data()
                if players_result["status"] == "success":
                    players = players_result["data"]
                    # Sort by form and display top 5
                    top_form = sorted(
                        players,
                        key=lambda x: float(x.get("form", "0") or "0"),
                        reverse=True,
                    )[:5]

                    for i, player in enumerate(top_form, 1):
                        form = float(player.get("form", "0") or "0")
                        cost = player.get("now_cost", 0) / 10.0
                        st.write(
                            f"{i}. **{format_player_name(player)}** - {form:.1f} form - {format_currency(cost)}"
                        )
                else:
                    st.error("Cannot load player data")
            except Exception as e:
                st.error(f"Error loading top form players: {str(e)}")

        with col2:
            st.markdown("#### 🎯 Best Value Players")
            try:
                players_result = load_players_data()
                if players_result["status"] == "success":
                    players = players_result["data"]
                    # Calculate points per million and display top 5
                    value_players = []
                    for player in players:
                        cost = player.get("now_cost", 0) / 10.0
                        points = player.get("total_points", 0)
                        if cost > 0:
                            value_players.append((player, points / cost))

                    value_players.sort(key=lambda x: x[1], reverse=True)

                    for i, (player, value) in enumerate(value_players[:5], 1):
                        cost = player.get("now_cost", 0) / 10.0
                        points = player.get("total_points", 0)
                        st.write(
                            f"{i}. **{format_player_name(player)}** - {value:.1f} pts/£m - {points}pts"
                        )
                else:
                    st.error("Cannot load player data")
            except Exception as e:
                st.error(f"Error loading value players: {str(e)}")

    with tab2:
        render_my_team_section()

    with tab3:
        render_players_explorer()

    with tab4:
        render_transfer_planner()

    with tab5:
        render_fixture_analysis()

    with tab6:
        render_statistics_hub()

    # Enhanced sidebar
    render_enhanced_sidebar()


def render_players_explorer():
    """Enhanced players explorer with advanced filtering."""
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
    st.subheader("🎛️ Smart Filters")

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
    col5, col6 = st.columns(2)

    with col5:
        team_filter = st.multiselect(
            "Teams (leave empty for all)",
            options=[team["name"] for team in teams],
            default=[],
        )

    with col6:
        search_term = st.text_input(
            "Search Player Name", placeholder="Type player name..."
        )

    # Sort options
    sort_by = st.selectbox(
        "Sort by",
        [
            "Total Points",
            "Form",
            "Points per Game",
            "Cost",
            "Ownership %",
            "Value (pts/£m)",
        ],
        index=0,
    )

    # Apply filters
    filtered_players = filter_players_advanced(
        players,
        team_lookup,
        position_filter,
        cost_range,
        points_range,
        form_threshold,
        team_filter,
        search_term,
    )

    # Sort players
    sort_key_map = {
        "Total Points": lambda x: x.get("total_points", 0),
        "Form": lambda x: float(x.get("form", "0") or "0"),
        "Points per Game": lambda x: float(x.get("points_per_game", "0") or "0"),
        "Cost": lambda x: x.get("now_cost", 0),
        "Ownership %": lambda x: float(x.get("selected_by_percent", "0") or "0"),
        "Value (pts/£m)": lambda x: x.get("total_points", 0)
        / max(x.get("now_cost", 1) / 10.0, 0.1),
    }

    filtered_players.sort(key=sort_key_map[sort_by], reverse=True)

    # Display results
    st.subheader(f"📋 Results ({len(filtered_players)} players)")

    if filtered_players:
        # Display options
        view_mode = st.radio(
            "View Mode",
            ["Detailed Cards", "Compact Table", "Quick Stats"],
            horizontal=True,
        )

        if view_mode == "Detailed Cards":
            # Card view with enhanced styling
            for player in filtered_players[:20]:  # Limit for performance
                team_name = team_lookup.get(player.get("team"), "Unknown")

                with st.expander(
                    f"{format_player_name(player)} - {team_name}", expanded=False
                ):
                    display_player_card(player, team_name, show_detailed=True)

                    # Additional action buttons
                    col_btn1, col_btn2, col_btn3 = st.columns(3)

                    with col_btn1:
                        if st.button("Add to Compare", key=f"compare_{player['id']}"):
                            if "comparison_list" not in st.session_state:
                                st.session_state.comparison_list = []
                            if player["id"] not in st.session_state.comparison_list:
                                st.session_state.comparison_list.append(player["id"])
                                st.success("Added to comparison!")

                    with col_btn2:
                        if st.button("View Details", key=f"details_{player['id']}"):
                            st.session_state.selected_player = player["id"]
                            st.info("Player details coming soon!")

                    with col_btn3:
                        if st.button("Transfer Target", key=f"transfer_{player['id']}"):
                            st.info("Transfer analysis coming soon!")

        elif view_mode == "Compact Table":
            # Enhanced table view
            table_data = []
            for player in filtered_players[:50]:
                cost = player.get("now_cost", 0) / 10.0
                value = player.get("total_points", 0) / max(cost, 0.1)

                table_data.append(
                    {
                        "Player": format_player_name(player),
                        "Position": get_position_name(player.get("element_type", 1)),
                        "Team": team_lookup.get(player.get("team"), "Unknown"),
                        "Cost": format_currency(cost),
                        "Points": player.get("total_points", 0),
                        "Form": f"{float(player.get('form', '0') or '0'):.1f}",
                        "PPG": f"{float(player.get('points_per_game', '0') or '0'):.1f}",
                        "Owned %": f"{float(player.get('selected_by_percent', '0') or '0'):.1f}%",
                        "Value": f"{value:.1f}",
                    }
                )

            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True, height=600)

        else:  # Quick Stats
            # Quick stats overview
            st.markdown("#### Top 10 Players")

            for i, player in enumerate(filtered_players[:10], 1):
                cost = player.get("now_cost", 0) / 10.0
                points = player.get("total_points", 0)
                form = float(player.get("form", "0") or "0")
                team_name = team_lookup.get(player.get("team"), "Unknown")
                position = get_position_name(player.get("element_type", 1))

                st.markdown(
                    f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; border: 1px solid #eee; border-radius: 8px; margin: 0.5rem 0; background: white;">
                    <div>
                        <strong>{i}. {format_player_name(player)}</strong><br>
                        <small>{position} | {team_name}</small>
                    </div>
                    <div style="text-align: right;">
                        <div><strong>{format_currency(cost)}</strong> | <strong>{points}pts</strong></div>
                        <div><small>Form: {form:.1f}</small></div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    else:
        st.info("No players match your current filters. Try adjusting the criteria.")


def filter_players_advanced(
    players: list,
    team_lookup: dict,
    position_filter: str,
    cost_range: tuple,
    points_range: tuple,
    form_threshold: float,
    team_filter: list,
    search_term: str,
) -> list:
    """Apply advanced filters to player list."""
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

        # Search filter
        if search_term:
            player_name = format_player_name(player).lower()
            if search_term.lower() not in player_name:
                continue

        filtered.append(player)

    return filtered


def render_transfer_planner():
    """Render enhanced transfer planner."""
    st.header("🔄 Transfer Planner")

    st.info("🚧 Enhanced transfer planning tools coming soon! This will include:")
    st.markdown(
        """
    - **Single & Double Transfer Analysis**: Compare potential transfers with projected points
    - **Wildcard Optimizer**: Build optimal teams within budget constraints  
    - **Transfer Timeline**: Plan transfers across multiple gameweeks
    - **Price Change Predictor**: Track player price movements
    - **Captain Analyzer**: Optimize captaincy choices based on fixtures
    """
    )

    # Basic transfer analysis
    st.subheader("Quick Transfer Analysis")

    col1, col2 = st.columns(2)

    with col1:
        player_out = st.text_input(
            "Player Out (ID)", placeholder="Enter player ID to transfer out"
        )

    with col2:
        player_in = st.text_input(
            "Player In (ID)", placeholder="Enter player ID to transfer in"
        )

    if player_out and player_in:
        if st.button("Analyze Transfer"):
            st.info(
                "Transfer analysis will compare projected points, fixtures, and value!"
            )


def render_fixture_analysis():
    """Render enhanced fixture analysis."""
    st.header("📅 Fixture Analysis")

    tab1, tab2, tab3 = st.tabs(
        ["Fixture Difficulty", "Team Schedules", "Blank/Double GWs"]
    )

    with tab1:
        st.subheader("🎯 Fixture Difficulty Rankings")

        analysis_period = st.selectbox(
            "Analysis Period", ["Next 3 GWs", "Next 5 GWs", "Next 8 GWs"], index=1
        )

        if st.button("Analyze Fixtures"):
            with st.spinner("Calculating fixture difficulty..."):
                try:
                    n_gameweeks = int(analysis_period.split()[1])
                    fixture_data = get_fixture_difficulty_rankings(next_n=n_gameweeks)

                    if fixture_data:
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("#### 🟢 Easiest Fixtures")
                            for i, team in enumerate(fixture_data[:8], 1):
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
                            hard_fixtures = fixture_data[-8:]
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

    with tab2:
        st.subheader("📋 Team Schedules")
        st.info("Detailed team fixture analysis coming soon!")

    with tab3:
        st.subheader("📅 Blank & Double Gameweeks")
        st.info(
            "BGW/DGW analysis will be available during the season when fixtures are confirmed."
        )


def render_statistics_hub():
    """Render enhanced statistics hub."""
    st.header("📊 Statistics Hub")

    tab1, tab2, tab3 = st.tabs(
        ["League Stats", "Player Comparisons", "Form & Projections"]
    )

    with tab1:
        st.subheader("🏆 League Statistics")

        players_result = load_players_data()
        if players_result["status"] == "success":
            players = players_result["data"]

            # Top performers by position
            st.markdown("#### Top Scorers by Position")

            positions = {"GK": 1, "DEF": 2, "MID": 3, "FWD": 4}

            cols = st.columns(4)

            for i, (pos_name, pos_id) in enumerate(positions.items()):
                pos_players = [p for p in players if p.get("element_type") == pos_id]
                if pos_players:
                    top_player = max(
                        pos_players, key=lambda x: x.get("total_points", 0)
                    )

                    with cols[i]:
                        points = top_player.get("total_points", 0)
                        cost = top_player.get("now_cost", 0) / 10.0

                        st.markdown(
                            create_metric_card(
                                f"Top {pos_name}",
                                format_player_name(top_player),
                                f"{points} pts | {format_currency(cost)}",
                            ),
                            unsafe_allow_html=True,
                        )

        else:
            st.error("Cannot load player statistics")

    with tab2:
        st.subheader("⚖️ Player Comparisons")

        # Check for comparison list
        if "comparison_list" not in st.session_state:
            st.session_state.comparison_list = []

        comparison_list = st.session_state.comparison_list

        if comparison_list:
            st.markdown(f"#### Comparing {len(comparison_list)} players")

            players_result = load_players_data()
            if players_result["status"] == "success":
                players = players_result["data"]
                player_lookup = {p["id"]: p for p in players}

                selected_players = [
                    player_lookup[pid]
                    for pid in comparison_list
                    if pid in player_lookup
                ]

                if selected_players:
                    # Display comparison
                    comparison_data = []
                    for player in selected_players:
                        cost = player.get("now_cost", 0) / 10.0
                        value = player.get("total_points", 0) / max(cost, 0.1)

                        comparison_data.append(
                            {
                                "Player": format_player_name(player),
                                "Position": get_position_name(
                                    player.get("element_type", 1)
                                ),
                                "Cost": format_currency(cost),
                                "Points": player.get("total_points", 0),
                                "Form": f"{float(player.get('form', '0') or '0'):.1f}",
                                "PPG": f"{float(player.get('points_per_game', '0') or '0'):.1f}",
                                "Owned %": f"{float(player.get('selected_by_percent', '0') or '0'):.1f}%",
                                "Value": f"{value:.1f}",
                            }
                        )

                    df = pd.DataFrame(comparison_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    if st.button("Clear Comparison List"):
                        st.session_state.comparison_list = []
                        st.rerun()

        else:
            st.info(
                "No players selected for comparison. Add players from the Players Explorer."
            )

    with tab3:
        st.subheader("📈 Form & Projections")

        players_result = load_players_data()
        if players_result["status"] == "success":
            players = players_result["data"]

            # Form trends chart
            st.markdown("#### Interactive Form Analysis")

            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                try:
                    form_chart = create_form_chart(players, limit=20)
                    st.plotly_chart(form_chart, use_container_width=True)
                except Exception as e:
                    st.error(f"Error creating form chart: {str(e)}")

            with col_chart2:
                try:
                    value_chart = create_value_analysis_chart(players, limit=15)
                    st.plotly_chart(value_chart, use_container_width=True)
                except Exception as e:
                    st.error(f"Error creating value chart: {str(e)}")

            # Form insights
            st.markdown("#### 🔥 Current Form Leaders")

            # Get top form players
            top_form_players = sorted(
                players, key=lambda x: float(x.get("form", "0") or "0"), reverse=True
            )[:10]

            form_cols = st.columns(5)

            for i, player in enumerate(top_form_players[:5]):
                with form_cols[i]:
                    form = float(player.get("form", "0") or "0")
                    cost = player.get("now_cost", 0) / 10.0
                    points = player.get("total_points", 0)

                    st.markdown(
                        create_metric_card(
                            f"#{i+1} Form",
                            f"{form:.1f}",
                            f"{format_player_name(player)} | {format_currency(cost)}",
                        ),
                        unsafe_allow_html=True,
                    )

            # Additional insights
            st.markdown("#### 📊 Form Analysis Insights")

            # Calculate form statistics
            all_forms = [
                float(p.get("form", "0") or "0") for p in players if p.get("form")
            ]
            avg_form = sum(all_forms) / len(all_forms) if all_forms else 0

            insight_col1, insight_col2, insight_col3 = st.columns(3)

            with insight_col1:
                st.info(f"**Average League Form**: {avg_form:.2f}")

            with insight_col2:
                hot_players = len([f for f in all_forms if f > 6.0])
                st.success(f"**Hot Form Players**: {hot_players} (6.0+ form)")

            with insight_col3:
                cold_players = len([f for f in all_forms if f < 3.0])
                st.warning(f"**Poor Form Players**: {cold_players} (sub-3.0 form)")

        else:
            st.error("Cannot load player data for form analysis")


def render_enhanced_sidebar():
    """Render enhanced sidebar with tools and information."""
    with st.sidebar:
        st.markdown("### ⚙️ FPL Toolkit Pro")

        # Quick stats
        st.markdown("#### 📊 Quick Stats")

        players_result = load_players_data()
        teams_result = load_teams_data()

        # Status indicators
        if players_result["status"] == "success":
            st.success("✅ Players data loaded")
        else:
            st.error("❌ Players data failed")

        if teams_result["status"] == "success":
            st.success("✅ Teams data loaded")
        else:
            st.error("❌ Teams data failed")

        # Quick actions
        st.markdown("#### ⚡ Quick Actions")

        if st.button("🔄 Refresh Data", help="Clear cache and reload data"):
            st.cache_data.clear()
            st.success("Data refreshed!")

        # Comparison list status
        if "comparison_list" in st.session_state and st.session_state.comparison_list:
            st.markdown("#### 📋 Comparison List")
            st.info(f"{len(st.session_state.comparison_list)} players selected")

            if st.button("Clear All"):
                st.session_state.comparison_list = []
                st.rerun()

        # Feature roadmap
        st.markdown("#### 🚧 Coming Soon")
        st.markdown(
            """
        - 🤖 AI-powered advice
        - 📱 Mobile app
        - 📈 Advanced charts
        - 🔔 Price alerts
        - 👥 Team imports
        - 📊 Custom analytics
        """
        )

        # App info
        st.markdown("#### ℹ️ About")
        st.markdown(
            """
        **FPL Toolkit Pro** brings together the best features from top FPL websites into one comprehensive platform.
        
        **Features:**
        - Real-time player data
        - Advanced filtering & search
        - Fixture difficulty analysis
        - Form tracking
        - Team building tools
        """
        )

        st.markdown("---")
        st.markdown("**Version**: 2.0.0 Pro  \n**Updated**: August 2025")


if __name__ == "__main__":
    main()
