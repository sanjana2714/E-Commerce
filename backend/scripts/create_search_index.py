import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.search.opensearch_client import opensearch_manager
from app.core.logging import logger

def main():
    logger.info("Initializing OpenSearch connection...")
    opensearch_manager.connect()
    if opensearch_manager.client:
        success = opensearch_manager.create_product_index()
        if success:
            logger.info("OpenSearch product index created successfully.")
        else:
            logger.error("Failed to create OpenSearch product index.")
    else:
        logger.error("Could not connect to OpenSearch cluster.")

if __name__ == "__main__":
    main()
