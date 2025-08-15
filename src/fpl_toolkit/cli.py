"""Command line interface for FPL Toolkit."""
import click
import os
from .db.engine import init_db
from .api.client import FPLClient
from .ai.advisor import FPLAdvisor
from .analysis.projections import calculate_horizon_projection
from .analysis.decisions import evaluate_team_decisions, find_transfer_targets
from .analysis.advanced_analysis import generate_custom_gameweek_projections
from .ai.scenario_planner import ScenarioPlanner


@click.group()
def main():
    """FPL Toolkit - Fantasy Premier League analysis and decision support."""
    pass


@main.command()
def init():
    """Initialize the database."""
    try:
        init_db()
        click.echo("✅ Database initialized successfully")
    except Exception as e:
        click.echo(f"❌ Error initializing database: {e}")


@main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the API server")
@click.option("--port", default=int(os.getenv("PORT", 8000)), type=int, help="Port to bind the API server")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def serve(host, port, reload):
    """Start the FastAPI server."""
    try:
        import uvicorn
        click.echo(f"🚀 Starting FPL Toolkit API server on {host}:{port}")
        uvicorn.run(
            "fpl_toolkit.service.api:app",
            host=host,
            port=port,
            reload=reload
        )
    except ImportError:
        click.echo("❌ uvicorn not installed. Install with: pip install 'fpl-toolkit[web]'")
    except Exception as e:
        click.echo(f"❌ Error starting server: {e}")


@main.command()
@click.option("--port", default=8501, help="Port for Streamlit app")
def streamlit(port):
    """Start the Streamlit web app."""
    try:
        import subprocess
        click.echo(f"🎯 Starting Streamlit app on port {port}")
        subprocess.run([
            "streamlit", "run", "streamlit_app.py",
            "--server.port", str(port),
            "--server.address", "0.0.0.0"
        ])
    except FileNotFoundError:
        click.echo("❌ streamlit not installed. Install with: pip install 'fpl-toolkit[web]'")
    except Exception as e:
        click.echo(f"❌ Error starting Streamlit: {e}")


@main.command()
@click.argument("player_ids", nargs=-1, type=int)
@click.option("--budget", default=100.0, help="Available budget")
@click.option("--free-transfers", default=1, help="Number of free transfers")
@click.option("--horizon", default=5, help="Number of gameweeks to analyze")
@click.option("--scenarios", is_flag=True, help="Include scenario planning")
@click.option("--weekly", is_flag=True, help="Include weekly strategy")
def advise(player_ids, budget, free_transfers, horizon, scenarios, weekly):
    """Get comprehensive AI advice for your team."""
    if not player_ids:
        click.echo("❌ Please provide player IDs: fpl-toolkit advise 1 2 3 ...")
        return
    
    try:
        advisor = FPLAdvisor()
        
        team_state = {
            "player_ids": list(player_ids),
            "budget": budget,
            "free_transfers": free_transfers,
            "horizon_gameweeks": horizon
        }
        
        click.echo("🤖 Analyzing your team with AI...")
        advice = advisor.advise_team(team_state)
        
        click.echo("\n📊 Team Analysis Summary:")
        click.echo(advice["summary"])
        
        # Show season context
        context = advice.get("season_context", {})
        if context:
            click.echo(f"\n🎯 Season Context: GW{context.get('gameweek', 1)} ({context.get('phase', 'unknown')} season)")
        
        # Show recommendations
        if advice["recommendations"]:
            click.echo("\n💡 AI Recommendations:")
            for rec in advice["recommendations"]:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec["priority"], "ℹ️")
                click.echo(f"  {priority_emoji} {rec['message']}")
                if rec.get("reasoning"):
                    click.echo(f"    └─ {rec['reasoning']}")
        
        # Show underperformers with AI analysis
        if advice["underperformers"]:
            click.echo("\n⚠️ Players flagged by AI analysis:")
            for under in advice["underperformers"][:3]:
                player = under["player"]
                name = f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()
                severity = under.get("severity_score", 0)
                ai_sentiment = under.get("ai_sentiment", {})
                
                severity_emoji = "🔥" if severity >= 5 else "⚠️" if severity >= 3 else "💭"
                click.echo(f"  {severity_emoji} {name} (severity: {severity})")
                click.echo(f"    └─ Issues: {', '.join(under['issues'])}")
                click.echo(f"    └─ {under.get('recommendation', '')}")
                
                if ai_sentiment.get("sentiment") != "neutral":
                    click.echo(f"    └─ AI sentiment: {ai_sentiment.get('sentiment')} (confidence: {ai_sentiment.get('confidence', 0):.2f})")
        
        # Show scenarios if requested
        if scenarios and advice.get("scenarios"):
            click.echo("\n📈 Scenario Analysis:")
            scenario_comp = advice.get("scenario_comparison", {})
            if scenario_comp:
                click.echo(f"  {scenario_comp.get('recommendation', '')}")
            
            for i, scenario in enumerate(advice["scenarios"][:3], 1):
                risk_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(scenario.get("risk_level"), "⚪")
                click.echo(f"\n  {i}. {scenario.get('name')} {risk_emoji}")
                click.echo(f"     Expected: {scenario.get('net_points', 0):.1f} points")
                click.echo(f"     Risk: {scenario.get('risk_level', 'Unknown')}")
                click.echo(f"     Description: {scenario.get('description', '')}")
        
        # Show weekly strategy if requested
        if weekly and advice.get("weekly_strategy"):
            weekly_strat = advice["weekly_strategy"]
            click.echo(f"\n📅 Weekly Strategy ({weekly_strat.get('weeks_planned', 0)} weeks):")
            click.echo(f"  {weekly_strat.get('summary', '')}")
        
        advisor.close()
        
    except Exception as e:
        click.echo(f"❌ Error generating advice: {e}")
        import traceback
        traceback.print_exc()


