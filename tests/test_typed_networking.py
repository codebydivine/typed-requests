from typing import TypedDict
from unittest.mock import MagicMock

import httpx
import pytest
from type_enforcer import ValidationError

from typed_requests.core import TypedResponse


# Define TypedDict classes outside of module level
# We'll use them inside fixtures to avoid pytest collection issues
def get_item_dict():
    class ItemDict(TypedDict):
        id: int
        name: str
        price: float

    return ItemDict


def get_response_dict():
    class ResponseDict(TypedDict):
        items: list[get_item_dict()]
        total: int
        next_page: str | None

    return ResponseDict


@pytest.fixture
def test_item_dict():
    return get_item_dict()


@pytest.fixture
def test_response_dict():
    return get_response_dict()


@pytest.fixture
def mock_httpx_response():
    """Create a mock HTTP response with JSON data."""
    mock_response = MagicMock(spec=httpx.Response)

    # Valid test data
    valid_data = {
        "items": [{"id": 1, "name": "Item 1", "price": 10.99}, {"id": 2, "name": "Item 2", "price": 20.50}],
        "total": 2,
        "next_page": None,
    }

    mock_response.json.return_value = valid_data
    mock_response.raise_for_status.return_value = None
    return mock_response


@pytest.fixture
def mock_invalid_response():
    """Create a mock HTTP response with invalid JSON data."""
    mock_response = MagicMock(spec=httpx.Response)

    # Invalid test data (missing required fields)
    invalid_data = {
        "items": [
            {"id": 1, "name": "Item 1"},  # Missing price
            {"id": 2, "price": 20.50},  # Missing name
        ],
        "total": 2,
    }

    mock_response.json.return_value = invalid_data
    mock_response.raise_for_status.return_value = None
    return mock_response


@pytest.mark.anyio
async def test_typed_response_creation(test_response_dict):
    """Test creating a TypedResponse from raw data."""
    # Create test data
    raw_data = {"items": [{"id": 1, "name": "Item 1", "price": 10.99}], "total": 1, "next_page": None}

    # Create a mock response
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = raw_data

    # Create TypedResponse
    typed_response = TypedResponse.from_response(mock_response, test_response_dict)

    # Validate the typed response
    assert typed_response.response == mock_response
    assert typed_response.data["items"][0]["id"] == 1
    assert typed_response.data["items"][0]["name"] == "Item 1"
    assert typed_response.data["items"][0]["price"] == 10.99
    assert typed_response.data["total"] == 1
    assert typed_response.data["next_page"] is None


@pytest.mark.anyio
async def test_typed_response_validation_error(test_response_dict):
    """Test TypedResponse with invalid data."""
    # Create invalid test data
    invalid_data = {
        "items": [
            {"id": "not-an-int", "name": "Item 1", "price": 10.99}  # id should be int
        ],
        "total": 1,
        "next_page": None,
    }

    # Create a mock response
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.json.return_value = invalid_data

    # Verify validation error is raised
    with pytest.raises(ValidationError):
        TypedResponse.from_response(mock_response, test_response_dict)
