"""
Example of validating API responses using divine-typed-requests library.

This example demonstrates how to use the divine-typed-requests library to make
HTTP requests with automatic type validation, particularly useful for
complex API responses like those from DexScreener or other financial APIs.
"""

import asyncio
from typing import Any, TypedDict

from type_enforcer import ValidationError, enforce

from typed_requests import networking_manager

# ===== Type Definitions for DexScreener API Response Validation =====
# These TypedDicts define the expected structure and types of the API response.
# Using TypedDict allows for precise validation of dictionary structures.


class TokenDict(TypedDict):
    address: str
    name: str
    symbol: str


class TransactionsDict(TypedDict, total=False):
    buys: int
    sells: int


class TxnsPeriodsDict(TypedDict, total=False):
    m5: TransactionsDict
    h1: TransactionsDict
    h6: TransactionsDict
    h24: TransactionsDict


class VolumeDict(TypedDict, total=False):
    h24: float
    h6: float
    h1: float
    m5: float


class PriceChangeDict(TypedDict, total=False):
    m5: float
    h1: float
    h6: float
    h24: float


class LiquidityDict(TypedDict, total=False):
    usd: float | None  # Field can be present but None
    base: float
    quote: float


class WebsiteDict(TypedDict):
    label: str
    url: str


class SocialDict(TypedDict, total=False):
    type: str
    url: str
    label: str | None


class InfoDict(TypedDict, total=False):
    imageUrl: str | None
    websites: list[WebsiteDict] | None
    socials: list[SocialDict] | None
    header: str | None
    openGraph: str | None


class BoostsDict(TypedDict, total=False):
    active: int | None


class PairDict(TypedDict, total=False):
    chainId: str
    dexId: str
    url: str
    pairAddress: str
    baseToken: TokenDict
    quoteToken: TokenDict
    priceNative: str
    priceUsd: str | None
    txns: TxnsPeriodsDict
    volume: VolumeDict
    priceChange: PriceChangeDict | None
    liquidity: LiquidityDict | None
    fdv: float | None
    marketCap: float | None
    pairCreatedAt: int | None
    info: InfoDict | None
    boosts: BoostsDict | None
    labels: list[str] | None
    moonshot: dict[str, Any] | None


class DexScreenerResponseDict(TypedDict):
    schemaVersion: str
    pairs: list[PairDict] | None
    pair: PairDict | None


# ===== API Client with Type Validation =====


class DexScreenerClient:
    """
    A client for interacting with DexScreener API using divine-typed-requests
    with automatic type validation.
    """

    def __init__(self):
        self.base_url = "https://api.dexscreener.com/latest"
        self.manager = networking_manager

    async def get_pairs_by_tokens(self, token_addresses: list[str]) -> DexScreenerResponseDict:
        """
        Get token pairs by token addresses with automatic type validation.

        Args:
            token_addresses: List of token addresses

        Returns:
            DexScreenerResponseDict: Validated response data

        Raises:
            ValidationError: If response doesn't match expected structure
        """
        try:
            # Join addresses with commas
            addresses = ",".join(token_addresses)

            # Make request with automatic type validation
            response = await self.manager.get(
                f"{self.base_url}/dex/tokens/{addresses}", expected_type=DexScreenerResponseDict
            )

            return response.data

        except ValidationError as e:
            print(f"API response validation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to fetch token pairs: {e}")
            raise

    async def get_pair_by_address(self, pair_address: str) -> DexScreenerResponseDict:
        """
        Get a specific pair by its address with automatic type validation.

        Args:
            pair_address: The pair address

        Returns:
            DexScreenerResponseDict: Validated response data
        """
        try:
            response = await self.manager.get(
                f"{self.base_url}/dex/pairs/{pair_address}", expected_type=DexScreenerResponseDict
            )

            return response.data

        except ValidationError as e:
            print(f"API response validation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to fetch pair: {e}")
            raise

    async def search_pairs(self, query: str) -> DexScreenerResponseDict:
        """
        Search for pairs with automatic type validation.

        Args:
            query: Search query

        Returns:
            DexScreenerResponseDict: Validated response data
        """
        try:
            response = await self.manager.get(
                f"{self.base_url}/dex/search", params={"q": query}, expected_type=DexScreenerResponseDict
            )

            return response.data

        except ValidationError as e:
            print(f"API response validation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to search pairs: {e}")
            raise


