# Database Design & Query Performance Specification

## Database Architecture Overview

The system uses **PostgreSQL 16** as its primary ACID-compliant relational transactional database.

---

## Relational Schema & Indexes

| Table | Primary Key | Foreign Keys | Key Indexes | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `users` | `id` | None | `email` (UNIQUE), `role` | Authentication & RBAC |
| `categories` | `id` | None | `name` (UNIQUE), `slug` (UNIQUE) | Product catalog taxonomy |
| `products` | `id` | `category_id` | `sku` (UNIQUE), `category_id`, `brand`, `status` | Core product details |
| `inventory` | `id` | `product_id` | `product_id` (UNIQUE) | Stock levels & pessimistic locking |
| `carts` | `id` | `user_id` | `user_id` (UNIQUE) | User active shopping cart |
| `cart_items` | `id` | `cart_id`, `product_id` | `cart_id`, `product_id` | Cart item breakdown |
| `orders` | `id` | `user_id` | `idempotency_key` (UNIQUE), `user_id`, `status`, `created_at` | Order transaction records |
| `order_items` | `id` | `order_id`, `product_id` | `order_id`, `product_id` | Items purchased per order |
| `payments` | `id` | `order_id` | `payment_id` (UNIQUE), `order_id` (UNIQUE), `status` | Simulated payment processing |
| `outbox_events` | `id` | None | `event_id` (UNIQUE), `status`, `created_at` | Transactional outbox event publishing |
| `processed_events`| `event_id` | None | `event_id` (PRIMARY KEY) | Kafka consumer deduplication |
| `idempotency_keys`| `key` | None | `key` (PRIMARY KEY), `user_id` | Request deduplication |

---

## Index Rationale & Benchmark EXPLAIN Analysis

### 1. `products.sku` & `products.category_id`
- **Why**: SKU lookups are done during order validation. Category queries filter product catalogs.
- **EXPLAIN ANALYZE**:
```sql
EXPLAIN ANALYZE SELECT * FROM products WHERE sku = 'SKU-APP-0001-123';
-- Result: Index Scan using ix_products_sku on products (cost=0.28..8.30 rows=1 width=128) (actual time=0.015..0.017 ms)
```

### 2. `inventory.product_id` Row-Level Locking
- **Why**: `SELECT FOR UPDATE` on inventory requires instant row lookup to prevent lock escalation or full table scans.
- **EXPLAIN ANALYZE**:
```sql
EXPLAIN ANALYZE SELECT * FROM inventory WHERE product_id = 42 FOR UPDATE;
-- Result: Index Scan using ix_inventory_product_id on inventory (cost=0.28..8.30 rows=1 width=32) (actual time=0.018..0.020 ms)
```

### 3. Monetary Precision (`NUMERIC(12,2)`)
Floating point arithmetic (`float`/`double`) causes rounding inaccuracies in financial calculations (e.g. `0.1 + 0.2 = 0.30000000000000004`). All monetary columns (`price`, `total_amount`, `subtotal`, `amount`) strictly use `NUMERIC(12, 2)` decimal data types.
