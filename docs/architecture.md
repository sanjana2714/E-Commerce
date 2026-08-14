# System Architecture & Design Specification

## Overview

The **Scalable E-Commerce Order & Product Search Platform** is built as an event-driven, highly concurrent distributed system designed for SDE technical interviews. It prioritizes strong transaction isolation, inventory consistency, idempotent order processing, outbox event delivery, and sub-millisecond search performance using OpenSearch.

---

## High-Level System Architecture

```mermaid
graph TD
    Client[React Frontend / Client] -->|HTTPS REST| API[FastAPI Backend Gateway]
    
    subgraph Primary Storage & Caching
        API -->|Read/Write Tx| DB[(PostgreSQL Primary DB)]
        API -->|Cache-Aside / Rate Limit| Redis[(Redis Cache)]
    end

    subgraph Transactional Outbox Pattern
        DB -->|Outbox Table Insert| Outbox[Transactional Outbox]
        Publisher[Outbox Publisher Worker] -->|Poll Pending| Outbox
        Publisher -->|Publish JSON Event| Kafka{Apache Kafka Event Bus}
    end

    subgraph Asynchronous Consumers
        Kafka -->|product-events| SearchConsumer[Search Consumer Worker]
        Kafka -->|inventory-events| InvConsumer[Inventory Consumer Worker]
        Kafka -->|payment-events| PayConsumer[Payment Consumer Worker]
        Kafka -->|notification-events| NotifConsumer[Notification Consumer Worker]
    end

    SearchConsumer -->|Bulk Index| OS[(OpenSearch Search Cluster)]
    NotifConsumer -->|Write Notification| DB
```

---

## Order Placement & Inventory Concurrency Flow

```mermaid
sequenceDiagram
    autonumber
    actor Customer
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant Outbox as Outbox Table
    participant Kafka as Kafka Bus
    participant Consumer as Search/Payment Consumer

    Customer->>API: POST /api/v1/orders (Header: Idempotency-Key)
    API->>DB: Check Idempotency Key Record
    alt Duplicate Request
        DB-->>API: Key Exists
        API-->>Customer: Return Cached Order Response
    else New Request
        API->>DB: BEGIN TRANSACTION
        API->>DB: SELECT * FROM inventory WHERE product_id = X FOR UPDATE
        DB-->>API: Lock Row & Return Stock
        alt Stock >= Requested
            API->>DB: Update stock_quantity = stock - qty, reserved = reserved + qty
            API->>DB: INSERT INTO orders & order_items
            API->>DB: INSERT INTO payments (status=PENDING)
            API->>DB: INSERT INTO outbox_events (event_type='OrderCreated')
            API->>DB: INSERT INTO idempotency_keys
            API->>DB: COMMIT TRANSACTION
            API-->>Customer: HTTP 201 Order Created
            
            loop Outbox Poller (Async)
                Publisher->>Outbox: Poll PENDING events
                Publisher->>Kafka: Publish OrderCreated Event
                Publisher->>Outbox: Mark PUBLISHED
            end
        else Insufficient Stock
            API->>DB: ROLLBACK TRANSACTION
            API-->>Customer: HTTP 409 Insufficient Inventory
        end
    end
```

---

## OpenSearch Event-Driven Sync Flow

```mermaid
sequenceDiagram
    autonumber
    actor Admin
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant Outbox as Outbox Table
    participant Kafka as Kafka Bus
    participant Consumer as Search Consumer Worker
    participant OS as OpenSearch Cluster

    Admin->>API: POST /api/v1/products (Create Product)
    API->>DB: BEGIN TRANSACTION
    API->>DB: INSERT INTO products & inventory
    API->>DB: INSERT INTO outbox_events (type='ProductCreated')
    API->>DB: COMMIT TRANSACTION
    API-->>Admin: HTTP 201 Product Created

    OutboxWorker->>DB: Fetch PENDING outbox events
    OutboxWorker->>Kafka: Publish to 'product-events' topic
    OutboxWorker->>DB: Update status='PUBLISHED'

    Consumer->>Kafka: Poll 'product-events'
    Consumer->>DB: Check processed_events table (Event Idempotency)
    alt New Event
        Consumer->>OS: Index Document into 'products_v1'
        Consumer->>DB: INSERT INTO processed_events (event_id, consumer_name)
    else Duplicate Event
        Consumer-->>Kafka: Skip Event Processing
    end
```

---

## Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    USERS ||--o{ CARTS : owns
    USERS ||--o{ ORDERS : places
    USERS ||--o{ NOTIFICATIONS : receives
    CATEGORIES ||--o{ PRODUCTS : contains
    PRODUCTS ||--|| INVENTORY : has
    CARTS ||--o{ CART_ITEMS : includes
    PRODUCTS ||--o{ CART_ITEMS : in
    ORDERS ||--o{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : ordered_in
    ORDERS ||--|| PAYMENTS : has
    
    USERS {
        int id PK
        string email UK
        string full_name
        string hashed_password
        string role
        timestamp created_at
    }
    
    PRODUCTS {
        int id PK
        string sku UK
        string name
        int category_id FK
        string brand
        numeric price
        float rating
        string status
        int version
    }
    
    INVENTORY {
        int id PK
        int product_id FK,UK
        int stock_quantity
        int reserved_quantity
        int version
    }

    ORDERS {
        int id PK
        int user_id FK
        string idempotency_key UK
        string status
        numeric total_amount
        timestamp created_at
    }

    OUTBOX_EVENTS {
        int id PK
        string event_id UK
        string aggregate_type
        string aggregate_id
        string event_type
        json payload
        string status
        int retry_count
    }
```
