from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import DomainException
from app.api.dependencies import check_rate_limit
from app.cache.redis_client import redis_client
from app.search.opensearch_client import opensearch_manager
from app.events.publisher import kafka_publisher
from app.search.index_manager import initialize_search_indexes

from app.api.routers import (
    auth,
    products,
    search,
    cart,
    orders,
    payments,
    admin,
    analytics,
    health,
)

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing application infrastructure connections...")
    await redis_client.connect()
    opensearch_manager.connect()
    initialize_search_indexes()
    kafka_publisher.connect()
    logger.info("Application startup sequence completed successfully.")
    yield
    logger.info("Shutting down application resources...")
    await redis_client.close()
    if kafka_publisher.producer:
        kafka_publisher.producer.close()

app = FastAPI(
    title="Scalable E-Commerce Order & Product Search Platform",
    description="High-performance, event-driven e-commerce backend built with FastAPI, PostgreSQL, Redis, OpenSearch, and Kafka.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler for Custom Domain Exceptions
@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

# Middleware for rate limiting
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Exempt health & metrics endpoints from rate limit
    if not request.url.path.startswith("/api/v1/health") and not request.url.path.startswith("/api/v1/metrics"):
        try:
            await check_rate_limit(request)
        except DomainException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": {"code": exc.code, "message": exc.message}}
            )
    response = await call_next(request)
    return response

# Mount API Routers under /api/v1 prefix
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(cart.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "title": "Scalable E-Commerce Order & Product Search Platform",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
