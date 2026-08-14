# Scalability & Performance System Design Analysis

## Scaling Roadmap (1K to 1M Users)

### 1. Scaling from 1,000 to 100,000 Users
- Deploy multiple stateless FastAPI instances behind an Application Load Balancer (ALB).
- Scale Redis read replicas for product detail lookups.
- Partition PostgreSQL database into Read Replicas (offloading SELECT queries).

### 2. Scaling from 100,000 to 1,000,000 Users
- **Database Sharding**: Shard PostgreSQL `orders` and `inventory` tables by `user_id` or `category_id`.
- **Kafka Partitioning**: Increase Kafka topic partitions (e.g. 16 partitions) and scale Consumer Groups across worker nodes.
- **OpenSearch Cluster Scaling**: Increase OpenSearch master and data nodes with multi-shard index partitioning.

---

## Bottleneck Identification

1. **Database Row Lock Contention**: Under high flash-sale load on a single item, `SELECT FOR UPDATE` causes thread queuing. *Mitigation: Implement redis-backed distributed inventory pre-reservation buckets.*
2. **Outbox Polling Overhead**: Constant DB polling for outbox events can add read load. *Mitigation: Transition outbox publisher to PostgreSQL Write-Ahead Log (WAL) Change Data Capture (CDC) via Debezium.*