# ===== Example Usage Functions =====


async def validate_with_mock_data():
    """Example using mock data to demonstrate type validation."""
    print("=== Validating Mock API Response Data ===")

    # Example valid data structure
    valid_api_response_data = {
        "schemaVersion": "1.0.0",
        "pairs": [
            {
                "chainId": "ethereum",
                "dexId": "uniswap",
                "url": "https://dexscreener.com/ethereum/0x123...",
                "pairAddress": "0x123...",
                "baseToken": {
                    "address": "0xabc...",
                    "name": "Example Token",
                    "symbol": "EXT",
                },
                "quoteToken": {
                    "address": "0xc0ffee...",
                    "name": "Wrapped Ether",
                    "symbol": "WETH",
                },
                "priceNative": "1500.5",
                "priceUsd": "3000000",
                "txns": {
                    "m5": {"buys": 10, "sells": 5},
                    "h1": {"buys": 100, "sells": 50},
                },
                "volume": {"h24": 1000000.0, "h6": 250000.0},
                "priceChange": {"m5": 0.1, "h1": 1.5},
                "liquidity": {"usd": 5000000.0, "base": 1666.6, "quote": 2500000.0},
                "fdv": 300000000.0,
                "pairCreatedAt": 1609459200000,
                "info": {
                    "imageUrl": "https://example.com/token.png",
                    "websites": [{"label": "Homepage", "url": "https://example.com"}],
                    "socials": [{"type": "twitter", "url": "https://twitter.com/example"}],
                },
            }
        ],
    }

    # Example invalid data
    invalid_api_response_data = {
        "schemaVersion": "1.0.0",
        "pairs": [
            {
                "chainId": "ethereum",
                "dexId": "uniswap",
                "url": "https://dexscreener.com/ethereum/0x123...",
                "pairAddress": "0x123...",
                "baseToken": {
                    "address": "0xabc...",
                    "name": "Example Token",
                    "symbol": 123,  # INVALID: symbol should be str
                },
                "quoteToken": {
                    "address": "0xc0ffee...",
                    "name": "Wrapped Ether",
                    "symbol": "WETH",
                },
                "priceNative": "1500.5",
            }
        ],
    }

    # Test with valid data
    try:
        # Use the type-enforcer directly for validation

        validated_data = enforce(valid_api_response_data, DexScreenerResponseDict)
        print("✅ Valid data structure conforms to DexScreenerResponseDict.")

        # Access validated data safely
        if validated_data["pairs"] and validated_data["pairs"][0]["baseToken"]:
            print(f"   Base Token Symbol: {validated_data['pairs'][0]['baseToken']['symbol']}")
        if validated_data["pairs"] and validated_data["pairs"][0]["liquidity"]:
            print(f"   Liquidity (USD): {validated_data['pairs'][0]['liquidity'].get('usd')}")

    except ValidationError as e:
        print(f"❌ Error validating valid data: {e}")

    # Test with invalid data
    try:
        _validate_invalid = enforce(invalid_api_response_data, DexScreenerResponseDict)
        print("❌ ERROR: Invalid data was incorrectly validated!")
    except ValidationError as e:
        print("✅ Successfully caught validation error in invalid data:")
        print(f"   {e}")


async def real_api_request_example():
    """Example of making real API requests with type validation."""
    print("\n=== Real API Request Example ===")

    client = DexScreenerClient()

    # Initialize the networking manager
    await networking_manager.startup()

    try:
        # Example 1: Search for popular tokens
        print("1. Searching for Ethereum pairs...")
        try:
            # Search for Ethereum-related pairs
            search_results = await client.search_pairs("ETH")

            if search_results["pairs"]:
                print(f"   Found {len(search_results['pairs'])} pairs")
                for i, pair in enumerate(search_results["pairs"][:3]):  # Show first 3
                    print(f"   {i + 1}. {pair['baseToken']['symbol']}/{pair['quoteToken']['symbol']}")
                    print(f"      Price: ${pair['priceUsd']}")
                    print(f"      Volume 24h: ${pair['volume'].get('h24', 0):,.2f}")
            else:
                print("   No pairs found")

        except Exception as e:  # noqa: BLE001
            print(f"   Search request failed: {e}")

        # Example 2: Get specific token information
        print("\n2. Getting WETH token information...")
        try:
            # WETH token address on Ethereum
            weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

            token_data = await client.get_pairs_by_tokens([weth_address])

            if token_data["pairs"]:
                print(f"   Found {len(token_data['pairs'])} pairs for WETH")
                # Show top pair by volume
                top_pair = max(token_data["pairs"], key=lambda p: p["volume"].get("h24", 0))
                print(f"   Top pair: {top_pair['baseToken']['symbol']}/{top_pair['quoteToken']['symbol']}")
                print(f"   24h Volume: ${top_pair['volume'].get('h24', 0):,.2f}")
            else:
                print("   No pairs found for WETH")

        except Exception as e:  # noqa: BLE001
            print(f"   Token request failed: {e}")

    finally:
        # Clean up
        await networking_manager.shutdown()


