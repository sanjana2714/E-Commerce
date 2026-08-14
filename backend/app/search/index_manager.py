from app.core.logging import logger
from app.search.opensearch_client import opensearch_manager


def initialize_search_indexes():
    """Idempotently ensure OpenSearch index exists with correct schema."""
    opensearch_manager.connect()
    if opensearch_manager.client:
        success = opensearch_manager.create_product_index()
        if success:
            logger.info("Search index initialization complete.")
        else:
            logger.warning("Failed to initialize OpenSearch index.")
    else:
        logger.warning("OpenSearch unavailable during index initialization.")
