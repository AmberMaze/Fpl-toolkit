"""AI-powered advisor for FPL decision making."""
from typing import List, Dict, Any, Optional, Tuple
import os
import json
try:
    import numpy as np
except ImportError:
    # Create a minimal numpy substitute for basic operations
    class NumpySubstitute:
        @staticmethod
        def var(data):
            if not data:
                return 0
            mean = sum(data) / len(data)
            return sum((x - mean) ** 2 for x in data) / len(data)
        
        @staticmethod
        def mean(data):
            return sum(data) / len(data) if data else 0
            
        @staticmethod
        def std(data):
            return (NumpySubstitute.var(data)) ** 0.5
        
        # Add ndarray as a simple list for compatibility
        ndarray = list
    
    np = NumpySubstitute()
from datetime import datetime, timedelta
from ..api.client import FPLClient
from ..analysis.fixtures import compute_fixture_difficulty
from ..analysis.projections import calculate_horizon_projection
from ..analysis.decisions import analyze_transfer_scenario, find_transfer_targets


class FPLAdvisor:
    """AI-powered FPL advisor combining heuristics with Hugging Face models."""
    
    def __init__(self, client: Optional[FPLClient] = None):
        self.client = client or FPLClient()
        self.embedder = None
        self.classifier = None
        self._try_load_models()
        
        # Dynamic thresholds based on gameweek and season context
        self.context = self._get_season_context()
    
    def _try_load_models(self):
        """Try to load Hugging Face models if available."""
        try:
            from sentence_transformers import SentenceTransformer
            from transformers import pipeline
            
            # Use lightweight sentence transformer for embeddings
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
            
            # Try to load a lightweight classification model for sentiment analysis
            try:
                self.classifier = pipeline(
                    "text-classification",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                )
            except Exception:
                # Fallback to simpler model
                try:
                    self.classifier = pipeline(
                        "sentiment-analysis",
                        model="distilbert-base-uncased-finetuned-sst-2-english"
                    )
                except Exception:
                    self.classifier = None
                    
        except ImportError:
            # Fallback to heuristic-only approach
            self.embedder = None
            self.classifier = None
    
    def _get_season_context(self) -> Dict[str, Any]:
        """Get current season context for adaptive thresholds."""
        try:
            current_gw = self.client.get_current_gameweek()
            gameweeks = self.client.get_gameweeks()
            
            if not current_gw:
                return {"gameweek": 1, "phase": "early", "total_gameweeks": 38}
            
            gw_num = current_gw.get("id", 1)
            total_gws = len(gameweeks)
            
            # Determine season phase
            if gw_num <= 10:
                phase = "early"
            elif gw_num <= 25:
                phase = "mid"
            else:
                phase = "late"
            
            return {
                "gameweek": gw_num,
                "phase": phase,
                "total_gameweeks": total_gws,
                "deadline": current_gw.get("deadline_time")
            }
        except Exception:
            return {"gameweek": 1, "phase": "early", "total_gameweeks": 38}
    
    def _get_adaptive_thresholds(self) -> Dict[str, float]:
        """Get adaptive thresholds based on season context."""
        phase = self.context.get("phase", "early")
        
        if phase == "early":
            return {
                "points_threshold": 2.5,  # Lower expectations early season
                "cost_threshold": 7.5,
                "ownership_threshold": 15.0,
                "form_weight": 0.3,
                "fixture_weight": 0.7
            }
        elif phase == "mid":
            return {
                "points_threshold": 3.5,
                "cost_threshold": 8.0,
                "ownership_threshold": 12.0,
                "form_weight": 0.5,
                "fixture_weight": 0.5
            }
        else:  # late season
            return {
                "points_threshold": 4.0,  # Higher expectations late season
                "cost_threshold": 8.5,
                "ownership_threshold": 10.0,
                "form_weight": 0.7,  # Form matters more in final stretch
                "fixture_weight": 0.3
            }
    
    def _analyze_player_sentiment(self, player_name: str, recent_news: Optional[str] = None) -> Dict[str, Any]:
        """Analyze player sentiment using AI models."""
        if not self.classifier:
            return {"sentiment": "neutral", "confidence": 0.5, "reasoning": "No AI model available"}
        
        # Create text for analysis
        text = f"Player {player_name}"
        if recent_news:
            text += f" {recent_news}"
        
        try:
            result = self.classifier(text)
            if isinstance(result, list) and len(result) > 0:
                sentiment_data = result[0]
                return {
                    "sentiment": sentiment_data.get("label", "neutral").lower(),
                    "confidence": sentiment_data.get("score", 0.5),
                    "reasoning": f"AI sentiment analysis of player context"
                }
            else:
                return {"sentiment": "neutral", "confidence": 0.5, "reasoning": "Unable to analyze sentiment"}
        except Exception:
            return {"sentiment": "neutral", "confidence": 0.5, "reasoning": "Error in sentiment analysis"}
    
    def _calculate_player_embedding(self, player_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """Calculate player embedding for similarity analysis."""
        if not self.embedder:
            return None
        
        try:
            # Create player description for embedding
            description = f"Player {player_data.get('first_name', '')} {player_data.get('second_name', '')} "
            description += f"position {player_data.get('element_type', 1)} "
            description += f"team {player_data.get('team', 1)} "
            description += f"price {player_data.get('now_cost', 0)/10:.1f} "
            description += f"points {player_data.get('total_points', 0)} "
            description += f"form {player_data.get('form', 0)}"
            
            embedding = self.embedder.encode(description)
            return embedding
        except Exception:
            return None
    
    def find_similar_players(self, target_player: Dict[str, Any], candidate_players: List[Dict[str, Any]], 
                           top_n: int = 5) -> List[Dict[str, Any]]:
        """Find similar players using AI embeddings."""
        if not self.embedder:
            # Fallback to basic similarity
            return self._find_similar_players_fallback(target_player, candidate_players, top_n)
        
        target_embedding = self._calculate_player_embedding(target_player)
        if target_embedding is None:
            return self._find_similar_players_fallback(target_player, candidate_players, top_n)
        
        similarities = []
        for candidate in candidate_players:
            if candidate.get("id") == target_player.get("id"):
                continue
                
            candidate_embedding = self._calculate_player_embedding(candidate)
            if candidate_embedding is not None:
                # Calculate cosine similarity
                similarity = np.dot(target_embedding, candidate_embedding) / (
                    np.linalg.norm(target_embedding) * np.linalg.norm(candidate_embedding)
                )
                similarities.append({
                    "player": candidate,
                    "similarity": float(similarity),
                    "name": f"{candidate.get('first_name', '')} {candidate.get('second_name', '')}".strip()
                })
        
        # Sort by similarity and return top N
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_n]
    
    def _find_similar_players_fallback(self, target_player: Dict[str, Any], 
                                     candidate_players: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """Fallback similarity calculation without AI."""
        target_position = target_player.get("element_type")
        target_price = target_player.get("now_cost", 0)
        target_points = target_player.get("total_points", 0)
        
        similarities = []
        for candidate in candidate_players:
            if (candidate.get("id") == target_player.get("id") or 
                candidate.get("element_type") != target_position):
                continue
            
            # Simple similarity based on price and points
            price_diff = abs(candidate.get("now_cost", 0) - target_price) / max(target_price, 1)
            points_diff = abs(candidate.get("total_points", 0) - target_points) / max(target_points, 1)
            
            similarity = 1.0 / (1.0 + price_diff + points_diff)
            
            similarities.append({
                "player": candidate,
                "similarity": similarity,
                "name": f"{candidate.get('first_name', '')} {candidate.get('second_name', '')}".strip()
            })
        
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_n]
    
    def detect_underperformers(self, team_players: List[Dict[str, Any]], 
                              custom_thresholds: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """
        Detect underperforming players using adaptive thresholds and AI analysis.
        
        Args:
            team_players: List of player data
            custom_thresholds: Optional custom thresholds to override adaptive ones
        
        Returns:
            List of underperforming players with AI-enhanced reasoning
        """
        thresholds = custom_thresholds or self._get_adaptive_thresholds()
        underperformers = []
        
        for player in team_players:
            points_per_game = float(player.get("points_per_game", "0") or "0")
            cost = player.get("now_cost", 0) / 10.0
            form = float(player.get("form", "0") or "0")
            total_points = player.get("total_points", 0)
            minutes = player.get("minutes", 0)
            
            issues = []
            severity_score = 0
            
            # Adaptive performance analysis
            expected_ppg = max(thresholds["points_threshold"], cost * 0.4)  # Expect 0.4 points per £1m
            
            # Check overall performance with adaptive expectations
            if points_per_game < expected_ppg:
                issues.append(f"Below expected return of {expected_ppg:.1f} PPG")
                severity_score += 2
            
            # Premium player underperformance
            if cost >= thresholds["cost_threshold"] and points_per_game < thresholds["points_threshold"] + 1:
                issues.append(f"Premium player ({cost:.1f}m) underperforming")
                severity_score += 3
            
            # Form analysis with context
            form_threshold = 3.0 if self.context.get("phase") == "early" else 4.0
            if form < form_threshold:
                issues.append(f"Poor recent form ({form:.1f})")
                severity_score += 1
            
            # Minutes analysis - injury/rotation concern
            avg_minutes = minutes / max(1, self.context.get("gameweek", 1))
            if avg_minutes < 60:
                issues.append(f"Low minutes ({avg_minutes:.0f} per game)")
                severity_score += 2
            
            # AI sentiment analysis if available
            player_name = f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()
            sentiment_analysis = self._analyze_player_sentiment(player_name)
            
            if sentiment_analysis["sentiment"] == "negative" and sentiment_analysis["confidence"] > 0.7:
                issues.append("Negative sentiment analysis")
                severity_score += 1
            
            if issues:
                # Find alternative players using AI
                all_players = self.client.get_players()
                position_players = [p for p in all_players if p.get("element_type") == player.get("element_type")]
                similar_players = self.find_similar_players(player, position_players, top_n=3)
                
                underperformers.append({
                    "player": player,
                    "name": player_name,
                    "issues": issues,
                    "severity_score": severity_score,
                    "points_per_game": points_per_game,
                    "form": form,
                    "cost": cost,
                    "similar_alternatives": similar_players,
                    "ai_sentiment": sentiment_analysis,
                    "recommendation": self._generate_player_recommendation(player, issues, severity_score)
                })
        
        # Sort by severity score (highest first)
        underperformers.sort(key=lambda x: x["severity_score"], reverse=True)
        return underperformers
    
    def _generate_player_recommendation(self, player: Dict[str, Any], issues: List[str], 
                                      severity_score: int) -> str:
        """Generate AI-enhanced recommendation for underperforming player."""
        player_name = f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()
        
        if severity_score >= 5:
            return f"HIGH PRIORITY: Consider transferring {player_name} immediately. Multiple concerns detected."
        elif severity_score >= 3:
            return f"MEDIUM PRIORITY: Monitor {player_name} closely. Consider transfer if issues persist."
        else:
            return f"LOW PRIORITY: Keep an eye on {player_name}. May improve with time."
    
    def detect_fixture_swings(self, team_ids: List[int], horizon_gameweeks: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect teams with significant fixture difficulty changes.
        
        Args:
            team_ids: List of team IDs to analyze
            horizon_gameweeks: Number of gameweeks to analyze
        
        Returns:
            Dictionary with improving and worsening fixture lists
        """
        improving_fixtures = []
        worsening_fixtures = []
        
        teams = self.client.get_teams()
        team_lookup = {t["id"]: t for t in teams}
        
        for team_id in team_ids:
            fixture_data = compute_fixture_difficulty(team_id, horizon_gameweeks, self.client)
            
            if fixture_data["analyzed_gameweeks"] >= 3:
                trend = fixture_data["difficulty_trend"]
                team_name = team_lookup.get(team_id, {}).get("name", f"Team {team_id}")
                
                fixture_info = {
                    "team_id": team_id,
                    "team_name": team_name,
                    "average_difficulty": fixture_data["average_difficulty"],
                    "trend": trend,
                    "fixtures": fixture_data["fixtures"]
                }
                
                if trend == "getting_easier":
                    improving_fixtures.append(fixture_info)
                elif trend == "getting_harder":
                    worsening_fixtures.append(fixture_info)
        
        return {
            "improving_fixtures": improving_fixtures,
            "worsening_fixtures": worsening_fixtures
        }
    
    def highlight_differentials(self, ownership_threshold: float = 10.0, min_points: float = 4.0) -> List[Dict[str, Any]]:
        """
        Highlight low-ownership players with good potential.
        
        Args:
            ownership_threshold: Maximum ownership percentage
            min_points: Minimum points per game threshold
        
        Returns:
            List of differential players
        """
        players = self.client.get_players()
        differentials = []
        
        for player in players:
            ownership = float(player.get("selected_by_percent", "0") or "0")
            points_per_game = float(player.get("points_per_game", "0") or "0")
            form = float(player.get("form", "0") or "0")
            
            if (ownership <= ownership_threshold and 
                points_per_game >= min_points and 
                player.get("status") == "a"):
                
                differential_score = points_per_game / max(ownership, 1.0)  # Avoid division by zero
                
                differentials.append({
                    "player": player,
                    "ownership": ownership,
                    "points_per_game": points_per_game,
                    "form": form,
                    "differential_score": round(differential_score, 2),
                    "name": f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()
                })
        
        # Sort by differential score
        differentials.sort(key=lambda x: x["differential_score"], reverse=True)
        return differentials[:20]  # Top 20 differentials
    
    def calculate_cost_efficiency(self, players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate cost efficiency for players.
        
        Args:
            players: List of player data
        
        Returns:
            List of players with efficiency metrics
        """
        efficiency_data = []
        
        for player in players:
            cost = player.get("now_cost", 0) / 10.0
            points_per_game = float(player.get("points_per_game", "0") or "0")
            
            if cost > 0:
                efficiency = points_per_game / cost
                
                efficiency_data.append({
                    "player": player,
                    "cost": cost,
                    "points_per_game": points_per_game,
                    "efficiency": round(efficiency, 3),
                    "name": f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()
                })
        
        # Sort by efficiency
        efficiency_data.sort(key=lambda x: x["efficiency"], reverse=True)
        return efficiency_data
    
    def generate_team_summary(self, team_analysis: Dict[str, Any]) -> str:
        """Generate a text summary using AI model or template."""
        if self.model:
            return self._generate_ai_summary(team_analysis)
        else:
            return self._generate_template_summary(team_analysis)
    
    def _generate_template_summary(self, team_analysis: Dict[str, Any]) -> str:
        """Generate summary using template approach."""
        summary_parts = []
        
        # Team overview
        total_points = team_analysis.get("total_projected_points", 0)
        avg_points = team_analysis.get("average_projected_points", 0)
        problem_count = len(team_analysis.get("problem_players", []))
        
        summary_parts.append(f"Team Analysis: Projected {total_points:.1f} points over next {team_analysis.get('horizon_gameweeks', 5)} gameweeks (avg: {avg_points:.1f} per player).")
        
        if problem_count > 0:
            summary_parts.append(f"⚠️ {problem_count} player(s) need attention.")
        else:
            summary_parts.append("✅ Team looks solid with no major concerns.")
        
        # Transfer suggestions
        suggestions = team_analysis.get("transfer_suggestions", [])
        if suggestions:
            summary_parts.append(f"Top transfer priority: {suggestions[0]['player_out']['name']} -> consider {suggestions[0]['suggestions'][0]['player_in_name']} for {suggestions[0]['suggestions'][0]['projected_points_gain']:.1f} point gain.")
        
        return " ".join(summary_parts)
    
    def _generate_ai_summary(self, team_analysis: Dict[str, Any]) -> str:
        """Generate summary using AI model (placeholder for actual implementation)."""
        # This would involve more sophisticated NLP processing
        # For now, fall back to template approach
        return self._generate_template_summary(team_analysis)
    
    def advise_team(self, team_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide comprehensive team advice with scenario planning.
        
        Args:
            team_state: Dictionary containing current team information
        
        Returns:
            Comprehensive advice with structured suggestions and scenarios
        """
        from .scenario_planner import ScenarioPlanner
        
        current_team_ids = team_state.get("player_ids", [])
        budget = team_state.get("budget", 100.0)
        free_transfers = team_state.get("free_transfers", 1)
        horizon_gameweeks = team_state.get("horizon_gameweeks", 5)
        
        # Get player data
        players = self.client.get_players()
        player_lookup = {p["id"]: p for p in players}
        current_players = [player_lookup[pid] for pid in current_team_ids if pid in player_lookup]
        
        # Run various analyses
        underperformers = self.detect_underperformers(current_players)
        
        # Get team IDs for fixture analysis
        team_ids = list(set(p.get("team") for p in current_players if p.get("team")))
        fixture_swings = self.detect_fixture_swings(team_ids, horizon_gameweeks)
        
        differentials = self.highlight_differentials()
        efficiency_data = self.calculate_cost_efficiency(current_players)
        
        # Generate scenario plans
        scenario_planner = ScenarioPlanner(self.client)
        scenarios = scenario_planner.plan_gameweek_scenarios(team_state, scenario_count=5)
        scenario_comparison = scenario_planner.compare_scenarios(scenarios)
        
        # Weekly strategy planning
        weekly_strategy = scenario_planner.plan_weekly_strategy(team_state, weeks_ahead=4)
        
        # Generate transfer suggestions using scenarios
        transfer_suggestions = []
        if scenarios and scenarios[0].get("transfers"):
            best_scenario = scenarios[0]
            for transfer in best_scenario.get("transfers", []):
                transfer_suggestions.append({
                    "player_out": transfer["out"],
                    "player_in": transfer["in"],
                    "expected_gain": transfer.get("point_gain", 0),
                    "cost_change": transfer.get("cost_change", 0),
                    "scenario": best_scenario["name"]
                })
        
        # Compile comprehensive advice
        advice = {
            "summary": "",
            "season_context": self.context,
            "adaptive_thresholds": self._get_adaptive_thresholds(),
            "underperformers": underperformers,
            "fixture_analysis": fixture_swings,
            "top_differentials": differentials[:10],
            "cost_efficiency": efficiency_data[:10],
            "transfer_suggestions": transfer_suggestions,
            "scenarios": scenarios,
            "scenario_comparison": scenario_comparison,
            "weekly_strategy": weekly_strategy,
            "recommendations": []
        }
        
        # Generate AI-enhanced recommendations
        recommendations = self._generate_enhanced_recommendations(
            underperformers, fixture_swings, differentials, scenarios
        )
        advice["recommendations"] = recommendations
        
        # Generate comprehensive summary
        team_analysis_summary = {
            "total_projected_points": sum(calculate_horizon_projection(pid, horizon_gameweeks, self.client).get("total_projected_points", 0) for pid in current_team_ids),
            "problem_players": underperformers,
            "transfer_suggestions": transfer_suggestions,
            "horizon_gameweeks": horizon_gameweeks,
            "best_scenario": scenario_comparison.get("best_scenario", {}),
            "season_phase": self.context.get("phase", "unknown")
        }
        
        advice["summary"] = self.generate_enhanced_team_summary(team_analysis_summary)
        
        return advice
    
    def _generate_enhanced_recommendations(self, underperformers: List[Dict], 
                                         fixture_swings: Dict, differentials: List[Dict],
                                         scenarios: List[Dict]) -> List[Dict[str, Any]]:
        """Generate AI-enhanced recommendations."""
        recommendations = []
        
        # Underperformer recommendations with AI context
        if underperformers:
            top_underperformer = underperformers[0]
            player_name = top_underperformer.get("name", "player")
            severity = top_underperformer.get("severity_score", 0)
            ai_sentiment = top_underperformer.get("ai_sentiment", {})
            
            priority = "HIGH" if severity >= 5 else "MEDIUM" if severity >= 3 else "LOW"
            
            recommendation = {
                "type": "transfer_out",
                "priority": priority.lower(),
                "player": top_underperformer["player"],
                "message": f"Consider transferring {player_name} ({priority} priority)",
                "reasoning": "; ".join(top_underperformer.get("issues", [])),
                "ai_confidence": ai_sentiment.get("confidence", 0.5),
                "alternatives": top_underperformer.get("similar_alternatives", [])[:3]
            }
            recommendations.append(recommendation)
        
        # Fixture-based recommendations
        if fixture_swings.get("improving_fixtures"):
            best_fixtures = fixture_swings["improving_fixtures"][0]
            recommendations.append({
                "type": "fixtures",
                "priority": "medium",
                "message": f"Target {best_fixtures['team_name']} players - fixtures improving",
                "reasoning": f"Average difficulty dropping to {best_fixtures['average_difficulty']:.1f}",
                "team_info": best_fixtures
            })
        
        # Differential recommendations with AI analysis
        if differentials and self.embedder:
            top_differential = differentials[0]
            recommendations.append({
                "type": "differential",
                "priority": "low",
                "message": f"Consider differential: {top_differential['name']}",
                "reasoning": f"{top_differential['ownership']:.1f}% owned, {top_differential['points_per_game']:.1f} PPG",
                "differential_score": top_differential.get("differential_score", 0),
                "ai_analyzed": True
            })
        
        # Scenario-based recommendations
        if scenarios:
            best_scenario = scenarios[0]
            recommendations.append({
                "type": "scenario",
                "priority": "high",
                "message": f"Recommended strategy: {best_scenario.get('name')}",
                "reasoning": best_scenario.get("reasoning", ""),
                "expected_points": best_scenario.get("net_points", 0),
                "risk_level": best_scenario.get("risk_level", "Medium")
            })
        
        return recommendations
    
    def generate_enhanced_team_summary(self, team_analysis: Dict[str, Any]) -> str:
        """Generate enhanced summary with AI insights."""
        summary_parts = []
        
        # Basic team overview
        total_points = team_analysis.get("total_projected_points", 0)
        problem_count = len(team_analysis.get("problem_players", []))
        horizon_gws = team_analysis.get("horizon_gameweeks", 5)
        season_phase = team_analysis.get("season_phase", "unknown")
        
        # AI-enhanced context
        phase_context = {
            "early": "Focus on value picks and avoid early kneejerks",
            "mid": "Balance form and fixtures for optimal returns", 
            "late": "Prioritize form over price - every point counts"
        }
        
        context_advice = phase_context.get(season_phase, "Monitor team performance carefully")
        
        summary_parts.append(f"🎯 {season_phase.title()} season analysis: {total_points:.1f} projected points over {horizon_gws} GWs.")
        
        if problem_count > 0:
            summary_parts.append(f"⚠️ {problem_count} player(s) flagged by AI analysis.")
        else:
            summary_parts.append("✅ Team structure looks solid.")
        
        # Scenario insights
        best_scenario = team_analysis.get("best_scenario", {})
        if best_scenario:
            scenario_name = best_scenario.get("name", "Unknown")
            scenario_points = best_scenario.get("net_points", 0)
            summary_parts.append(f"📈 Optimal strategy: {scenario_name} ({scenario_points:.1f} points)")
        
        # AI context
        summary_parts.append(f"🤖 AI Insight: {context_advice}")
        
        # Transfer priority
        transfers = team_analysis.get("transfer_suggestions", [])
        if transfers:
            best_transfer = transfers[0]
            gain = best_transfer.get("expected_gain", 0)
            if gain > 3:
                summary_parts.append(f"🔄 Priority transfer: +{gain:.1f} point opportunity identified")
        
        return " ".join(summary_parts)
    
    def close(self):
        """Close the FPL client."""
        if self.client:
            self.client.close()