from typing import Any, TypeVar, overload

import httpx
from type_enforcer import ValidationError, enforce

from .logger import get_logger
from .tls import TLS_CONTEXT_HTTP2

logger = get_logger(__name__)

T = TypeVar("T")


class TypedResponse[T]:
    """A wrapper for HTTP responses with type validation."""

    __slots__ = ("_data", "response")

    response: httpx.Response

    def __init__(self, response: httpx.Response, data: T) -> None:
        self.response = response
        self._data = data

    @property
    def data(self) -> T:
        """Get the validated response data with proper typing."""
        return self._data

    @classmethod
    def from_response(cls, response: httpx.Response, expected_type: type[T]) -> "TypedResponse[T]":
        """Create a TypedResponse with type validation."""
        try:
            validated_data = enforce(response.json(), expected_type)
            return cls(response, validated_data)
        except ValidationError as e:
            logger.error(f"Response validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error processing response: {e}", exc_info=True)
            raise


class NetworkingManager:
    """Async HTTP client with type validation support."""

    DEFAULT_TIMEOUT = 9
    DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:130.0) Gecko/20100101 Firefox/130.0"

    def __init__(self, tls_context=TLS_CONTEXT_HTTP2, enable_http2: bool = True):
        """Initialize NetworkingManager with TLS context and HTTP/2 setting."""
        self._client: httpx.AsyncClient | None = None
        self._tls_context = tls_context
        self._enable_http2 = enable_http2

    async def startup(self):
        """Initialize the persistent HTTP client."""
        if self._client is None:
            logger.info("Initializing persistent HTTP client")
            self._client = httpx.AsyncClient(http2=self._enable_http2, verify=self._tls_context)
        else:
            logger.warning("HTTP client already initialized")

    async def shutdown(self):
        """Close the persistent HTTP client."""
        if self._client is not None:
            logger.info("Closing persistent HTTP client")
            await self._client.aclose()
            self._client = None
        else:
            logger.warning("HTTP client not initialized or already closed")

    @overload
    async def request(self, method: str, url: str, *, expected_type: type[T], **kwargs: Any) -> TypedResponse[T]: ...

    @overload
    async def request(self, method: str, url: str, *, expected_type: None = None, **kwargs: Any) -> httpx.Response: ...

    async def request(
        self, method: str, url: str, *, expected_type: type[T] | None = None, **kwargs: Any
    ) -> httpx.Response | TypedResponse[T]:
        if self._client is None:
            logger.info("NetworkingManager not started. Calling startup()")
            await self.startup()

        if self._client is None:
            raise RuntimeError("Client should be initialized after startup")

        try:
            # Extract and prepare headers
            headers = kwargs.pop("headers", {})
            timeout = kwargs.pop("timeout", self.DEFAULT_TIMEOUT)
            kwargs.pop("proxy", None)  # Remove proxy if present
            logger.info(f"Requesting {method} {url} with timeout {timeout}")

            # Prepare default headers
            default_headers = {
                "accept": "*/*",
                "user-agent": self.DEFAULT_USER_AGENT,
                "accept-encoding": "gzip,deflate",
            }
            default_headers.update(headers)

            # Make the request
            response = await self._client.request(method, url, timeout=timeout, headers=default_headers, **kwargs)
            response.raise_for_status()

            # Return typed response if expected_type is provided
            if expected_type is not None:
                return TypedResponse.from_response(response, expected_type)

            # Warn about deprecated non-typed responses
            logger.warning(
                "Non-typed responses are deprecated and will be removed in a future version. Please specify an expected_type parameter."
            )
            return response
        except Exception as e:
            logger.error(f"Request to {url} failed: {e!s}", exc_info=True)
            raise

    # HTTP method helpers - simplified without repetitive docstrings
    @overload
    async def get(self, url: str, *, expected_type: type[T], **kwargs: Any) -> TypedResponse[T]: ...

    @overload
    async def get(self, url: str, *, expected_type: None = None, **kwargs: Any) -> httpx.Response: ...

    async def get(
        self, url: str, *, expected_type: type[T] | None = None, **kwargs: Any
    ) -> httpx.Response | TypedResponse[T]:
        """Make a GET request with optional type validation."""
        return await self.request("GET", url, expected_type=expected_type, **kwargs)

    @overload
    async def post(self, url: str, *, expected_type: type[T], **kwargs: Any) -> TypedResponse[T]: ...

    @overload
    async def post(self, url: str, *, expected_type: None = None, **kwargs: Any) -> httpx.Response: ...

    async def post(
        self, url: str, *, expected_type: type[T] | None = None, **kwargs: Any
    ) -> httpx.Response | TypedResponse[T]:
        """Make a POST request with optional type validation."""
        return await self.request("POST", url, expected_type=expected_type, **kwargs)

    @overload
    async def put(self, url: str, *, expected_type: type[T], **kwargs: Any) -> TypedResponse[T]: ...

    @overload
    async def put(self, url: str, *, expected_type: None = None, **kwargs: Any) -> httpx.Response: ...

    async def put(
        self, url: str, *, expected_type: type[T] | None = None, **kwargs: Any
    ) -> httpx.Response | TypedResponse[T]:
        """Make a PUT request with optional type validation."""
        return await self.request("PUT", url, expected_type=expected_type, **kwargs)

    @overload
    async def delete(self, url: str, *, expected_type: type[T], **kwargs: Any) -> TypedResponse[T]: ...

    @overload
    async def delete(self, url: str, *, expected_type: None = None, **kwargs: Any) -> httpx.Response: ...

    async def delete(
        self, url: str, *, expected_type: type[T] | None = None, **kwargs: Any
    ) -> httpx.Response | TypedResponse[T]:
        """Make a DELETE request with optional type validation."""
        return await self.request("DELETE", url, expected_type=expected_type, **kwargs)

    @overload
    async def head(self, url: str, *, expected_type: type[T], **kwargs: Any) -> TypedResponse[T]: ...

    @overload
    async def head(self, url: str, *, expected_type: None = None, **kwargs: Any) -> httpx.Response: ...

    async def head(
        self, url: str, *, expected_type: type[T] | None = None, **kwargs: Any
    ) -> httpx.Response | TypedResponse[T]:
        """Make a HEAD request with optional type validation."""
        return await self.request("HEAD", url, expected_type=expected_type, **kwargs)

    @overload
    async def options(self, url: str, *, expected_type: type[T], **kwargs: Any) -> TypedResponse[T]: ...

    @overload
    async def options(self, url: str, *, expected_type: None = None, **kwargs: Any) -> httpx.Response: ...

    async def options(
        self, url: str, *, expected_type: type[T] | None = None, **kwargs: Any
    ) -> httpx.Response | TypedResponse[T]:
        """Make an OPTIONS request with optional type validation."""
        return await self.request("OPTIONS", url, expected_type=expected_type, **kwargs)

    @overload
    async def patch(self, url: str, *, expected_type: type[T], **kwargs: Any) -> TypedResponse[T]: ...

    @overload
    async def patch(self, url: str, *, expected_type: None = None, **kwargs: Any) -> httpx.Response: ...

    async def patch(
        self, url: str, *, expected_type: type[T] | None = None, **kwargs: Any
    ) -> httpx.Response | TypedResponse[T]:
        """Make a PATCH request with optional type validation."""
        return await self.request("PATCH", url, expected_type=expected_type, **kwargs)


# Global instance for convenience
networking_manager = NetworkingManager()
