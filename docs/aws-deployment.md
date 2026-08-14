# AWS Cloud Production Architecture Guide

## Overview

This document maps local Docker components to enterprise AWS Cloud services.

---

## Local vs AWS Service Mapping

| Local Component | AWS Production Equivalent | Technical Rationale |
| :--- | :--- | :--- |
| `FastAPI Backend` | **AWS ECS (Fargate)** or **AWS EKS** | Serverless container execution with auto-scaling based on CPU/RAM metrics |
| `PostgreSQL 16` | **Amazon RDS for PostgreSQL** (Multi-AZ) | Automated backups, automatic failover, read replicas for query offloading |
| `Redis 7` | **Amazon ElastiCache for Redis** | In-memory cluster mode with multi-node replication and sub-millisecond latency |
| `Apache Kafka` | **Amazon MSK** (Managed Streaming for Kafka) | Managed Kafka cluster with automated broker patching, ZooKeeper/KRaft management |
| `OpenSearch 2.11` | **Amazon OpenSearch Service** | Managed search cluster with automated index lifecycle management (ISM) |
| `Prometheus / Grafana` | **Amazon Managed Prometheus & Grafana** | Serverless metrics storage and enterprise dashboarding |
| `React Frontend` | **AWS S3 + CloudFront CDN** | Static web hosting with global edge caching and TLS termination |

---

## AWS Infrastructure Topology

```
                         [ AWS Cloud Infrastructure ]
                                      |
                              +-------v-------+
                              | AWS CloudFront| (Global CDN)
                              +-------+-------+
                                      |
                              +-------v-------+
                              | Application LB| (ALB)
                              +-------+-------+
                                      |
                      +---------------+---------------+
                      |                               |
              +-------v-------+               +-------v-------+
              | ECS Service 1 |               | ECS Service 2 |
              | (AZ-1)        |               | (AZ-2)        |
              +-------+-------+               +-------+-------+
                      |                               |
        +-------------+-------------+-----------------+-------------+
        |                           |                               |
+-------v-------+           +-------v-------+               +-------v-------+
| RDS Postgres  |           | ElastiCache   |               |  Amazon MSK   |
| Primary + Read|           | Redis Cluster |               | Kafka Brokers |
+---------------+           +---------------+               +---------------+
```
