"""
Comprehensive tests for the requests core module.

This test suite covers all functionality of the NetworkingManager class,
including HTTP methods, type validation, lifecycle management, and edge cases.
"""

from typing import Any, TypedDict
from unittest import mock
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from typed_requests import logger
from typed_requests.core import NetworkingManager, TypedResponse
from typed_requests.core import networking_manager as global_networking_manager


# Test data types
class SimpleResponseDict(TypedDict):
    success: bool
    data: dict[str, Any]


@pytest.fixture
def networking_manager():
    """Create a fresh instance of NetworkingManager for each test"""
    return NetworkingManager()


@pytest.fixture
def mock_httpx_response():
    """Create a mock HTTP response with JSON data."""
    mock_response = MagicMock(spec=httpx.Response)

    # Valid test data
    test_data = {"success": True, "data": {"message": "Hello World", "count": 42}}

    mock_response.json.return_value = test_data
    mock_response.raise_for_status.return_value = None
    return mock_response


# =============================================================================
# Basic HTTP Request Tests
# =============================================================================


@pytest.mark.anyio
async def test_request_successful(networking_manager, monkeypatch):
    """Test successful request with default parameters"""
    # Create a mock response
    mock_response = mock.MagicMock(spec=httpx.Response)
    mock_response.raise_for_status = mock.MagicMock()

    # Create a mock AsyncClient instance
    mock_client_instance = mock.AsyncMock(spec=httpx.AsyncClient)
    mock_client_instance.request = mock.AsyncMock(return_value=mock_response)

    # Set the internal client of the NetworkingManager instance to our mock
    networking_manager._client = mock_client_instance

    # Call the method (no need to explicitly call startup() as we manually set _client)
    response = await networking_manager.request("GET", "https://example.com")

    # Verify request was called on the mock client with correct parameters
    mock_client_instance.request.assert_called_once()
    args, kwargs = mock_client_instance.request.call_args
    assert args[0] == "GET"
    assert args[1] == "https://example.com"

    # Verify timeout is set to default
    assert kwargs.get("timeout") == networking_manager.DEFAULT_TIMEOUT

    # Verify default headers are included
    headers = kwargs.get("headers", {})
    assert "accept" in headers
    assert "user-agent" in headers
    assert "accept-encoding" in headers

    # Verify response.raise_for_status was called
    mock_response.raise_for_status.assert_called_once()

    # Verify the correct response was returned
    assert response == mock_response


@pytest.mark.anyio
async def test_request_with_custom_headers(networking_manager, monkeypatch):
    """Test request with custom headers"""
    # Create a mock response
    mock_response = mock.MagicMock(spec=httpx.Response)
    mock_response.raise_for_status = mock.MagicMock()

    # Create a mock AsyncClient instance
    mock_client_instance = mock.AsyncMock(spec=httpx.AsyncClient)
    mock_client_instance.request = mock.AsyncMock(return_value=mock_response)

    # Set the internal client of the NetworkingManager instance to our mock
    networking_manager._client = mock_client_instance

    # Custom headers to pass
    custom_headers = {"X-Test-Header": "test-value", "Authorization": "Bearer token123"}

    # Call the method with custom headers
    await networking_manager.request("GET", "https://example.com", headers=custom_headers)

    # Verify request was called on the mock client with headers merged correctly
    mock_client_instance.request.assert_called_once()
    args, kwargs = mock_client_instance.request.call_args
    headers = kwargs.get("headers", {})

    # Default headers should still be present
    assert "accept" in headers
    assert "user-agent" in headers
    assert "accept-encoding" in headers

    # Custom headers should be present
    assert headers.get("X-Test-Header") == "test-value"
    assert headers.get("Authorization") == "Bearer token123"


@pytest.mark.anyio
async def test_request_with_custom_timeout(networking_manager, monkeypatch):
    """Test request with custom timeout"""
    # Create a mock response
    mock_response = mock.MagicMock(spec=httpx.Response)
    mock_response.raise_for_status = mock.MagicMock()

    # Create a mock AsyncClient instance
    mock_client_instance = mock.AsyncMock(spec=httpx.AsyncClient)
    mock_client_instance.request = mock.AsyncMock(return_value=mock_response)

    # Set the internal client of the NetworkingManager instance to our mock
    networking_manager._client = mock_client_instance

    # Custom timeout value
    custom_timeout = 30.0

    # Call the method with custom timeout
    await networking_manager.request("GET", "https://example.com", timeout=custom_timeout)

    # Verify request was called on the mock client with custom timeout
    mock_client_instance.request.assert_called_once()
    args, kwargs = mock_client_instance.request.call_args
    assert kwargs.get("timeout") == custom_timeout


