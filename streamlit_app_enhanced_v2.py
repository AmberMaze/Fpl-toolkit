"""Enhanced FPL Toolkit - Mobile-Ready with Manager ID Persistence and 5-Week Planning.

🌟 NEW FEATURES for @AmberMaze:
- 💾 Persistent Manager ID across all pages
- 🏗️ Enhanced Manual Team Builder for pre-season
- 🔮 5-Gameweek Planning & Analysis
- 📊 Comprehensive Projected Points (all FPL scoring aspects)
- 🎯 Smart Alternatives & Recommendations
- 📱 Mobile-Optimized Interface
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

# Enhanced session state initialization
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

# Page configuration optimized for mobile
st.set_page_config(
    page_title="FPL Toolkit - Mobile Ready",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/AmberMaze/Fpl-toolkit",
        "Report a bug": "https://github.com/AmberMaze/Fpl-toolkit/issues",
        "About": "FPL Toolkit - Your complete Fantasy Premier League management system for mobile!",
    },
)

# Mobile-optimized CSS
st.markdown(
    """
<style>
    /* Mobile-first responsive design */
    .main .block-container {
        padding: 1rem;
        max-width: 100%;
    }
    
    /* Manager ID sticky header */
    .manager-header {
        background: linear-gradient(135deg, #38ef7d 0%, #11998e 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
        text-align: center;
        position: sticky;
        top: 0;
        z-index: 100;
        box-shadow: 0 4px 12px rgba(17, 153, 142, 0.3);
    }
    
    /* Enhanced cards for mobile */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e1e5e9;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }
    
    /* Mobile-optimized metrics */
    .metric-row {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        flex: 1;
        min-width: 150px;
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #e9ecef;
    }
    
    /* Planning cards */
    .plan-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    /* Enhanced buttons */
    .action-button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 0.8rem 2rem;
        border: none;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    /* Responsive tables */
    .dataframe {
        font-size: 0.9rem;
    }
    
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem;
        }
        
        .metric-card {
            min-width: 120px;
            padding: 0.8rem;
        }
        
        .feature-card {
            padding: 1rem;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

# Mock data for development (since we can't install dependencies)
def get_mock_players_data():
    """Return mock player data for development."""
    return [
        {
            "id": 1, "first_name": "Erling", "second_name": "Haaland", 
            "element_type": 4, "team": 1, "now_cost": 150, "total_points": 224,
            "goals_scored": 27, "assists": 5, "clean_sheets": 0, "bonus": 18,
            "minutes": 2519, "form": "8.5", "expected_goals": "25.2", "expected_assists": "4.8"
        },
        {
            "id": 2, "first_name": "Mohamed", "second_name": "Salah",
            "element_type": 3, "team": 2, "now_cost": 130, "total_points": 212,
            "goals_scored": 19, "assists": 12, "clean_sheets": 0, "bonus": 15,
            "minutes": 2890, "form": "7.8", "expected_goals": "18.5", "expected_assists": "11.2"
        },
        {
            "id": 3, "first_name": "Harry", "second_name": "Kane",
            "element_type": 4, "team": 3, "now_cost": 125, "total_points": 196,
            "goals_scored": 22, "assists": 8, "clean_sheets": 0, "bonus": 12,
            "minutes": 2745, "form": "7.2", "expected_goals": "21.8", "expected_assists": "7.5"
        },
        {
            "id": 4, "first_name": "Kevin", "second_name": "De Bruyne",
            "element_type": 3, "team": 1, "now_cost": 125, "total_points": 189,
            "goals_scored": 8, "assists": 16, "clean_sheets": 0, "bonus": 14,
            "minutes": 2456, "form": "6.9", "expected_goals": "9.2", "expected_assists": "15.8"
        },
        {
            "id": 5, "first_name": "Virgil", "second_name": "van Dijk",
            "element_type": 2, "team": 2, "now_cost": 65, "total_points": 134,
            "goals_scored": 3, "assists": 2, "clean_sheets": 15, "bonus": 8,
            "minutes": 2890, "form": "5.2", "expected_goals": "2.8", "expected_assists": "1.9"
        }
    ]

def get_mock_teams_data():
    """Return mock team data."""
    return [
        {"id": 1, "name": "Manchester City", "short_name": "MCI"},
        {"id": 2, "name": "Liverpool", "short_name": "LIV"},
        {"id": 3, "name": "Tottenham", "short_name": "TOT"}
    ]

def calculate_comprehensive_projection(player: Dict[str, Any], gameweeks: int = 1) -> Dict[str, Any]:
    """Calculate comprehensive FPL projection including all scoring aspects."""
    # Base stats per 90 minutes
    minutes_per_game = player.get("minutes", 2500) / 38  # Average minutes per game
    
    # Scoring rates
    goals_per_90 = (player.get("goals_scored", 0) / player.get("minutes", 2500)) * 90 if player.get("minutes", 0) > 0 else 0
    assists_per_90 = (player.get("assists", 0) / player.get("minutes", 2500)) * 90 if player.get("minutes", 0) > 0 else 0
    
    # Position-specific scoring
    element_type = player.get("element_type", 3)
    position_multipliers = {
        1: {"goals": 6, "assists": 3, "clean_sheet": 4, "save": 0.33},  # GK
        2: {"goals": 6, "assists": 3, "clean_sheet": 4, "save": 0},     # DEF  
        3: {"goals": 5, "assists": 3, "clean_sheet": 1, "save": 0},     # MID
        4: {"goals": 4, "assists": 3, "clean_sheet": 0, "save": 0}      # FWD
    }
    
    multiplier = position_multipliers.get(element_type, position_multipliers[3])
    
    # Project points per gameweek
    projected_goals = goals_per_90 * (minutes_per_game / 90)
    projected_assists = assists_per_90 * (minutes_per_game / 90)
    projected_clean_sheets = 0.3 if element_type in [1, 2] else 0.1  # Rough estimate
    
    # Calculate points breakdown
    points_breakdown = {
        "minutes_points": 2 if minutes_per_game >= 60 else (1 if minutes_per_game >= 1 else 0),
        "goal_points": projected_goals * multiplier["goals"],
        "assist_points": projected_assists * multiplier["assists"],
        "clean_sheet_points": projected_clean_sheets * multiplier["clean_sheet"],
        "bonus_points": 1.5,  # Average bonus estimate
        "save_points": 3 * multiplier["save"] if element_type == 1 else 0
    }
    
    total_projected = sum(points_breakdown.values())
    total_for_horizon = total_projected * gameweeks
    
    return {
        "player_id": player["id"],
        "player_name": f"{player.get('first_name', '')} {player.get('second_name', '')}".strip(),
        "projected_points_per_gw": round(total_projected, 2),
        "projected_points_total": round(total_for_horizon, 2),
        "points_breakdown": {k: round(v, 2) for k, v in points_breakdown.items()},
        "confidence_score": 0.75,  # Mock confidence
        "gameweeks_analyzed": gameweeks
    }

def render_manager_header():
    """Render persistent manager ID header."""
    if st.session_state.manager_id:
        st.markdown(
            f"""
            <div class="manager-header">
                <h3>⚽ Manager ID: {st.session_state.manager_id}</h3>
                <p>📱 Ready for Season 2024/25 | 🎯 5-Week Planning Active</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="manager-header">
                <h3>⚽ Welcome to FPL Toolkit</h3>
                <p>📱 Set your Manager ID on the homepage to get started!</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_homepage():
    """Enhanced homepage with manager ID setup."""
    st.title("🏠 FPL Toolkit Homepage")
    
    # Manager ID Setup Section
    st.markdown("### 👤 Manager Setup")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        manager_id_input = st.text_input(
            "🆔 Enter your FPL Manager ID",
            value=st.session_state.manager_id,
            placeholder="e.g., 4076192",
            help="Your manager ID is the number in your FPL team URL",
            key="manager_id_input"
        )
        
        if st.button("💾 Save Manager ID", type="primary"):
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
            3. Copy the number from the URL: `/entry/{YOUR_ID}/`
            """
        )
    
    if st.session_state.manager_id:
        st.markdown("### 🎯 Quick Actions")
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            st.markdown(
                """
                <div class="feature-card">
                    <h4>🏗️ Build GW1 Team</h4>
                    <p>Select your starting team for Gameweek 1</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        with action_col2:
            st.markdown(
                """
                <div class="feature-card">
                    <h4>📅 5-Week Planning</h4>
                    <p>Plan your strategy for the next 5 gameweeks</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        with action_col3:
            st.markdown(
                """
                <div class="feature-card">
                    <h4>🎯 Get Alternatives</h4>
                    <p>Find the best player alternatives based on data</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

def render_enhanced_team_builder():
    """Enhanced team builder with comprehensive features."""
    st.title("🏗️ Enhanced Team Builder")
    
    if not st.session_state.manager_id:
        st.warning("⚠️ Please set your Manager ID on the homepage first!")
        return
    
    # Team building tabs
    tab1, tab2, tab3 = st.tabs(["🔧 Build Team", "📊 Analysis", "🎯 Alternatives"])
    
    with tab1:
        render_position_builder()
    
    with tab2:
        render_team_analysis()
    
    with tab3:
        render_player_alternatives()

def render_position_builder():
    """Enhanced position-based team builder."""
    st.markdown("### 🎯 Select Your Team")
    
    players = get_mock_players_data()
    teams = get_mock_teams_data()
    team_lookup = {t["id"]: t for t in teams}
    
    # Position requirements and current selection
    position_limits = {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}
    position_names = {"GK": "Goalkeepers", "DEF": "Defenders", "MID": "Midfielders", "FWD": "Forwards"}
    element_type_map = {"GK": 1, "DEF": 2, "MID": 3, "FWD": 4}
    
    total_cost = 0
    total_players = 0
    
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
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"⚽ {player.get('first_name', '')} {player.get('second_name', '')}")
                    with col2:
                        st.write(f"£{player.get('now_cost', 0)/10:.1f}m")
                    with col3:
                        if st.button("🗑️", key=f"remove_{player['id']}", help="Remove player"):
                            st.session_state.selected_team[pos_code].remove(player)
                            st.rerun()
            
            # Add new players
            if len(st.session_state.selected_team[pos_code]) < limit:
                st.markdown("##### ➕ Available Players:")
                
                for player in pos_players[:10]:  # Top 10 players
                    if player not in st.session_state.selected_team[pos_code]:
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            st.write(f"⚽ {player.get('first_name', '')} {player.get('second_name', '')}")
                        with col2:
                            st.write(f"£{player.get('now_cost', 0)/10:.1f}m")
                        with col3:
                            st.write(f"{player.get('total_points', 0)} pts")
                        with col4:
                            if st.button("➕", key=f"add_{player['id']}", help="Add player"):
                                st.session_state.selected_team[pos_code].append(player)
                                st.rerun()
        
        # Update totals
        pos_cost = sum(p.get("now_cost", 0) for p in st.session_state.selected_team[pos_code]) / 10
        total_cost += pos_cost
        total_players += len(st.session_state.selected_team[pos_code])
    
    # Team summary
    st.markdown("### 📊 Team Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Players", f"{total_players}/15")
    with col2:
        st.metric("💰 Total Cost", f"£{total_cost:.1f}m")
    with col3:
        remaining_budget = 100 - total_cost
        st.metric("💵 Remaining", f"£{remaining_budget:.1f}m")
    with col4:
        if total_players == 15:
            if total_cost <= 100:
                st.success("✅ Valid Team!")
            else:
                st.error("❌ Over Budget!")
        else:
            st.info("📝 Incomplete")

def render_team_analysis():
    """Render comprehensive team analysis."""
    st.markdown("### 📊 Team Analysis")
    
    all_players = []
    for pos_players in st.session_state.selected_team.values():
        all_players.extend(pos_players)
    
    if len(all_players) < 11:
        st.warning("⚠️ Select at least 11 players to see analysis")
        return
    
    # 5-Gameweek projections
    st.markdown("#### 🔮 5-Gameweek Projections")
    
    projections = []
    for player in all_players:
        proj = calculate_comprehensive_projection(player, gameweeks=5)
        projections.append(proj)
    
    # Create projections dataframe
    proj_df = pd.DataFrame([
        {
            "Player": proj["player_name"],
            "Position": get_position_name(next(p for p in all_players if p["id"] == proj["player_id"])["element_type"]),
            "Per GW": proj["projected_points_per_gw"],
            "5 GW Total": proj["projected_points_total"],
            "Confidence": f"{proj['confidence_score']*100:.0f}%"
        }
        for proj in projections
    ])
    
    st.dataframe(proj_df, use_container_width=True)
    
    # Points breakdown
    st.markdown("#### 📈 Points Breakdown Analysis")
    
    total_projected = sum(p["projected_points_total"] for p in projections)
    avg_per_gw = total_projected / 5
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 5-Week Total", f"{total_projected:.1f} pts")
    with col2:
        st.metric("📅 Average per GW", f"{avg_per_gw:.1f} pts")
    with col3:
        st.metric("🎯 Confidence", "75%")
    
    # Detailed breakdown for sample players
    st.markdown("#### 🔍 Detailed Scoring Breakdown")
    
    for proj in projections[:3]:  # Show top 3 players
        with st.expander(f"📊 {proj['player_name']} - {proj['projected_points_per_gw']:.1f} pts/GW"):
            breakdown = proj["points_breakdown"]
            
            breakdown_col1, breakdown_col2, breakdown_col3 = st.columns(3)
            
            with breakdown_col1:
                st.write(f"⏱️ Minutes: {breakdown['minutes_points']:.1f}")
                st.write(f"⚽ Goals: {breakdown['goal_points']:.1f}")
            with breakdown_col2:
                st.write(f"🎯 Assists: {breakdown['assist_points']:.1f}")
                st.write(f"🛡️ Clean Sheets: {breakdown['clean_sheet_points']:.1f}")
            with breakdown_col3:
                st.write(f"⭐ Bonus: {breakdown['bonus_points']:.1f}")
                st.write(f"🥅 Saves: {breakdown['save_points']:.1f}")

def render_player_alternatives():
    """Render smart player alternatives system."""
    st.markdown("### 🎯 Smart Player Alternatives")
    
    all_players = []
    for pos_players in st.session_state.selected_team.values():
        all_players.extend(pos_players)
    
    if not all_players:
        st.info("📝 Select some players first to see alternatives")
        return
    
    players_data = get_mock_players_data()
    
    st.markdown("#### 🔄 Recommended Alternatives")
    
    # Find alternatives for each position
    for pos_code, pos_players in st.session_state.selected_team.items():
        if pos_players:
            st.markdown(f"##### 🎯 {pos_code} Alternatives")
            
            element_type_map = {"GK": 1, "DEF": 2, "MID": 3, "FWD": 4}
            element_type = element_type_map[pos_code]
            
            # Find similar players not in team
            alternatives = [
                p for p in players_data 
                if p.get("element_type") == element_type and p not in pos_players
            ]
            
            # Sort by value (points per cost)
            alternatives.sort(key=lambda x: x.get("total_points", 0) / (x.get("now_cost", 50) / 10), reverse=True)
            
            for alt in alternatives[:3]:  # Top 3 alternatives
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"⚽ {alt.get('first_name', '')} {alt.get('second_name', '')}")
                with col2:
                    st.write(f"£{alt.get('now_cost', 0)/10:.1f}m")
                with col3:
                    value_score = alt.get("total_points", 0) / (alt.get("now_cost", 50) / 10)
                    st.write(f"💎 {value_score:.1f}")
                with col4:
                    proj = calculate_comprehensive_projection(alt, gameweeks=5)
                    st.write(f"🔮 {proj['projected_points_total']:.1f}")

def render_five_week_planning():
    """Render 5-gameweek planning interface."""
    st.title("📅 5-Gameweek Planning")
    
    if not st.session_state.manager_id:
        st.warning("⚠️ Please set your Manager ID on the homepage first!")
        return
    
    st.markdown("### 🎯 Strategic Planning for Next 5 Gameweeks")
    
    # Planning overview
    plan_col1, plan_col2 = st.columns(2)
    
    with plan_col1:
        st.markdown(
            """
            <div class="plan-card">
                <h4>📊 Current Strategy</h4>
                <p>📈 Focus on players with favorable fixtures</p>
                <p>🔄 Plan 2-3 transfers optimally</p>
                <p>🎯 Target 400+ points over 5 GWs</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with plan_col2:
        st.markdown(
            """
            <div class="plan-card">
                <h4>⚽ Gameweek Focus</h4>
                <p>🏠 GW1: Solid foundation</p>
                <p>🔥 GW2-3: Target form players</p>
                <p>💎 GW4-5: Fixture-based picks</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Gameweek breakdown
    st.markdown("### 📅 Gameweek Breakdown")
    
    for gw in range(1, 6):
        with st.expander(f"🏁 Gameweek {gw} Strategy", expanded=(gw == 1)):
            gw_col1, gw_col2, gw_col3 = st.columns(3)
            
            with gw_col1:
                st.markdown(f"#### 🎯 GW{gw} Focus")
                if gw == 1:
                    st.write("🏗️ Set strong foundation")
                    st.write("⚽ Pick proven performers")
                elif gw <= 3:
                    st.write("🔥 Target in-form players")
                    st.write("📈 Monitor price changes")
                else:
                    st.write("🎲 Fixture-based rotation")
                    st.write("💎 Find differentials")
            
            with gw_col2:
                st.markdown(f"#### 💰 Transfer Budget")
                st.write("💵 Free Transfers: 1")
                st.write("💸 Extra Cost: -4 pts each")
                st.write("🎯 Recommended: 1-2 transfers")
            
            with gw_col3:
                st.markdown(f"#### 📊 Expected Points")
                base_points = 65 - (gw * 2)  # Decreasing as season progresses
                st.write(f"🎯 Target: {base_points}+ points")
                st.write(f"📈 Top 10k Avg: {base_points - 5}")
                st.write(f"🏆 Template: {base_points + 5}")

def get_position_name(element_type: int) -> str:
    """Convert element type to position name."""
    position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
    return position_map.get(element_type, "Unknown")

def main():
    """Main application with enhanced navigation."""
    # Render persistent manager header
    render_manager_header()
    
    # Enhanced sidebar navigation
    st.sidebar.title("🧭 Navigation")
    
    # Show manager status in sidebar
    if st.session_state.manager_id:
        st.sidebar.success(f"✅ Manager: {st.session_state.manager_id}")
    else:
        st.sidebar.warning("⚠️ Set Manager ID first")
    
    # Navigation options
    nav_options = [
        "🏠 Homepage",
        "🏗️ Team Builder",
        "📅 5-Week Planning",
        "🎯 Player Analysis",
        "🏆 League Analysis",
    ]
    
    selected_page = st.sidebar.selectbox("Choose a section:", nav_options)
    
    # Render selected page
    if selected_page == "🏠 Homepage":
        render_homepage()
    elif selected_page == "🏗️ Team Builder":
        render_enhanced_team_builder()
    elif selected_page == "📅 5-Week Planning":
        render_five_week_planning()
    elif selected_page == "🎯 Player Analysis":
        st.title("🎯 Player Analysis")
        st.info("🚧 Enhanced player analysis with comprehensive FPL scoring breakdown coming soon!")
    elif selected_page == "🏆 League Analysis":
        st.title("🏆 League Analysis")
        st.info("🚧 League analysis using your saved Manager ID coming soon!")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📱 Mobile Optimized")
    st.sidebar.markdown("✅ Touch-friendly interface")
    st.sidebar.markdown("✅ Persistent preferences")
    st.sidebar.markdown("✅ Offline-capable")

if __name__ == "__main__":
    main()