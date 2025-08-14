"""Tests for advanced breakdown functionality."""

import pytest
from unittest.mock import Mock, patch, mock_open
import json
from src.fpl_toolkit.analysis.advanced_metrics import (
    get_player_expected_rates,
    load_zone_weakness,
    get_player_zone_side,
    apply_zone_weakness_adjustment,
    enhance_breakdown_with_advanced_metrics,
    _simple_event_breakdown,
    _normalize_player_name,
    _names_match
)


class TestAdvancedMetrics:
    """Test advanced metrics functionality."""
    
    def test_get_player_expected_rates_disabled(self):
        """Test expected rates when ENABLE_UNDERSTAT is disabled."""
        player = {
            "first_name": "Erling",
            "second_name": "Haaland",
            "web_name": "Haaland"
        }
        
        with patch.dict('os.environ', {'ENABLE_UNDERSTAT': '0'}):
            with patch('src.fpl_toolkit.analysis.advanced_metrics._get_local_expected_rates') as mock_local:
                mock_local.return_value = {"xg_per90": 1.28, "xa_per90": 0.15}
                
                result = get_player_expected_rates(player)
                
                mock_local.assert_called_once_with(player)
                assert result["xg_per90"] == 1.28
                assert result["xa_per90"] == 0.15
    
    def test_normalize_player_name(self):
        """Test player name normalization."""
        # Test with web_name
        player1 = {"web_name": "Haaland", "first_name": "Erling", "second_name": "Haaland"}
        assert _normalize_player_name(player1) == "haaland"
        
        # Test without web_name
        player2 = {"first_name": "Mohamed", "second_name": "Salah"}
        assert _normalize_player_name(player2) == "mohamed salah"
        
        # Test with empty web_name
        player3 = {"web_name": "", "first_name": "Bruno", "second_name": "Fernandes"}
        assert _normalize_player_name(player3) == "bruno fernandes"
    
    def test_names_match(self):
        """Test name matching logic."""
        # Exact match
        assert _names_match("haaland", "haaland") is True
        
        # Contains match
        assert _names_match("erling haaland", "haaland") is True
        assert _names_match("haaland", "erling haaland") is True
        
        # Last name match
        assert _names_match("erling haaland", "e. haaland") is True
        
        # No match
        assert _names_match("haaland", "salah") is False
    
    def test_load_zone_weakness_success(self):
        """Test successful zone weakness loading."""
        mock_data = {
            "1": {
                "left_conceded_index": 0.95,
                "center_conceded_index": 1.02,
                "right_conceded_index": 1.03
            }
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            with patch("pathlib.Path.exists", return_value=True):
                result = load_zone_weakness()
                assert result == mock_data
    
    def test_load_zone_weakness_file_not_found(self):
        """Test zone weakness loading when file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            result = load_zone_weakness()
            assert result == {}
    
    def test_get_player_zone_side(self):
        """Test player zone side determination."""
        # Test specific mapping
        assert get_player_zone_side(7, "MID") == "right"  # Sterling
        assert get_player_zone_side(233, "MID") == "left"  # Rashford
        assert get_player_zone_side(283, "FWD") == "center"  # Haaland
        
        # Test default fallback
        assert get_player_zone_side(999, "DEF") == "center"
    
    def test_apply_zone_weakness_adjustment(self):
        """Test zone weakness adjustment application."""
        zone_data = {
            "1": {
                "left_conceded_index": 0.95,
                "center_conceded_index": 1.02,
                "right_conceded_index": 1.05
            }
        }
        
        # Test right zone adjustment
        adjusted, multiplier = apply_zone_weakness_adjustment(
            5.0, 1, "right", zone_data
        )
        assert adjusted == 5.25  # 5.0 * 1.05
        assert multiplier == 1.05
        
        # Test team not in data
        adjusted, multiplier = apply_zone_weakness_adjustment(
            5.0, 999, "right", zone_data
        )
        assert adjusted == 5.0
        assert multiplier == 1.0
    
    def test_simple_event_breakdown(self):
        """Test simple event breakdown generation."""
        player_data = {
            "minutes": 1800,  # 20 games * 90 minutes
            "goals_scored": 10,
            "assists": 5,
            "clean_sheets": 8,
            "bonus": 12
        }
        
        result = _simple_event_breakdown(player_data)
        
        # Check structure
        assert "appearance" in result
        assert "goals" in result
        assert "assists" in result
        assert "cs" in result
        assert "bonus" in result
        assert "misc" in result
        assert "total" in result
        
        # Check values are reasonable
        assert result["appearance"] == 2.0
        assert result["total"] == sum([
            result["appearance"],
            result["goals"],
            result["assists"],
            result["cs"],
            result["bonus"],
            result["misc"]
        ])
    
    def test_enhance_breakdown_with_advanced_metrics(self):
        """Test breakdown enhancement with advanced metrics."""
        base_breakdown = {
            "appearance": 2.0,
            "goals": 3.0,
            "assists": 1.0,
            "cs": 0.5,
            "bonus": 0.8,
            "misc": 0.5
        }
        
        player = {
            "first_name": "Erling",
            "second_name": "Haaland",
            "web_name": "Haaland"
        }
        
        # Mock expected rates
        with patch('src.fpl_toolkit.analysis.advanced_metrics.get_player_expected_rates') as mock_rates:
            mock_rates.return_value = {"xg_per90": 1.2, "xa_per90": 0.3}
            
            # Mock zone weakness
            with patch('src.fpl_toolkit.analysis.advanced_metrics.apply_zone_weakness_adjustment') as mock_zone:
                mock_zone.return_value = (4.2, 1.05)  # 4.0 * 1.05
                
                result = enhance_breakdown_with_advanced_metrics(
                    base_breakdown, player, opponent_team_id=1, player_id=283
                )
                
                # Check adjustments were applied
                assert "adjustments" in result
                assert result["adjustments"]["xg_per90"] == 1.2
                assert result["adjustments"]["xa_per90"] == 0.3
                assert result["adjustments"]["zone_multiplier"] == 1.05
                
                # Check total was recalculated
                assert "total" in result
    
    def test_enhance_breakdown_no_advanced_metrics(self):
        """Test breakdown enhancement with no advanced metrics available."""
        base_breakdown = {
            "appearance": 2.0,
            "goals": 3.0,
            "assists": 1.0,
            "cs": 0.5,
            "bonus": 0.8,
            "misc": 0.5
        }
        
        player = {"first_name": "Unknown", "second_name": "Player"}
        
        # Mock no expected rates available
        with patch('src.fpl_toolkit.analysis.advanced_metrics.get_player_expected_rates') as mock_rates:
            mock_rates.return_value = {"xg_per90": None, "xa_per90": None}
            
            result = enhance_breakdown_with_advanced_metrics(base_breakdown, player)
            
            # Should return enhanced breakdown without adjustments
            assert result["appearance"] == 2.0
            assert result["goals"] == 3.0
            assert result["assists"] == 1.0
            # No adjustments block should be present if no metrics applied
            if "adjustments" in result:
                # Only zone_multiplier might be present
                assert len(result["adjustments"]) <= 1


class TestTeamSummaryIntegration:
    """Test team summary endpoint integration."""
    
    @patch('src.fpl_toolkit.service.api.FPLClient')
    def test_team_summary_endpoint_basic(self, mock_client_class):
        """Test basic team summary endpoint functionality."""
        from fastapi.testclient import TestClient
        from src.fpl_toolkit.service.api import app
        
        # Mock client instance
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock team info
        mock_client.get_user_team.return_value = {
            "name": "Test Team",
            "player_first_name": "John",
            "player_last_name": "Doe",
            "summary_overall_points": 1500,
            "summary_event_points": 85,
            "summary_overall_rank": 50000,
            "summary_event_rank": 25000
        }
        
        # Mock current gameweek
        mock_client.get_current_gameweek.return_value = {"id": 10}
        
        # Mock team picks
        mock_client.get_team_picks.return_value = {
            "picks": [
                {
                    "element": 283,
                    "is_captain": True,
                    "is_vice_captain": False,
                    "multiplier": 2
                },
                {
                    "element": 254,
                    "is_captain": False,
                    "is_vice_captain": True,
                    "multiplier": 1
                }
            ],
            "entry_history": {
                "event_transfers": 1,
                "bank": 15
            }
        }
        
        # Mock players data
        mock_client.get_players.return_value = [
            {
                "id": 283,
                "first_name": "Erling",
                "second_name": "Haaland",
                "element_type": 4,
                "team": 1,
                "now_cost": 130,
                "total_points": 200,
                "goals_scored": 15,
                "assists": 3
            },
            {
                "id": 254,
                "first_name": "Mohamed",
                "second_name": "Salah",
                "element_type": 3,
                "team": 2,
                "now_cost": 125,
                "total_points": 180,
                "goals_scored": 12,
                "assists": 8
            }
        ]
        
        # Mock team fixtures
        mock_client.get_team_fixtures.return_value = [
            {
                "team_h": 1,
                "team_a": 3,
                "event": 11
            }
        ]
        
        # Mock transfers
        mock_client.get_team_transfers.return_value = [
            {"event": 10}
        ]
        
        client = TestClient(app)
        response = client.get("/team/12345/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check basic structure
        assert data["team_id"] == 12345
        assert data["team_name"] == "Test Team"
        assert data["manager_name"] == "John Doe"
        assert data["captain_name"] == "Erling Haaland"
        assert data["vice_captain_name"] == "Mohamed Salah"
        assert len(data["players"]) == 2
        
        # Check player structure includes breakdown
        for player in data["players"]:
            assert "breakdown" in player
            assert "total" in player["breakdown"]


if __name__ == "__main__":
    pytest.main([__file__])