@pytest.mark.anyio
async def test_request_with_json_data(networking_manager, monkeypatch):
    """Test request with JSON data"""
    # Create a mock response
    mock_response = mock.MagicMock(spec=httpx.Response)
    mock_response.raise_for_status = mock.MagicMock()

    # Create a mock AsyncClient instance
    mock_client_instance = mock.AsyncMock(spec=httpx.AsyncClient)
    mock_client_instance.request = mock.AsyncMock(return_value=mock_response)

    # Set the internal client of the NetworkingManager instance to our mock
    networking_manager._client = mock_client_instance

    # JSON data to send
    json_data = {"key1": "value1", "key2": {"nested": "value2"}}

    # Call the method with JSON data
    await networking_manager.request("POST", "https://example.com", json=json_data)

    # Verify request was called on the mock client with JSON data
    mock_client_instance.request.assert_called_once()
    args, kwargs = mock_client_instance.request.call_args
    assert kwargs.get("json") == json_data


@pytest.mark.anyio
async def test_request_exception_handling(networking_manager, monkeypatch):
    """Test request exception handling"""
    # Create a mock AsyncClient instance configured to raise an error
    mock_client_instance = mock.AsyncMock(spec=httpx.AsyncClient)
    mock_client_instance.request = mock.AsyncMock(side_effect=httpx.RequestError("Test error"))

    # Set the internal client of the NetworkingManager instance to our mock
    networking_manager._client = mock_client_instance

    # Call the method and expect the exception to be re-raised
    with pytest.raises(httpx.RequestError):
        await networking_manager.request("GET", "https://example.com")


# =============================================================================
# HTTP Method Tests
# =============================================================================


@pytest.mark.anyio
async def test_get_method(networking_manager):
    """Test the GET convenience method"""
    # Mock the request method
    networking_manager.request = mock.AsyncMock()

    # Call the GET method
    await networking_manager.get("https://example.com", param1="value1")

    # Verify request was called with GET method and expected_type=None
    networking_manager.request.assert_called_once_with(
        "GET", "https://example.com", expected_type=None, param1="value1"
    )


@pytest.mark.anyio
async def test_post_method(networking_manager):
    """Test the POST convenience method"""
    # Mock the request method
    networking_manager.request = mock.AsyncMock()

    # Call the POST method
    await networking_manager.post("https://example.com", json={"data": "value"})

    # Verify request was called with POST method and expected_type=None
    networking_manager.request.assert_called_once_with(
        "POST", "https://example.com", expected_type=None, json={"data": "value"}
    )


@pytest.mark.anyio
async def test_put_method(networking_manager):
    """Test the PUT convenience method"""
    # Mock the request method
    networking_manager.request = mock.AsyncMock()

    # Call the PUT method
    await networking_manager.put("https://example.com", json={"data": "value"})

    # Verify request was called with PUT method and expected_type=None
    networking_manager.request.assert_called_once_with(
        "PUT", "https://example.com", expected_type=None, json={"data": "value"}
    )


@pytest.mark.anyio
async def test_delete_method(networking_manager):
    """Test the DELETE convenience method"""
    # Mock the request method
    networking_manager.request = mock.AsyncMock()

    # Call the DELETE method
    await networking_manager.delete("https://example.com")

    # Verify request was called with DELETE method and expected_type=None
    networking_manager.request.assert_called_once_with("DELETE", "https://example.com", expected_type=None)


@pytest.mark.anyio
async def test_head_method(networking_manager):
    """Test the HEAD convenience method"""
    # Mock the request method
    networking_manager.request = mock.AsyncMock()

    # Call the HEAD method
    await networking_manager.head("https://example.com")

    # Verify request was called with HEAD method and expected_type=None
    networking_manager.request.assert_called_once_with("HEAD", "https://example.com", expected_type=None)


@pytest.mark.anyio
async def test_options_method(networking_manager):
    """Test the OPTIONS convenience method"""
    # Mock the request method
    networking_manager.request = mock.AsyncMock()

    # Call the OPTIONS method
    await networking_manager.options("https://example.com")

    # Verify request was called with OPTIONS method and expected_type=None
    networking_manager.request.assert_called_once_with("OPTIONS", "https://example.com", expected_type=None)