async def error_handling_example():
    """Example of handling various error scenarios."""
    print("\n=== Error Handling Example ===")

    client = DexScreenerClient()

    await networking_manager.startup()

    try:
        # Example 1: Invalid token address
        print("1. Testing with invalid token address...")
        try:
            invalid_address = "invalid_address"
            result = await client.get_pairs_by_tokens([invalid_address])
            print(f"   Unexpected success: {result}")
        except ValidationError as e:
            print(f"   ✅ Validation error caught: {e}")
        except Exception as e:  # noqa: BLE001
            print(f"   \u2705 Request error caught: {type(e).__name__}: {e}")

        # Example 2: Network timeout
        print("\n2. Testing with timeout...")
        try:
            # Set a very short timeout to test timeout handling
            response = await networking_manager.get(
                "https://api.dexscreener.com/latest/dex/search",
                params={"q": "ETH"},
                timeout=0.001,  # 1ms timeout - should fail
                expected_type=DexScreenerResponseDict,
            )
            print(f"   Unexpected success: {response}")
        except Exception as e:  # noqa: BLE001
            print(f"   \u2705 Timeout error caught: {type(e).__name__}: {e}")

    finally:
        await networking_manager.shutdown()


async def advanced_validation_example():
    """Example of advanced type validation features."""
    print("\n=== Advanced Validation Example ===")

    # Example: Validating sub-structures
    print("1. Validating sub-structures...")

    # Valid token data
    valid_token_data = {"address": "0x111...", "name": "Sub Token", "symbol": "SUB"}

    # Invalid token data
    invalid_token_data = {
        "address": "0x222...",
        "name": 123,  # name should be string
        "symbol": "SUB",
    }

    try:
        validated_token = enforce(valid_token_data, TokenDict)
        print(f"   ✅ Valid token: {validated_token}")
    except ValidationError as e:
        print(f"   ❌ Error validating valid token: {e}")

    try:
        enforce(invalid_token_data, TokenDict)
        print("   ❌ ERROR: Invalid token was incorrectly validated!")
    except ValidationError as e:
        print(f"   ✅ Successfully caught validation error in invalid token: {e}")

    # Example: Optional field handling
    print("\n2. Testing optional field handling...")

    minimal_pair_data = {
        "chainId": "ethereum",
        "dexId": "uniswap",
        "url": "https://dexscreener.com/ethereum/0x123...",
        "pairAddress": "0x123...",
        "baseToken": {
            "address": "0xabc...",
            "name": "Example Token",
            "symbol": "EXT",
        },
        "quoteToken": {
            "address": "0xc0ffee...",
            "name": "Wrapped Ether",
            "symbol": "WETH",
        },
        "priceNative": "1500.5",
        "txns": {},
        "volume": {},
    }

    try:
        validated_pair = enforce(minimal_pair_data, PairDict)
        print("   ✅ Minimal pair data validated successfully")
        print(f"      Base token: {validated_pair['baseToken']['symbol']}")
        print(f"      Quote token: {validated_pair['quoteToken']['symbol']}")
    except ValidationError as e:
        print(f"   ❌ Error validating minimal pair: {e}")


# ===== Main Example Function =====


async def main():
    """Run all API response validation examples."""
    print("Divine Requests Library - API Response Validation Examples")
    print("=" * 65)

    try:
        await validate_with_mock_data()
        await real_api_request_example()
        await error_handling_example()
        await advanced_validation_example()

        print("\n" + "=" * 65)
        print("All API response validation examples completed!")

    except Exception as e:  # noqa: BLE001
        print(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