@main.command()
@click.argument("team_id", type=int)
@click.option("--gameweek", type=int, help="Specific gameweek (default: current)")
def team(team_id, gameweek):
    """Fetch and analyze a user's team from FPL."""
    try:
        with FPLClient() as client:
            # Get team information
            team_info = client.get_user_team(team_id)
            picks = client.get_team_picks(team_id, gameweek)
            
            click.echo(f"👤 Team: {team_info.get('name', 'Unknown')}")
            click.echo(f"📊 Manager: {team_info.get('player_first_name', '')} {team_info.get('player_last_name', '')}")
            click.echo(f"🏆 Overall Points: {team_info.get('summary_overall_points', 0)}")
            click.echo(f"📈 Overall Rank: {team_info.get('summary_overall_rank', 'N/A'):,}")
            click.echo(f"💰 Bank: £{picks.get('entry_history', {}).get('bank', 0) / 10:.1f}m")
            
            # Get player details
            all_players = client.get_players()
            player_lookup = {p["id"]: p for p in all_players}
            
            current_picks = picks.get("picks", [])
            if current_picks:
                click.echo(f"\n📋 Current Team (GW {picks.get('entry_history', {}).get('event', '?')}):")
                click.echo("-" * 70)
                
                total_value = 0
                for pick in current_picks:
                    player_id = pick.get("element")
                    if player_id in player_lookup:
                        player = player_lookup[player_id]
                        name = f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()
                        cost = player.get("now_cost", 0) / 10.0
                        position = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}.get(player.get("element_type"), "?")
                        
                        total_value += cost
                        
                        captain_status = ""
                        if pick.get("is_captain"):
                            captain_status = " (C)"
                        elif pick.get("is_vice_captain"):
                            captain_status = " (V)"
                        
                        bench_status = " [BENCH]" if pick.get("position", 1) > 11 else ""
                        
                        click.echo(f"{name:<25} {position:<3} £{cost:>5.1f}m{captain_status}{bench_status}")
                
                click.echo(f"\n💰 Total Team Value: £{total_value:.1f}m")
            
    except Exception as e:
        click.echo(f"❌ Error fetching team: {e}")