@pytest.mark.anyio
async def test_patch_method(networking_manager):
    """Test the PATCH convenience method"""
    # Mock the request method
    networking_manager.request = mock.AsyncMock()

    # Call the PATCH method
    await networking_manager.patch("https://example.com", json={"data": "value"})

    # Verify request was called with PATCH method and expected_type=None
    networking_manager.request.assert_called_once_with(
        "PATCH", "https://example.com", expected_type=None, json={"data": "value"}
    )


# =============================================================================
# Advanced HTTP Method Tests with Mocked Requests
# =============================================================================


@pytest.mark.anyio
async def test_post_method_with_mock():
    """Test the post method."""
    with patch("typed_requests.core.NetworkingManager.request", new_callable=AsyncMock) as mock_request:
        manager = NetworkingManager()
        await manager.post("https://example.com", json={"data": "value"})
        mock_request.assert_called_once_with("POST", "https://example.com", expected_type=None, json={"data": "value"})


@pytest.mark.anyio
async def test_post_method_with_new_instance():
    """Test the post method with a new instance."""
    with patch("typed_requests.core.NetworkingManager.request", new_callable=AsyncMock) as mock_request:
        manager = NetworkingManager()
        await manager.post("https://example.com", json={"data": "value"})
        mock_request.assert_called_once_with("POST", "https://example.com", expected_type=None, json={"data": "value"})


@pytest.mark.anyio
async def test_put_method_with_mock():
    """Test the put method."""
    with patch("typed_requests.core.NetworkingManager.request", new_callable=AsyncMock) as mock_request:
        manager = NetworkingManager()
        await manager.put("https://example.com", json={"data": "value"})
        mock_request.assert_called_once_with("PUT", "https://example.com", expected_type=None, json={"data": "value"})


@pytest.mark.anyio
async def test_delete_method_with_mock():
    """Test the delete method."""
    with patch("typed_requests.core.NetworkingManager.request", new_callable=AsyncMock) as mock_request:
        manager = NetworkingManager()
        await manager.delete("https://example.com")
        mock_request.assert_called_once_with("DELETE", "https://example.com", expected_type=None)


@pytest.mark.anyio
async def test_head_method_with_mock():
    """Test the head method."""
    with patch("typed_requests.core.NetworkingManager.request", new_callable=AsyncMock) as mock_request:
        manager = NetworkingManager()
        await manager.head("https://example.com")
        mock_request.assert_called_once_with("HEAD", "https://example.com", expected_type=None)


@pytest.mark.anyio
async def test_options_method_with_mock():
    """Test the options method."""
    with patch("typed_requests.core.NetworkingManager.request", new_callable=AsyncMock) as mock_request:
        manager = NetworkingManager()
        await manager.options("https://example.com")
        mock_request.assert_called_once_with("OPTIONS", "https://example.com", expected_type=None)


@pytest.mark.anyio
async def test_patch_method_with_mock():
    """Test the patch method."""
    with patch("typed_requests.core.NetworkingManager.request", new_callable=AsyncMock) as mock_request:
        manager = NetworkingManager()
        await manager.patch("https://example.com", json={"data": "value"})
        mock_request.assert_called_once_with("PATCH", "https://example.com", expected_type=None, json={"data": "value"})


# =============================================================================
# Type Validation Tests
# =============================================================================


@pytest.mark.anyio
async def test_typed_response_json_exception(mock_httpx_response):
    """Test TypedResponse when JSON parsing fails."""
    # Mock the response to raise an exception when json() is called
    mock_httpx_response.json.side_effect = ValueError("Invalid JSON")

    with pytest.raises(ValueError):
        TypedResponse.from_response(mock_httpx_response, SimpleResponseDict)


@pytest.mark.anyio
async def test_get_with_type_validation():
    """Test GET request with type validation."""
    manager = NetworkingManager()

    # Mock the request method to return a typed response
    mock_typed_response = MagicMock(spec=TypedResponse)
    manager.request = AsyncMock(return_value=mock_typed_response)

    # Call get with type validation
    result = await manager.get("https://example.com", expected_type=SimpleResponseDict)

    # Verify the request was called with the expected type
    manager.request.assert_called_once_with("GET", "https://example.com", expected_type=SimpleResponseDict)
    assert result == mock_typed_response


@pytest.mark.anyio
async def test_post_with_type_validation():
    """Test POST request with type validation."""
    manager = NetworkingManager()

    # Mock the request method to return a typed response
    mock_typed_response = MagicMock(spec=TypedResponse)
    manager.request = AsyncMock(return_value=mock_typed_response)

    # Call post with type validation
    result = await manager.post("https://example.com", json={"test": "data"}, expected_type=SimpleResponseDict)

    # Verify the request was called with the expected type
    manager.request.assert_called_once_with(
        "POST", "https://example.com", expected_type=SimpleResponseDict, json={"test": "data"}
    )
    assert result == mock_typed_response


