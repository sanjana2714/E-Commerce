from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
    HTTP_REQUEST_COUNTER = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
except ImportError:
    generate_latest = lambda: b""
    CONTENT_TYPE_LATEST = "text/plain"

from app.cache.redis_client import redis_client
from app.db.session import get_db
from app.events.publisher import kafka_publisher
from app.search.opensearch_client import opensearch_manager

router = APIRouter(tags=["Health & Metrics"])

@router.get("/health")
def health_check():
    return {"status": "UP", "message": "System core service operational."}

@router.get("/health/live")
def liveness_check():
    return {"status": "ALIVE"}

@router.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    dependencies = {
        "postgres": False,
        "redis": False,
        "opensearch": False,
        "kafka": False
    }

    # 1. Check PostgreSQL
    try:
        db.execute(text("SELECT 1"))
        dependencies["postgres"] = True
    except Exception:  # noqa: BLE001
        dependencies["postgres"] = False

    # 2. Check Redis
    if redis_client.redis:
        try:
            dependencies["redis"] = True
        except Exception:  # noqa: BLE001
            dependencies["redis"] = False

    # 3. Check OpenSearch
    if opensearch_manager.client:
        try:
            dependencies["opensearch"] = opensearch_manager.client.ping()
        except Exception:  # noqa: BLE001
            dependencies["opensearch"] = False

    # 4. Check Kafka
    if kafka_publisher.producer:
        dependencies["kafka"] = True
    else:
        dependencies["kafka"] = False

    all_ready = dependencies["postgres"]
    status_code = status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return Response(
        content=str({
            "status": "READY" if all_ready else "DEGRADED",
            "dependencies": dependencies
        }),
        media_type="application/json",
        status_code=status_code
    )

@router.get("/metrics")
def get_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
