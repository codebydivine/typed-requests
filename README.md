# Typed Requests

[![PyPI version](https://badge.fury.io/py/divine-typed-requests.svg)](https://badge.fury.io/py/divine-typed-requests)
[![Python versions](https://img.shields.io/pypi/pyversions/divine-typed-requests.svg)](https://pypi.org/project/divine-typed-requests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Test Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/divinescreener/typed-requests)
[![Built with httpx](https://img.shields.io/badge/built%20with-httpx-blue.svg)](https://www.python-httpx.org/)

A modern, type-safe HTTP client for Python 3.13+ that validates API responses at runtime. Built on [httpx](https://www.python-httpx.org/) with complete type validation, it catches data issues before they become bugs.

## 🎯 Why Typed Requests?

### The Problem

Working with external APIs in Python is risky:

- **API responses don't always match documentation** 📋❌
- **Silent type mismatches cause bugs deep in your code** 🐛
- **No runtime validation of response structures** 🏗️
- **Poor error messages when things go wrong** 😕

### The Solution

Typed Requests provides **automatic runtime validation** for all your HTTP requests:

```python
# Without Typed Requests - Hope the API is correct 🤞
response = requests.get("https://api.example.com/user/123")
user_data = response.json()
# This might crash anywhere in your code:
print(f"User {user_data['name']} has {user_data['credits']} credits")

# With Typed Requests - Validated and type-safe ✅
from typed_requests import networking_manager
from typing import TypedDict

class User(TypedDict):
    name: str
    credits: int

response = await networking_manager.get(
    "https://api.example.com/user/123",
    expected_type=User
)
# Safe to use - guaranteed to match User structure
print(f"User {response.data['name']} has {response.data['credits']} credits")
```

## ✨ Features

- 🛡️ **Runtime Type Validation**: Catch API changes and inconsistencies immediately
- 🔍 **Clear Error Messages**: Know exactly what's wrong: `data.users[0].email: Expected str, got null`
- 🚀 **Built on httpx**: Modern async HTTP with HTTP/2 support
- 🎯 **Type-Safe Returns**: Get `TypedResponse[T]` with full IDE autocomplete
- 🔄 **Smart Type Conversion**: Automatically converts compatible types (dict → dataclass)
- ⚡ **High Performance**: Connection pooling and persistent sessions
- 🐍 **Pure Python Types**: Works with TypedDict, dataclass, Optional, Union, and more
- ✅ **100% Test Coverage**: Battle-tested and production-ready

## 📦 Installation

```bash
# Using pip
pip install divine-typed-requests

# Using uv
uv add divine-typed-requests

# For development
git clone https://github.com/divine/typed-requests
cd typed-requests
uv sync
```

### Requirements
- Python 3.13+
- httpx
- divine-type-enforcer

## 🚀 Quick Start

```python
import asyncio
from typed_requests import networking_manager
from typing import TypedDict, List

class Post(TypedDict):
    id: int
    title: str
    content: str
    author: str
    likes: int

class PostsResponse(TypedDict):
    posts: List[Post]
    total: int
    page: int

async def main():
    # Fetch and validate blog posts
    response = await networking_manager.get(
        "https://api.example.com/posts",
        expected_type=PostsResponse
    )
    
    # response.data is fully typed and validated
    for post in response.data['posts']:
        print(f"{post['title']} by {post['author']} ({post['likes']} likes)")
    
    print(f"Showing page {response.data['page']} of {response.data['total']} posts")

asyncio.run(main())
```

## 📖 Usage Examples

### Basic Requests (Untyped)

For simple requests without validation:

```python
from typed_requests import networking_manager

# Simple GET request
response = await networking_manager.get("https://api.github.com/users/octocat")
print(response.json()["name"])  # "The Octocat"

# POST with JSON data
response = await networking_manager.post(
    "https://api.example.com/users",
    json={"name": "Alice", "email": "alice@example.com"}
)
print(response.status_code)  # 201
```

### Type-Safe Requests

Add type validation to catch issues early:

```python
from typing import TypedDict, Optional, List
from typed_requests import networking_manager
from type_enforcer import ValidationError

class GitHubUser(TypedDict):
    login: str
    id: int
    name: Optional[str]
    email: Optional[str]
    bio: Optional[str]
    public_repos: int
    followers: int
    following: int

try:
    # Fetch with type validation
    response = await networking_manager.get(
        "https://api.github.com/users/octocat",
        expected_type=GitHubUser
    )
    
    # response.data is now typed as GitHubUser
    user = response.data
    print(f"{user['login']} has {user['followers']} followers")
    
except ValidationError as e:
    print(f"API response doesn't match expected structure: {e}")
```

### Working with Complex APIs

```python
from typing import TypedDict, List, Optional, Literal
from datetime import datetime

class Repository(TypedDict):
    id: int
    name: str
    full_name: str
    description: Optional[str]
    private: bool
    fork: bool
    created_at: str
    updated_at: str
    pushed_at: str
    language: Optional[str]
    stargazers_count: int
    watchers_count: int
    forks_count: int

class SearchResponse(TypedDict):
    total_count: int
    incomplete_results: bool
    items: List[Repository]

# Search GitHub repositories with full type safety
response = await networking_manager.get(
    "https://api.github.com/search/repositories",
    params={"q": "language:python stars:>1000", "sort": "stars"},
    expected_type=SearchResponse
)

# Process validated results
for repo in response.data['items'][:5]:
    print(f"⭐ {repo['stargazers_count']:,} - {repo['full_name']}")
    if repo['description']:
        print(f"   {repo['description'][:60]}...")
```

### Error Handling

```python
from typed_requests import networking_manager
from type_enforcer import ValidationError
import httpx

class ExpectedResponse(TypedDict):
    status: str
    data: dict[str, any]

try:
    response = await networking_manager.get(
        "https://api.example.com/data",
        expected_type=ExpectedResponse,
        timeout=30.0
    )
    print(f"Status: {response.data['status']}")
    
except ValidationError as e:
    # Handle validation errors
    print(f"Response validation failed: {e}")
    # Example: "data.status: Expected str, got int"
    
except httpx.HTTPStatusError as e:
    # Handle HTTP errors (4xx, 5xx)
    print(f"HTTP error {e.response.status_code}: {e.response.text}")
    
except httpx.RequestError as e:
    # Handle connection errors
    print(f"Connection error: {e}")
```

### All HTTP Methods

```python
from typed_requests import networking_manager

# GET request
user = await networking_manager.get(
    "https://api.example.com/users/123",
    expected_type=UserResponse
)

# POST request
new_user = await networking_manager.post(
    "https://api.example.com/users",
    json={"name": "Bob", "email": "bob@example.com"},
    expected_type=UserResponse
)

# PUT request
updated_user = await networking_manager.put(
    "https://api.example.com/users/123",
    json={"name": "Robert", "email": "robert@example.com"},
    expected_type=UserResponse
)

# PATCH request
patched_user = await networking_manager.patch(
    "https://api.example.com/users/123",
    json={"name": "Rob"},
    expected_type=UserResponse
)

# DELETE request
await networking_manager.delete("https://api.example.com/users/123")

# HEAD request
headers = await networking_manager.head("https://api.example.com/users/123")

# OPTIONS request
options = await networking_manager.options("https://api.example.com/users")
```

### Custom Headers and Authentication

```python
# Bearer token authentication
response = await networking_manager.get(
    "https://api.example.com/protected",
    headers={"Authorization": "Bearer your-token-here"},
    expected_type=ProtectedResource
)

# Custom headers
response = await networking_manager.post(
    "https://api.example.com/data",
    json={"key": "value"},
    headers={
        "X-API-Key": "your-api-key",
        "X-Client-Version": "1.0.0"
    },
    expected_type=ApiResponse
)
```

### Advanced Configuration

```python
from typed_requests import NetworkingManager
from typed_requests.tls import TLS_CONTEXT_HTTP2

# Create custom manager with specific configuration
async def create_custom_client():
    manager = NetworkingManager(
        tls_context=TLS_CONTEXT_HTTP2,
        enable_http2=True
    )
    await manager.startup()
    
    try:
        # Use the manager
        response = await manager.get(
            "https://api.example.com/data",
            timeout=60.0,  # 60 second timeout
            expected_type=DataResponse
        )
        return response.data
        
    finally:
        # Always cleanup
        await manager.shutdown()

# Run with proper lifecycle management
data = await create_custom_client()
```

## 🏗️ Real-World Example: Financial API Integration

Here's a complete example using the DexScreener API:

```python
from typing import TypedDict, List, Optional
from typed_requests import networking_manager
from decimal import Decimal

class Token(TypedDict):
    address: str
    name: str
    symbol: str

class Liquidity(TypedDict):
    usd: float
    base: float
    quote: float

class Volume(TypedDict):
    h24: float
    h6: float
    h1: float
    m5: float

class PriceChange(TypedDict):
    h24: float
    h6: float
    h1: float
    m5: float

class TokenPair(TypedDict):
    chainId: str
    dexId: str
    url: str
    pairAddress: str
    labels: Optional[List[str]]
    baseToken: Token
    quoteToken: Token
    priceNative: str
    priceUsd: str
    liquidity: Liquidity
    fdv: float
    marketCap: float
    pairCreatedAt: int
    volume: Volume
    priceChange: PriceChange
    trades: dict[str, int]
    quoteTokenSymbol: str

class DexScreenerResponse(TypedDict):
    schemaVersion: str
    pairs: List[TokenPair]

async def get_trending_tokens():
    """Fetch and analyze trending tokens from DexScreener"""
    
    response = await networking_manager.get(
        "https://api.dexscreener.com/latest/dex/tokens/SOL",
        expected_type=DexScreenerResponse
    )
    
    # Process validated data safely
    pairs = response.data['pairs']
    
    # Sort by 24h volume
    sorted_pairs = sorted(
        pairs,
        key=lambda p: p['volume']['h24'],
        reverse=True
    )
    
    print("🔥 Top Trending SOL Tokens by Volume:\n")
    
    for pair in sorted_pairs[:10]:
        symbol = pair['baseToken']['symbol']
        price = float(pair['priceUsd'])
        volume_24h = pair['volume']['h24']
        change_24h = pair['priceChange']['h24']
        liquidity = pair['liquidity']['usd']
        
        # Emoji based on price change
        trend = "🟢" if change_24h > 0 else "🔴"
        
        print(f"{trend} {symbol}")
        print(f"   Price: ${price:.6f}")
        print(f"   24h Volume: ${volume_24h:,.0f}")
        print(f"   24h Change: {change_24h:+.2f}%")
        print(f"   Liquidity: ${liquidity:,.0f}")
        print(f"   DEX: {pair['dexId']}")
        print()

# Run the analysis
await get_trending_tokens()
```

## 📚 API Reference

### `NetworkingManager`

The main class for making HTTP requests.

#### Methods

All methods support the same parameters:

```python
async def get(url: str, *, expected_type: Optional[Type[T]] = None, **kwargs) -> Union[Response, TypedResponse[T]]
async def post(url: str, *, expected_type: Optional[Type[T]] = None, **kwargs) -> Union[Response, TypedResponse[T]]
async def put(url: str, *, expected_type: Optional[Type[T]] = None, **kwargs) -> Union[Response, TypedResponse[T]]
async def patch(url: str, *, expected_type: Optional[Type[T]] = None, **kwargs) -> Union[Response, TypedResponse[T]]
async def delete(url: str, *, expected_type: Optional[Type[T]] = None, **kwargs) -> Union[Response, TypedResponse[T]]
async def head(url: str, *, expected_type: Optional[Type[T]] = None, **kwargs) -> Union[Response, TypedResponse[T]]
async def options(url: str, *, expected_type: Optional[Type[T]] = None, **kwargs) -> Union[Response, TypedResponse[T]]
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | `str` | The URL to request |
| `expected_type` | `Optional[Type[T]]` | Expected response type for validation |
| `**kwargs` | `Any` | Additional arguments passed to httpx |

Common kwargs:
- `params`: Query parameters
- `json`: JSON data for request body
- `headers`: Custom headers
- `timeout`: Request timeout in seconds
- `follow_redirects`: Whether to follow redirects

### `TypedResponse[T]`

A generic wrapper containing validated response data.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `response` | `httpx.Response` | Original HTTP response |
| `data` | `T` | Validated and typed response data |

### Global Instance

A pre-configured global instance is available:

```python
from typed_requests import networking_manager

# Ready to use without initialization
response = await networking_manager.get(url)
```

## 🛡️ Best Practices

### 1. Define Response Types Upfront

```python
# types/api.py
from typing import TypedDict, List, Optional

class PaginatedResponse(TypedDict):
    items: List[dict]
    total: int
    page: int
    per_page: int
    has_next: bool

class ErrorResponse(TypedDict):
    error: str
    message: str
    code: Optional[str]
```

### 2. Create API Client Classes

```python
from typed_requests import NetworkingManager
from typing import Optional

class MyAPIClient:
    def __init__(self, api_key: str):
        self.manager = NetworkingManager()
        self.api_key = api_key
        self.base_url = "https://api.example.com"
    
    async def __aenter__(self):
        await self.manager.startup()
        return self
    
    async def __aexit__(self, *args):
        await self.manager.shutdown()
    
    def _headers(self) -> dict:
        return {"X-API-Key": self.api_key}
    
    async def get_user(self, user_id: int) -> UserResponse:
        response = await self.manager.get(
            f"{self.base_url}/users/{user_id}",
            headers=self._headers(),
            expected_type=UserResponse
        )
        return response.data

# Usage
async with MyAPIClient("your-api-key") as client:
    user = await client.get_user(123)
    print(user['name'])
```

### 3. Handle Errors Gracefully

```python
from type_enforcer import ValidationError
import httpx

async def safe_api_call(url: str, expected_type: type) -> Optional[dict]:
    try:
        response = await networking_manager.get(url, expected_type=expected_type)
        return response.data
    
    except ValidationError as e:
        logger.error(f"Response validation failed: {e}")
        # Log the actual response for debugging
        raw_response = await networking_manager.get(url)
        logger.debug(f"Raw response: {raw_response.text}")
        return None
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP {e.response.status_code}: {e.response.text}")
        return None
    
    except httpx.RequestError as e:
        logger.error(f"Request failed: {e}")
        return None
```

## 🔧 Development

### Setup

```bash
# Clone the repository
git clone https://github.com/divinescreener/typed-requests
cd typed-requests

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check
uv run mypy src
```

### Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

Key points:
- Maintain 100% test coverage
- Follow the existing code style  
- Add tests for new features
- Update documentation as needed

## 📊 Performance

Typed Requests is built for production use:

- **Connection Pooling**: Reuses connections for better performance
- **HTTP/2 Support**: Multiplexed requests when supported
- **Async Throughout**: Non-blocking I/O for high concurrency
- **Smart Validation**: Only validates when `expected_type` is provided

## 🔒 Security

- **TLS Verification**: Secure by default with certificate validation
- **No Code Execution**: Type validation never executes arbitrary code
- **Timeout Protection**: Prevents hanging on slow endpoints
- **Memory Efficient**: Streams large responses when needed

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built on the excellent [httpx](https://www.python-httpx.org/) library
- Type validation powered by [divine-type-enforcer](https://github.com/divinescreener/type-enforcer)
- Inspired by the need for safer API integrations

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/divinescreener">DIVINE</a>
</p>