@main.command()
@click.argument("team_id", type=int)
@click.option("--budget", type=float, help="Available budget (auto-detected if not provided)")
@click.option("--free-transfers", type=int, help="Free transfers (auto-detected if not provided)")
@click.option("--scenarios", default=5, help="Number of scenarios to generate")
def scenarios(team_id, budget, free_transfers, scenarios):
    """Generate scenario plans for a user's team."""
    try:
        from .ai.scenario_planner import ScenarioPlanner
        
        with FPLClient() as client:
            # Get current team
            picks = client.get_team_picks(team_id)
            team_info = client.get_user_team(team_id)
            
            current_picks = picks.get("picks", [])
            player_ids = [pick.get("element") for pick in current_picks if pick.get("position", 1) <= 11]
            
            # Auto-detect budget and transfers if not provided
            if budget is None:
                bank = picks.get("entry_history", {}).get("bank", 0) / 10.0
                budget = bank  # Available cash
            
            if free_transfers is None:
                # This would need to be calculated based on transfer history
                free_transfers = 1  # Default assumption
            
            team_state = {
                "player_ids": player_ids,
                "budget": budget,
                "free_transfers": free_transfers,
                "horizon_gameweeks": 5
            }
            
            click.echo(f"📊 Generating {scenarios} scenarios for team {team_info.get('name', 'Unknown')}...")
            click.echo(f"💰 Available budget: £{budget:.1f}m")
            click.echo(f"🔄 Free transfers: {free_transfers}")
            
            planner = ScenarioPlanner(client)
            scenario_list = planner.plan_gameweek_scenarios(team_state, scenarios)
            comparison = planner.compare_scenarios(scenario_list)
            
            click.echo("\n🎯 Scenario Analysis:")
            click.echo(f"  {comparison.get('recommendation', '')}")
            click.echo(f"  Point range: {comparison.get('point_range', 0):.1f} between best and worst")
            
            click.echo("\n📈 Scenarios (ranked by expected points):")
            click.echo("=" * 80)
            
            for i, scenario in enumerate(scenario_list, 1):
                risk_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(scenario.get("risk_level"), "⚪")
                
                click.echo(f"\n{i}. {scenario.get('name')} {risk_emoji}")
                click.echo(f"   Expected Points: {scenario.get('net_points', 0):.1f}")
                click.echo(f"   Transfer Cost: -{scenario.get('transfer_cost', 0)} points")
                click.echo(f"   Risk Level: {scenario.get('risk_level', 'Unknown')}")
                click.echo(f"   Description: {scenario.get('description', '')}")
                
                transfers = scenario.get("transfers", [])
                if transfers:
                    click.echo("   Transfers:")
                    for transfer in transfers:
                        out_name = transfer.get("out", {}).get("second_name", "Unknown")
                        in_name = transfer.get("in", {}).get("second_name", "Unknown")
                        point_gain = transfer.get("point_gain", 0)
                        click.echo(f"     • {out_name} → {in_name} (+{point_gain:.1f} pts)")
                
                click.echo(f"   Reasoning: {scenario.get('reasoning', '')}")
            
    except Exception as e:
        click.echo(f"❌ Error generating scenarios: {e}")
        import traceback
        traceback.print_exc()


