"""Test decision support functionality."""
import pytest
from unittest.mock import Mock, patch
from src.fpl_toolkit.analysis.decisions import (
    analyze_transfer_scenario,
    find_transfer_targets,
    analyze_multiple_transfers,
    evaluate_team_decisions
)


class TestDecisionSupport:
    """Test decision support functions."""
    
    @patch('src.fpl_toolkit.analysis.decisions.FPLClient')
    @patch('src.fpl_toolkit.analysis.decisions.calculate_horizon_projection')
    def test_analyze_transfer_scenario_basic(self, mock_projection, mock_client_class):
        """Test basic transfer scenario analysis."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock player data
        players = [
            {
                "id": 1,
                "first_name": "Player",
                "second_name": "One",
                "now_cost": 80,  # £8.0m
                "form": "3.0",
                "selected_by_percent": "15.5",
                "status": "a"
            },
            {
                "id": 2,
                "first_name": "Player",
                "second_name": "Two",
                "now_cost": 90,  # £9.0m
                "form": "5.0",
                "selected_by_percent": "8.2",
                "status": "a"
            }
        ]
        
        mock_client.get_players.return_value = players
        
        # Mock projections
        mock_projection.side_effect = [
            {
                "total_projected_points": 20.0,
                "average_confidence": 0.7
            },
            {
                "total_projected_points": 25.0,
                "average_confidence": 0.8
            }
        ]
        
        result = analyze_transfer_scenario(1, 2, 5, mock_client)
        
        assert "error" not in result
        assert result["player_out_id"] == 1
        assert result["player_in_id"] == 2
        assert result["player_out_name"] == "Player One"
        assert result["player_in_name"] == "Player Two"
        assert result["cost_change"] == 1.0  # £9.0m - £8.0m
        assert result["projected_points_gain"] == 5.0  # 25.0 - 20.0
        assert result["confidence_score"] == 0.75  # (0.7 + 0.8) / 2
        assert result["recommendation"] in ["Strongly Recommended", "Recommended", "Consider", "Neutral", "Not Recommended"]
    
    @patch('src.fpl_toolkit.analysis.decisions.FPLClient')
    def test_analyze_transfer_scenario_player_not_found(self, mock_client_class):
        """Test transfer scenario with non-existent player."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_client.get_players.return_value = []
        
        result = analyze_transfer_scenario(1, 2, 5, mock_client)
        
        assert "error" in result
        assert result["error"] == "One or both players not found"
    
    @patch('src.fpl_toolkit.analysis.decisions.FPLClient')
    @patch('src.fpl_toolkit.analysis.decisions.analyze_transfer_scenario')
    def test_find_transfer_targets(self, mock_analyze, mock_client_class):
        """Test finding transfer targets."""
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Mock player data
        player_out = {
            "id": 1,
            "now_cost": 80,  # £8.0m
            "element_type": 3,  # Midfielder
            "status": "a"
        }
        
        candidates = [
            {
                "id": 2,
                "now_cost": 85,  # £8.5m
                "element_type": 3,  # Same position
                "status": "a"
            },
            {
                "id": 3,
                "now_cost": 95,  # £9.5m - too expensive with max_cost_increase=1.0
                "element_type": 3,
                "status": "a"
            },
            {
                "id": 4,
                "now_cost": 75,  # £7.5m
                "element_type": 2,  # Different position
                "status": "a"
            }
        ]
        
        all_players = [player_out] + candidates
        mock_client.get_players.return_value = all_players
        
        # Mock scenario analysis - only player 2 should be analyzed
        mock_analyze.return_value = {
            "player_in_id": 2,
            "projected_points_gain": 3.0,
            "cost_change": 0.5,
            "recommendation": "Recommended"
        }
        
        result = find_transfer_targets(1, max_cost_increase=1.0, same_position_only=True, limit=5)
        
        # Should only find player 2 (same position, within cost limit)
        mock_analyze.assert_called_once()
        assert len(result) == 1
        assert result[0]["player_in_id"] == 2
    
    @patch('src.fpl_toolkit.analysis.decisions.FPLClient')
    @patch('src.fpl_toolkit.analysis.decisions.analyze_transfer_scenario')
    def test_analyze_multiple_transfers(self, mock_analyze, mock_client_class):
        """Test analyzing multiple transfers together."""
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Mock transfer scenarios
        mock_analyze.side_effect = [
            {
                "cost_change": 1.0,
                "projected_points_gain": 3.0,
                "confidence_score": 0.8,
                "risk_score": 0.3
            },
            {
                "cost_change": -0.5,
                "projected_points_gain": 2.0,
                "confidence_score": 0.7,
                "risk_score": 0.4
            }
        ]
        
        transfer_pairs = [(1, 2), (3, 4)]
        result = analyze_multiple_transfers(transfer_pairs, horizon_gameweeks=5)
        
        assert len(result["scenarios"]) == 2
        assert result["total_cost_change"] == 0.5  # 1.0 + (-0.5)
        assert result["total_projected_points_gain"] == 5.0  # 3.0 + 2.0
        assert result["average_confidence"] == 0.75  # (0.8 + 0.7) / 2
        assert result["average_risk_score"] == 0.35  # (0.3 + 0.4) / 2
        assert result["transfer_count"] == 2
        assert result["overall_recommendation"] in ["Strongly Recommended", "Recommended", "Consider", "Not Recommended"]
    
    @patch('src.fpl_toolkit.analysis.decisions.FPLClient')
    @patch('src.fpl_toolkit.analysis.decisions.calculate_horizon_projection')
    @patch('src.fpl_toolkit.analysis.decisions.find_transfer_targets')
    def test_evaluate_team_decisions(self, mock_targets, mock_projection, mock_client_class):
        """Test team-wide decision evaluation."""
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Mock player data
        players = [
            {
                "id": 1,
                "first_name": "Good",
                "second_name": "Player",
                "now_cost": 80,
                "status": "a",
                "form": "5.0"
            },
            {
                "id": 2,
                "first_name": "Problem",
                "second_name": "Player",
                "now_cost": 90,
                "status": "i",  # Injured
                "form": "1.0"
            }
        ]
        
        mock_client.get_players.return_value = players
        
        # Mock projections
        mock_projection.side_effect = [
            {
                "total_projected_points": 25.0,
                "player_id": 1
            },
            {
                "total_projected_points": 5.0,  # Low due to injury
                "player_id": 2
            }
        ]
        
        # Mock transfer targets for problem player
        mock_targets.return_value = [
            {
                "player_in_name": "Better Player",
                "projected_points_gain": 10.0
            }
        ]
        
        current_team_ids = [1, 2]
        result = evaluate_team_decisions(current_team_ids, budget=0.5, free_transfers=1)
        
        assert len(result["team_analysis"]) == 2
        assert result["total_projected_points"] == 30.0  # 25.0 + 5.0
        assert result["average_projected_points"] == 15.0
        assert len(result["problem_players"]) == 1  # Player 2 should be flagged
        assert result["problem_players"][0]["player"]["id"] == 2
        assert len(result["transfer_suggestions"]) == 1  # Should suggest replacing problem player
        assert result["free_transfers"] == 1
        assert result["budget"] == 0.5
    
    def test_analyze_transfer_scenario_risk_factors(self):
        """Test risk factor calculation in transfer scenario."""
        # This would test the specific risk calculation logic
        # For now, we'll test that the function handles edge cases
        
        # Test with mock data that should trigger various risk factors
        with patch('src.fpl_toolkit.analysis.decisions.FPLClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # High cost, poor form player coming in
            players = [
                {
                    "id": 1,
                    "first_name": "Player",
                    "second_name": "Out",
                    "now_cost": 80,
                    "form": "6.0",  # Good form
                    "selected_by_percent": "25.0",  # Popular
                    "status": "a"
                },
                {
                    "id": 2,
                    "first_name": "Player",
                    "second_name": "In",
                    "now_cost": 120,  # Expensive
                    "form": "2.0",  # Poor form
                    "selected_by_percent": "3.0",  # Differential
                    "status": "d"  # Doubtful
                }
            ]
            
            mock_client.get_players.return_value = players
            
            with patch('src.fpl_toolkit.analysis.decisions.calculate_horizon_projection') as mock_proj:
                mock_proj.side_effect = [
                    {"total_projected_points": 20.0, "average_confidence": 0.8},
                    {"total_projected_points": 18.0, "average_confidence": 0.4}
                ]
                
                result = analyze_transfer_scenario(1, 2, 5, mock_client)
                
                # Should have high risk score due to multiple risk factors
                assert result["risk_score"] > 0.5
                assert len(result["risk_factors"]) > 0
                assert result["recommendation"] in ["Not Recommended", "Consider"]