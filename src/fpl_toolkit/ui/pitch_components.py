"""Football pitch lineup visualization component."""

from typing import Any, Dict, List, Optional

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


def create_football_pitch_layout() -> go.Figure:
    """Create a football pitch layout using Plotly."""
    fig = go.Figure()

    # Pitch dimensions (scaled for visualization)
    pitch_length = 100
    pitch_width = 64

    # Draw the pitch outline
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=pitch_length,
        y1=pitch_width,
        line=dict(color="white", width=3),
        fillcolor="rgba(34, 139, 34, 0.3)",  # Light green background
    )

    # Center circle
    fig.add_shape(
        type="circle",
        x0=pitch_length / 2 - 9.15,
        y0=pitch_width / 2 - 9.15,
        x1=pitch_length / 2 + 9.15,
        y1=pitch_width / 2 + 9.15,
        line=dict(color="white", width=2),
        fillcolor="rgba(0,0,0,0)",
    )

    # Center line
    fig.add_shape(
        type="line",
        x0=pitch_length / 2,
        y0=0,
        x1=pitch_length / 2,
        y1=pitch_width,
        line=dict(color="white", width=2),
    )

    # Goal areas
    # Left goal area
    fig.add_shape(
        type="rect",
        x0=0,
        y0=pitch_width / 2 - 9.16,
        x1=5.5,
        y1=pitch_width / 2 + 9.16,
        line=dict(color="white", width=2),
        fillcolor="rgba(0,0,0,0)",
    )

    # Right goal area
    fig.add_shape(
        type="rect",
        x0=pitch_length - 5.5,
        y0=pitch_width / 2 - 9.16,
        x1=pitch_length,
        y1=pitch_width / 2 + 9.16,
        line=dict(color="white", width=2),
        fillcolor="rgba(0,0,0,0)",
    )

    # Penalty areas
    # Left penalty area
    fig.add_shape(
        type="rect",
        x0=0,
        y0=pitch_width / 2 - 20.15,
        x1=16.5,
        y1=pitch_width / 2 + 20.15,
        line=dict(color="white", width=2),
        fillcolor="rgba(0,0,0,0)",
    )

    # Right penalty area
    fig.add_shape(
        type="rect",
        x0=pitch_length - 16.5,
        y0=pitch_width / 2 - 20.15,
        x1=pitch_length,
        y1=pitch_width / 2 + 20.15,
        line=dict(color="white", width=2),
        fillcolor="rgba(0,0,0,0)",
    )

    # Goals
    fig.add_shape(
        type="rect",
        x0=-2,
        y0=pitch_width / 2 - 3.66,
        x1=0,
        y1=pitch_width / 2 + 3.66,
        line=dict(color="white", width=2),
        fillcolor="rgba(255,255,255,0.3)",
    )

    fig.add_shape(
        type="rect",
        x0=pitch_length,
        y0=pitch_width / 2 - 3.66,
        x1=pitch_length + 2,
        y1=pitch_width / 2 + 3.66,
        line=dict(color="white", width=2),
        fillcolor="rgba(255,255,255,0.3)",
    )

    # Configure layout
    fig.update_layout(
        xaxis=dict(
            range=[-5, pitch_length + 5],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
        ),
        yaxis=dict(
            range=[-5, pitch_width + 5],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            scaleanchor="x",
            scaleratio=1,
        ),
        plot_bgcolor="rgba(34, 139, 34, 0.8)",  # Dark green
        paper_bgcolor="rgba(34, 139, 34, 0.8)",
        height=400,
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
    )

    return fig