@main.command()
@click.argument("player_ids", nargs=-1, type=int)
@click.option("--budget", default=100.0, help="Available budget (£m)")
@click.option("--free-transfers", default=1, help="Number of free transfers")
@click.option("--gameweeks", default=6, help="Number of gameweeks to simulate")
@click.option("--team-id", type=int, help="FPL team ID (auto-fetches current team)")
@click.option("--formation", default="3-5-2", help="Preferred formation (e.g., 3-4-3, 3-5-2)")
def simulate(player_ids, budget, free_transfers, gameweeks, team_id, formation):
    """Run comprehensive team simulation with optimal XI, transfers, and projections."""
    
    # Determine player_ids from team_id if provided
    if team_id and not player_ids:
        try:
            with FPLClient() as client:
                picks = client.get_team_picks(team_id)
                team_info = client.get_user_team(team_id)
                current_picks = picks.get("picks", [])
                player_ids = [pick.get("element") for pick in current_picks]
                
                # Auto-detect budget and transfers if not provided
                if budget == 100.0:  # Default value
                    bank = picks.get("entry_history", {}).get("bank", 0) / 10.0
                    budget = bank
                
                click.echo(f"🏆 Simulating team: {team_info.get('name', 'Unknown')}")
        except Exception as e:
            click.echo(f"❌ Error fetching team {team_id}: {e}")
            return
    elif not player_ids:
        click.echo("❌ Please provide player IDs or team ID: fpl-toolkit simulate --team-id 123 or fpl-toolkit simulate 1 2 3 ...")
        return
    
    try:
        click.echo(f"🎮 Running comprehensive {gameweeks}-gameweek simulation...")
        click.echo(f"💰 Budget: £{budget:.1f}m | 🔄 Free Transfers: {free_transfers}")
        click.echo("=" * 70)
        
        with FPLClient() as client:
            # Get current gameweek
            current_gw = client.get_current_gameweek()
            start_gw = current_gw.get("id", 1) if current_gw else 1
            end_gw = start_gw + gameweeks - 1
            
            click.echo(f"📅 Simulating GW{start_gw} to GW{end_gw}")
            
            # 1. Generate optimal XI for the gameweek range
            click.echo("\n🎯 OPTIMAL XI ANALYSIS")
            click.echo("-" * 30)
            
            optimal_xi = _generate_optimal_xi(client, list(player_ids), formation, start_gw, end_gw)
            _display_optimal_xi(optimal_xi, formation)
            
            # 2. Transfer recommendations with timing
            click.echo("\n🔄 TRANSFER RECOMMENDATIONS")
            click.echo("-" * 35)
            
            transfer_analysis = _analyze_transfer_opportunities(client, list(player_ids), budget, free_transfers, gameweeks)
            _display_transfer_recommendations(transfer_analysis)
            
            # 3. Players to watch
            click.echo("\n👀 PLAYERS TO WATCH")
            click.echo("-" * 25)
            
            watchlist = _generate_watchlist(client, list(player_ids), gameweeks)
            _display_watchlist(watchlist)
            
            # 4. Opportunity cost analysis
            click.echo("\n💸 OPPORTUNITY COST ANALYSIS")
            click.echo("-" * 35)
            
            opportunity_costs = _calculate_opportunity_costs(client, list(player_ids), gameweeks)
            _display_opportunity_costs(opportunity_costs)
            
            # 5. Ranking projections (scenarios)
            click.echo("\n📈 GAMEWEEK RANKING PROJECTIONS")
            click.echo("-" * 40)
            
            ranking_scenarios = _generate_ranking_scenarios(client, list(player_ids), optimal_xi, gameweeks)
            _display_ranking_scenarios(ranking_scenarios)
            
            # 6. Summary and recommendations
            click.echo("\n🎯 SIMULATION SUMMARY")
            click.echo("-" * 25)
            
            summary = _generate_simulation_summary(optimal_xi, transfer_analysis, watchlist, opportunity_costs, ranking_scenarios)
            _display_simulation_summary(summary)
            
    except Exception as e:
        click.echo(f"❌ Error running simulation: {e}")
        import traceback
        traceback.print_exc()


@main.command()
@click.argument("team_id", type=int)
@click.option("--weeks", default=4, help="Number of weeks to plan ahead")
def weekly(team_id, weeks):
    """Generate weekly strategy for upcoming gameweeks."""
    try:
        from .ai.scenario_planner import ScenarioPlanner
        
        with FPLClient() as client:
            # Get current team
            picks = client.get_team_picks(team_id)
            team_info = client.get_user_team(team_id)
            
            current_picks = picks.get("picks", [])
            player_ids = [pick.get("element") for pick in current_picks if pick.get("position", 1) <= 11]
            
            team_state = {
                "player_ids": player_ids,
                "budget": picks.get("entry_history", {}).get("bank", 0) / 10.0,
                "free_transfers": 1,  # Default assumption
                "horizon_gameweeks": 5
            }
            
            click.echo(f"📅 Generating {weeks}-week strategy for {team_info.get('name', 'Unknown')}...")
            
            planner = ScenarioPlanner(client)
            weekly_strategy = planner.plan_weekly_strategy(team_state, weeks)
            
            click.echo(f"\n🎯 Strategy Summary:")
            click.echo(f"  {weekly_strategy.get('summary', '')}")
            click.echo(f"  Current GW: {weekly_strategy.get('current_gameweek', 'Unknown')}")
            click.echo(f"  Total transfers planned: {weekly_strategy.get('total_transfers_planned', 0)}")
            
            weekly_plans = weekly_strategy.get("weekly_strategy", {})
            
            click.echo(f"\n📊 Week-by-Week Analysis:")
            click.echo("=" * 60)
            
            for gw_key, plan in weekly_plans.items():
                click.echo(f"\n{gw_key}:")
                click.echo(f"  Expected Points: {plan.get('expected_points', 0):.1f}")
                click.echo(f"  Fixture Summary: {plan.get('fixture_summary', 'N/A')}")
                
                recommended_transfers = plan.get("recommended_transfers", [])
                if recommended_transfers:
                    click.echo("  Recommended Transfers:")
                    for transfer in recommended_transfers:
                        player_name = transfer.get("out", {}).get("second_name", "Unknown")
                        reason = transfer.get("reason", "")
                        priority = transfer.get("priority", "medium")
                        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "ℹ️")
                        click.echo(f"    {priority_emoji} Consider transferring {player_name}: {reason}")
                else:
                    click.echo("  ✅ No transfers recommended")
            
    except Exception as e:
        click.echo(f"❌ Error generating weekly strategy: {e}")
        import traceback
        traceback.print_exc()


