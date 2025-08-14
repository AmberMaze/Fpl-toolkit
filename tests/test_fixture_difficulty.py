"""Test fixture difficulty analysis."""
import pytest
from unittest.mock import Mock, patch
from src.fpl_toolkit.analysis.fixtures import (
    compute_fixture_difficulty, 
    calculate_opponent_difficulty,
    get_fixture_difficulty_rankings,
    compare_team_fixtures
)


class TestFixtureDifficulty:
    """Test fixture difficulty analysis functions."""
    
    def test_calculate_opponent_difficulty_empty(self):
        """Test opponent difficulty calculation with empty data."""
        result = calculate_opponent_difficulty({})
        assert result == 3.0
    
    def test_calculate_opponent_difficulty_normal(self):
        """Test opponent difficulty calculation with normal data."""
        opponent_team = {
            "strength_overall_home": 4,
            "strength_overall_away": 3,
            "strength_attack_home": 4,
            "strength_attack_away": 3,
            "strength_defence_home": 4,
            "strength_defence_away": 3
        }
        
        result = calculate_opponent_difficulty(opponent_team)
        expected = (4 + 3 + 4 + 3 + 4 + 3) / 6.0
        assert result == expected
    
    def test_calculate_opponent_difficulty_bounds(self):
        """Test opponent difficulty calculation bounds."""
        # Test minimum bound
        weak_team = {
            "strength_overall_home": 1,
            "strength_overall_away": 1,
            "strength_attack_home": 1,
            "strength_attack_away": 1,
            "strength_defence_home": 1,
            "strength_defence_away": 1
        }
        
        result = calculate_opponent_difficulty(weak_team)
        assert result >= 1.0
        
        # Test maximum bound
        strong_team = {
            "strength_overall_home": 5,
            "strength_overall_away": 5,
            "strength_attack_home": 5,
            "strength_attack_away": 5,
            "strength_defence_home": 5,
            "strength_defence_away": 5
        }
        
        result = calculate_opponent_difficulty(strong_team)
        assert result <= 5.0
    
    @patch('src.fpl_toolkit.analysis.fixtures.FPLClient')
    def test_compute_fixture_difficulty_no_fixtures(self, mock_client_class):
        """Test fixture difficulty computation with no fixtures."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_team_fixtures.return_value = []
        mock_client.get_teams.return_value = []
        
        result = compute_fixture_difficulty(1, 5, mock_client)
        
        assert result["team_id"] == 1
        assert result["fixtures"] == []
        assert result["average_difficulty"] == 3.0
        assert result["total_difficulty"] == 0.0
        assert result["home_fixtures"] == 0
        assert result["away_fixtures"] == 0
        assert result["difficulty_trend"] == "neutral"
    
    @patch('src.fpl_toolkit.analysis.fixtures.FPLClient')
    def test_compute_fixture_difficulty_with_fixtures(self, mock_client_class):
        """Test fixture difficulty computation with fixtures."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock fixtures data
        fixtures = [
            {
                "event": 10,
                "team_h": 1,  # Home team
                "team_a": 2,  # Away team
                "kickoff_time": "2024-01-01T15:00:00Z"
            },
            {
                "event": 11,
                "team_h": 3,  # Away fixture for team 1
                "team_a": 1,
                "kickoff_time": "2024-01-08T15:00:00Z"
            }
        ]
        
        teams = [
            {
                "id": 1,
                "name": "Team 1",
                "strength_overall_home": 3,
                "strength_overall_away": 3,
                "strength_attack_home": 3,
                "strength_attack_away": 3,
                "strength_defence_home": 3,
                "strength_defence_away": 3
            },
            {
                "id": 2,
                "name": "Team 2",
                "strength_overall_home": 4,
                "strength_overall_away": 4,
                "strength_attack_home": 4,
                "strength_attack_away": 4,
                "strength_defence_home": 4,
                "strength_defence_away": 4
            },
            {
                "id": 3,
                "name": "Team 3",
                "strength_overall_home": 2,
                "strength_overall_away": 2,
                "strength_attack_home": 2,
                "strength_attack_away": 2,
                "strength_defence_home": 2,
                "strength_defence_away": 2
            }
        ]
        
        mock_client.get_team_fixtures.return_value = fixtures
        mock_client.get_teams.return_value = teams
        
        result = compute_fixture_difficulty(1, 2, mock_client)
        
        assert result["team_id"] == 1
        assert len(result["fixtures"]) == 2
        assert result["home_fixtures"] == 1
        assert result["away_fixtures"] == 1
        assert result["average_difficulty"] > 0
        assert result["difficulty_trend"] in ["neutral", "getting_easier", "getting_harder"]
        
        # Check fixture details
        home_fixture = next(f for f in result["fixtures"] if f["is_home"])
        away_fixture = next(f for f in result["fixtures"] if not f["is_home"])
        
        assert home_fixture["opponent_name"] == "Team 2"
        assert away_fixture["opponent_name"] == "Team 3"
    
    @patch('src.fpl_toolkit.analysis.fixtures.FPLClient')
    def test_get_fixture_difficulty_rankings(self, mock_client_class):
        """Test fixture difficulty rankings."""
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        teams = [
            {"id": 1, "name": "Easy Team"},
            {"id": 2, "name": "Hard Team"}
        ]
        
        mock_client.get_teams.return_value = teams
        
        # Mock different difficulty levels
        with patch('src.fpl_toolkit.analysis.fixtures.compute_fixture_difficulty') as mock_compute:
            mock_compute.side_effect = [
                {
                    "team_id": 1,
                    "average_difficulty": 2.0,
                    "total_difficulty": 10.0,
                    "analyzed_gameweeks": 5,
                    "difficulty_trend": "getting_easier",
                    "home_fixtures": 3,
                    "away_fixtures": 2
                },
                {
                    "team_id": 2,
                    "average_difficulty": 4.0,
                    "total_difficulty": 20.0,
                    "analyzed_gameweeks": 5,
                    "difficulty_trend": "getting_harder",
                    "home_fixtures": 2,
                    "away_fixtures": 3
                }
            ]
            
            result = get_fixture_difficulty_rankings([1, 2], 5)
            
            assert len(result) == 2
            # Should be sorted by difficulty (easiest first)
            assert result[0]["team_id"] == 1
            assert result[0]["average_difficulty"] == 2.0
            assert result[1]["team_id"] == 2
            assert result[1]["average_difficulty"] == 4.0
    
    @patch('src.fpl_toolkit.analysis.fixtures.FPLClient')
    def test_compare_team_fixtures(self, mock_client_class):
        """Test team fixture comparison."""
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        with patch('src.fpl_toolkit.analysis.fixtures.compute_fixture_difficulty') as mock_compute:
            mock_compute.side_effect = [
                {
                    "team_id": 1,
                    "average_difficulty": 2.0,
                    "fixtures": []
                },
                {
                    "team_id": 2,
                    "average_difficulty": 4.0,
                    "fixtures": []
                }
            ]
            
            result = compare_team_fixtures([1, 2], 5)
            
            assert len(result["comparisons"]) == 2
            assert result["easiest_fixtures"]["team_id"] == 1
            assert result["hardest_fixtures"]["team_id"] == 2
            assert result["analyzed_gameweeks"] == 5