def add_players_to_pitch(
    fig: go.Figure,
    formation: str,
    players: List[Dict[str, Any]],
    teams_data: List[Dict[str, Any]],
) -> go.Figure:
    """Add players to the football pitch based on formation."""

    # Formation configurations (x, y coordinates)
    formations = {
        "4-4-2": {
            "GK": [(10, 32)],
            "DEF": [(25, 10), (25, 25), (25, 39), (25, 54)],
            "MID": [(50, 15), (50, 25), (50, 39), (50, 49)],
            "FWD": [(75, 25), (75, 39)],
        },
        "4-3-3": {
            "GK": [(10, 32)],
            "DEF": [(25, 10), (25, 25), (25, 39), (25, 54)],
            "MID": [(50, 20), (50, 32), (50, 44)],
            "FWD": [(75, 15), (75, 32), (75, 49)],
        },
        "3-5-2": {
            "GK": [(10, 32)],
            "DEF": [(25, 20), (25, 32), (25, 44)],
            "MID": [(45, 10), (45, 25), (45, 32), (45, 39), (45, 54)],
            "FWD": [(75, 25), (75, 39)],
        },
        "5-3-2": {
            "GK": [(10, 32)],
            "DEF": [(25, 5), (25, 20), (25, 32), (25, 44), (25, 59)],
            "MID": [(50, 20), (50, 32), (50, 44)],
            "FWD": [(75, 25), (75, 39)],
        },
        "3-4-3": {
            "GK": [(10, 32)],
            "DEF": [(25, 20), (25, 32), (25, 44)],
            "MID": [(50, 15), (50, 25), (50, 39), (50, 49)],
            "FWD": [(75, 20), (75, 32), (75, 44)],
        },
    }

    formation_config = formations.get(formation, formations["4-4-2"])

    # Team lookup for colors
    team_lookup = {t["id"]: t for t in teams_data}

    # Position mapping
    position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}

    # Group players by position
    players_by_position = {"GK": [], "DEF": [], "MID": [], "FWD": []}

    for player in players[:11]:  # Only starting XI
        pos = position_map.get(player.get("element_type", 1), "GK")
        players_by_position[pos].append(player)

    # Color scheme for positions
    position_colors = {
        "GK": "#FFD700",  # Gold
        "DEF": "#4169E1",  # Royal Blue
        "MID": "#32CD32",  # Lime Green
        "FWD": "#FF4500",  # Orange Red
    }

    # Add players to pitch
    for position, coords in formation_config.items():
        players_in_position = players_by_position.get(position, [])

        for i, (x, y) in enumerate(coords):
            if i < len(players_in_position):
                player = players_in_position[i]
                player_name = f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()

                # Get team info
                team_info = team_lookup.get(player.get("team"), {})
                team_name = team_info.get("short_name", "")

                # Player stats
                points = player.get("total_points", 0)
                cost = player.get("now_cost", 0) / 10.0
                form = float(player.get("form", "0") or "0")

                # Add player circle
                fig.add_trace(
                    go.Scatter(
                        x=[x],
                        y=[y],
                        mode="markers+text",
                        marker=dict(
                            size=25,
                            color=position_colors[position],
                            line=dict(width=2, color="white"),
                            symbol="circle",
                        ),
                        text=player_name.split()[-1][:8],  # Last name, truncated
                        textposition="middle center",
                        textfont=dict(color="white", size=8, family="Arial Black"),
                        hovertemplate=(
                            f"<b>{player_name}</b><br>"
                            f"Position: {position}<br>"
                            f"Team: {team_name}<br>"
                            f"Cost: £{cost:.1f}m<br>"
                            f"Points: {points}<br>"
                            f"Form: {form:.1f}<br>"
                            "<extra></extra>"
                        ),
                        showlegend=False,
                        name=player_name,
                    )
                )

    return fig


