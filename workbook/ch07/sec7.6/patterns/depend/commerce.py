from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


# ============================================================================
# DOMAIN MODELS
# ============================================================================

class OrderStatus(Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    PAYMENT_PROCESSED = "payment_processed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class OrderItem:
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    
    @property
    def total_price(self) -> float:
        return self.quantity * self.unit_price


@dataclass
class ShippingAddress:
    street: str
    city: str
    state: str
    zip_code: str
    country: str


@dataclass
class Order:
    order_id: str
    customer_id: str
    items: List[OrderItem]
    shipping_address: ShippingAddress
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    total_amount: float = 0.0
    
    def calculate_total(self) -> float:
        self.total_amount = sum(item.total_price for item in self.items)
        return self.total_amount


# ============================================================================
# REPOSITORY INTERFACES (Data Access Layer)
# ============================================================================

class OrderRepository(ABC):
    """Interface for order persistence"""
    
    @abstractmethod
    def save(self, order: Order) -> bool:
        pass
    
    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        pass
    
    @abstractmethod
    def find_by_customer(self, customer_id: str) -> List[Order]:
        pass
    
    @abstractmethod
    def update_status(self, order_id: str, status: OrderStatus) -> bool:
        pass


class InventoryRepository(ABC):
    """Interface for inventory management"""
    
    @abstractmethod
    def check_availability(self, product_id: str, quantity: int) -> bool:
        pass
    
    @abstractmethod
    def reserve_stock(self, product_id: str, quantity: int) -> bool:
        pass
    
    @abstractmethod
    def release_stock(self, product_id: str, quantity: int) -> bool:
        pass


# ============================================================================
# SERVICE INTERFACES (Business Logic Layer)
# ============================================================================

class PaymentGateway(ABC):
    """Interface for payment processing"""
    
    @abstractmethod
    def process_payment(self, order: Order, payment_method: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def refund_payment(self, transaction_id: str, amount: float) -> bool:
        pass


class NotificationService(ABC):
    """Interface for customer notifications"""
    
    @abstractmethod
    def send_order_confirmation(self, order: Order, customer_email: str) -> bool:
        pass
    
    @abstractmethod
    def send_shipment_notification(self, order: Order, tracking_number: str) -> bool:
        pass


class ShippingService(ABC):
    """Interface for shipping logistics"""
    
    @abstractmethod
    def calculate_shipping_cost(self, order: Order) -> float:
        pass
    
    @abstractmethod
    def create_shipment(self, order: Order) -> str:  # Returns tracking number
        pass


# ============================================================================
# CONCRETE IMPLEMENTATIONS - REPOSITORIES
# ============================================================================

class InMemoryOrderRepository(OrderRepository):
    """Simple in-memory implementation for demonstration"""
    
    def __init__(self):
        self._orders: Dict[str, Order] = {}
        print("  [Repository] InMemoryOrderRepository initialized")
    
    def save(self, order: Order) -> bool:
        self._orders[order.order_id] = order
        print(f"  [Repository] Saved order {order.order_id}")
        return True
    
    def find_by_id(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)
    
    def find_by_customer(self, customer_id: str) -> List[Order]:
        return [o for o in self._orders.values() if o.customer_id == customer_id]
    
    def update_status(self, order_id: str, status: OrderStatus) -> bool:
        if order_id in self._orders:
            self._orders[order_id].status = status
            print(f"  [Repository] Updated order {order_id} status to {status.value}")
            return True
        return False


class MockInventoryRepository(InventoryRepository):
    """Mock inventory with simulated stock levels"""
    
    def __init__(self):
        self._stock = {
            "PROD-001": 100,
            "PROD-002": 50,
            "PROD-003": 25,
            "PROD-004": 0
        }
        print("  [Repository] MockInventoryRepository initialized")
    
    def check_availability(self, product_id: str, quantity: int) -> bool:
        available = self._stock.get(product_id, 0)
        result = available >= quantity
        print(f"  [Inventory] Check {product_id}: requested={quantity}, available={available}, result={result}")
        return result
    
    def reserve_stock(self, product_id: str, quantity: int) -> bool:
        if self.check_availability(product_id, quantity):
            self._stock[product_id] -= quantity
            print(f"  [Inventory] Reserved {quantity} units of {product_id}")
            return True
        return False
    
    def release_stock(self, product_id: str, quantity: int) -> bool:
        self._stock[product_id] = self._stock.get(product_id, 0) + quantity
        print(f"  [Inventory] Released {quantity} units of {product_id}")
        return True


# ============================================================================
# CONCRETE IMPLEMENTATIONS - SERVICES
# ============================================================================

class StripePaymentGateway(PaymentGateway):
    """Simulated Stripe payment integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._transactions: Dict[str, Dict] = {}
        print(f"  [Payment] StripePaymentGateway initialized with key {api_key[:10]}...")
    
    def process_payment(self, order: Order, payment_method: str) -> Dict[str, Any]:
        transaction_id = f"TXN-{order.order_id}-{datetime.now().timestamp()}"
        result = {
            "success": True,
            "transaction_id": transaction_id,
            "amount": order.total_amount,
            "payment_method": payment_method,
            "timestamp": datetime.now().isoformat()
        }
        self._transactions[transaction_id] = result
        print(f"  [Payment] Processed ${order.total_amount:.2f} via {payment_method}")
        return result
    
    def refund_payment(self, transaction_id: str, amount: float) -> bool:
        if transaction_id in self._transactions:
            print(f"  [Payment] Refunded ${amount:.2f} for {transaction_id}")
            return True
        return False


class EmailNotificationService(NotificationService):
    """Email-based notification system"""
    
    def __init__(self, smtp_host: str, from_address: str):
        self.smtp_host = smtp_host
        self.from_address = from_address
        print(f"  [Notification] EmailNotificationService initialized ({smtp_host})")
    
    def send_order_confirmation(self, order: Order, customer_email: str) -> bool:
        message = f"""
        Order Confirmation - {order.order_id}
        
        Thank you for your order!
        Total: ${order.total_amount:.2f}
        Items: {len(order.items)}
        Status: {order.status.value}
        """
        print(f"  [Notification] Sent confirmation email to {customer_email}")
        return True
    
    def send_shipment_notification(self, order: Order, tracking_number: str) -> bool:
        message = f"Your order {order.order_id} has shipped! Tracking: {tracking_number}"
        print(f"  [Notification] Sent shipment email with tracking {tracking_number}")
        return True


class FedExShippingService(ShippingService):
    """FedEx shipping integration"""
    
    def __init__(self, account_number: str, api_endpoint: str):
        self.account_number = account_number
        self.api_endpoint = api_endpoint
        print(f"  [Shipping] FedExShippingService initialized (account: {account_number})")
    
    def calculate_shipping_cost(self, order: Order) -> float:
        # Simplified calculation
        base_cost = 5.99
        weight_cost = len(order.items) * 2.50
        total = base_cost + weight_cost
        print(f"  [Shipping] Calculated shipping cost: ${total:.2f}")
        return total
    
    def create_shipment(self, order: Order) -> str:
        tracking_number = f"FEDEX-{order.order_id}-{datetime.now().strftime('%Y%m%d')}"
        print(f"  [Shipping] Created shipment with tracking {tracking_number}")
        return tracking_number


# ============================================================================
# APPLICATION SERVICES (Orchestration Layer)
# ============================================================================

class OrderProcessor:
    """
    High-level service that orchestrates order processing.
    All dependencies are injected via constructor.
    """
    
    def __init__(
        self,
        order_repository: OrderRepository,
        inventory_repository: InventoryRepository,
        payment_gateway: PaymentGateway,
        notification_service: NotificationService,
        shipping_service: ShippingService
    ):
        # DEPENDENCY INJECTION via constructor
        self.order_repo = order_repository
        self.inventory_repo = inventory_repository
        self.payment_gateway = payment_gateway
        self.notification_service = notification_service
        self.shipping_service = shipping_service
        print("\n[OrderProcessor] Initialized with injected dependencies")
    
    def process_order(
        self, 
        order: Order, 
        payment_method: str, 
        customer_email: str
    ) -> Dict[str, Any]:
        """
        Complete order processing workflow using injected services
        """
        print(f"\n{'='*60}")
        print(f"Processing Order: {order.order_id}")
        print(f"{'='*60}\n")
        
        result = {
            "success": False,
            "order_id": order.order_id,
            "steps": []
        }
        
        try:
            # Step 1: Calculate total
            print("[Step 1] Calculating order total...")
            order.calculate_total()
            result["steps"].append({"step": "calculate_total", "success": True})
            
            # Step 2: Check inventory availability
            print("\n[Step 2] Checking inventory...")
            for item in order.items:
                if not self.inventory_repo.check_availability(item.product_id, item.quantity):
                    raise Exception(f"Insufficient stock for {item.product_name}")
            result["steps"].append({"step": "inventory_check", "success": True})
            
            # Step 3: Reserve inventory
            print("\n[Step 3] Reserving inventory...")
            for item in order.items:
                self.inventory_repo.reserve_stock(item.product_id, item.quantity)
            result["steps"].append({"step": "inventory_reserve", "success": True})
            
            # Step 4: Process payment
            print("\n[Step 4] Processing payment...")
            payment_result = self.payment_gateway.process_payment(order, payment_method)
            if not payment_result["success"]:
                raise Exception("Payment failed")
            result["transaction_id"] = payment_result["transaction_id"]
            result["steps"].append({"step": "payment", "success": True})
            
            # Step 5: Update order status
            print("\n[Step 5] Updating order status...")
            order.status = OrderStatus.PAYMENT_PROCESSED
            self.order_repo.save(order)
            self.order_repo.update_status(order.order_id, OrderStatus.PAYMENT_PROCESSED)
            result["steps"].append({"step": "save_order", "success": True})
            
            # Step 6: Calculate shipping
            print("\n[Step 6] Calculating shipping...")
            shipping_cost = self.shipping_service.calculate_shipping_cost(order)
            result["shipping_cost"] = shipping_cost
            result["steps"].append({"step": "calculate_shipping", "success": True})
            
            # Step 7: Create shipment
            print("\n[Step 7] Creating shipment...")
            tracking_number = self.shipping_service.create_shipment(order)
            result["tracking_number"] = tracking_number
            order.status = OrderStatus.SHIPPED
            self.order_repo.update_status(order.order_id, OrderStatus.SHIPPED)
            result["steps"].append({"step": "create_shipment", "success": True})
            
            # Step 8: Send notifications
            print("\n[Step 8] Sending notifications...")
            self.notification_service.send_order_confirmation(order, customer_email)
            self.notification_service.send_shipment_notification(order, tracking_number)
            result["steps"].append({"step": "notifications", "success": True})
            
            result["success"] = True
            print("\n[SUCCESS] Order processed successfully!")
            
        except Exception as e:
            print(f"\n[ERROR] Order processing failed: {e}")
            result["error"] = str(e)
            
            # Rollback: Release reserved inventory
            print("\n[Rollback] Releasing reserved inventory...")
            for item in order.items:
                self.inventory_repo.release_stock(item.product_id, item.quantity)
        
        return result


# ============================================================================
# DEPENDENCY INJECTION CONTAINER
# ============================================================================

class ServiceContainer:
    """
    Simple DI container that manages service instantiation and lifecycle
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        print("\n[Container] Service container initialized\n")
    
    def register_singleton(self, name: str, instance: Any):
        """Register a pre-created singleton instance"""
        self._singletons[name] = instance
        print(f"[Container] Registered singleton: {name}")
    
    def register(self, name: str, factory: callable):
        """Register a factory function for creating instances"""
        self._services[name] = factory
        print(f"[Container] Registered service: {name}")
    
    def get(self, name: str) -> Any:
        """Resolve a service dependency"""
        if name in self._singletons:
            return self._singletons[name]
        
        if name in self._services:
            return self._services[name]()
        
        raise Exception(f"Service '{name}' not found in container")


def configure_production_container() -> ServiceContainer:
    """
    Configure container with production implementations
    """
    print("="*60)
    print("CONFIGURING PRODUCTION SERVICES")
    print("="*60)
    
    container = ServiceContainer()
    
    # Register repositories
    container.register_singleton('order_repository', InMemoryOrderRepository())
    container.register_singleton('inventory_repository', MockInventoryRepository())
    
    # Register external services
    container.register_singleton(
        'payment_gateway', 
        StripePaymentGateway(api_key='sk_live_abc123xyz789')
    )
    container.register_singleton(
        'notification_service',
        EmailNotificationService(
            smtp_host='smtp.company.com',
            from_address='orders@company.com'
        )
    )
    container.register_singleton(
        'shipping_service',
        FedExShippingService(
            account_number='FEDEX-123456',
            api_endpoint='https://api.fedex.com'
        )
    )
    
    # Register OrderProcessor with all dependencies injected
    container.register(
        'order_processor',
        lambda: OrderProcessor(
            order_repository=container.get('order_repository'),
            inventory_repository=container.get('inventory_repository'),
            payment_gateway=container.get('payment_gateway'),
            notification_service=container.get('notification_service'),
            shipping_service=container.get('shipping_service')
        )
    )
    
    print("\n[Container] All services configured successfully\n")
    return container


# ============================================================================
# DEMONSTRATION
# ============================================================================

def main():
    print("\n" + "="*60)
    print("DEPENDENCY INJECTION DEMO: E-COMMERCE ORDER PROCESSING")
    print("="*60 + "\n")
    
    # Setup: Configure the DI container
    container = configure_production_container()
    
    # Create a sample order
    order = Order(
        order_id="ORD-2024-001",
        customer_id="CUST-12345",
        items=[
            OrderItem("PROD-001", "Laptop Computer", 1, 999.99),
            OrderItem("PROD-002", "Wireless Mouse", 2, 29.99),
            OrderItem("PROD-003", "USB-C Cable", 3, 12.99)
        ],
        shipping_address=ShippingAddress(
            street="123 Main St",
            city="San Francisco",
            state="CA",
            zip_code="94105",
            country="USA"
        )
    )
    
    # Get the order processor from container (with all dependencies injected)
    order_processor = container.get('order_processor')
    
    # Process the order
    result = order_processor.process_order(
        order=order,
        payment_method="credit_card",
        customer_email="customer@example.com"
    )
    
    # Display results
    print("\n" + "="*60)
    print("PROCESSING RESULT")
    print("="*60)
    print(json.dumps(result, indent=2, default=str))
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60 + "\n")
    
    # Demonstrate easy swapping of implementations
    print("\nNOTE: To use different implementations, simply register different")
    print("services in the container. For example:")
    print("  - Use PayPalPaymentGateway instead of StripePaymentGateway")
    print("  - Use SMSNotificationService instead of EmailNotificationService")
    print("  - Use DatabaseOrderRepository instead of InMemoryOrderRepository")
    print("\nNo changes needed to OrderProcessor class!")


if __name__ == "__main__":
    main()