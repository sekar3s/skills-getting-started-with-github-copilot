"""
Tests for the FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from src.app import activities


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root path redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoint"""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test successful retrieval of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Check structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that all expected activities are returned"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Soccer Team",
            "Basketball Club", "Art Workshop", "Drama Club", "Math Olympiad", "Science Club"
        ]
        
        for activity_name in expected_activities:
            assert activity_name in data


class TestSignupEndpoint:
    """Tests for the signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # Ensure student is not already signed up
        assert email not in activities[activity_name]["participants"]
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify student was added to activity
        assert email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_registration(self, client, reset_activities):
        """Test that duplicate registration is prevented"""
        email = "michael@mergington.edu"  # Already registered for Chess Club
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity"""
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_url_encoding(self, client, reset_activities):
        """Test signup with URL-encoded activity name and email"""
        email = "test+student@mergington.edu"
        activity_name = "Art Workshop"  # Contains space
        
        # Test with URL encoding
        encoded_email = "test%2Bstudent@mergington.edu"
        encoded_activity = "Art%20Workshop"
        
        response = client.post(f"/activities/{encoded_activity}/signup?email={encoded_email}")
        assert response.status_code == 200
        
        # Verify student was added
        assert "test+student@mergington.edu" in activities["Art Workshop"]["participants"]


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Pre-registered for Chess Club
        activity_name = "Chess Club"
        
        # Ensure student is registered
        assert email in activities[activity_name]["participants"]
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify student was removed from activity
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregistration when student is not registered"""
        email = "notregistered@mergington.edu"
        activity_name = "Chess Club"
        
        # Ensure student is not registered
        assert email not in activities[activity_name]["participants"]
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistration from non-existent activity"""
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_unregister_url_encoding(self, client, reset_activities):
        """Test unregister with URL-encoded activity name and email"""
        # First register a student with special characters
        email = "test+student@mergington.edu"
        activity_name = "Art Workshop"
        
        # Add student to activity
        activities[activity_name]["participants"].append(email)
        
        # Test unregister with URL encoding
        encoded_email = "test%2Bstudent@mergington.edu"
        encoded_activity = "Art%20Workshop"
        
        response = client.delete(f"/activities/{encoded_activity}/unregister?email={encoded_email}")
        assert response.status_code == 200
        
        # Verify student was removed
        assert "test+student@mergington.edu" not in activities["Art Workshop"]["participants"]


class TestIntegrationScenarios:
    """Integration tests for complete user workflows"""
    
    def test_signup_and_unregister_workflow(self, client, reset_activities):
        """Test complete workflow of signing up and then unregistering"""
        email = "workflow@mergington.edu"
        activity_name = "Science Club"
        
        # Initial state - student not registered
        assert email not in activities[activity_name]["participants"]
        
        # Step 1: Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
        
        # Step 2: Verify activity list shows the registration
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]
        
        # Step 3: Unregister
        unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        
        # Step 4: Verify activity list shows the unregistration
        final_activities_response = client.get("/activities")
        final_activities_data = final_activities_response.json()
        assert email not in final_activities_data[activity_name]["participants"]
    
    def test_multiple_registrations_same_student(self, client, reset_activities):
        """Test student registering for multiple activities"""
        email = "multireg@mergington.edu"
        activities_to_register = ["Chess Club", "Programming Class", "Art Workshop"]
        
        # Register for multiple activities
        for activity_name in activities_to_register:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
            assert email in activities[activity_name]["participants"]
        
        # Verify all registrations
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for activity_name in activities_to_register:
            assert email in activities_data[activity_name]["participants"]
    
    def test_activity_capacity_management(self, client, reset_activities):
        """Test activity capacity tracking (implicit through participant count)"""
        activity_name = "Math Olympiad"  # Has max_participants: 10
        
        # Get initial state
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        initial_count = len(activities_data[activity_name]["participants"])
        max_participants = activities_data[activity_name]["max_participants"]
        
        # Calculate how many more participants can be added
        spots_available = max_participants - initial_count
        
        # Add participants up to capacity
        for i in range(spots_available):
            email = f"student{i}@mergington.edu"
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify final count
        final_response = client.get("/activities")
        final_data = final_response.json()
        final_count = len(final_data[activity_name]["participants"])
        
        assert final_count == max_participants