from typing import Any, Generic, Optional, Type, TypeVar, Union, overload

import httpx

from .tls import TLS_CONTEXT_HTTP2
from .logger import get_logger
from .validation import ValidationError, validate

logger = get_logger(__name__)

T = TypeVar('T')

class TypedResponse(Generic[T]):
    """
    A wrapper for HTTP responses that enforces type validation.
    
    This class wraps the standard httpx.Response and adds type validation
    for the response data. It ensures that the JSON response conforms to
    the expected type schema.
    
    Attributes:
        response: The original httpx.Response object
        data: The validated response data with the correct type
    """
    
    def __init__(self, response: httpx.Response, data: T):
        self.response = response
        self.data = data
    
    @classmethod
    def from_response(cls, response: httpx.Response, expected_type: Type[T]) -> 'TypedResponse[T]':
        """
        Create a TypedResponse from an httpx.Response with type validation.
        
        Args:
            response: The original HTTP response
            expected_type: The expected type for the response data
                         
        Returns:
            A TypedResponse with validated data
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            json_data = response.json()
            validated_data = validate(json_data, expected_type)
            return cls(response, validated_data)
        except ValidationError as e:
            logger.error(f"Response validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error processing response: {e}", exc_info=True)
            raise

class NetworkingManager:
    DEFAULT_TIMEOUT = 9 # Default timeout in seconds
    DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:130.0) Gecko/20100101 Firefox/130.0" # Default user agent

    # httpx is thread-safe, so we can use a single instance for all requests
    # see https://github.com/encode/httpx/discussions/1633#discussioncomment-717658
    _client: Optional[httpx.AsyncClient] = None

    def __init__(self, tls_context=TLS_CONTEXT_HTTP2, enable_http2: bool = True):
        """Initializes the NetworkingManager with specified TLS context and HTTP/2 setting."""
        self._tls_context = tls_context
        self._enable_http2 = enable_http2

    async def startup(self):
        """Initializes the persistent HTTP client."""
        if self._client is None:
            logger.info("Initializing persistent HTTP client")
            self._client = httpx.AsyncClient(http2=self._enable_http2, verify=self._tls_context)
        else:
            logger.warning("HTTP client already initialized.")

    async def shutdown(self):
        """Closes the persistent HTTP client."""
        if self._client is not None:
            logger.info("Closing persistent HTTP client")
            await self._client.aclose()
            self._client = None
        else:
            logger.warning("HTTP client not initialized or already closed.")

    @overload
    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response: ...
    
    @overload
    async def request(self, method: str, url: str, *, expected_type: Type[T], **kwargs: Any) -> TypedResponse[T]: ...
    
    async def request(self, method: str, url: str, *, expected_type: Optional[Type[T]] = None, **kwargs: Any) -> Union[httpx.Response, TypedResponse[T]]:
        if self._client is None:
            logger.info("NetworkingManager not started. Calling startup()...")
            await self.startup()
            
        try:
            headers = kwargs.pop('headers', {})
            timeout: float = kwargs.pop("timeout", self.DEFAULT_TIMEOUT) # Default timeout is 9 seconds
            kwargs.pop('proxy', None)  # No default proxy, just pop and discard
            logger.info(f"Requesting {method} {url} with timeout {timeout}")

            # Do the request
            response: httpx.Response = await self._client.request(
                method, url, timeout=timeout,  headers={**{
                    "accept": "*/*",
                    "user-agent": self.DEFAULT_USER_AGENT,
                    "accept-encoding": "gzip,deflate",
                }, **headers}, **kwargs
            )
            response.raise_for_status()
            
            # Handle typed response if expected_type is provided
            if expected_type is not None:
                return TypedResponse.from_response(response, expected_type)
            
            # Warn about deprecated non-typed responses
            logger.warning(
                "Non-typed responses are deprecated and will be removed in a future version. Please specify an expected_type parameter."
            )
            return response
        except Exception as e:
            logger.error(f"Request to {url} failed: {str(e)}", exc_info=True)
            raise

    async def get(self, url: str, *, expected_type: Optional[Type[T]] = None, **kwargs: Any) -> Union[httpx.Response, TypedResponse[T]]:
        """
        Make a GET request, with optional type validation if expected_type is provided.
        
        Args:
            url: URL to request
            expected_type: Optional. If provided, validates response against this type
            **kwargs: Additional arguments to pass to the request method
            
        Returns:
            httpx.Response if no expected_type is provided
            TypedResponse with validated data if expected_type is provided
        """
        return await self.request('GET', url, expected_type=expected_type, **kwargs)

    async def post(self, url: str, *, expected_type: Optional[Type[T]] = None, **kwargs: Any) -> Union[httpx.Response, TypedResponse[T]]:
        """
        Make a POST request, with optional type validation if expected_type is provided.
        
        Args:
            url: URL to request
            expected_type: Optional. If provided, validates response against this type
            **kwargs: Additional arguments to pass to the request method
            
        Returns:
            httpx.Response if no expected_type is provided
            TypedResponse with validated data if expected_type is provided
        """
        return await self.request('POST', url, expected_type=expected_type, **kwargs)

    async def put(self, url: str, *, expected_type: Optional[Type[T]] = None, **kwargs: Any) -> Union[httpx.Response, TypedResponse[T]]:
        """
        Make a PUT request, with optional type validation.
        
        Args:
            url: URL to request
            expected_type: Optional. If provided, validates response against this type
            **kwargs: Additional arguments to pass to the request method
            
        Returns:
            httpx.Response if no expected_type is provided
            TypedResponse with validated data if expected_type is provided
        """
        return await self.request('PUT', url, expected_type=expected_type, **kwargs)

    async def delete(self, url: str, *, expected_type: Optional[Type[T]] = None, **kwargs: Any) -> Union[httpx.Response, TypedResponse[T]]:
        """
        Make a DELETE request, with optional type validation.
        
        Args:
            url: URL to request
            expected_type: Optional. If provided, validates response against this type
            **kwargs: Additional arguments to pass to the request method
            
        Returns:
            httpx.Response if no expected_type is provided
            TypedResponse with validated data if expected_type is provided
        """
        return await self.request('DELETE', url, expected_type=expected_type, **kwargs)

    async def head(self, url: str, *, expected_type: Optional[Type[T]] = None, **kwargs: Any) -> Union[httpx.Response, TypedResponse[T]]:
        """
        Make a HEAD request, with optional type validation.
        
        Args:
            url: URL to request
            expected_type: Optional. If provided, validates response against this type
            **kwargs: Additional arguments to pass to the request method
            
        Returns:
            httpx.Response if no expected_type is provided
            TypedResponse with validated data if expected_type is provided
        """
        return await self.request('HEAD', url, expected_type=expected_type, **kwargs)

    async def options(self, url: str, *, expected_type: Optional[Type[T]] = None, **kwargs: Any) -> Union[httpx.Response, TypedResponse[T]]:
        """
        Make an OPTIONS request, with optional type validation.
        
        Args:
            url: URL to request
            expected_type: Optional. If provided, validates response against this type
            **kwargs: Additional arguments to pass to the request method
            
        Returns:
            httpx.Response if no expected_type is provided
            TypedResponse with validated data if expected_type is provided
        """
        return await self.request('OPTIONS', url, expected_type=expected_type, **kwargs)

    async def patch(self, url: str, *, expected_type: Optional[Type[T]] = None, **kwargs: Any) -> Union[httpx.Response, TypedResponse[T]]:
        """
        Make a PATCH request, with optional type validation.
        
        Args:
            url: URL to request
            expected_type: Optional. If provided, validates response against this type
            **kwargs: Additional arguments to pass to the request method
            
        Returns:
            httpx.Response if no expected_type is provided
            TypedResponse with validated data if expected_type is provided
        """
        return await self.request('PATCH', url, expected_type=expected_type, **kwargs)

# Global instance for convenience
networking_manager = NetworkingManager()
