"""
Basic API testing patterns using Playwright's APIRequestContext.
Tests GET, POST, PUT, DELETE requests, response validation, and query parameters.
"""
import pytest
from playwright.sync_api import APIRequestContext
from utils.api_client import APIClient
from utils.test_helpers import (
    assert_json_structure,
    assert_status_code_in_range,
    generate_test_user,
    generate_test_post
)


@pytest.mark.api
class TestAPIBasics:
    """Basic API testing examples."""
    
    def test_get_request(self, api_request_context: APIRequestContext):
        """Test basic GET request."""
        response = api_request_context.get("/posts/1")
        
        assert response.status == 200
        assert response.ok
        
        data = response.json()
        assert "id" in data
        assert "title" in data
        assert "body" in data
        assert data["id"] == 1
    
    def test_get_with_query_params(self, api_request_context: APIRequestContext):
        """Test GET request with query parameters."""
        response = api_request_context.get(
            "/posts",
            params={"userId": 1}
        )
        
        assert response.status == 200
        
        posts = response.json()
        assert isinstance(posts, list)
        assert all(post["userId"] == 1 for post in posts)
    
    def test_post_request(self, api_request_context: APIRequestContext):
        """Test POST request to create a resource."""
        test_post = generate_test_post()
        test_post["userId"] = 1
        
        response = api_request_context.post(
            "/posts",
            data=test_post
        )
        
        assert response.status == 201
        
        created_post = response.json()
        assert created_post["title"] == test_post["title"]
        assert created_post["body"] == test_post["body"]
        assert "id" in created_post
    
    def test_put_request(self, api_request_context: APIRequestContext):
        """Test PUT request to update a resource."""
        updated_data = {
            "id": 1,
            "title": "Updated Title",
            "body": "Updated body content",
            "userId": 1
        }
        
        response = api_request_context.put(
            "/posts/1",
            data=updated_data
        )
        
        assert response.status == 200
        
        updated_post = response.json()
        assert updated_post["title"] == updated_data["title"]
        assert updated_post["body"] == updated_data["body"]
    
    def test_patch_request(self, api_request_context: APIRequestContext):
        """Test PATCH request for partial updates."""
        patch_data = {
            "title": "Patched Title"
        }
        
        response = api_request_context.patch(
            "/posts/1",
            data=patch_data
        )
        
        assert response.status == 200
        
        patched_post = response.json()
        assert patched_post["title"] == patch_data["title"]
    
    def test_delete_request(self, api_request_context: APIRequestContext):
        """Test DELETE request."""
        response = api_request_context.delete("/posts/1")
        
        assert response.status == 200 or response.status == 204
    
    def test_response_json_parsing(self, api_request_context: APIRequestContext):
        """Test JSON response parsing and validation."""
        response = api_request_context.get("/posts/1")
        
        data = response.json()
        
        # Validate JSON structure
        assert_json_structure(
            data,
            ["id", "title", "body", "userId"]
        )
        
        # Validate data types
        assert isinstance(data["id"], int)
        assert isinstance(data["title"], str)
        assert isinstance(data["body"], str)
        assert isinstance(data["userId"], int)
    
    def test_response_status_codes(self, api_request_context: APIRequestContext):
        """Test various HTTP status codes."""
        # Success
        response = api_request_context.get("/posts/1")
        assert_status_code_in_range(response.status, 200, 299)
        
        # Not found
        response = api_request_context.get("/posts/99999")
        assert response.status == 404
    
    def test_request_headers(self, api_request_context: APIRequestContext):
        """Test custom request headers."""
        custom_headers = {
            "X-Custom-Header": "test-value",
            "User-Agent": "Playwright-Test"
        }
        
        response = api_request_context.get(
            "/posts/1",
            headers=custom_headers
        )
        
        assert response.status == 200
    
    def test_api_client_wrapper(self, api_request_context: APIRequestContext):
        """Test using APIClient wrapper for requests."""
        client = APIClient(api_request_context)
        
        response = client.get("/posts/1")
        client.assert_status(response, 200)
        
        data = response.json()
        client.assert_json(response, {"id": 1})


@pytest.mark.api
class TestAPIErrorHandling:
    """Test API error handling scenarios."""
    
    def test_404_not_found(self, api_request_context: APIRequestContext):
        """Test handling 404 Not Found errors."""
        response = api_request_context.get("/posts/99999")
        
        assert response.status == 404
        assert not response.ok
    
    def test_invalid_endpoint(self, api_request_context: APIRequestContext):
        """Test handling invalid endpoints."""
        response = api_request_context.get("/invalid/endpoint")
        
        assert response.status == 404
    
    def test_malformed_request(self, api_request_context: APIRequestContext):
        """Test handling malformed requests."""
        # Attempt to POST invalid data
        response = api_request_context.post(
            "/posts",
            data="invalid json"
        )
        
        # API may return 400 or 500 depending on implementation
        assert response.status >= 400

