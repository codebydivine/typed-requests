"""
Tests for the examples in the examples/ directory.

This test suite ensures that all examples work correctly and demonstrates
the proper usage patterns for the divine-typed-requests library.
"""

import asyncio
import importlib.util
import os

# Import example modules
import sys
from typing import Any, TypedDict, get_type_hints
from unittest.mock import AsyncMock, MagicMock

import anyio
import httpx
import pytest
from type_enforcer import ValidationError, enforce

from typed_requests import NetworkingManager, networking_manager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "examples"))

# We can't directly import the examples since they have async main functions
# Instead, we'll test the core functionality they demonstrate


class TestBasicUsagePatterns:
    """Test basic usage patterns demonstrated in examples."""

    @pytest.mark.anyio
    async def test_basic_get_request(self):
        """Test basic GET request without type validation."""
        manager = NetworkingManager()

        # Mock response
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"key": "value"}

        # Mock client
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request.return_value = mock_response
        manager._client = mock_client

        # Make request
        response = await manager.get("https://httpbin.org/get")

        # Verify
        assert response.status_code == 200
        assert response.json() == {"key": "value"}
        mock_client.request.assert_called_once()

    @pytest.mark.anyio
    async def test_basic_post_request(self):
        """Test basic POST request with JSON data."""
        manager = NetworkingManager()

        # Mock response
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        # Mock client
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request.return_value = mock_response
        manager._client = mock_client

        # Test data
        post_data = {"title": "Test Post", "body": "Test content"}

        # Make request
        response = await manager.post("https://httpbin.org/post", json=post_data)

        # Verify
        assert response.status_code == 200
        assert response.json() == {"success": True}
        mock_client.request.assert_called_once()

        # Check that JSON data was passed
        args, kwargs = mock_client.request.call_args
        assert kwargs.get("json") == post_data

    @pytest.mark.anyio
    async def test_typed_request_with_validation(self):
        """Test typed request with response validation."""
        manager = NetworkingManager()

        # Mock response with valid data
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": {"id": 1}}
        mock_response.raise_for_status.return_value = None

        # Mock client
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request.return_value = mock_response
        manager._client = mock_client

        # Make typed request
        response = await manager.get("https://httpbin.org/json", expected_type=dict[str, Any])

        # Verify we got a TypedResponse
        assert hasattr(response, "data")
        assert hasattr(response, "response")
        assert response.data == {"success": True, "data": {"id": 1}}
        assert response.response == mock_response

    @pytest.mark.anyio
    async def test_custom_headers(self):
        """Test request with custom headers."""
        manager = NetworkingManager()

        # Mock response
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"headers": {"received": "ok"}}

        # Mock client
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request.return_value = mock_response
        manager._client = mock_client

        # Custom headers
        custom_headers = {"Authorization": "Bearer token123", "X-Custom-Header": "custom-value"}

        # Make request
        response = await manager.get("https://httpbin.org/headers", headers=custom_headers)

        # Verify
        assert response.status_code == 200

        # Check headers were included
        args, kwargs = mock_client.request.call_args
        headers = kwargs.get("headers", {})
        assert headers.get("Authorization") == "Bearer token123"
        assert headers.get("X-Custom-Header") == "custom-value"

    @pytest.mark.anyio
    async def test_timeout_handling(self):
        """Test timeout handling."""
        manager = NetworkingManager()

        # Mock client that raises timeout
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request.side_effect = httpx.TimeoutException("Request timed out")
        manager._client = mock_client

        # Make request with timeout
        with pytest.raises(httpx.TimeoutException):
            await manager.get("https://httpbin.org/delay/5", timeout=2.0)

        # Verify timeout was passed
        args, kwargs = mock_client.request.call_args
        assert kwargs.get("timeout") == 2.0


