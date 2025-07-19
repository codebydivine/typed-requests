# Divine Requests Examples

This directory contains comprehensive examples demonstrating how to use the `divine-typed-requests` library for various real-world scenarios.

## Available Examples

### 1. Basic Usage (`basic_usage.py`)
Demonstrates fundamental features including:
- Simple GET/POST requests
- Type-safe requests with validation
- Custom headers and timeouts
- Error handling patterns
- Basic request lifecycle

**Run with:**
```bash
python examples/basic_usage.py
```

### 2. API Response Validation (`api_response_validation.py`)
Shows how to validate complex API responses using:
- DexScreener API integration
- Complex nested TypedDict structures
- Real-time financial data validation
- Error handling for invalid responses
- Advanced type validation patterns

**Run with:**
```bash
python examples/api_response_validation.py
```

### 3. Advanced API Integration (`advanced_api_integration.py`)
Demonstrates sophisticated API client patterns:
- GitHub API client implementation
- Async context manager patterns
- Retry logic and error handling
- Data transformation and analysis
- Authentication workflows

**Run with:**
```bash
python examples/advanced_api_integration.py
```

### 4. E-commerce API Client (`e_commerce_api_client.py`)
Comprehensive e-commerce API client example featuring:
- Product catalog management
- Shopping cart operations
- Order processing workflows
- Payment integration patterns
- User authentication and authorization

**Run with:**
```bash
python examples/e_commerce_api_client.py
```

## Key Patterns Demonstrated

### Type-Safe HTTP Requests
```python
from requests import networking_manager
from typing import TypedDict

class UserResponse(TypedDict):
    id: int
    name: str
    email: str

# Type-safe request with automatic validation
response = await networking_manager.get(
    "https://api.example.com/users/1",
    expected_type=UserResponse
)

# response.data is now fully typed and validated
user_id = response.data["id"]  # Type: int
user_name = response.data["name"]  # Type: str
```

### API Client Class Pattern
```python
class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.manager = NetworkingManager()

    async def __aenter__(self):
        await self.manager.startup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.manager.shutdown()

    async def get_user(self, user_id: int) -> UserResponse:
        response = await self.manager.get(
            f"{self.base_url}/users/{user_id}",
            expected_type=UserResponse
        )
        return response.data

# Usage
async with APIClient("https://api.example.com") as client:
    user = await client.get_user(1)
    print(user["name"])
```

### Error Handling and Retry Logic
```python
async def fetch_with_retry(url: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            response = await networking_manager.get(url)
            return response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Complex Type Validation
```python
class PaginatedResponse(TypedDict):
    items: List[ItemDict]
    page: int
    per_page: int
    total: int
    has_next: bool

# Automatically validates the entire response structure
response = await networking_manager.get(
    "https://api.example.com/items",
    expected_type=PaginatedResponse
)

# All fields are now type-safe
items = response.data["items"]  # Type: List[ItemDict]
has_more = response.data["has_next"]  # Type: bool
```

## Running the Examples

### Prerequisites
- Python 3.13+
- `divine-typed-requests` library installed
- `divine-type-enforcer` library (automatically installed as dependency)

### Installation
```bash
pip install divine-typed-requests
```

### Running Individual Examples
Each example can be run independently:

```bash
# Basic usage patterns
python examples/basic_usage.py

# API response validation
python examples/api_response_validation.py

# Advanced API integration
python examples/advanced_api_integration.py

# E-commerce patterns
python examples/e_commerce_api_client.py
```

## Testing the Examples

The examples are thoroughly tested to ensure they work correctly:

```bash
# Run example tests
python -m pytest tests/test_examples.py -v

# Run all tests including examples
python -m pytest tests/ -v
```

## Key Features Demonstrated

1. **Type Safety**: All API responses are validated against expected types
2. **Error Handling**: Comprehensive error handling patterns for network, validation, and API errors
3. **Async/Await**: Modern async/await patterns for efficient I/O operations
4. **Context Managers**: Proper resource management with async context managers
5. **Real-World Patterns**: Practical patterns for authentication, pagination, retry logic, and more
6. **Flexibility**: Examples work with any HTTP API by adapting the type definitions

## Best Practices

1. **Always use type validation** for production APIs to catch issues early
2. **Implement proper error handling** for network and validation errors
3. **Use async context managers** for proper resource cleanup
4. **Define clear TypedDict structures** for API responses
5. **Implement retry logic** for resilient API clients
6. **Use authentication patterns** for secure API access

## Contributing

Feel free to contribute additional examples or improvements to existing ones. All examples should:

1. Be well-documented with clear explanations
2. Include proper error handling
3. Use type-safe patterns
4. Be testable and include test coverage
5. Follow the established patterns in the codebase
