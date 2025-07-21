"""
Basic usage examples for divine-typed-requests library.

This example demonstrates the fundamental features of the divine-typed-requests library
including making simple HTTP requests and basic type validation.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, TypedDict

from type_enforcer import ValidationError

from typed_requests import networking_manager

# ===== Type Definitions =====


class UserResponse(TypedDict):
    id: int
    name: str
    email: str
    active: bool


class PostResponse(TypedDict):
    id: int
    title: str
    body: str
    userId: int


@dataclass
class APIError:
    error: str
    message: str
    status_code: int


# ===== Basic HTTP Requests =====


async def basic_get_request():
    """Example of making a basic GET request without type validation."""
    print("=== Basic GET Request ===")

    try:
        # Make a simple GET request
        response = await networking_manager.get("https://httpbin.org/get")

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.json()}")

    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}")


async def basic_post_request():
    """Example of making a basic POST request with JSON data."""
    print("\n=== Basic POST Request ===")

    try:
        # Prepare JSON data
        post_data = {"title": "My New Post", "body": "This is the content of my post", "userId": 1}

        # Make POST request
        response = await networking_manager.post("https://httpbin.org/post", json=post_data)

        print(f"Status Code: {response.status_code}")
        print(f"Posted Data: {response.json()['json']}")

    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}")


# ===== Type-Safe HTTP Requests =====


async def typed_get_request():
    """Example of making a GET request with type validation."""
    print("\n=== Type-Safe GET Request ===")

    # Mock user data structure (in real usage, this would come from an API)
    # We'll use httpbin.org which returns predictable JSON structure

    try:
        # Make a typed GET request
        response = await networking_manager.get(
            "https://httpbin.org/json",
            expected_type=dict[str, Any],  # Basic type validation
        )

        print(f"Status Code: {response.response.status_code}")
        print(f"Validated Data: {response.data}")
        print(f"Data Type: {type(response.data)}")

    except ValidationError as e:
        print(f"Validation Error: {e}")
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}")


async def typed_post_with_validation():
    """Example of making a POST request with response type validation."""
    print("\n=== Type-Safe POST Request ===")

    try:
        # Prepare data
        post_data = {"title": "Test Post", "body": "This is a test post", "userId": 1}

        # Make typed POST request
        response = await networking_manager.post(
            "https://httpbin.org/post",
            json=post_data,
            expected_type=dict[str, Any],  # Validate response structure
        )

        print(f"Status Code: {response.response.status_code}")
        print(f"Original Data: {response.data['json']}")
        print(f"Request Headers: {response.data['headers']}")

    except ValidationError as e:
        print(f"Validation Error: {e}")
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}")


# ===== Error Handling Examples =====


async def error_handling_examples():
    """Examples of handling different types of errors."""
    print("\n=== Error Handling Examples ===")

    # Example 1: Network error
    print("1. Network Error Example:")
    try:
        await networking_manager.get("https://nonexistent-domain-12345.com")
        print("This should not print")
    except Exception as e:  # noqa: BLE001
        print(f"   Caught network error: {type(e).__name__}: {e}")

    # Example 2: HTTP error (404)
    print("\n2. HTTP Error Example:")
    try:
        await networking_manager.get("https://httpbin.org/status/404")
        print("This should not print")
    except Exception as e:  # noqa: BLE001
        print(f"   Caught HTTP error: {type(e).__name__}: {e}")

    # Example 3: Validation error
    print("\n3. Validation Error Example:")
    try:
        # Try to validate response against a strict type
        await networking_manager.get(
            "https://httpbin.org/json",
            expected_type=UserResponse,  # This will fail validation
        )
        print("This should not print")
    except ValidationError as e:
        print(f"   Caught validation error: {e}")
    except Exception as e:  # noqa: BLE001
        print(f"   Caught other error: {type(e).__name__}: {e}")


# ===== Custom Headers and Configuration =====


async def custom_headers_example():
    """Example of using custom headers."""
    print("\n=== Custom Headers Example ===")

    try:
        # Custom headers
        headers = {
            "User-Agent": "divine-typed-requests-Example/1.0",
            "Authorization": "Bearer fake-token-123",
            "X-Custom-Header": "custom-value",
        }

        response = await networking_manager.get("https://httpbin.org/headers", headers=headers)

        print(f"Status Code: {response.status_code}")
        print(f"Request Headers Received: {response.json()['headers']}")

    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}")


async def timeout_example():
    """Example of using custom timeout."""
    print("\n=== Timeout Example ===")

    try:
        # Set a very short timeout to demonstrate timeout handling
        await networking_manager.get(
            "https://httpbin.org/delay/5",  # This endpoint delays for 5 seconds
            timeout=2.0,  # But we timeout after 2 seconds
        )
        print("This should not print")
    except Exception as e:  # noqa: BLE001
        print(f"Caught timeout error: {type(e).__name__}: {e}")


# ===== Main Example Function =====


async def main():
    """Run all examples."""
    print("Divine Requests Library - Basic Usage Examples")
    print("=" * 50)

    # Initialize the networking manager
    await networking_manager.startup()

    try:
        # Run all examples
        await basic_get_request()
        await basic_post_request()
        await typed_get_request()
        await typed_post_with_validation()
        await error_handling_examples()
        await custom_headers_example()
        await timeout_example()

        print("\n" + "=" * 50)
        print("All examples completed!")

    finally:
        # Clean up
        await networking_manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