class TestAdvancedPatterns:
    """Test advanced usage patterns."""

    @pytest.mark.anyio
    async def test_api_client_pattern(self):
        """Test API client class pattern."""

        class TestAPIClient:
            def __init__(self):
                self.base_url = "https://api.example.com"
                self.manager = NetworkingManager()
                self.headers = {"User-Agent": "Test-Client/1.0"}

            async def __aenter__(self):
                await self.manager.startup()
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                await self.manager.shutdown()

            async def get_user(self, user_id: int) -> dict[str, Any]:
                response = await self.manager.get(
                    f"{self.base_url}/users/{user_id}", headers=self.headers, expected_type=dict[str, Any]
                )
                return response.data

        # Test the client
        client = TestAPIClient()

        # Mock the manager
        mock_response_data = {"id": 1, "name": "Test User"}
        mock_typed_response = MagicMock()
        mock_typed_response.data = mock_response_data

        client.manager.get = AsyncMock(return_value=mock_typed_response)
        client.manager.startup = AsyncMock()
        client.manager.shutdown = AsyncMock()

        # Use as context manager
        async with client:
            user = await client.get_user(1)
            assert user == mock_response_data

        # Verify lifecycle methods were called
        client.manager.startup.assert_called_once()
        client.manager.shutdown.assert_called_once()

    @pytest.mark.anyio
    async def test_retry_logic_pattern(self):
        """Test retry logic pattern."""

        async def fetch_with_retry(manager: NetworkingManager, url: str, max_retries: int = 3):
            """Fetch data with retry logic."""
            for attempt in range(max_retries):
                try:
                    response = await manager.get(url)
                    return response.json()
                except Exception:
                    if attempt == max_retries - 1:
                        raise
                    # Use anyio.sleep for compatibility with both asyncio and trio
                    try:
                        await anyio.sleep(0.1)  # Short delay for testing
                    except ImportError:
                        # Fallback to asyncio if anyio not available
                        await asyncio.sleep(0.1)

        manager = NetworkingManager()

        # Mock client that fails twice then succeeds
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_responses = [
            httpx.RequestError("Network error"),
            httpx.RequestError("Network error"),
            MagicMock(spec=httpx.Response),
        ]
        mock_responses[2].json.return_value = {"success": True}
        mock_client.request.side_effect = mock_responses
        manager._client = mock_client

        # Test retry logic
        result = await fetch_with_retry(manager, "https://api.example.com/data")

        # Verify it succeeded after retries
        assert result == {"success": True}
        assert mock_client.request.call_count == 3


class TestTypeValidationPatterns:
    """Test type validation patterns from examples."""

    def test_direct_type_validation(self):
        """Test direct type validation with type-enforcer."""

        # Test valid data
        valid_data = {"id": 1, "name": "Test User", "email": "test@example.com"}

        # Define expected type

        class UserDict(TypedDict):
            id: int
            name: str
            email: str

        # Validate
        result = enforce(valid_data, UserDict)
        assert result == valid_data

        # Test invalid data
        invalid_data = {
            "id": "not-a-number",  # Should be int
            "name": "Test User",
            "email": "test@example.com",
        }

        with pytest.raises(ValidationError):
            enforce(invalid_data, UserDict)

    @pytest.mark.anyio
    async def test_api_response_validation(self):
        """Test API response validation pattern."""

        # Define API response structure
        class APIResponse(TypedDict):
            success: bool
            data: list[dict[str, Any]] | None
            message: str

        manager = NetworkingManager()

        # Mock valid response
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": [{"id": 1, "name": "Item 1"}], "message": "Success"}
        mock_response.raise_for_status.return_value = None

        # Mock client
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request.return_value = mock_response
        manager._client = mock_client

        # Make validated request
        response = await manager.get("https://api.example.com/items", expected_type=APIResponse)

        # Verify response is properly typed
        assert response.data["success"] is True
        assert len(response.data["data"]) == 1
        assert response.data["message"] == "Success"

    @pytest.mark.anyio
    async def test_validation_error_handling(self):
        """Test validation error handling pattern."""

        class StrictResponse(TypedDict):
            required_field: str
            required_number: int

        manager = NetworkingManager()

        # Mock response with missing required field
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "required_field": "present",
            # missing required_number
        }
        mock_response.raise_for_status.return_value = None

        # Mock client
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request.return_value = mock_response
        manager._client = mock_client

        # Make request and expect validation error
        with pytest.raises(ValidationError):
            await manager.get("https://api.example.com/strict", expected_type=StrictResponse)


