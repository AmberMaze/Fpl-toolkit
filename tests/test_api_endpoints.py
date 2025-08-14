"""Test FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from src.fpl_toolkit.service.api import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


class TestAPIEndpoints:
    """Test FastAPI endpoint functionality."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "FPL Toolkit API"
        assert data["version"] == "0.1.0"
        assert "endpoints" in data
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "fpl-toolkit-api"
    
    @patch('src.fpl_toolkit.service.api.FPLClient')
    def test_get_players_basic(self, mock_client_class, client):
        """Test basic players endpoint."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock player data
        players = [
            {
                "id": 1,
                "first_name": "Test",
                "second_name": "Player",
                "team": 1,
                "element_type": 3,  # Midfielder
                "now_cost": 80,  # £8.0m
                "total_points": 100,
                "form": "5.5",
                "selected_by_percent": "15.2",
                "status": "a"
            },
            {
                "id": 2,
                "first_name": "Another",
                "second_name": "Player",
                "team": 2,
                "element_type": 1,  # Goalkeeper
                "now_cost": 50,  # £5.0m
                "total_points": 80,
                "form": "4.0",
                "selected_by_percent": "8.5",
                "status": "a"
            }
        ]
        
        mock_client.get_players.return_value = players
        
        response = client.get("/players")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        
        # Check first player
        player1 = data[0]  # Should be sorted by points (highest first)
        assert player1["id"] == 1
        assert player1["name"] == "Test Player"
        assert player1["position"] == "MID"
        assert player1["cost"] == 8.0
        assert player1["total_points"] == 100
    
    @patch('src.fpl_toolkit.service.api.FPLClient')
    def test_get_players_with_filters(self, mock_client_class, client):
        """Test players endpoint with filters."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        players = [
            {
                "id": 1,
                "first_name": "Expensive",
                "second_name": "Midfielder",
                "team": 1,
                "element_type": 3,  # Midfielder
                "now_cost": 120,  # £12.0m
                "total_points": 150,
                "form": "6.0",
                "selected_by_percent": "25.0",
                "status": "a"
            },
            {
                "id": 2,
                "first_name": "Cheap",
                "second_name": "Defender",
                "team": 2,
                "element_type": 2,  # Defender
                "now_cost": 40,  # £4.0m
                "total_points": 60,
                "form": "3.0",
                "selected_by_percent": "5.0",
                "status": "a"
            }
        ]
        
        mock_client.get_players.return_value = players
        
        # Test position filter
        response = client.get("/players?position=MID")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["position"] == "MID"
        
        # Test cost filter
        response = client.get("/players?max_cost=10.0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["cost"] <= 10.0
        
        # Test points filter
        response = client.get("/players?min_points=100")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["total_points"] >= 100
    
    @patch('src.fpl_toolkit.service.api.FPLClient')
    def test_get_player_details(self, mock_client_class, client):
        """Test player details endpoint."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock players list
        players = [
            {
                "id": 1,
                "first_name": "Test",
                "second_name": "Player",
                "team": 1,
                "element_type": 3,
                "now_cost": 80,
                "total_points": 100,
                "form": "5.5",
                "selected_by_percent": "15.2",
                "status": "a",
                "points_per_game": "5.2",
                "minutes": 1800,
                "goals_scored": 8,
                "assists": 6,
                "clean_sheets": 2
            }
        ]
        
        # Mock detailed player data
        player_details = {
            "history": [
                {"round": 1, "total_points": 8},
                {"round": 2, "total_points": 12}
            ],
            "fixtures": [
                {"event": 3, "opponent_team": 2, "is_home": True},
                {"event": 4, "opponent_team": 3, "is_home": False}
            ]
        }
        
        mock_client.get_players.return_value = players
        mock_client.get_player_details.return_value = player_details
        
        response = client.get("/player/1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test Player"
        assert data["position"] == "MID"
        assert len(data["recent_history"]) == 2
        assert len(data["upcoming_fixtures"]) == 2
    
    def test_get_player_details_not_found(self, client):
        """Test player details endpoint with non-existent player."""
        with patch('src.fpl_toolkit.service.api.FPLClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.get_players.return_value = []
            
            response = client.get("/player/999")
            assert response.status_code == 404
            assert "Player not found" in response.json()["detail"]
    
    @patch('src.fpl_toolkit.service.api.compare_player_projections')
    def test_compare_players(self, mock_compare, client):
        """Test player comparison endpoint."""
        mock_compare.return_value = {
            "comparisons": [
                {"name": "Player 1", "total_projected_points": 25.0},
                {"name": "Player 2", "total_projected_points": 30.0}
            ],
            "best_projection": {"name": "Player 2", "total_projected_points": 30.0}
        }
        
        request_data = {
            "player_ids": [1, 2],
            "horizon_gameweeks": 5
        }
        
        response = client.post("/compare", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["comparisons"]) == 2
        assert data["best_projection"]["name"] == "Player 2"
        assert data["horizon_gameweeks"] == 5
        assert data["players_compared"] == 2
    
    def test_compare_players_validation(self, client):
        """Test player comparison validation."""
        # Test with only 1 player (should fail)
        request_data = {"player_ids": [1]}
        response = client.post("/compare", json=request_data)
        assert response.status_code == 400
        assert "At least 2 players required" in response.json()["detail"]
        
        # Test with too many players
        request_data = {"player_ids": list(range(1, 12))}  # 11 players
        response = client.post("/compare", json=request_data)
        assert response.status_code == 400
        assert "Maximum 10 players allowed" in response.json()["detail"]
    
    @patch('src.fpl_toolkit.service.api.FPLAdvisor')
    def test_advisor_endpoint(self, mock_advisor_class, client):
        """Test AI advisor endpoint."""
        mock_advisor = Mock()
        mock_advisor_class.return_value = mock_advisor
        
        mock_advice = {
            "summary": "Your team looks good",
            "recommendations": [
                {"type": "transfer", "priority": "high", "message": "Consider transfer"}
            ],
            "underperformers": [
                {"player": {"name": "Problem Player"}, "issues": ["Poor form"]}
            ],
            "top_differentials": [
                {"name": "Differential Player", "ownership": 5.0}
            ],
            "transfer_suggestions": [
                {"player_out": {"name": "Out"}, "suggestions": []}
            ]
        }
        
        mock_advisor.advise_team.return_value = mock_advice
        
        request_data = {
            "player_ids": [1, 2, 3],
            "budget": 2.0,
            "free_transfers": 1,
            "horizon_gameweeks": 5
        }
        
        response = client.post("/advisor", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["summary"] == "Your team looks good"
        assert len(data["recommendations"]) == 1
        assert len(data["underperformers"]) == 1
        assert data["horizon_gameweeks"] == 5
    
    @patch('src.fpl_toolkit.service.api.calculate_horizon_projection')
    @patch('src.fpl_toolkit.service.api.FPLClient')
    def test_projections_endpoint(self, mock_client_class, mock_projection, client):
        """Test player projections endpoint."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock next gameweek
        mock_client.get_next_gameweek.return_value = {"id": 10}
        
        # Mock projection
        mock_projection.return_value = {
            "projections": [
                {
                    "player_id": 1,
                    "gameweek": 10,
                    "projected_points": 8.5,
                    "projected_minutes": 90,
                    "confidence_score": 0.8,
                    "fixture_difficulty": 3.0
                }
            ]
        }
        
        response = client.get("/projections/1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["player_id"] == 1
        assert data["gameweek"] == 10
        assert data["projected_points"] == 8.5
        assert data["projected_minutes"] == 90
        assert data["confidence_score"] == 0.8
        assert data["fixture_difficulty"] == 3.0
    
    @patch('src.fpl_toolkit.service.api.analyze_transfer_scenario')
    def test_transfer_scenario_endpoint(self, mock_analyze, client):
        """Test transfer scenario analysis endpoint."""
        mock_analyze.return_value = {
            "player_out_name": "Player Out",
            "player_in_name": "Player In",
            "cost_change": 1.5,
            "projected_points_gain": 5.2,
            "confidence_score": 0.75,
            "risk_score": 0.3,
            "recommendation": "Recommended",
            "reasoning": "Good transfer based on projections"
        }
        
        request_data = {
            "player_out_id": 1,
            "player_in_id": 2,
            "horizon_gameweeks": 5
        }
        
        response = client.post("/transfer-scenario", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["player_out_name"] == "Player Out"
        assert data["player_in_name"] == "Player In"
        assert data["cost_change"] == 1.5
        assert data["projected_points_gain"] == 5.2
        assert data["recommendation"] == "Recommended"
        assert data["horizon_gameweeks"] == 5
    
    @patch('src.fpl_toolkit.service.api.compute_fixture_difficulty')
    @patch('src.fpl_toolkit.service.api.FPLClient')
    def test_fixture_difficulty_endpoint(self, mock_client_class, mock_compute, client):
        """Test fixture difficulty endpoint."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_compute.return_value = {
            "team_id": 1,
            "average_difficulty": 2.8,
            "difficulty_trend": "getting_easier",
            "fixtures": [
                {"gameweek": 10, "opponent_name": "Easy Team", "difficulty": 2.0}
            ],
            "home_fixtures": 3,
            "away_fixtures": 2
        }
        
        response = client.get("/fixtures/1?next_n=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["team_id"] == 1
        assert data["average_difficulty"] == 2.8
        assert data["difficulty_trend"] == "getting_easier"
        assert len(data["fixtures"]) == 1
        assert data["home_fixtures"] == 3
        assert data["away_fixtures"] == 2
    
    @patch('src.fpl_toolkit.service.api.find_transfer_targets')
    def test_transfer_targets_endpoint(self, mock_targets, client):
        """Test transfer targets endpoint."""
        mock_targets.return_value = [
            {
                "player_in_name": "Target 1",
                "cost_change": 0.5,
                "projected_points_gain": 3.0,
                "recommendation": "Recommended",
                "confidence_score": 0.8,
                "risk_score": 0.2
            },
            {
                "player_in_name": "Target 2", 
                "cost_change": -0.3,
                "projected_points_gain": 1.5,
                "recommendation": "Consider",
                "confidence_score": 0.6,
                "risk_score": 0.4
            }
        ]
        
        response = client.get("/transfer-targets/1?max_cost_increase=2.0&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["player_id"] == 1
        assert len(data["transfer_targets"]) == 2
        assert data["max_cost_increase"] == 2.0
        
        # Check target format
        target1 = data["transfer_targets"][0]
        assert target1["player_in_name"] == "Target 1"
        assert target1["cost_change"] == 0.5
        assert target1["projected_points_gain"] == 3.0