@main.command()
@click.argument("player_out_id", type=int)
@click.argument("player_in_id", type=int)
@click.option("--horizon", default=5, help="Number of gameweeks to analyze")
def transfer(player_out_id, player_in_id, horizon):
    """Analyze a transfer scenario."""
    try:
        from .analysis.decisions import analyze_transfer_scenario
        
        click.echo(f"⚖️ Analyzing transfer: {player_out_id} -> {player_in_id}")
        
        scenario = analyze_transfer_scenario(player_out_id, player_in_id, horizon)
        
        if "error" in scenario:
            click.echo(f"❌ {scenario['error']}")
            return
        
        click.echo(f"\n📈 Transfer Analysis:")
        click.echo(f"  Out: {scenario['player_out_name']}")
        click.echo(f"  In:  {scenario['player_in_name']}")
        click.echo(f"  Cost change: £{scenario['cost_change']:.1f}m")
        click.echo(f"  Projected points gain: {scenario['projected_points_gain']:.1f}")
        click.echo(f"  Confidence: {scenario['confidence_score']:.2f}")
        click.echo(f"  Risk: {scenario['risk_score']:.2f}")
        click.echo(f"  Recommendation: {scenario['recommendation']}")
        click.echo(f"\n💭 Reasoning: {scenario['reasoning']}")
        
    except Exception as e:
        click.echo(f"❌ Error analyzing transfer: {e}")


@main.command()
@click.option("--position", help="Filter by position (GK, DEF, MID, FWD)")
@click.option("--max-cost", type=float, help="Maximum cost filter")
@click.option("--limit", default=10, help="Number of players to show")
def players(position, max_cost, limit):
    """List top players with optional filters."""
    try:
        with FPLClient() as client:
            all_players = client.get_players()
        
        # Filter players
        position_map = {"GK": 1, "DEF": 2, "MID": 3, "FWD": 4}
        filtered_players = []
        
        for player in all_players:
            if position and player.get("element_type") != position_map.get(position):
                continue
            
            if max_cost and player.get("now_cost", 0) / 10.0 > max_cost:
                continue
            
            filtered_players.append(player)
        
        # Sort by total points
        filtered_players.sort(key=lambda x: x.get("total_points", 0), reverse=True)
        
        click.echo(f"🏆 Top {min(limit, len(filtered_players))} Players:")
        click.echo("-" * 60)
        
        for player in filtered_players[:limit]:
            name = f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()
            cost = player.get("now_cost", 0) / 10.0
            points = player.get("total_points", 0)
            form = float(player.get("form", "0") or "0")
            
            position_name = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}.get(player.get("element_type"), "?")
            
            click.echo(f"{name:<25} {position_name:<3} £{cost:>5.1f}m {points:>3}pts Form:{form:>4.1f}")
        
    except Exception as e:
        click.echo(f"❌ Error fetching players: {e}")


@main.command()
def version():
    """Show version information."""
    from . import __version__
    click.echo(f"FPL Toolkit v{__version__}")


