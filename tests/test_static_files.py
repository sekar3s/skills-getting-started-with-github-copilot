"""
Tests for static file serving and frontend integration
"""
import pytest


class TestStaticFiles:
    """Tests for static file serving"""
    
    def test_static_index_html_accessible(self, client):
        """Test that static index.html is accessible"""
        response = client.get("/static/index.html")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_static_css_accessible(self, client):
        """Test that static CSS file is accessible"""
        response = client.get("/static/styles.css")
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")
    
    def test_static_js_accessible(self, client):
        """Test that static JavaScript file is accessible"""
        response = client.get("/static/app.js")
        assert response.status_code == 200
        # JavaScript files might be served as text/plain or application/javascript
        content_type = response.headers.get("content-type", "")
        assert any(expected in content_type for expected in ["javascript", "text/plain"])
    
    def test_nonexistent_static_file(self, client):
        """Test request for non-existent static file"""
        response = client.get("/static/nonexistent.html")
        assert response.status_code == 404


class TestHTMLContent:
    """Tests for HTML content validation"""
    
    def test_index_html_contains_expected_elements(self, client):
        """Test that index.html contains expected form elements"""
        response = client.get("/static/index.html")
        html_content = response.text
        
        # Check for essential HTML elements
        assert '<form id="signup-form">' in html_content
        assert 'id="email"' in html_content
        assert 'id="activity"' in html_content
        assert 'id="activities-list"' in html_content
    
    def test_html_includes_javascript(self, client):
        """Test that HTML includes the JavaScript file"""
        response = client.get("/static/index.html")
        html_content = response.text
        
        assert '<script src="app.js"></script>' in html_content
    
    def test_html_includes_css(self, client):
        """Test that HTML includes the CSS file"""
        response = client.get("/static/index.html")
        html_content = response.text
        
        assert 'href="styles.css"' in html_content


class TestJavaScriptContent:
    """Tests for JavaScript content validation"""
    
    def test_javascript_contains_expected_functions(self, client):
        """Test that JavaScript contains expected function definitions"""
        response = client.get("/static/app.js")
        js_content = response.text
        
        # Check for key functions and event handlers
        assert 'fetchActivities' in js_content
        assert 'addEventListener' in js_content
        assert 'signup-form' in js_content
        assert 'delete-participant' in js_content
    
    def test_javascript_contains_api_calls(self, client):
        """Test that JavaScript contains API endpoint calls"""
        response = client.get("/static/app.js")
        js_content = response.text
        
        # Check for API endpoints
        assert '/activities' in js_content
        assert '/signup' in js_content
        assert '/unregister' in js_content


class TestCSSContent:
    """Tests for CSS content validation"""
    
    def test_css_contains_expected_styles(self, client):
        """Test that CSS contains expected style definitions"""
        response = client.get("/static/styles.css")
        css_content = response.text
        
        # Check for key CSS classes and elements
        assert '.activity-card' in css_content
        assert '.participants-list' in css_content
        assert '.delete-participant' in css_content
        assert 'form' in css_content or 'button' in css_content
    
    def test_css_responsive_design(self, client):
        """Test that CSS includes responsive design elements"""
        response = client.get("/static/styles.css")
        css_content = response.text
        
        # Check for responsive design patterns
        assert '@media' in css_content or 'flex' in css_content or 'grid' in css_content


class TestFrontendBackendIntegration:
    """Tests for frontend-backend integration aspects"""
    
    def test_api_endpoints_match_frontend_calls(self, client, reset_activities):
        """Test that backend endpoints match what frontend expects"""
        # This test verifies that the endpoints the frontend calls actually exist
        
        # Test GET /activities (used by fetchActivities)
        response = client.get("/activities")
        assert response.status_code == 200
        
        # Test POST /activities/{name}/signup (used by signup form)
        response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        assert response.status_code == 200
        
        # Test DELETE /activities/{name}/unregister (used by delete buttons)
        response = client.delete("/activities/Chess Club/unregister?email=test@mergington.edu")
        assert response.status_code == 200
    
    def test_activity_data_structure_matches_frontend_expectations(self, client, reset_activities):
        """Test that API returns data in the format frontend expects"""
        response = client.get("/activities")
        data = response.json()
        
        # Check that each activity has the fields the frontend uses
        for activity_name, activity_data in data.items():
            # Fields used in the frontend JavaScript
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            
            # Verify participants is a list (frontend does .length and .map)
            assert isinstance(activity_data["participants"], list)
    
    def test_error_responses_match_frontend_expectations(self, client, reset_activities):
        """Test that error responses have the format frontend expects"""
        # Test 404 error
        response = client.post("/activities/Nonexistent/signup?email=test@mergington.edu")
        error_data = response.json()
        
        # Frontend checks for result.detail
        assert "detail" in error_data
        
        # Test 400 error
        response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
        error_data = response.json()
        
        # Frontend checks for result.detail
        assert "detail" in error_data