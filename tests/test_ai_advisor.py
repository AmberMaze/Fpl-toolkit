"""Test AI advisor functionality."""
import pytest
from unittest.mock import Mock, patch
from src.fpl_toolkit.ai.advisor import FPLAdvisor


class TestFPLAdvisor:
    """Test AI advisor functionality."""
    
    def setup_method(self):
        """Setup test method."""
        with patch('src.fpl_toolkit.ai.advisor.FPLClient'):
            self.advisor = FPLAdvisor()
    
    def test_detect_underperformers_basic(self):
        """Test basic underperformer detection."""
        team_players = [
            {
                "id": 1,
                "first_name": "Good",
                "second_name": "Player",
                "points_per_game": "5.5",
                "now_cost": 80,  # £8.0m
                "form": "4.5",
                "status": "a"
            },
            {
                "id": 2,
                "first_name": "Bad",
                "second_name": "Player",
                "points_per_game": "2.0",  # Below threshold
                "now_cost": 60,
                "form": "1.5",  # Poor form
                "status": "a"
            },
            {
                "id": 3,
                "first_name": "Expensive",
                "second_name": "Underperformer",
                "points_per_game": "4.0",  # Low for premium player
                "now_cost": 120,  # £12.0m premium
                "form": "3.0",
                "status": "a"
            }
        ]
        
        underperformers = self.advisor.detect_underperformers(team_players)
        
        # Should find 2 underperformers (players 2 and 3)
        assert len(underperformers) == 2
        
        # Check that expensive underperformer has higher priority
        priorities = [u["priority"] for u in underperformers]
        assert max(priorities) >= 2  # Premium underperformer should have high priority
    
    def test_detect_underperformers_injury(self):
        """Test underperformer detection with injured players."""
        team_players = [
            {
                "id": 1,
                "first_name": "Injured",
                "second_name": "Player",
                "points_per_game": "6.0",
                "now_cost": 80,
                "form": "5.0",
                "status": "i"  # Injured
            }
        ]
        
        underperformers = self.advisor.detect_underperformers(team_players)
        
        assert len(underperformers) == 1
        assert "Injury/suspension concerns" in underperformers[0]["issues"]
    
    @patch('src.fpl_toolkit.ai.advisor.compute_fixture_difficulty')
    def test_detect_fixture_swings(self, mock_compute):
        """Test fixture difficulty swing detection."""
        # Mock teams data
        self.advisor.client.get_teams.return_value = [
            {"id": 1, "name": "Team A"},
            {"id": 2, "name": "Team B"}
        ]
        
        # Mock fixture difficulty results
        mock_compute.side_effect = [
            {
                "analyzed_gameweeks": 5,
                "difficulty_trend": "getting_easier",
                "average_difficulty": 2.5,
                "fixtures": []
            },
            {
                "analyzed_gameweeks": 5,
                "difficulty_trend": "getting_harder",
                "average_difficulty": 4.0,
                "fixtures": []
            }
        ]
        
        result = self.advisor.detect_fixture_swings([1, 2])
        
        assert len(result["improving_fixtures"]) == 1
        assert len(result["worsening_fixtures"]) == 1
        assert result["improving_fixtures"][0]["team_name"] == "Team A"
        assert result["worsening_fixtures"][0]["team_name"] == "Team B"
    
    def test_highlight_differentials(self):
        """Test differential player highlighting."""
        # Mock players data
        players = [
            {
                "id": 1,
                "first_name": "Popular",
                "second_name": "Player",
                "selected_by_percent": "25.0",  # High ownership
                "points_per_game": "6.0",
                "status": "a"
            },
            {
                "id": 2,
                "first_name": "Differential",
                "second_name": "Player",
                "selected_by_percent": "5.0",  # Low ownership
                "points_per_game": "5.0",  # Good points
                "form": "4.0",
                "status": "a"
            },
            {
                "id": 3,
                "first_name": "Bad",
                "second_name": "Differential",
                "selected_by_percent": "3.0",  # Low ownership
                "points_per_game": "2.0",  # Poor points
                "form": "1.0",
                "status": "a"
            }
        ]
        
        self.advisor.client.get_players.return_value = players
        
        differentials = self.advisor.highlight_differentials()
        
        # Should only include player 2 (low ownership + good points)
        assert len(differentials) == 1
        assert differentials[0]["player"]["id"] == 2
        assert differentials[0]["ownership"] == 5.0
        assert differentials[0]["differential_score"] > 0
    
    def test_calculate_cost_efficiency(self):
        """Test cost efficiency calculation."""
        players = [
            {
                "id": 1,
                "first_name": "Efficient",
                "second_name": "Player",
                "now_cost": 80,  # £8.0m
                "points_per_game": "6.0"  # Good efficiency: 6.0/8.0 = 0.75
            },
            {
                "id": 2,
                "first_name": "Inefficient",
                "second_name": "Player",
                "now_cost": 120,  # £12.0m
                "points_per_game": "4.0"  # Poor efficiency: 4.0/12.0 = 0.33
            }
        ]
        
        efficiency_data = self.advisor.calculate_cost_efficiency(players)
        
        assert len(efficiency_data) == 2
        # Should be sorted by efficiency (highest first)
        assert efficiency_data[0]["efficiency"] > efficiency_data[1]["efficiency"]
        assert efficiency_data[0]["player"]["id"] == 1
    
    def test_generate_template_summary(self):
        """Test template summary generation."""
        team_analysis = {
            "total_projected_points": 75.5,
            "average_projected_points": 5.0,
            "horizon_gameweeks": 5,
            "problem_players": [{"player": {"name": "Problem Player"}}],
            "transfer_suggestions": [
                {
                    "player_out": {"name": "Out Player"},
                    "suggestions": [
                        {
                            "player_in_name": "In Player",
                            "projected_points_gain": 3.2
                        }
                    ]
                }
            ]
        }
        
        summary = self.advisor._generate_template_summary(team_analysis)
        
        assert "75.5 points" in summary
        assert "5.0 per player" in summary
        assert "1 player(s) need attention" in summary
        assert "In Player" in summary
        assert "3.2 point gain" in summary
    
    @patch('src.fpl_toolkit.ai.advisor.calculate_horizon_projection')
    @patch('src.fpl_toolkit.ai.advisor.find_transfer_targets')
    def test_advise_team_comprehensive(self, mock_targets, mock_projection):
        """Test comprehensive team advice generation."""
        # Mock player data
        self.advisor.client.get_players.return_value = [
            {
                "id": 1,
                "first_name": "Good",
                "second_name": "Player",
                "now_cost": 80,
                "team": 1,
                "form": "5.0",
                "status": "a",
                "points_per_game": "6.0"
            },
            {
                "id": 2,
                "first_name": "Problem",
                "second_name": "Player",
                "now_cost": 90,
                "team": 2,
                "form": "1.0",
                "status": "i",
                "points_per_game": "2.0"
            }
        ]
        
        # Mock projections
        mock_projection.side_effect = [
            {"total_projected_points": 25.0},
            {"total_projected_points": 5.0}
        ]
        
        # Mock transfer targets
        mock_targets.return_value = [
            {
                "player_in_name": "Better Player",
                "projected_points_gain": 8.0
            }
        ]
        
        # Mock fixture analysis
        with patch.object(self.advisor, 'detect_fixture_swings') as mock_fixtures:
            mock_fixtures.return_value = {
                "improving_fixtures": [],
                "worsening_fixtures": []
            }
            
            # Mock differentials
            with patch.object(self.advisor, 'highlight_differentials') as mock_diffs:
                mock_diffs.return_value = [
                    {
                        "name": "Differential Pick",
                        "ownership": 3.5,
                        "points_per_game": 5.0
                    }
                ]
                
                team_state = {
                    "player_ids": [1, 2],
                    "budget": 1.0,
                    "free_transfers": 1,
                    "horizon_gameweeks": 5
                }
                
                advice = self.advisor.advise_team(team_state)
                
                assert "summary" in advice
                assert "underperformers" in advice
                assert "transfer_suggestions" in advice
                assert "recommendations" in advice
                assert "fixture_analysis" in advice
                assert "top_differentials" in advice
                
                # Should identify problem player
                assert len(advice["underperformers"]) == 1
                assert advice["underperformers"][0]["player"]["id"] == 2
                
                # Should have transfer suggestions
                assert len(advice["transfer_suggestions"]) == 1
                
                # Should have recommendations
                assert len(advice["recommendations"]) > 0
    
    def test_model_loading_fallback(self):
        """Test that advisor works without sentence-transformers."""
        with patch('src.fpl_toolkit.ai.advisor.FPLClient'):
            # Test with ImportError (no sentence-transformers)
            with patch('src.fpl_toolkit.ai.advisor.SentenceTransformer', side_effect=ImportError):
                advisor = FPLAdvisor()
                assert advisor.model is None
                
                # Should still generate summaries using template
                team_analysis = {
                    "total_projected_points": 50.0,
                    "average_projected_points": 5.0,
                    "horizon_gameweeks": 3,
                    "problem_players": [],
                    "transfer_suggestions": []
                }
                
                summary = advisor.generate_team_summary(team_analysis)
                assert isinstance(summary, str)
                assert "50.0 points" in summary