class TestRealWorldPatterns:
    """Test real-world usage patterns."""

    @pytest.mark.anyio
    async def test_pagination_pattern(self):
        """Test pagination handling pattern."""

        class PaginatedResponse(TypedDict):
            items: list[dict[str, Any]]
            page: int
            per_page: int
            total: int
            has_next: bool

        async def fetch_all_pages(manager: NetworkingManager, base_url: str) -> list[dict[str, Any]]:
            """Fetch all pages of results."""
            all_items = []
            page = 1

            while True:
                response = await manager.get(f"{base_url}?page={page}", expected_type=PaginatedResponse)

                all_items.extend(response.data["items"])

                if not response.data["has_next"]:
                    break

                page += 1

            return all_items

        manager = NetworkingManager()

        # Mock responses for multiple pages
        page1_response = MagicMock(spec=httpx.Response)
        page1_response.status_code = 200
        page1_response.json.return_value = {
            "items": [{"id": 1}, {"id": 2}],
            "page": 1,
            "per_page": 2,
            "total": 3,
            "has_next": True,
        }
        page1_response.raise_for_status.return_value = None

        page2_response = MagicMock(spec=httpx.Response)
        page2_response.status_code = 200
        page2_response.json.return_value = {
            "items": [{"id": 3}],
            "page": 2,
            "per_page": 2,
            "total": 3,
            "has_next": False,
        }
        page2_response.raise_for_status.return_value = None

        # Mock client with different responses for each page
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request.side_effect = [page1_response, page2_response]
        manager._client = mock_client

        # Test pagination
        all_items = await fetch_all_pages(manager, "https://api.example.com/items")

        # Verify all items were collected
        assert len(all_items) == 3
        assert all_items == [{"id": 1}, {"id": 2}, {"id": 3}]
        assert mock_client.request.call_count == 2

    @pytest.mark.anyio
    async def test_authentication_pattern(self):
        """Test authentication pattern."""

        class AuthenticatedClient:
            def __init__(self, api_key: str):
                self.api_key = api_key
                self.manager = NetworkingManager()
                self.access_token = None

            async def authenticate(self):
                """Authenticate and get access token."""
                response = await self.manager.post("https://api.example.com/auth", json={"api_key": self.api_key})
                auth_data = response.json()
                self.access_token = auth_data["access_token"]
                return auth_data

            def get_auth_headers(self):
                """Get headers with authentication."""
                headers = {"Content-Type": "application/json"}
                if self.access_token:
                    headers["Authorization"] = f"Bearer {self.access_token}"
                return headers

            async def get_protected_resource(self, resource_id: int):
                """Get a protected resource."""
                response = await self.manager.get(
                    f"https://api.example.com/protected/{resource_id}", headers=self.get_auth_headers()
                )
                return response.json()

        # Test authentication flow
        client = AuthenticatedClient("test-api-key")

        # Mock authentication response
        auth_response = MagicMock(spec=httpx.Response)
        auth_response.status_code = 200
        auth_response.json.return_value = {"access_token": "mock-token", "expires_in": 3600}

        # Mock protected resource response
        protected_response = MagicMock(spec=httpx.Response)
        protected_response.status_code = 200
        protected_response.json.return_value = {"id": 1, "data": "protected"}

        # Mock client
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request.side_effect = [auth_response, protected_response]
        client.manager._client = mock_client

        # Test authentication
        auth_data = await client.authenticate()
        assert auth_data["access_token"] == "mock-token"
        assert client.access_token == "mock-token"

        # Test protected resource access
        resource_data = await client.get_protected_resource(1)
        assert resource_data == {"id": 1, "data": "protected"}

        # Verify authentication header was used
        args, kwargs = mock_client.request.call_args
        headers = kwargs.get("headers", {})
        assert headers.get("Authorization") == "Bearer mock-token"


class TestLifecycleManagement:
    """Test lifecycle management patterns."""

    @pytest.mark.anyio
    async def test_startup_shutdown_pattern(self):
        """Test proper startup/shutdown pattern."""
        manager = NetworkingManager()

        # Test initial state
        assert manager._client is None

        # Test startup
        await manager.startup()
        assert manager._client is not None

        # Test operations work after startup
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}

        # Replace the actual client with a mock
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request.return_value = mock_response
        manager._client = mock_client

        response = await manager.get("https://api.example.com/status")
        assert response.json() == {"status": "ok"}

        # Test shutdown
        await manager.shutdown()
        assert manager._client is None

    @pytest.mark.anyio
    async def test_global_instance_usage(self):
        """Test using the global networking_manager instance."""
        # The global instance should be available
        assert networking_manager is not None
        assert isinstance(networking_manager, NetworkingManager)

        # Test that it can be used for requests
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"global": "instance"}

        # Mock the client
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request.return_value = mock_response

        # Store original client and replace with mock
        original_client = networking_manager._client
        networking_manager._client = mock_client

        try:
            response = await networking_manager.get("https://api.example.com/global")
            assert response.json() == {"global": "instance"}
        finally:
            # Restore original client
            networking_manager._client = original_client


