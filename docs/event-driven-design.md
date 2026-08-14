# Event-Driven Architecture & Transactional Outbox

## Overview

The platform uses an event-driven architecture powered by **Apache Kafka 7.5.0** and the **Transactional Outbox Pattern**.

---

## Event Topics & Message Envelope

### Kafka Topics
- `product-events`: Product lifecycle updates (`ProductCreated`, `ProductUpdated`, `ProductDeleted`)
- `order-events`: Order lifecycle changes (`OrderCreated`, `OrderStateChangedToCONFIRMED`, `OrderStateChangedToCANCELLED`)
- `payment-events`: Payment processing results (`PaymentSucceeded`, `PaymentFailed`)
- `notification-events`: User alert triggers
- `dead-letter-events`: Failed message DLQ

### Event JSON Schema
```json
{
  "event_id": "c7a8b9d0-1234-5678-9abc-def012345678",
  "event_type": "OrderCreated",
  "aggregate_type": "Order",
  "aggregate_id": "42",
  "timestamp": "2026-08-13T14:00:00.000Z",
  "correlation_id": "req-9876-5432",
  "version": 1,
  "payload": {
    "order_id": 42,
    "user_id": 1,
    "total_amount": 1999.98,
    "status": "PENDING"
  }
}
```

---

## Consumer Idempotency Architecture

To prevent duplicate message processing (e.g. on consumer crash before offset commit), consumers check the `processed_events` table before executing business logic:

```sql
SELECT 1 FROM processed_events WHERE event_id = 'c7a8b9d0-1234-5678-9abc-def012345678';
```
- If found: Consumer logs warning and skips.
- If not found: Consumer processes payload, then inserts `(event_id, consumer_name, now())` into `processed_events`.
