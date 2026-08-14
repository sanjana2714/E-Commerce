# SDE Technical Interview Questions & Answers Guide

This document contains 28 in-depth questions and answers designed specifically for SDE technical interviews (e.g. Amazon, Google, Meta) based on the **Scalable E-Commerce Order & Product Search Platform**.

---

### Q1: Why FastAPI over Django or Flask?
**Answer**: FastAPI provides asynchronous native `async/await` execution built on top of Starlette and Pydantic. It offers automatic data validation, high throughput comparable to NodeJS/Go, auto-generated OpenAPI/Swagger documentation, and native dependency injection, making it ideal for high-concurrency microservice APIs.

### Q2: Why PostgreSQL for primary storage?
**Answer**: E-commerce transactional domains demand strict ACID guarantees (Atomicity, Consistency, Isolation, Durability). PostgreSQL offers robust row-level locking (`SELECT FOR UPDATE`), check constraints (`stock_quantity >= 0`), rich indexing (B-Tree, GIN), and mature transactional outbox capabilities.

### Q3: Why Redis?
**Answer**: Redis acts as an in-memory key-value cache layer to reduce database read pressure for hot product detail lookups and user carts. It also powers our sliding-window rate limiter using atomic Redis sorted sets (`ZSET`).

### Q4: Why OpenSearch instead of searching directly against PostgreSQL?
**Answer**: PostgreSQL `LIKE '%query%'` queries require full sequential table scans ($O(N)$), causing severe latency at scale. OpenSearch uses an inverted index with edge N-gram tokenizers to execute full-text, fuzzy match, multi-field, and faceted queries in single-digit milliseconds ($O(1)$ lookup per term).

### Q5: Why Kafka instead of direct synchronous HTTP API calls between workers?
**Answer**: Direct HTTP calls create tight temporal coupling—if a downstream search or notification service goes down or experiences latency, the primary order checkout API fails or slows down. Kafka decouples production from consumption, providing durable log persistence, asynchronous processing, and buffer capacity during traffic spikes.

### Q6: What is the Transactional Outbox Pattern and why is it necessary?
**Answer**: Dual writes (writing to DB and calling Kafka directly) can fail if Kafka is down or the network drops after DB commit, leading to split-brain inconsistencies. The Transactional Outbox Pattern writes the domain event into an `outbox_events` database table *inside the same database transaction* as the order/product change. A separate background worker reads the outbox table and publishes to Kafka. If Kafka is unavailable, the DB state remains consistent and events publish when Kafka recovers.

### Q7: How does your system prevent duplicate order creation?
**Answer**: The client provides an `Idempotency-Key` header with each order request. The order service checks an `idempotency_keys` database table. If the key exists, the service returns the previous order response without re-executing inventory deduction or order creation.

### Q8: How do you prevent overselling under heavy concurrent purchase traffic?
**Answer**: We use pessimistic row-level locking via `SELECT FOR UPDATE` on the target product's `inventory` table row inside an active PostgreSQL transaction. When 100 concurrent threads attempt to purchase stock of 10, PostgreSQL serializes access to the locked row. The first 10 reservations succeed, deducting stock to 0. The remaining 90 threads read `stock_quantity = 0` and throw an `InsufficientInventoryError`.

### Q9: How does row-level locking work internally in PostgreSQL?
**Answer**: When `SELECT ... FOR UPDATE` is called, PostgreSQL places an Exclusive Lock (`XLock`) on the tuple header of the selected row. Other transactions attempting to acquire a lock on the same tuple block until the holding transaction issues a `COMMIT` or `ROLLBACK`.

### Q10: What happens when Kafka is completely unavailable?
**Answer**: Primary order placement and product management continue without interruption. Outbox events are stored safely in PostgreSQL with status `PENDING`. When Kafka recovers, the Outbox Publisher process resumes polling and flushes all queued events in chronological order.

### Q11: What happens when Redis is unavailable?
**Answer**: The system gracefully degrades. Cache misses trigger direct PostgreSQL reads. The rate limiter fails open (allows requests) to maintain availability while logging system warnings.

### Q12: What happens when OpenSearch is unavailable?
**Answer**: The search service detects OpenSearch ping failure and automatically falls back to indexed PostgreSQL queries (`ILIKE` / category filtering), maintaining full search availability.

### Q13: Why at-least-once delivery instead of exactly-once delivery?
**Answer**: Truly distributed exactly-once delivery requires heavy two-phase commit (2PC) protocols that severely limit throughput. Instead, we implement at-least-once delivery combined with **idempotent consumers**, ensuring duplicate messages can be safely retried without side effects.

### Q14: How are duplicate Kafka events handled by consumers?
**Answer**: Each Kafka event contains a unique `event_id`. Before processing an event, consumer workers check a `processed_events` PostgreSQL table. If `event_id` exists, the consumer skips processing. Otherwise, it executes the payload action and records `event_id` atomically.

### Q15: What is the complexity of your Top-K Product Analytics algorithm?
**Answer**:
- **Time Complexity**: $O(N \log K)$ where $N$ is total products and $K$ is target count.
- **Space Complexity**: $O(K)$ memory footprint.
- **Why Heap**: A full sort takes $O(N \log N)$. For $N=1,000,000$ and $K=10$, a min-heap requires 3.3 million operations versus 20 million operations for quicksort.

### Q16: How would you scale this architecture on AWS?
**Answer**:
- FastAPI Backend → AWS ECS Fargate or EKS with Auto Scaling Group.
- PostgreSQL → AWS RDS PostgreSQL Multi-AZ with Read Replicas.
- Redis → AWS ElastiCache for Redis Cluster Mode.
- Kafka → AWS MSK (Managed Streaming for Apache Kafka).
- OpenSearch → Amazon OpenSearch Service.

### Q17: What would you change for a production deployment?
**Answer**: Enable TLS/SSL for all service communications, implement distributed tracing using OpenTelemetry/Jaeger, add secret management via AWS Secrets Manager, configure Multi-AZ failover for Postgres and MSK, and enforce CI/CD deployment pipelines.
