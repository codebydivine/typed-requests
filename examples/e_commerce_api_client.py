"""
E-commerce API client example using divine-typed-requests library.

This example demonstrates building a comprehensive e-commerce API client with:
- Product catalog management
- User authentication
- Shopping cart operations
- Order processing
- Payment integration patterns
- Inventory management
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, TypedDict

from type_enforcer import ValidationError

from typed_requests import NetworkingManager

# ===== E-commerce Type Definitions =====


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"


class ProductCategory(TypedDict):
    id: int
    name: str
    slug: str
    description: str | None
    parent_id: int | None


class Product(TypedDict):
    id: int
    name: str
    slug: str
    description: str
    price: float
    sale_price: float | None
    sku: str
    category_id: int
    category: ProductCategory
    images: list[str]
    stock_quantity: int
    weight: float | None
    dimensions: dict[str, float] | None
    attributes: dict[str, Any]
    created_at: str
    updated_at: str
    is_active: bool


class User(TypedDict):
    id: int
    email: str
    first_name: str
    last_name: str
    phone: str | None
    is_active: bool
    created_at: str
    updated_at: str


class Address(TypedDict):
    id: int
    user_id: int
    type: str  # billing, shipping
    first_name: str
    last_name: str
    company: str | None
    address_line_1: str
    address_line_2: str | None
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool


class CartItem(TypedDict):
    id: int
    product_id: int
    product: Product
    quantity: int
    price: float
    subtotal: float


class Cart(TypedDict):
    id: int
    user_id: int
    items: list[CartItem]
    total_items: int
    subtotal: float
    tax_amount: float
    shipping_amount: float
    discount_amount: float
    total_amount: float
    created_at: str
    updated_at: str


class OrderItem(TypedDict):
    id: int
    order_id: int
    product_id: int
    product: Product
    quantity: int
    price: float
    subtotal: float


class Order(TypedDict):
    id: int
    user_id: int
    order_number: str
    status: str
    payment_status: str
    items: list[OrderItem]
    billing_address: Address
    shipping_address: Address
    total_items: int
    subtotal: float
    tax_amount: float
    shipping_amount: float
    discount_amount: float
    total_amount: float
    notes: str | None
    created_at: str
    updated_at: str
    shipped_at: str | None
    delivered_at: str | None


class AuthToken(TypedDict):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class PaymentMethod(TypedDict):
    id: int
    user_id: int
    type: str  # card, bank_account, digital_wallet
    provider: str  # stripe, paypal, etc.
    last_four: str
    expires_at: str | None
    is_default: bool


# ===== E-commerce API Client =====


class ECommerceAPIClient:
    """
    Comprehensive e-commerce API client demonstrating real-world patterns.
    """

    def __init__(self, base_url: str, api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.manager = NetworkingManager()
        self.api_key = api_key
        self.access_token: str | None = None
        self.headers = {"Content-Type": "application/json", "User-Agent": "divine-typed-requests-ECommerce-Client/1.0"}

        if api_key:
            self.headers["X-API-Key"] = api_key

    async def __aenter__(self):
        """Async context manager entry."""
        await self.manager.startup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.manager.shutdown()

    def _get_auth_headers(self) -> dict[str, str]:
        """Get headers with authentication."""
        headers = self.headers.copy()
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    # ===== Authentication =====

    async def login(self, email: str, password: str) -> AuthToken:
        """
        Authenticate user and get access token.

        Args:
            email: User email
            password: User password

        Returns:
            AuthToken: Authentication token data
        """
        try:
            response = await self.manager.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password},
                headers=self.headers,
                expected_type=AuthToken,
            )

            # Store access token for future requests
            self.access_token = response.data["access_token"]
            return response.data

        except ValidationError as e:
            print(f"Login response validation failed: {e}")
            raise
        except Exception as e:
            print(f"Login failed: {e}")
            raise

    async def register(
        self, email: str, password: str, first_name: str, last_name: str, phone: str | None = None
    ) -> User:
        """
        Register a new user.

        Args:
            email: User email
            password: User password
            first_name: User first name
            last_name: User last name
            phone: Optional phone number

        Returns:
            User: Created user data
        """
        try:
            user_data = {"email": email, "password": password, "first_name": first_name, "last_name": last_name}

            if phone:
                user_data["phone"] = phone

            response = await self.manager.post(
                f"{self.base_url}/auth/register", json=user_data, headers=self.headers, expected_type=User
            )

            return response.data

        except ValidationError as e:
            print(f"Registration response validation failed: {e}")
            raise
        except Exception as e:
            print(f"Registration failed: {e}")
            raise

    # ===== Product Catalog =====

    async def get_products(self, category_id: int | None = None, page: int = 1, per_page: int = 20) -> list[Product]:
        """
        Get products from catalog.

        Args:
            category_id: Optional category filter
            page: Page number
            per_page: Items per page

        Returns:
            List[Product]: Product list
        """
        try:
            params = {"page": page, "per_page": per_page}
            if category_id:
                params["category_id"] = category_id

            response = await self.manager.get(
                f"{self.base_url}/products", params=params, headers=self.headers, expected_type=list[Product]
            )

            return response.data

        except ValidationError as e:
            print(f"Products response validation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to fetch products: {e}")
            raise

    async def get_product(self, product_id: int) -> Product:
        """
        Get a specific product by ID.

        Args:
            product_id: Product ID

        Returns:
            Product: Product data
        """
        try:
            response = await self.manager.get(
                f"{self.base_url}/products/{product_id}", headers=self.headers, expected_type=Product
            )

            return response.data

        except ValidationError as e:
            print(f"Product response validation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to fetch product {product_id}: {e}")
            raise

    async def search_products(self, query: str, page: int = 1, per_page: int = 20) -> list[Product]:
        """
        Search products by query.

        Args:
            query: Search query
            page: Page number
            per_page: Items per page

        Returns:
            List[Product]: Search results
        """
        try:
            response = await self.manager.get(
                f"{self.base_url}/products/search",
                params={"q": query, "page": page, "per_page": per_page},
                headers=self.headers,
                expected_type=list[Product],
            )

            return response.data

        except ValidationError as e:
            print(f"Search response validation failed: {e}")
            raise
        except Exception as e:
            print(f"Product search failed: {e}")
            raise

    # ===== Shopping Cart =====

    async def get_cart(self) -> Cart:
        """
        Get user's shopping cart.

        Returns:
            Cart: Cart data
        """
        try:
            response = await self.manager.get(
                f"{self.base_url}/cart", headers=self._get_auth_headers(), expected_type=Cart
            )

            return response.data

        except ValidationError as e:
            print(f"Cart response validation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to fetch cart: {e}")
            raise

    async def add_to_cart(self, product_id: int, quantity: int = 1) -> Cart:
        """
        Add item to cart.

        Args:
            product_id: Product ID
            quantity: Quantity to add

        Returns:
            Cart: Updated cart data
        """
        try:
            response = await self.manager.post(
                f"{self.base_url}/cart/items",
                json={"product_id": product_id, "quantity": quantity},
                headers=self._get_auth_headers(),
                expected_type=Cart,
            )

            return response.data

        except ValidationError as e:
            print(f"Add to cart response validation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to add item to cart: {e}")
            raise

    async def update_cart_item(self, item_id: int, quantity: int) -> Cart:
        """
        Update cart item quantity.

        Args:
            item_id: Cart item ID
            quantity: New quantity

        Returns:
            Cart: Updated cart data
        """
        try:
            response = await self.manager.put(
                f"{self.base_url}/cart/items/{item_id}",
                json={"quantity": quantity},
                headers=self._get_auth_headers(),
                expected_type=Cart,
            )

            return response.data

        except ValidationError as e:
            print(f"Update cart response validation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to update cart item: {e}")
            raise

    async def remove_from_cart(self, item_id: int) -> Cart:
        """
        Remove item from cart.

        Args:
            item_id: Cart item ID

        Returns:
            Cart: Updated cart data
        """
        try:
            response = await self.manager.delete(
                f"{self.base_url}/cart/items/{item_id}", headers=self._get_auth_headers(), expected_type=Cart
            )

            return response.data

        except ValidationError as e:
            print(f"Remove from cart response validation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to remove item from cart: {e}")
            raise

    # ===== Order Management =====

    async def create_order(
        self, billing_address_id: int, shipping_address_id: int, payment_method_id: int, notes: str | None = None
    ) -> Order:
        """
        Create an order from cart.

        Args:
            billing_address_id: Billing address ID
            shipping_address_id: Shipping address ID
            payment_method_id: Payment method ID
            notes: Optional order notes

        Returns:
            Order: Created order data
        """
        try:
            order_data = {
                "billing_address_id": billing_address_id,
                "shipping_address_id": shipping_address_id,
                "payment_method_id": payment_method_id,
            }

            if notes:
                order_data["notes"] = notes

            response = await self.manager.post(
                f"{self.base_url}/orders", json=order_data, headers=self._get_auth_headers(), expected_type=Order
            )

            return response.data

        except ValidationError as e:
            print(f"Create order response validation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to create order: {e}")
            raise

    async def get_orders(self, page: int = 1, per_page: int = 20) -> list[Order]:
        """
        Get user's orders.

        Args:
            page: Page number
            per_page: Items per page

        Returns:
            List[Order]: Order list
        """
        try:
            response = await self.manager.get(
                f"{self.base_url}/orders",
                params={"page": page, "per_page": per_page},
                headers=self._get_auth_headers(),
                expected_type=list[Order],
            )

            return response.data

        except ValidationError as e:
            print(f"Orders response validation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to fetch orders: {e}")
            raise

    async def get_order(self, order_id: int) -> Order:
        """
        Get a specific order.

        Args:
            order_id: Order ID

        Returns:
            Order: Order data
        """
        try:
            response = await self.manager.get(
                f"{self.base_url}/orders/{order_id}", headers=self._get_auth_headers(), expected_type=Order
            )

            return response.data

        except ValidationError as e:
            print(f"Order response validation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to fetch order {order_id}: {e}")
            raise


# ===== Usage Examples =====


async def product_browsing_example():
    """Example of browsing products."""
    print("=== Product Browsing Example ===")

    # Using a mock API base URL - in real usage, this would be your actual API
    async with ECommerceAPIClient("https://api.example-store.com"):
        try:
            # This would normally work with a real API
            print("Note: This example uses a mock API URL for demonstration")
            print("In real usage, you would:")
            print("1. Browse product categories")
            print("2. Search for products")
            print("3. View product details")
            print("4. Check inventory status")

        except Exception as e:  # noqa: BLE001
            print(f"Expected error with mock API: {type(e).__name__}")


async def shopping_cart_example():
    """Example of shopping cart operations."""
    print("\n=== Shopping Cart Example ===")

    async with ECommerceAPIClient("https://api.example-store.com"):
        try:
            print("Note: This example demonstrates the API client pattern")
            print("Cart operations would include:")
            print("1. Add items to cart")
            print("2. Update item quantities")
            print("3. Remove items")
            print("4. Calculate totals with tax and shipping")

        except Exception as e:  # noqa: BLE001
            print(f"Expected error with mock API: {type(e).__name__}")


async def order_processing_example():
    """Example of order processing workflow."""
    print("\n=== Order Processing Example ===")

    async with ECommerceAPIClient("https://api.example-store.com"):
        try:
            print("Note: This example shows the complete order workflow")
            print("Order processing would include:")
            print("1. User authentication")
            print("2. Address validation")
            print("3. Payment method selection")
            print("4. Order creation")
            print("5. Payment processing")
            print("6. Order confirmation")
            print("7. Inventory updates")
            print("8. Shipping notifications")

        except Exception as e:  # noqa: BLE001
            print(f"Expected error with mock API: {type(e).__name__}")


async def comprehensive_workflow_example():
    """Example of a complete e-commerce workflow."""
    print("\n=== Comprehensive E-commerce Workflow Example ===")

    # This demonstrates the complete flow structure
    @dataclass
    class ShoppingSession:
        user_id: int | None = None
        cart_total: float = 0.0
        items_count: int = 0
        session_start: datetime = datetime.now()

    def calculate_cart_totals(items: list[dict[str, Any]]) -> dict[str, float]:
        """Calculate cart totals."""
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        tax_rate = 0.08  # 8% tax
        tax_amount = subtotal * tax_rate
        shipping_amount = 0.0 if subtotal > 50 else 5.99  # Free shipping over $50
        total = subtotal + tax_amount + shipping_amount

        return {"subtotal": subtotal, "tax_amount": tax_amount, "shipping_amount": shipping_amount, "total": total}

    # Simulate a shopping session
    ShoppingSession()

    # Mock cart items
    cart_items = [
        {"product_id": 1, "name": "Laptop", "price": 999.99, "quantity": 1},
        {"product_id": 2, "name": "Mouse", "price": 29.99, "quantity": 2},
        {"product_id": 3, "name": "Keyboard", "price": 79.99, "quantity": 1},
    ]

    # Calculate totals
    totals = calculate_cart_totals(cart_items)

    print("Shopping Session Details:")
    print(f"  Items in cart: {len(cart_items)}")
    print(f"  Subtotal: ${totals['subtotal']:.2f}")
    print(f"  Tax: ${totals['tax_amount']:.2f}")
    print(f"  Shipping: ${totals['shipping_amount']:.2f}")
    print(f"  Total: ${totals['total']:.2f}")

    # Simulate order states
    order_states = ["pending", "confirmed", "processing", "shipped", "delivered"]
    print(f"\nOrder State Flow: {' → '.join(order_states)}")


# ===== Main Example Function =====


async def main():
    """Run all e-commerce examples."""
    print("Divine Requests Library - E-commerce API Client Examples")
    print("=" * 65)

    try:
        await product_browsing_example()
        await shopping_cart_example()
        await order_processing_example()
        await comprehensive_workflow_example()

        print("\n" + "=" * 65)
        print("All e-commerce examples completed!")
        print("\nNote: These examples demonstrate the API client structure and patterns.")
        print("In production, you would connect to a real e-commerce API endpoint.")

    except Exception as e:  # noqa: BLE001
        print(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