# Helper functions for the simulate command
def _generate_optimal_xi(client, player_ids, formation, start_gw, end_gw):
    """Generate optimal XI based on projections."""
    players = client.get_players()
    player_lookup = {p["id"]: p for p in players}
    
    # Get projections for all players
    projections = []
    for pid in player_ids:
        if pid not in player_lookup:
            continue
            
        projection = calculate_horizon_projection(pid, end_gw - start_gw + 1, client)
        if "error" not in projection:
            player_data = player_lookup[pid]
            projections.append({
                "player_id": pid,
                "player": player_data,
                "projection": projection,
                "position": player_data.get("element_type", 1),
                "expected_points": projection.get("total_projected_points", 0)
            })
    
    # Sort by position and expected points
    by_position = {1: [], 2: [], 3: [], 4: []}
    for proj in projections:
        pos = proj["position"]
        by_position[pos].append(proj)
    
    # Sort each position by expected points
    for pos in by_position:
        by_position[pos].sort(key=lambda x: x["expected_points"], reverse=True)
    
    # Parse formation (e.g., "3-5-2" -> [3, 5, 2])
    formation_counts = [int(x) for x in formation.split("-")]
    if len(formation_counts) != 3:
        formation_counts = [3, 5, 2]  # Default
    
    # Select optimal XI based on formation
    optimal_xi = {
        "goalkeeper": by_position[1][:1],  # Always 1 GK
        "defenders": by_position[2][:formation_counts[0]],
        "midfielders": by_position[3][:formation_counts[1]], 
        "forwards": by_position[4][:formation_counts[2]]
    }
    
    # Calculate total expected points
    total_points = sum([
        sum(p["expected_points"] for p in pos_players)
        for pos_players in optimal_xi.values()
    ])
    
    optimal_xi["total_expected_points"] = total_points
    optimal_xi["formation"] = formation
    
    return optimal_xi


def _display_optimal_xi(optimal_xi, formation):
    """Display the optimal XI."""
    click.echo(f"Formation: {formation}")
    click.echo(f"Total Expected Points: {optimal_xi['total_expected_points']:.1f}")
    click.echo()
    
    positions = [
        ("Goalkeeper", optimal_xi["goalkeeper"]), 
        ("Defenders", optimal_xi["defenders"]),
        ("Midfielders", optimal_xi["midfielders"]),
        ("Forwards", optimal_xi["forwards"])
    ]
    
    for pos_name, players in positions:
        if players:
            click.echo(f"{pos_name}:")
            for player in players:
                p = player["player"]
                name = f"{p.get('first_name', '')} {p.get('second_name', '')}".strip()
                points = player["expected_points"]
                cost = p.get("now_cost", 0) / 10.0
                click.echo(f"  • {name} - {points:.1f} pts (£{cost:.1f}m)")


def _analyze_transfer_opportunities(client, player_ids, budget, free_transfers, gameweeks):
    """Analyze transfer opportunities."""
    # Use existing decision analysis
    decisions = evaluate_team_decisions(player_ids, budget, free_transfers, gameweeks)
    
    # Enhance with timing analysis
    transfer_suggestions = decisions.get("transfer_suggestions", [])
    
    # Add timing recommendations
    for suggestion in transfer_suggestions:
        # Simple timing logic - prioritize by urgency
        urgency = suggestion.get("priority", 1)
        if urgency == 1:
            suggestion["timing"] = "Immediate"
        elif urgency <= 2:
            suggestion["timing"] = "Next 1-2 GWs"
        else:
            suggestion["timing"] = "Monitor"
    
    return {
        "suggestions": transfer_suggestions[:5],  # Top 5
        "summary": decisions.get("summary", "No major issues detected")
    }


def _display_transfer_recommendations(transfer_analysis):
    """Display transfer recommendations."""
    suggestions = transfer_analysis["suggestions"]
    
    if not suggestions:
        click.echo("✅ No urgent transfers needed")
        return
    
    click.echo(f"Found {len(suggestions)} transfer opportunities:")
    click.echo()
    
    for i, suggestion in enumerate(suggestions, 1):
        problem_player = suggestion.get("problem_player", {})
        replacement_suggestions = suggestion.get("replacement_suggestions", [])
        timing = suggestion.get("timing", "Monitor")
        
        p_name = f"{problem_player.get('first_name', '')} {problem_player.get('second_name', '')}".strip()
        
        click.echo(f"{i}. Transfer out: {p_name}")
        click.echo(f"   Timing: {timing}")
        click.echo(f"   Issues: {', '.join(suggestion.get('issues', []))}")
        
        if replacement_suggestions:
            best_replacement = replacement_suggestions[0]
            r_player = best_replacement.get("player_in", {})
            r_name = f"{r_player.get('first_name', '')} {r_player.get('second_name', '')}".strip()
            points_gain = best_replacement.get("projected_points_gain", 0)
            click.echo(f"   Best replacement: {r_name} (+{points_gain:.1f} pts)")
        click.echo()


