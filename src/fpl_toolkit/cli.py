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
@click.option("--port", default=8000, help="Port to bind the API server")
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
def advise(player_ids, budget, free_transfers, horizon):
    """Get AI advice for your team."""
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
        
        click.echo("🤖 Analyzing your team...")
        advice = advisor.advise_team(team_state)
        
        click.echo("\n📊 Team Analysis Summary:")
        click.echo(advice["summary"])
        
        if advice["recommendations"]:
            click.echo("\n💡 Recommendations:")
            for rec in advice["recommendations"]:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec["priority"], "ℹ️")
                click.echo(f"  {priority_emoji} {rec['message']}")
        
        if advice["underperformers"]:
            click.echo("\n⚠️ Players to consider transferring:")
            for under in advice["underperformers"][:3]:
                player = under["player"]
                name = f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()
                click.echo(f"  • {name}: {', '.join(under['issues'])}")
        
        advisor.close()
        
    except Exception as e:
        click.echo(f"❌ Error generating advice: {e}")


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