# ===== Test Running Examples =====


class TestExampleExecution:
    """Test that examples can be executed without errors."""

    @pytest.mark.anyio
    async def test_example_imports(self):
        """Test that examples can be imported without errors."""
        # Test importing example modules
        try:
            # Add examples directory to path
            examples_dir = os.path.join(os.path.dirname(__file__), "..", "examples")
            sys.path.insert(0, examples_dir)

            # Import modules to check for syntax errors

            # Test basic_usage
            spec = importlib.util.spec_from_file_location("basic_usage", os.path.join(examples_dir, "basic_usage.py"))
            basic_usage = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(basic_usage)

            # Test api_response_validation
            spec = importlib.util.spec_from_file_location(
                "api_response_validation", os.path.join(examples_dir, "api_response_validation.py")
            )
            api_validation = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(api_validation)

            # Test advanced_api_integration
            spec = importlib.util.spec_from_file_location(
                "advanced_api_integration", os.path.join(examples_dir, "advanced_api_integration.py")
            )
            advanced_api = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(advanced_api)

            # Test e_commerce_api_client
            spec = importlib.util.spec_from_file_location(
                "e_commerce_api_client", os.path.join(examples_dir, "e_commerce_api_client.py")
            )
            ecommerce = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ecommerce)

            # If we get here, all examples imported successfully
            assert True

        except Exception as e:
            pytest.fail(f"Failed to import examples: {e}")

    @pytest.mark.anyio
    async def test_type_definitions_validity(self):
        """Test that type definitions in examples are valid."""
        # Import type definitions from api_response_validation
        examples_dir = os.path.join(os.path.dirname(__file__), "..", "examples")
        sys.path.insert(0, examples_dir)

        spec = importlib.util.spec_from_file_location(
            "api_response_validation", os.path.join(examples_dir, "api_response_validation.py")
        )
        api_validation = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_validation)

        # Test that TypedDict classes are properly defined
        assert hasattr(api_validation, "TokenDict")
        assert hasattr(api_validation, "DexScreenerResponseDict")

        # Test that we can get type hints
        try:
            hints = get_type_hints(api_validation.TokenDict)
            assert "address" in hints
            assert "name" in hints
            assert "symbol" in hints
        except Exception as e:
            pytest.fail(f"Failed to get type hints: {e}")


# ===== Integration Tests =====


class TestExampleIntegration:
    """Integration tests that combine multiple example patterns."""

    @pytest.mark.anyio
    async def test_full_workflow_integration(self):
        """Test a complete workflow combining multiple patterns."""

        # Define types
        class User(TypedDict):
            id: int
            name: str
            email: str

        class UserListResponse(TypedDict):
            users: list[User]
            total: int

        # Create client
        manager = NetworkingManager()

        # Mock responses
        user_list_response = MagicMock(spec=httpx.Response)
        user_list_response.status_code = 200
        user_list_response.json.return_value = {
            "users": [
                {"id": 1, "name": "User 1", "email": "user1@example.com"},
                {"id": 2, "name": "User 2", "email": "user2@example.com"},
            ],
            "total": 2,
        }
        user_list_response.raise_for_status.return_value = None

        user_detail_response = MagicMock(spec=httpx.Response)
        user_detail_response.status_code = 200
        user_detail_response.json.return_value = {"id": 1, "name": "User 1", "email": "user1@example.com"}
        user_detail_response.raise_for_status.return_value = None

        # Mock client
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.request.side_effect = [user_list_response, user_detail_response]
        manager._client = mock_client

        # Test workflow
        # 1. Get list of users
        users_response = await manager.get("https://api.example.com/users", expected_type=UserListResponse)

        assert len(users_response.data["users"]) == 2
        assert users_response.data["total"] == 2

        # 2. Get specific user details
        user_id = users_response.data["users"][0]["id"]
        user_response = await manager.get(f"https://api.example.com/users/{user_id}", expected_type=User)

        assert user_response.data["id"] == 1
        assert user_response.data["name"] == "User 1"

        # Verify both requests were made
        assert mock_client.request.call_count == 2
