# Fault Tolerance & Failure Handling Specification

## Component Failure Matrix

| Service Failure | Impact | Failure Handling & System Recovery |
| :--- | :--- | :--- |
| **PostgreSQL Down** | Core APIs return 500/503 | Read replicas promote to primary; connection pool retries with backoff. |
| **Redis Down** | Cache misses, rate limit bypass | Fails open gracefully; API falls back to PostgreSQL & OpenSearch. |
| **Kafka Down** | Outbox workers cannot publish | Events remain safe in `outbox_events` DB table (`PENDING`); flushed upon recovery. |
| **OpenSearch Down**| Search fallback triggered | Search service falls back to PostgreSQL indexed queries (`ILIKE` / category filtering). |
| **Consumer Failure**| Event execution paused | Kafka offset remains uncommitted; worker container restarts and re-processes event. |

---

## Dead Letter Queue (DLQ) & Retry Policy
- Events failing execution undergo **exponential backoff retries** (1s, 2s, 4s, 8s, 16s).
- After **5 consecutive retries**, the event status transitions to `DEAD_LETTER`.
- Admins can inspect and re-trigger DLQ events via `GET /api/v1/admin/dead-letter-events` and `POST /api/v1/admin/outbox-events/{id}/retry`.