def render_team_lineup_pitch(
    players: List[Dict[str, Any]],
    teams_data: List[Dict[str, Any]],
    formation: str = "4-4-2",
) -> None:
    """Render team lineup in football pitch format."""

    st.markdown("#### ⚽ Team Lineup - Football Pitch View")

    # Formation selector
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        selected_formation = st.selectbox(
            "Formation",
            ["4-4-2", "4-3-3", "3-5-2", "5-3-2", "3-4-3"],
            index=(
                0
                if formation == "4-4-2"
                else (
                    ["4-4-2", "4-3-3", "3-5-2", "5-3-2", "3-4-3"].index(formation)
                    if formation in ["4-4-2", "4-3-3", "3-5-2", "5-3-2", "3-4-3"]
                    else 0
                )
            ),
        )

    if len(players) < 11:
        st.warning("⚠️ Need at least 11 players to display lineup")
        return

    # Create pitch and add players
    fig = create_football_pitch_layout()
    fig = add_players_to_pitch(fig, selected_formation, players, teams_data)

    # Display the pitch
    st.plotly_chart(fig, use_container_width=True)

    # Bench players
    if len(players) > 11:
        st.markdown("#### 🪑 Bench")
        bench_players = players[11:15]  # Positions 12-15

        bench_cols = st.columns(min(len(bench_players), 4))

        for i, player in enumerate(bench_players):
            with bench_cols[i]:
                player_name = f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()
                cost = player.get("now_cost", 0) / 10.0
                points = player.get("total_points", 0)
                position = ["", "GK", "DEF", "MID", "FWD"][
                    player.get("element_type", 1)
                ]

                # Team info
                team_info = next(
                    (t for t in teams_data if t["id"] == player.get("team")), {}
                )
                team_name = team_info.get("short_name", "")

                st.markdown(
                    f"""
                <div style="text-align: center; padding: 0.75rem; border: 1px solid #ddd; border-radius: 8px; margin: 0.25rem; background: #f8f9fa;">
                    <div style="font-weight: 600; font-size: 0.9rem; color: #495057;">{player_name}</div>
                    <div style="font-size: 0.8rem; color: #6c757d; margin: 0.25rem 0;">
                        <span style="background: #007bff; color: white; padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.7rem;">{position}</span>
                        <span style="margin-left: 0.5rem;">{team_name}</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #495057;">
                        £{cost:.1f}m | {points}pts
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )


def create_team_stats_overview(players: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create team statistics overview."""
    if not players:
        return {}

    starting_xi = players[:11]
    bench = players[11:15] if len(players) > 11 else []

    # Calculate team stats
    total_cost = sum(p.get("now_cost", 0) for p in players) / 10.0
    total_points = sum(p.get("total_points", 0) for p in players)
    avg_form = sum(float(p.get("form", "0") or "0") for p in players) / len(players)

    # Position breakdown
    position_counts = {"GK": 0, "DEF": 0, "MID": 0, "FWD": 0}
    position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}

    for player in players:
        pos = position_map.get(player.get("element_type", 1), "GK")
        position_counts[pos] += 1

    # Team performance metrics
    starting_xi_points = sum(p.get("total_points", 0) for p in starting_xi)
    bench_points = sum(p.get("total_points", 0) for p in bench)

    # Most expensive and cheapest players
    most_expensive = (
        max(players, key=lambda x: x.get("now_cost", 0)) if players else None
    )
    cheapest = min(players, key=lambda x: x.get("now_cost", 0)) if players else None

    # Top performers
    top_scorer = (
        max(players, key=lambda x: x.get("total_points", 0)) if players else None
    )
    best_form = (
        max(players, key=lambda x: float(x.get("form", "0") or "0"))
        if players
        else None
    )

    return {
        "total_players": len(players),
        "total_cost": round(total_cost, 1),
        "remaining_budget": round(100.0 - total_cost, 1),
        "total_points": total_points,
        "avg_form": round(avg_form, 1),
        "position_counts": position_counts,
        "starting_xi_points": starting_xi_points,
        "bench_points": bench_points,
        "bench_contribution": round((bench_points / max(total_points, 1)) * 100, 1),
        "most_expensive": {
            "name": (
                f"{most_expensive.get('first_name', '')} {most_expensive.get('second_name', '')}".strip()
                if most_expensive
                else ""
            ),
            "cost": most_expensive.get("now_cost", 0) / 10.0 if most_expensive else 0,
        },
        "cheapest": {
            "name": (
                f"{cheapest.get('first_name', '')} {cheapest.get('second_name', '')}".strip()
                if cheapest
                else ""
            ),
            "cost": cheapest.get("now_cost", 0) / 10.0 if cheapest else 0,
        },
        "top_scorer": {
            "name": (
                f"{top_scorer.get('first_name', '')} {top_scorer.get('second_name', '')}".strip()
                if top_scorer
                else ""
            ),
            "points": top_scorer.get("total_points", 0) if top_scorer else 0,
        },
        "best_form": {
            "name": (
                f"{best_form.get('first_name', '')} {best_form.get('second_name', '')}".strip()
                if best_form
                else ""
            ),
            "form": float(best_form.get("form", "0") or "0") if best_form else 0,
        },
    }


