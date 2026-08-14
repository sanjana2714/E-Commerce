# REST API Design Specification

## Overview

All REST API endpoints are prefixed with `/api/v1` and return structured JSON responses.

---

## Standard Error Response Format

```json
{
  "error": {
    "code": "INSUFFICIENT_INVENTORY",
    "message": "Cannot reserve 5 units for product ID 42. Only 2 available in stock.",
    "details": null
  }
}
```

---

## Core API Endpoints

### Authentication & Profile
- `POST /api/v1/auth/register` - Register a new user (`CUSTOMER`, `ADMIN`, `INVENTORY_MANAGER`)
- `POST /api/v1/auth/login` - Authenticate user and return JWT bearer token
- `GET /api/v1/auth/me` - Get current authenticated user profile

### Product Management & OpenSearch Search
- `GET /api/v1/products/search` - Full-text search with filtering (`q`, `category_id`, `brand`, `min_price`, `max_price`, `sort_by`, `page`)
- `GET /api/v1/products/{id}` - Retrieve product details with stock level
- `POST /api/v1/products` - Admin product creation
- `PUT /api/v1/products/{id}` - Admin product update
- `DELETE /api/v1/products/{id}` - Admin product deactivation

### Shopping Cart
- `GET /api/v1/cart` - Get current user cart
- `POST /api/v1/cart/items` - Add item to cart
- `PUT /api/v1/cart/items/{id}` - Update item quantity
- `DELETE /api/v1/cart/items/{id}` - Remove item from cart

### Orders & Payments
- `POST /api/v1/orders` - Idempotent order placement (Requires `Idempotency-Key` header)
- `GET /api/v1/orders` - List user orders
- `GET /api/v1/orders/{id}` - Get order details
- `POST /api/v1/payments/{order_id}/process` - Process simulated payment

### Admin & Observability
- `GET /api/v1/admin/dead-letter-events` - Inspect DLQ failed events
- `GET /api/v1/analytics/top-products` - Top-K heap sales analytics (`?k=10`)
- `GET /api/v1/health/ready` - Readiness check inspecting DB, Redis, Kafka, OpenSearch
- `GET /api/v1/metrics` - Prometheus metrics scraper endpoint