@pytest.mark.anyio
async def test_typed_validation_with_strict_mode():
    """Test type validation with strict mode enabled."""
    manager = NetworkingManager()

    # Create a mock response with valid JSON
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = {"success": True, "data": {"message": "Hello", "count": 42}}
    mock_response.raise_for_status.return_value = None

    # Mock the internal client
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.request.return_value = mock_response
    manager._client = mock_client

    # Make a request with type validation
    result = await manager.get("https://example.com", expected_type=SimpleResponseDict)

    # Verify we got a TypedResponse
    assert isinstance(result, TypedResponse)
    assert result.response == mock_response
    assert result.data == {"success": True, "data": {"message": "Hello", "count": 42}}


@pytest.mark.anyio
async def test_all_typed_methods():
    """Test all HTTP methods with type validation."""
    manager = NetworkingManager()

    # Mock the request method
    mock_typed_response = MagicMock(spec=TypedResponse)
    manager.request = AsyncMock(return_value=mock_typed_response)

    # Test all methods with type validation
    methods_and_calls = [
        ("get", lambda: manager.get("https://example.com", expected_type=SimpleResponseDict)),
        ("post", lambda: manager.post("https://example.com", expected_type=SimpleResponseDict, json={"test": "data"})),
        ("put", lambda: manager.put("https://example.com", expected_type=SimpleResponseDict, json={"test": "data"})),
        ("delete", lambda: manager.delete("https://example.com", expected_type=SimpleResponseDict)),
        ("head", lambda: manager.head("https://example.com", expected_type=SimpleResponseDict)),
        ("options", lambda: manager.options("https://example.com", expected_type=SimpleResponseDict)),
        (
            "patch",
            lambda: manager.patch("https://example.com", expected_type=SimpleResponseDict, json={"test": "data"}),
        ),
    ]

    for _method_name, method_call in methods_and_calls:
        manager.request.reset_mock()
        result = await method_call()
        assert result == mock_typed_response
        assert manager.request.called


# =============================================================================
# Lifecycle Management Tests
# =============================================================================


@pytest.mark.anyio
async def test_get_client_with_default_params():
    """Test request method with default parameters"""
    # Create instance of NetworkingManager
    manager = NetworkingManager()

    # Create a mock AsyncClient instance
    mock_client_instance = AsyncMock(spec=httpx.AsyncClient)
    # Setup the mock request method to return a basic mock response
    mock_client_instance.request = AsyncMock(return_value=MagicMock(spec=httpx.Response))
    mock_client_instance.request.return_value.raise_for_status = MagicMock()

    # Set the internal client of the NetworkingManager instance to our mock
    manager._client = mock_client_instance

    # Call the request method
    await manager.request("GET", "https://example.com")

    # Verify the request was called with default parameters
    mock_client_instance.request.assert_called_once()
    args, kwargs = mock_client_instance.request.call_args

    # Check method and URL
    assert args[0] == "GET"
    assert args[1] == "https://example.com"

    # Check default timeout
    assert kwargs.get("timeout") == manager.DEFAULT_TIMEOUT

    # Check default headers
    headers = kwargs.get("headers", {})
    assert headers.get("accept") == "*/*"
    assert headers.get("user-agent") == manager.DEFAULT_USER_AGENT
    assert headers.get("accept-encoding") == "gzip,deflate"


@pytest.mark.anyio
async def test_startup_when_client_already_initialized():
    """Test calling startup() when client is already initialized - covers core.py line 75"""
    manager = NetworkingManager()

    # Initialize client first
    await manager.startup()
    assert manager._client is not None

    # Call startup again - this should trigger the "else" branch
    await manager.startup()

    # Cleanup
    await manager.shutdown()


@pytest.mark.anyio
async def test_shutdown_when_client_not_initialized():
    """Test calling shutdown() when client is not initialized - covers core.py lines 83-84"""
    manager = NetworkingManager()

    # Client should be None initially
    assert manager._client is None

    # Call shutdown without initializing - this should trigger the "else" branch
    await manager.shutdown()


