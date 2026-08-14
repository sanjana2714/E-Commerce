import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.models.product import Product, ProductStatus
from app.search.opensearch_client import opensearch_manager
from app.core.logging import logger

def reindex_all_products():
    logger.info("Starting OpenSearch product reindexing script...")
    opensearch_manager.connect()
    
    if not opensearch_manager.client:
        logger.error("OpenSearch cluster is not reachable. Aborting reindex.")
        return

    # Ensure index exists
    opensearch_manager.create_product_index()

    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        products = db.query(Product).filter(Product.status == ProductStatus.ACTIVE).all()
        total_products = len(products)
        logger.info(f"Fetched {total_products} active products from PostgreSQL.")

        products_list = []
        for p in products:
            prod_dict = {
                "id": p.id,
                "sku": p.sku,
                "name": p.name,
                "description": p.description,
                "category_id": p.category_id,
                "brand": p.brand,
                "price": float(p.price),
                "currency": p.currency,
                "rating": float(p.rating),
                "status": p.status.value,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            products_list.append(prod_dict)

        # Batch indexing in chunks of 200
        chunk_size = 200
        total_indexed = 0

        for i in range(0, len(products_list), chunk_size):
            chunk = products_list[i : i + chunk_size]
            indexed_count = opensearch_manager.bulk_index_products(chunk)
            total_indexed += indexed_count

        logger.info(f"Reindexing Complete! Successfully indexed {total_indexed}/{total_products} products into OpenSearch.")

    except Exception as e:
        logger.error(f"Reindexing failed with error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reindex_all_products()
