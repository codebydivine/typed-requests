# Divine Requests

A type-safe HTTP client library for Python 3.13+ with validation and detailed error reporting.

This library provides a clean, efficient way to make HTTP requests with automatic type validation,
ensuring that your API responses match the expected structure and types before processing them.

## Features

*   **Type-Safe HTTP Requests:** Automatic validation of response data against expected types.
*   **Detailed Error Reporting:** Pinpoints exactly where validation failed in nested API responses.
*   **Complex Type Support:** Supports `List`, `Dict`, `Tuple`, `Optional`, `Union`, `Literal`, `Enum`, `TypedDict`, and `dataclass`.
*   **Clean API:** Simple async HTTP methods with optional type validation.
*   **HTTP/2 Support:** Built on httpx with modern HTTP features.
*   **Performance Optimized:** Persistent connections and connection pooling.
*   **Python 3.13+:** Leverages modern Python features.
*   **100% Test Coverage:** Every line of code is thoroughly tested, ensuring reliability and stability.

## Why Divine Requests Is Useful

### Type-Safe API Integration
When working with external APIs, responses may not always conform to documentation. Divine Requests validates responses before your code processes them, preventing cascading errors from malformed data.

### Better Error Messages
Instead of cryptic `AttributeError` or `TypeError` deep in your processing logic, Divine Requests provides clear, path-based error messages like `data.users[0].settings.notifications: Expected bool, got str`.

### Schema Documentation
TypedDict and dataclass definitions serve as living documentation of your API response structures, making code more maintainable and self-documenting.

### Gradual Typing
While type annotations help at development time, Divine Requests extends their value to runtime, offering a bridge between static and dynamic typing that's especially valuable for API responses.

### Data Transformation
Beyond validation, Divine Requests can convert compatible types (like dictionaries to dataclasses), simplifying your data pipeline.

## Installation

```bash
pip install divine-requests
```

## Usage

Import the networking manager and use it to make type-safe HTTP requests:

```python
import asyncio
from requests import networking_manager
from type_enforcer import ValidationError
from typing import List, Dict, Optional, TypedDict
from dataclasses import dataclass

# Define response types
class UserResponse(TypedDict):
    id: int
    name: str
    email: str
    is_active: bool

class UsersListResponse(TypedDict):
    users: List[UserResponse]
    total: int
    page: int

# Basic untyped request
response = await networking_manager.get("https://api.example.com/users")
# >> <Response [200 OK]>
print(response.status_code)
# >> 200
print(response.json())
# >> {'users': [{'id': 1, 'name': 'Alice', 'email': 'alice@example.com', 'is_active': True}], 'total': 1, 'page': 1}

# Type-safe request with validation
typed_response = await networking_manager.get(
    "https://api.example.com/users",
    expected_type=UsersListResponse
)
# >> TypedResponse containing validated data

# Access validated and typed data
users = typed_response.data["users"]
for user in users:
    print(f"User: {user['name']} ({user['email']})")
# >> User: Alice (alice@example.com)

# POST request with JSON data
post_data = {
    "title": "My New Post",
    "content": "This is the content of my post",
    "author_id": 123
}

response = await networking_manager.post(
    "https://api.example.com/posts",
    json=post_data
)
# >> <Response [201 Created]>

# Error handling for validation failures
try:
    response = await networking_manager.get(
        "https://api.example.com/malformed",
        expected_type=UsersListResponse
    )
except ValidationError as e:
    print(e)
# >> users[0].id: Expected int, got str

# Error handling for HTTP failures
try:
    response = await networking_manager.get("https://api.example.com/notfound")
except Exception as e:
    print(f"Request failed: {e}")
# >> Request failed: 404 Client Error: Not Found

# Custom headers and timeout
response = await networking_manager.get(
    "https://api.example.com/protected",
    headers={"Authorization": "Bearer token123"},
    timeout=30.0
)

# Different HTTP methods
response = await networking_manager.post("https://api.example.com/data", json={"key": "value"})
response = await networking_manager.put("https://api.example.com/data/1", json={"key": "updated"})
response = await networking_manager.patch("https://api.example.com/data/1", json={"key": "patched"})
response = await networking_manager.delete("https://api.example.com/data/1")

# Using with custom NetworkingManager instance
from requests import NetworkingManager

async def main():
    manager = NetworkingManager()
    await manager.startup()
    try:
        response = await manager.get(
            "https://api.example.com/users",
            expected_type=UsersListResponse
        )
        print(f"Got {len(response.data['users'])} users")
    finally:
        await manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### NetworkingManager

The main class for making HTTP requests with optional type validation.

#### Methods

- `get(url, *, expected_type=None, **kwargs)` - Make a GET request
- `post(url, *, expected_type=None, **kwargs)` - Make a POST request
- `put(url, *, expected_type=None, **kwargs)` - Make a PUT request
- `patch(url, *, expected_type=None, **kwargs)` - Make a PATCH request
- `delete(url, *, expected_type=None, **kwargs)` - Make a DELETE request
- `head(url, *, expected_type=None, **kwargs)` - Make a HEAD request
- `options(url, *, expected_type=None, **kwargs)` - Make an OPTIONS request

#### Parameters

- `url` (str): The URL to request
- `expected_type` (Optional[Type[T]]): The expected type for response validation
- `**kwargs`: Additional arguments passed to httpx (headers, timeout, etc.)

#### Returns

- `httpx.Response` if no `expected_type` is provided
- `TypedResponse[T]` if `expected_type` is provided

### TypedResponse

A wrapper around httpx.Response that includes validated data.

#### Attributes

- `response`: The original httpx.Response object
- `data`: The validated response data with the correct type

## Configuration

The networking manager can be configured with custom settings:

```python
from requests import NetworkingManager
from requests.tls import TLS_CONTEXT_HTTP2

# Custom configuration
manager = NetworkingManager(
    tls_context=TLS_CONTEXT_HTTP2,
    enable_http2=True
)

# Custom timeout and headers
response = await manager.get(
    "https://api.example.com/data",
    timeout=30.0,
    headers={"Authorization": "Bearer token"}
)
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

The project maintains 100% test coverage, which helps ensure stability and correctness as new features are added. Any contributions should include appropriate tests to maintain this coverage level.

## Real-World Examples

Check out the `examples/` directory for real-world use cases of divine-requests:

### API Response Validation

See [`examples/api_response_validation.py`](examples/api_response_validation.py) for a comprehensive example of validating complex API responses. This example shows how to:

- Define nested TypedDict structures for complex JSON responses
- Validate responses against these structures
- Handle validation errors gracefully
- Work with deeply nested optional fields

This pattern is especially useful when working with third-party APIs where you need to ensure the response matches your expected structure before processing it further.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
