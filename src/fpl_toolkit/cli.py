"""Command line interface for FPL Toolkit."""
import click
import os
from .db.engine import init_db
from .api.client import FPLClient
from .ai.advisor import FPLAdvisor


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


if __name__ == "__main__":
    main()