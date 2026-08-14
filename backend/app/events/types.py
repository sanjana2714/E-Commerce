import enum


class KafkaTopic(str, enum.Enum):
    PRODUCT_EVENTS = "product-events"
    ORDER_EVENTS = "order-events"
    INVENTORY_EVENTS = "inventory-events"
    PAYMENT_EVENTS = "payment-events"
    NOTIFICATION_EVENTS = "notification-events"
    DEAD_LETTER_EVENTS = "dead-letter-events"

class EventType(str, enum.Enum):
    PRODUCT_CREATED = "ProductCreated"
    PRODUCT_UPDATED = "ProductUpdated"
    PRODUCT_DELETED = "ProductDeleted"
    ORDER_CREATED = "OrderCreated"
    ORDER_CONFIRMED = "OrderConfirmed"
    ORDER_CANCELLED = "OrderCancelled"
    INVENTORY_RESERVED = "InventoryReserved"
    INVENTORY_RESERVATION_FAILED = "InventoryReservationFailed"
    PAYMENT_SUCCEEDED = "PaymentSucceeded"
    PAYMENT_FAILED = "PaymentFailed"