def render_team_stats_cards(stats: Dict[str, Any]) -> None:
    """Render team statistics cards."""
    if not stats:
        return

    st.markdown("#### 📊 Team Statistics")

    # Main stats row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Team Value",
            f"£{stats['total_cost']:.1f}m",
            f"£{stats['remaining_budget']:.1f}m remaining",
        )

    with col2:
        st.metric(
            "Total Points",
            f"{stats['total_points']:,}",
            f"Avg form: {stats['avg_form']:.1f}",
        )

    with col3:
        st.metric(
            "Starting XI",
            f"{stats['starting_xi_points']} pts",
            f"{stats['bench_points']} bench pts",
        )

    with col4:
        st.metric(
            "Bench Impact", f"{stats['bench_contribution']:.1f}%", "of total points"
        )

    # Position breakdown
    st.markdown("##### Squad Composition")
    pos_col1, pos_col2, pos_col3, pos_col4 = st.columns(4)

    position_colors = {"GK": "🥅", "DEF": "🛡️", "MID": "⚽", "FWD": "🎯"}

    for i, (pos, count) in enumerate(stats["position_counts"].items()):
        col = [pos_col1, pos_col2, pos_col3, pos_col4][i]
        with col:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 0.75rem; border: 1px solid #e9ecef; border-radius: 8px; background: #f8f9fa;">
                    <div style="font-size: 1.5rem;">{position_colors[pos]}</div>
                    <div style="font-weight: 600; font-size: 1.2rem; color: #495057;">{count}</div>
                    <div style="font-size: 0.9rem; color: #6c757d;">{pos}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Key players
    st.markdown("##### 🌟 Key Players")
    key_col1, key_col2, key_col3 = st.columns(3)

    with key_col1:
        st.markdown(
            f"""
            **💰 Most Expensive**  
            {stats['most_expensive']['name']}  
            £{stats['most_expensive']['cost']:.1f}m
            """
        )

    with key_col2:
        st.markdown(
            f"""
            **🏆 Top Scorer**  
            {stats['top_scorer']['name']}  
            {stats['top_scorer']['points']} points
            """
        )

    with key_col3:
        st.markdown(
            f"""
            **🔥 Best Form**  
            {stats['best_form']['name']}  
            {stats['best_form']['form']:.1f} form
            """
        )


def create_player_comparison_radar(players: List[Dict[str, Any]]) -> go.Figure:
    """Create a radar chart comparing multiple players."""
    if len(players) < 2:
        return go.Figure()

    # Metrics to compare
    metrics = [
        "total_points",
        "form",
        "points_per_game",
        "selected_by_percent",
        "goals_scored",
        "assists",
    ]

    metric_labels = [
        "Total Points",
        "Form",
        "Points/Game",
        "Ownership %",
        "Goals",
        "Assists",
    ]

    fig = go.Figure()

    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57"]

    for i, player in enumerate(players[:5]):  # Limit to 5 players
        player_name = (
            f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()
        )

        # Normalize values for radar chart (0-100 scale)
        values = []
        for metric in metrics:
            value = float(player.get(metric, 0) or 0)

            # Normalize different metrics to 0-100 scale
            if metric == "total_points":
                normalized = min(100, (value / 200) * 100)  # Max reasonable: 200 points
            elif metric == "form":
                normalized = min(100, (value / 10) * 100)  # Max: 10
            elif metric == "points_per_game":
                normalized = min(100, (value / 8) * 100)  # Max reasonable: 8 PPG
            elif metric == "selected_by_percent":
                normalized = min(100, value)  # Already 0-100
            elif metric in ["goals_scored", "assists"]:
                normalized = min(100, (value / 20) * 100)  # Max reasonable: 20
            else:
                normalized = value

            values.append(normalized)

        # Close the radar chart
        values.append(values[0])
        labels = metric_labels + [metric_labels[0]]

        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=labels,
                fill="toself",
                name=player_name,
                line_color=colors[i % len(colors)],
                opacity=0.7,
            )
        )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title="Player Comparison Radar Chart",
        height=500,
    )

    return fig