@pytest.mark.anyio
async def test_shutdown_sequence():
    """Test the full shutdown sequence - covers core.py lines 79-82"""
    manager = NetworkingManager()

    # Initialize client
    await manager.startup()
    assert manager._client is not None

    # Now shutdown - this should trigger the "if" branch
    await manager.shutdown()
    assert manager._client is None

    # Call shutdown again to cover the "else" branch
    await manager.shutdown()


@pytest.mark.anyio
async def test_networking_manager_lifecycle():
    """Test complete lifecycle of NetworkingManager to ensure all paths are covered"""
    manager = NetworkingManager()

    # Test initial state
    assert manager._client is None

    # Test startup
    await manager.startup()
    assert manager._client is not None

    # Test double startup (should warn)
    await manager.startup()
    assert manager._client is not None

    # Test shutdown
    await manager.shutdown()
    assert manager._client is None

    # Test double shutdown (should warn)
    await manager.shutdown()
    assert manager._client is None


@pytest.mark.anyio
async def test_request_triggers_startup():
    """Test that request() method triggers startup when client is not initialized"""
    manager = NetworkingManager()

    # Mock the client to avoid actual HTTP requests
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.raise_for_status.return_value = None
    mock_client.request.return_value = mock_response

    # Initially no client
    assert manager._client is None

    # Mock the startup method to set our mock client
    async def mock_startup():
        manager._client = mock_client

    manager.startup = mock_startup

    # Make a request - this should trigger startup
    await manager.request("GET", "https://example.com")

    # Verify client was set and request was made
    assert manager._client is mock_client
    mock_client.request.assert_called_once()


# =============================================================================
# Additional Coverage Tests
# =============================================================================


@pytest.mark.anyio
async def test_request_method_success(mock_httpx_response):
    """Test successful request method execution."""
    manager = NetworkingManager()

    # Mock the internal client
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.request.return_value = mock_httpx_response
    manager._client = mock_client

    # Make a request
    response = await manager.request("GET", "https://example.com")

    # Verify the response
    assert response == mock_httpx_response
    mock_client.request.assert_called_once()


@pytest.mark.anyio
async def test_post_method_direct(mock_httpx_response):
    """Test POST method directly with mocked client."""
    manager = NetworkingManager()

    # Mock the internal client
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.request.return_value = mock_httpx_response
    manager._client = mock_client

    # Make a POST request
    response = await manager.post("https://example.com", json={"test": "data"})

    # Verify the response
    assert response == mock_httpx_response
    mock_client.request.assert_called_once()


@pytest.mark.anyio
async def test_all_http_methods_comprehensive():
    """Test all HTTP methods comprehensively."""
    manager = NetworkingManager()

    # Mock the request method
    manager.request = AsyncMock()

    # Test data
    test_data = {"test": "data"}

    # Test all methods
    await manager.get("https://example.com")
    await manager.post("https://example.com", json=test_data)
    await manager.put("https://example.com", json=test_data)
    await manager.delete("https://example.com")
    await manager.head("https://example.com")
    await manager.options("https://example.com")
    await manager.patch("https://example.com", json=test_data)

    # Verify all methods were called
    assert manager.request.call_count == 7


# =============================================================================
# Logger Tests
# =============================================================================


def test_debug_logging_enabled():
    """Test debug logging when ENABLE_DEBUG is True - covers logger.py lines 20-21"""
    # Import the logger module to modify ENABLE_DEBUG

    # Save original value
    original_debug = logger.ENABLE_DEBUG

    try:
        # Enable debug logging
        logger.ENABLE_DEBUG = True

        # Create logger and test debug method
        test_logger = logger.get_logger("test")

        # This should now execute the debug logging code
        test_logger.debug("Test debug message")

    finally:
        # Restore original value
        logger.ENABLE_DEBUG = original_debug


def test_debug_logging_disabled():
    """Test debug logging when ENABLE_DEBUG is False - baseline test"""
    # Import the logger module

    # Ensure debug is disabled
    logger.ENABLE_DEBUG = False

    # Create logger and test debug method
    test_logger = logger.get_logger("test")

    # This should not execute the debug logging code
    test_logger.debug("Test debug message")


# =============================================================================
# Global Instance Tests
# =============================================================================


def test_global_networking_manager_instance():
    """Test that the global networking_manager instance is properly created."""
    # Test that the global instance exists
    assert global_networking_manager is not None
    assert isinstance(global_networking_manager, NetworkingManager)

    # Test that it has the expected default configuration
    assert global_networking_manager.DEFAULT_TIMEOUT == 9
    assert (
        global_networking_manager.DEFAULT_USER_AGENT
        == "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:130.0) Gecko/20100101 Firefox/130.0"
    )
