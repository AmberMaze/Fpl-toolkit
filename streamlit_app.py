"""Minimal Streamlit app for FPL Toolkit with responsive layout."""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from src.fpl_toolkit.api.client import FPLClient
from src.fpl_toolkit.ai.advisor import FPLAdvisor
from src.fpl_toolkit.analysis.projections import compare_player_projections, get_top_projected_players
from src.fpl_toolkit.analysis.decisions import analyze_transfer_scenario, find_transfer_targets
from src.fpl_toolkit.analysis.fixtures import get_fixture_difficulty_rankings


# Configure page
st.set_page_config(
    page_title="FPL Toolkit",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for mobile responsiveness
st.markdown("""
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
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_players_data():
    """Cached function to get players data."""
    with FPLClient() as client:
        return client.get_players()


@st.cache_data(ttl=3600)
def get_teams_data():
    """Cached function to get teams data."""
    with FPLClient() as client:
        return client.get_teams()


def format_player_name(player):
    """Format player name from FPL data."""
    return f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()


def display_player_card(player, show_detailed=False):
    """Display a player card with key information."""
    position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
    
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**{format_player_name(player)}**")
            st.write(f"{position_map.get(player.get('element_type'), 'Unknown')}")
        
        with col2:
            st.metric("Cost", f"£{player.get('now_cost', 0) / 10:.1f}m")
        
        with col3:
            st.metric("Points", f"{player.get('total_points', 0)}")
        
        if show_detailed:
            col4, col5, col6 = st.columns(3)
            with col4:
                st.metric("Form", f"{float(player.get('form', '0') or '0'):.1f}")
            with col5:
                st.metric("PPG", f"{float(player.get('points_per_game', '0') or '0'):.1f}")
            with col6:
                st.metric("Owned", f"{float(player.get('selected_by_percent', '0') or '0'):.1f}%")


def main():
    """Main Streamlit app."""
    st.title("⚽ FPL Toolkit")
    st.markdown("Fantasy Premier League analysis and decision support")
    
    # Initialize session state
    if 'selected_players' not in st.session_state:
        st.session_state.selected_players = []
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Players", "⚖️ Compare", "🤖 Advisor", "📊 Analysis"])
    
    with tab1:
        st.header("Player Search")
        
        # Load players data
        try:
            players = get_players_data()
            teams = get_teams_data()
            team_lookup = {t["id"]: t["name"] for t in teams}
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            position_filter = st.selectbox(
                "Position",
                ["All", "GK", "DEF", "MID", "FWD"],
                index=0
            )
        
        with col2:
            max_cost = st.slider("Max Cost (£m)", 4.0, 15.0, 15.0, 0.5)
        
        with col3:
            min_points = st.slider("Min Points", 0, 200, 0, 10)
        
        # Search box
        search_term = st.text_input("Search by name")
        
        # Filter players
        position_map = {"GK": 1, "DEF": 2, "MID": 3, "FWD": 4}
        filtered_players = []
        
        for player in players:
            # Position filter
            if position_filter != "All":
                if player.get("element_type") != position_map[position_filter]:
                    continue
            
            # Cost filter
            if player.get("now_cost", 0) / 10.0 > max_cost:
                continue
            
            # Points filter
            if player.get("total_points", 0) < min_points:
                continue
            
            # Search filter
            if search_term:
                player_name = format_player_name(player).lower()
                if search_term.lower() not in player_name:
                    continue
            
            filtered_players.append(player)
        
        # Sort by points
        filtered_players.sort(key=lambda x: x.get("total_points", 0), reverse=True)
        
        # Display results
        st.subheader(f"Found {len(filtered_players)} players")
        
        # Limit for performance
        display_limit = min(20, len(filtered_players))
        
        for i, player in enumerate(filtered_players[:display_limit]):
            with st.expander(f"{format_player_name(player)} - {team_lookup.get(player.get('team'), 'Unknown')}"):
                display_player_card(player, show_detailed=True)
                
                # Add to comparison button
                if st.button(f"Add to comparison", key=f"add_{player['id']}"):
                    if player['id'] not in st.session_state.selected_players:
                        st.session_state.selected_players.append(player['id'])
                        st.success(f"Added {format_player_name(player)} to comparison")
                    else:
                        st.warning("Player already in comparison list")
    
    with tab2:
        st.header("Player Comparison")
        
        # Show selected players
        if st.session_state.selected_players:
            st.subheader("Selected Players")
            
            players = get_players_data()
            player_lookup = {p["id"]: p for p in players}
            
            # Display selected players
            for player_id in st.session_state.selected_players:
                player = player_lookup.get(player_id)
                if player:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"• {format_player_name(player)} (£{player.get('now_cost', 0) / 10:.1f}m)")
                    with col2:
                        if st.button("Remove", key=f"remove_{player_id}"):
                            st.session_state.selected_players.remove(player_id)
                            st.experimental_rerun()
            
            # Clear all button
            if st.button("Clear All"):
                st.session_state.selected_players = []
                st.experimental_rerun()
            
            # Comparison parameters
            horizon_gws = st.slider("Gameweeks to analyze", 1, 10, 5)
            
            # Run comparison
            if st.button("Compare Players") and len(st.session_state.selected_players) >= 2:
                with st.spinner("Analyzing players..."):
                    try:
                        comparison_data = compare_player_projections(
                            st.session_state.selected_players, 
                            horizon_gws
                        )
                        
                        st.subheader("Comparison Results")
                        
                        # Create comparison table
                        comparison_rows = []
                        for comp in comparison_data["comparisons"]:
                            comparison_rows.append({
                                "Player": comp["name"],
                                "Cost": f"£{comp['cost']:.1f}m",
                                "Current Points": comp["current_points"],
                                "Projected Points": f"{comp['total_projected_points']:.1f}",
                                "Avg Confidence": f"{comp['average_confidence']:.2f}",
                                "Points per £m": f"{comp['points_per_million']:.1f}"
                            })
                        
                        df = pd.DataFrame(comparison_rows)
                        st.dataframe(df, use_container_width=True)
                        
                        # Best projection highlight
                        if comparison_data["best_projection"]:
                            best = comparison_data["best_projection"]
                            st.success(f"🏆 Best projection: **{best['name']}** with {best['total_projected_points']:.1f} projected points")
                    
                    except Exception as e:
                        st.error(f"Error during comparison: {str(e)}")
        else:
            st.info("No players selected for comparison. Add players from the Players tab.")
    
    with tab3:
        st.header("AI Advisor")
        
        # Team input
        st.subheader("Current Team")
        team_input = st.text_area(
            "Enter your team player IDs (one per line or comma-separated)",
            placeholder="e.g., 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15",
            help="You can find player IDs from the Players tab"
        )
        
        # Team parameters
        col1, col2, col3 = st.columns(3)
        with col1:
            budget = st.number_input("Available Budget (£m)", 0.0, 20.0, 0.0, 0.1)
        with col2:
            free_transfers = st.number_input("Free Transfers", 0, 5, 1)
        with col3:
            horizon_gws = st.slider("Analysis Horizon (GWs)", 1, 10, 5, key="advisor_horizon")
        
        if st.button("Get Team Advice"):
            if team_input.strip():
                try:
                    # Parse team IDs
                    team_ids = []
                    for item in team_input.replace("\n", ",").split(","):
                        try:
                            player_id = int(item.strip())
                            team_ids.append(player_id)
                        except ValueError:
                            continue
                    
                    if not team_ids:
                        st.error("No valid player IDs found")
                        return
                    
                    with st.spinner("Analyzing your team..."):
                        advisor = FPLAdvisor()
                        
                        team_state = {
                            "player_ids": team_ids,
                            "budget": budget,
                            "free_transfers": free_transfers,
                            "horizon_gameweeks": horizon_gws
                        }
                        
                        advice = advisor.advise_team(team_state)
                        
                        # Display advice
                        st.subheader("Team Analysis Summary")
                        st.info(advice["summary"])
                        
                        # Recommendations
                        if advice["recommendations"]:
                            st.subheader("Recommendations")
                            for rec in advice["recommendations"]:
                                priority_color = {
                                    "high": "🔴",
                                    "medium": "🟡", 
                                    "low": "🟢"
                                }.get(rec["priority"], "ℹ️")
                                
                                st.write(f"{priority_color} **{rec['type'].title()}**: {rec['message']}")
                        
                        # Underperformers
                        if advice["underperformers"]:
                            st.subheader("Players to Consider Transferring")
                            for under in advice["underperformers"][:3]:
                                player = under["player"]
                                st.warning(f"**{format_player_name(player)}**: {', '.join(under['issues'])}")
                        
                        # Top differentials
                        if advice["top_differentials"]:
                            st.subheader("Differential Picks")
                            for diff in advice["top_differentials"][:5]:
                                st.write(f"• **{diff['name']}** - {diff['ownership']:.1f}% owned, {diff['points_per_game']:.1f} PPG")
                        
                        advisor.close()
                
                except Exception as e:
                    st.error(f"Error generating advice: {str(e)}")
            else:
                st.warning("Please enter your team player IDs")
    
    with tab4:
        st.header("League Analysis")
        
        # Top projected players
        st.subheader("Top Projected Players")
        
        col1, col2 = st.columns(2)
        with col1:
            position_analysis = st.selectbox(
                "Position Filter",
                ["All", "GK", "DEF", "MID", "FWD"],
                key="analysis_position"
            )
        with col2:
            max_cost_analysis = st.slider("Max Cost Filter (£m)", 4.0, 15.0, 15.0, 0.5, key="analysis_cost")
        
        if st.button("Get Top Projections"):
            with st.spinner("Calculating projections..."):
                try:
                    pos_filter = None if position_analysis == "All" else position_analysis
                    
                    top_players = get_top_projected_players(
                        position=pos_filter,
                        max_cost=max_cost_analysis,
                        limit=10
                    )
                    
                    if top_players:
                        proj_rows = []
                        for player in top_players:
                            proj_rows.append({
                                "Player": player["name"],
                                "Position": player["position"],
                                "Cost": f"£{player['cost']:.1f}m",
                                "Projected Points": f"{player['projected_points']:.1f}",
                                "Confidence": f"{player['confidence_score']:.2f}",
                                "Current Form": f"{player['form']:.1f}",
                                "Ownership": f"{player['selected_by_percent']:.1f}%"
                            })
                        
                        df = pd.DataFrame(proj_rows)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.warning("No players found matching the criteria")
                
                except Exception as e:
                    st.error(f"Error calculating projections: {str(e)}")
        
        # Fixture difficulty
        st.subheader("Fixture Difficulty Rankings")
        
        if st.button("Analyze Fixture Difficulty"):
            with st.spinner("Analyzing fixtures..."):
                try:
                    fixture_rankings = get_fixture_difficulty_rankings(next_n=5)
                    
                    if fixture_rankings:
                        # Show easiest fixtures
                        st.write("**🟢 Easiest Fixtures (Top 10)**")
                        easy_fixtures = fixture_rankings[:10]
                        
                        fixture_rows = []
                        for team in easy_fixtures:
                            fixture_rows.append({
                                "Team": team["team_name"],
                                "Avg Difficulty": f"{team['average_difficulty']:.1f}",
                                "Trend": team["difficulty_trend"].replace("_", " ").title(),
                                "Home": team["home_fixtures"],
                                "Away": team["away_fixtures"]
                            })
                        
                        df_easy = pd.DataFrame(fixture_rows)
                        st.dataframe(df_easy, use_container_width=True)
                        
                        # Show hardest fixtures
                        st.write("**🔴 Hardest Fixtures (Bottom 10)**")
                        hard_fixtures = fixture_rankings[-10:]
                        
                        fixture_rows_hard = []
                        for team in hard_fixtures:
                            fixture_rows_hard.append({
                                "Team": team["team_name"],
                                "Avg Difficulty": f"{team['average_difficulty']:.1f}",
                                "Trend": team["difficulty_trend"].replace("_", " ").title(),
                                "Home": team["home_fixtures"],
                                "Away": team["away_fixtures"]
                            })
                        
                        df_hard = pd.DataFrame(fixture_rows_hard)
                        st.dataframe(df_hard, use_container_width=True)
                
                except Exception as e:
                    st.error(f"Error analyzing fixtures: {str(e)}")
    
    # Sidebar with quick info
    with st.sidebar:
        st.header("Quick Info")
        st.write("📱 **Mobile Friendly**")
        st.write("This app is optimized for mobile devices")
        
        st.write("🔄 **Data Updates**")
        st.write("Data is cached for 1 hour for performance")
        
        st.write("📊 **Features**")
        st.write("• Player search & comparison")
        st.write("• AI-powered team advice")
        st.write("• Projection analysis")
        st.write("• Fixture difficulty")
        
        if st.button("Clear Cache", help="Clear cached data to fetch latest"):
            st.cache_data.clear()
            st.success("Cache cleared!")


if __name__ == "__main__":
    main()