def _generate_watchlist(client, player_ids, gameweeks):
    """Generate watchlist of promising players."""
    players = client.get_players()
    owned_players = set(player_ids)
    
    # Find promising players not in team
    candidates = []
    for player in players:
        if player["id"] in owned_players:
            continue
        
        # Filter by availability and basic criteria
        if (player.get("status") != "a" or 
            float(player.get("selected_by_percent", "0") or "0") < 1.0):
            continue
        
        # Get projection
        projection = calculate_horizon_projection(player["id"], gameweeks, client)
        if "error" in projection:
            continue
            
        # Calculate value metrics
        expected_points = projection.get("total_projected_points", 0)
        cost = player.get("now_cost", 0) / 10.0
        value = expected_points / cost if cost > 0 else 0
        
        candidates.append({
            "player": player,
            "expected_points": expected_points,
            "value": value,
            "projection": projection
        })
    
    # Sort by value and take top performers by position
    candidates.sort(key=lambda x: x["value"], reverse=True)
    
    watchlist = {}
    position_names = {1: "Goalkeepers", 2: "Defenders", 3: "Midfielders", 4: "Forwards"}
    
    for pos in [1, 2, 3, 4]:
        pos_candidates = [c for c in candidates if c["player"].get("element_type") == pos]
        watchlist[position_names[pos]] = pos_candidates[:3]  # Top 3 per position
    
    return watchlist


def _display_watchlist(watchlist):
    """Display watchlist."""
    for position, players in watchlist.items():
        if players:
            click.echo(f"{position}:")
            for player_data in players:
                p = player_data["player"]
                name = f"{p.get('first_name', '')} {p.get('second_name', '')}".strip()
                points = player_data["expected_points"]
                cost = p.get("now_cost", 0) / 10.0
                value = player_data["value"]
                ownership = p.get("selected_by_percent", "0")
                click.echo(f"  • {name} - {points:.1f} pts, £{cost:.1f}m, Value: {value:.2f}, Own: {ownership}%")
            click.echo()


def _calculate_opportunity_costs(client, player_ids, gameweeks):
    """Calculate opportunity cost for players not in team."""
    players = client.get_players()
    owned_players = set(player_ids)
    
    # Get projections for owned vs available players by position
    opportunity_costs = {}
    position_names = {1: "Goalkeepers", 2: "Defenders", 3: "Midfielders", 4: "Forwards"}
    
    for pos in [1, 2, 3, 4]:
        # Find best available player in position
        best_available = None
        best_points = 0
        
        for player in players:
            if (player["id"] not in owned_players and 
                player.get("element_type") == pos and
                player.get("status") == "a"):
                
                projection = calculate_horizon_projection(player["id"], gameweeks, client)
                if "error" not in projection:
                    points = projection.get("total_projected_points", 0)
                    if points > best_points:
                        best_points = points
                        best_available = {
                            "player": player,
                            "expected_points": points,
                            "projection": projection
                        }
        
        # Find current best owned player in position
        best_owned = None
        best_owned_points = 0
        
        for pid in player_ids:
            player = next((p for p in players if p["id"] == pid), None)
            if player and player.get("element_type") == pos:
                projection = calculate_horizon_projection(pid, gameweeks, client)
                if "error" not in projection:
                    points = projection.get("total_projected_points", 0)
                    if points > best_owned_points:
                        best_owned_points = points
                        best_owned = {
                            "player": player,
                            "expected_points": points
                        }
        
        if best_available and best_owned:
            opportunity_cost = best_points - best_owned_points
            opportunity_costs[position_names[pos]] = {
                "available": best_available,
                "owned": best_owned,
                "cost": opportunity_cost
            }
    
    return opportunity_costs


