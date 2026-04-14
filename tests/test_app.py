import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestActivities:
    """Test suite for /activities endpoint"""

    def test_get_activities(self, client):
        """Test retrieving all activities"""
        # Arrange
        expected_activities = {"Chess Club", "Programming Class", "Gym Class"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(activities, dict)
        assert all(activity in activities for activity in expected_activities)
        
        # Verify activity structure
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignup:
    """Test suite for signup endpoint"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert "message" in response.json()
        assert email in response.json()["message"]
        
        # Verify the participant was actually added
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]

    def test_signup_duplicate(self, client):
        """Test that duplicate signup is rejected"""
        # Arrange
        email = "duplicate@mergington.edu"
        activity = "Chess Club"
        
        # Act - First signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert - First signup succeeds
        assert response1.status_code == 200
        
        # Act - Second signup with same email
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert - Second signup fails with 400
        assert response2.status_code == 400
        assert "Already signed up" in response2.json()["detail"]

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        # Arrange
        email = "test@mergington.edu"
        nonexistent_activity = "Nonexistent Club"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregister:
    """Test suite for unregister endpoint"""

    def test_unregister_success(self, client):
        """Test successful participant removal"""
        # Arrange
        email = "remove@mergington.edu"
        activity = "Chess Club"
        
        # First, sign up the participant
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Act - Unregister the participant
        response = client.delete(
            f"/activities/{activity}/participants?email={email}"
        )
        
        # Assert - Response is successful
        assert response.status_code == 200
        assert "message" in response.json()
        
        # Verify the participant was actually removed
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]

    def test_unregister_not_found(self, client):
        """Test unregistering a participant not in the activity"""
        # Arrange
        email = "notexist@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_unregister_activity_not_found(self, client):
        """Test unregister for non-existent activity"""
        # Arrange
        email = "test@mergington.edu"
        nonexistent_activity = "Nonexistent Club"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRoot:
    """Test suite for root endpoint"""

    def test_root_redirect(self, client):
        """Test that root redirects to static index"""
        # Arrange
        expected_location = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location
