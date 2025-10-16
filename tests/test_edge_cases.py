"""
Tests for error handling and edge cases
"""
import pytest
from unittest.mock import patch
from src.app import activities


class TestErrorHandling:
    """Tests for various error conditions and edge cases"""
    
    def test_invalid_email_formats(self, client, reset_activities):
        """Test signup with various invalid email formats"""
        invalid_emails = [
            "",  # Empty email
            "invalid-email",  # No @ symbol
            "@mergington.edu",  # Missing username
            "student@",  # Missing domain
            "student@@mergington.edu",  # Double @ symbol
        ]
        
        activity_name = "Chess Club"
        
        for email in invalid_emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            # The endpoint doesn't validate email format, so it should still work
            # This test documents current behavior
            if email:  # Non-empty emails
                assert response.status_code in [200, 400]
    
    def test_very_long_email(self, client, reset_activities):
        """Test signup with extremely long email"""
        long_email = "a" * 500 + "@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={long_email}")
        # Should handle long emails gracefully
        assert response.status_code in [200, 400]
    
    def test_special_characters_in_email(self, client, reset_activities):
        """Test signup with special characters in email"""
        special_emails = [
            ("test.dot@mergington.edu", "test.dot@mergington.edu"),
            ("test-dash@mergington.edu", "test-dash@mergington.edu"), 
            ("test_underscore@mergington.edu", "test_underscore@mergington.edu"),
        ]
        
        activity_name = "Programming Class"
        
        for original_email, expected_email in special_emails:
            response = client.post(f"/activities/{activity_name}/signup?email={original_email}")
            assert response.status_code == 200
            assert expected_email in activities[activity_name]["participants"]
    
    def test_case_sensitive_activity_names(self, client, reset_activities):
        """Test that activity names are case-sensitive"""
        email = "case@mergington.edu"
        
        # Try with different cases
        response1 = client.post(f"/activities/chess club/signup?email={email}")
        assert response1.status_code == 404  # lowercase should fail
        
        response2 = client.post(f"/activities/CHESS CLUB/signup?email={email}")
        assert response2.status_code == 404  # uppercase should fail
        
        response3 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response3.status_code == 200  # exact case should work
    
    def test_missing_query_parameters(self, client, reset_activities):
        """Test endpoints with missing query parameters"""
        activity_name = "Chess Club"
        
        # Test signup without email parameter
        response1 = client.post(f"/activities/{activity_name}/signup")
        assert response1.status_code == 422  # Validation error
        
        # Test unregister without email parameter
        response2 = client.delete(f"/activities/{activity_name}/unregister")
        assert response2.status_code == 422  # Validation error


class TestConcurrencyAndRaceConditions:
    """Tests for potential concurrency issues"""
    
    def test_simultaneous_registrations_same_activity(self, client, reset_activities):
        """Test multiple simultaneous registrations for the same activity"""
        activity_name = "Drama Club"
        emails = [f"concurrent{i}@mergington.edu" for i in range(5)]
        
        # Simulate concurrent registrations
        responses = []
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            responses.append(response)
        
        # All should succeed since there's no actual concurrency in tests
        for response in responses:
            assert response.status_code == 200
        
        # Verify all emails are registered
        for email in emails:
            assert email in activities[activity_name]["participants"]
    
    def test_signup_then_immediate_unregister(self, client, reset_activities):
        """Test rapid signup followed by unregister"""
        email = "rapid@mergington.edu"
        activity_name = "Basketball Club"
        
        # Rapid signup and unregister
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200
        
        unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Final state should be unregistered
        assert email not in activities[activity_name]["participants"]


class TestDataIntegrity:
    """Tests for data consistency and integrity"""
    
    def test_activity_data_immutability(self, client, reset_activities):
        """Test that activity metadata doesn't change during operations"""
        activity_name = "Science Club"
        
        # Get initial activity data
        initial_response = client.get("/activities")
        initial_data = initial_response.json()[activity_name]
        
        original_description = initial_data["description"]
        original_schedule = initial_data["schedule"]
        original_max_participants = initial_data["max_participants"]
        
        # Perform some operations
        email = "integrity@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={email}")
        client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Check that metadata is unchanged
        final_response = client.get("/activities")
        final_data = final_response.json()[activity_name]
        
        assert final_data["description"] == original_description
        assert final_data["schedule"] == original_schedule
        assert final_data["max_participants"] == original_max_participants
    
    def test_participant_list_uniqueness(self, client, reset_activities):
        """Test that participant lists maintain uniqueness"""
        activity_name = "Art Workshop"
        email = "unique@mergington.edu"
        
        # Try to register the same email multiple times
        for _ in range(3):
            client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Should only appear once in the list
        activity_data = activities[activity_name]
        email_count = activity_data["participants"].count(email)
        assert email_count <= 1  # Should be 0 or 1, not more
    
    def test_empty_activities_handling(self, client):
        """Test behavior when activities dict is empty"""
        # Temporarily clear activities
        original_activities = activities.copy()
        activities.clear()
        
        try:
            # Test get activities with empty dict
            response = client.get("/activities")
            assert response.status_code == 200
            assert response.json() == {}
            
            # Test signup with empty activities
            response = client.post("/activities/Any Activity/signup?email=test@mergington.edu")
            assert response.status_code == 404
            
        finally:
            # Restore original activities
            activities.clear()
            activities.update(original_activities)


class TestResponseFormat:
    """Tests for API response format consistency"""
    
    def test_success_response_format(self, client, reset_activities):
        """Test that success responses have consistent format"""
        email = "format@mergington.edu"
        activity_name = "Gym Class"
        
        # Test signup response format
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        signup_data = signup_response.json()
        
        assert "message" in signup_data
        assert isinstance(signup_data["message"], str)
        
        # Test unregister response format
        unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        unregister_data = unregister_response.json()
        
        assert "message" in unregister_data
        assert isinstance(unregister_data["message"], str)
    
    def test_error_response_format(self, client, reset_activities):
        """Test that error responses have consistent format"""
        # Test 404 error format
        response_404 = client.post("/activities/Nonexistent/signup?email=test@mergington.edu")
        error_data_404 = response_404.json()
        
        assert "detail" in error_data_404
        assert isinstance(error_data_404["detail"], str)
        
        # Test 400 error format  
        response_400 = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
        error_data_400 = response_400.json()
        
        assert "detail" in error_data_400
        assert isinstance(error_data_400["detail"], str)
    
    def test_activities_response_structure(self, client, reset_activities):
        """Test that activities endpoint returns properly structured data"""
        response = client.get("/activities")
        data = response.json()
        
        assert isinstance(data, dict)
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            
            # Check required fields
            required_fields = ["description", "schedule", "max_participants", "participants"]
            for field in required_fields:
                assert field in activity_data
            
            # Check field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Check that all participants are strings
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)