def _display_opportunity_costs(opportunity_costs):
    """Display opportunity cost analysis."""
    total_cost = 0
    
    for position, data in opportunity_costs.items():
        if data["cost"] > 0:  # Only show positive opportunity costs
            avail = data["available"]["player"]
            owned = data["owned"]["player"]
            cost = data["cost"]
            total_cost += cost
            
            avail_name = f"{avail.get('first_name', '')} {avail.get('second_name', '')}".strip()
            owned_name = f"{owned.get('first_name', '')} {owned.get('second_name', '')}".strip()
            
            click.echo(f"{position}: Missing {cost:.1f} pts")
            click.echo(f"  Current: {owned_name} ({data['owned']['expected_points']:.1f} pts)")
            click.echo(f"  Best available: {avail_name} ({data['available']['expected_points']:.1f} pts)")
            click.echo()
    
    if total_cost > 0:
        click.echo(f"Total opportunity cost: {total_cost:.1f} points")
    else:
        click.echo("✅ No significant opportunity costs detected")


def _generate_ranking_scenarios(client, player_ids, optimal_xi, gameweeks):
    """Generate ranking projection scenarios."""
    base_points = optimal_xi["total_expected_points"]
    
    # Generate different scenarios
    scenarios = {
        "best": base_points * 1.3,      # 30% above expectation
        "expected": base_points,         # Expected performance
        "unlucky": base_points * 0.7,   # 30% below expectation  
        "worst": base_points * 0.5      # 50% below expectation
    }
    
    # Estimate rankings based on average scores
    # These are rough estimates - real implementation would need league data
    avg_gw_score = 50  # Typical average
    scenarios_with_ranks = {}
    
    for scenario, points in scenarios.items():
        if points > avg_gw_score * 1.5:
            rank_estimate = "Top 10%"
        elif points > avg_gw_score * 1.2:
            rank_estimate = "Top 25%"
        elif points > avg_gw_score:
            rank_estimate = "Above Average"
        elif points > avg_gw_score * 0.8:
            rank_estimate = "Below Average"
        else:
            rank_estimate = "Bottom 25%"
        
        scenarios_with_ranks[scenario] = {
            "points": points,
            "rank_estimate": rank_estimate
        }
    
    return scenarios_with_ranks


def _display_ranking_scenarios(ranking_scenarios):
    """Display ranking scenarios."""
    click.echo("Projected Performance Scenarios:")
    click.echo()
    
    for scenario, data in ranking_scenarios.items():
        emoji = {
            "best": "🚀",
            "expected": "📊", 
            "unlucky": "😐",
            "worst": "😞"
        }.get(scenario, "📈")
        
        click.echo(f"{emoji} {scenario.title()}: {data['points']:.1f} pts ({data['rank_estimate']})")


def _generate_simulation_summary(optimal_xi, transfer_analysis, watchlist, opportunity_costs, ranking_scenarios):
    """Generate overall simulation summary."""
    summary = {
        "optimal_points": optimal_xi["total_expected_points"],
        "formation": optimal_xi["formation"],
        "transfer_count": len(transfer_analysis["suggestions"]),
        "opportunity_cost": sum(data.get("cost", 0) for data in opportunity_costs.values()),
        "expected_rank": ranking_scenarios["expected"]["rank_estimate"]
    }
    return summary


def _display_simulation_summary(summary):
    """Display simulation summary."""
    click.echo(f"🎯 Expected Points (Optimal XI): {summary['optimal_points']:.1f}")
    click.echo(f"📋 Recommended Formation: {summary['formation']}")
    click.echo(f"🔄 Transfers Suggested: {summary['transfer_count']}")
    click.echo(f"💸 Total Opportunity Cost: {summary['opportunity_cost']:.1f} pts")
    click.echo(f"📈 Expected Rank: {summary['expected_rank']}")
    click.echo()
    
    if summary['transfer_count'] > 0:
        click.echo("💡 Priority: Focus on suggested transfers")
    elif summary['opportunity_cost'] > 5:
        click.echo("💡 Priority: Monitor watchlist players for future transfers") 
    else:
        click.echo("✅ Team looks solid - monitor form and fixtures")


if __name__ == "__main__":
    main()