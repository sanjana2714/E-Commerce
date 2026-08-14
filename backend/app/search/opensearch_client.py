from typing import Any

try:
    from opensearchpy import OpenSearch
    from opensearchpy.exceptions import OpenSearchException
except ImportError:
    OpenSearch = None
    class OpenSearchException(Exception):
        pass

from app.core.config import settings
from app.core.logging import logger


class OpenSearchManager:
    def __init__(self):
        self.client: Any | None = None

    def connect(self):
        if not OpenSearch:
            logger.warning("opensearchpy module not installed. OpenSearch running in fallback mode.")
            self.client = None
            return

        try:
            self.client = OpenSearch(
                hosts=[{"host": settings.OPENSEARCH_HOST, "port": settings.OPENSEARCH_PORT}],
                http_compress=True,
                use_ssl=False,
                verify_certs=False,
                ssl_assert_hostname=False,
                ssl_show_warn=False,
                timeout=1,
                max_retries=0,
            )
            if self.client.ping():
                logger.info("Connected to OpenSearch cluster successfully.")
            else:
                logger.warning("OpenSearch ping failed. Search service running in fallback mode.")
                self.client = None
        except OpenSearchException:
            logger.warning(f"OpenSearch unavailable at {settings.OPENSEARCH_URL}. Running in fallback mode.")
            self.client = None

    def create_product_index(self, index_name: str = settings.OPENSEARCH_INDEX_PRODUCTS) -> bool:
        if not self.client:
            return False
        
        mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "autocomplete_analyzer": {
                            "tokenizer": "autocomplete_tokenizer",
                            "filter": ["lowercase"]
                        }
                    },
                    "tokenizer": {
                        "autocomplete_tokenizer": {
                            "type": "edge_ngram",
                            "min_gram": 2,
                            "max_gram": 10,
                            "token_chars": ["letter", "digit"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "sku": {"type": "keyword"},
                    "name": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "autocomplete": {
                                "type": "text",
                                "analyzer": "autocomplete_analyzer",
                                "search_analyzer": "standard"
                            },
                            "raw": {"type": "keyword"}
                        }
                    },
                    "description": {"type": "text"},
                    "category_id": {"type": "integer"},
                    "brand": {"type": "keyword"},
                    "price": {"type": "double"},
                    "currency": {"type": "keyword"},
                    "rating": {"type": "float"},
                    "status": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
        }

        try:
            if not self.client.indices.exists(index=index_name):
                self.client.indices.create(index=index_name, body=mapping)
                logger.info(f"Created OpenSearch index '{index_name}' with autocomplete mapping.")
            return True
        except OpenSearchException as e:
            logger.error(f"Error creating OpenSearch index {index_name}: {e}")
            return False

    def index_product(self, product_dict: dict[str, Any], index_name: str = settings.OPENSEARCH_INDEX_PRODUCTS) -> bool:
        if not self.client:
            return False
        try:
            doc_id = str(product_dict["id"])
            self.client.index(index=index_name, body=product_dict, id=doc_id, refresh=True)
            return True
        except OpenSearchException as e:
            logger.error(f"Error indexing product {product_dict.get('id')}: {e}")
            return False

    def delete_product_document(self, product_id: int, index_name: str = settings.OPENSEARCH_INDEX_PRODUCTS) -> bool:
        if not self.client:
            return False
        try:
            self.client.delete(index=index_name, id=str(product_id), ignore=[404], refresh=True)
            return True
        except OpenSearchException as e:
            logger.error(f"Error deleting product document {product_id}: {e}")
            return False

    def bulk_index_products(self, products_list: list[dict[str, Any]], index_name: str = settings.OPENSEARCH_INDEX_PRODUCTS) -> int:
        if not self.client or not products_list:
            return 0
        
        actions = []
        for prod in products_list:
            actions.append({"index": {"_index": index_name, "_id": str(prod["id"])}})
            actions.append(prod)

        try:
            response = self.client.bulk(body=actions, refresh=True)
            indexed_count = len([item for item in response.get("items", []) if "index" in item and item["index"].get("status") in (200, 201)])
            logger.info(f"Bulk indexed {indexed_count}/{len(products_list)} items into OpenSearch.")
            return indexed_count
        except OpenSearchException as e:
            logger.error(f"Bulk indexing error: {e}")
            return 0

    def search_products(
        self,
        query_text: str | None = None,
        category_id: int | None = None,
        brand: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_rating: float | None = None,
        sort_by: str = "relevance",
        page: int = 1,
        size: int = 20,
        index_name: str = settings.OPENSEARCH_INDEX_PRODUCTS
    ) -> dict[str, Any]:
        if not self.client:
            return {"total": 0, "hits": []}

        must_clause = []
        filter_clause = [{"term": {"status": "ACTIVE"}}]

        if query_text:
            must_clause.append({
                "multi_match": {
                    "query": query_text,
                    "fields": ["name^3", "name.autocomplete^2", "description", "brand^2"],
                    "fuzziness": "AUTO"
                }
            })
        else:
            must_clause.append({"match_all": {}})

        if category_id is not None:
            filter_clause.append({"term": {"category_id": category_id}})
        if brand is not None:
            filter_clause.append({"term": {"brand": brand}})

        price_range = {}
        if min_price is not None:
            price_range["gte"] = min_price
        if max_price is not None:
            price_range["lte"] = max_price
        if price_range:
            filter_clause.append({"range": {"price": price_range}})

        if min_rating is not None:
            filter_clause.append({"range": {"rating": {"gte": min_rating}}})

        sort_clause = []
        if sort_by == "price_asc":
            sort_clause.append({"price": {"order": "asc"}})
        elif sort_by == "price_desc":
            sort_clause.append({"price": {"order": "desc"}})
        elif sort_by == "rating_desc":
            sort_clause.append({"rating": {"order": "desc"}})
        elif sort_by == "newest":
            sort_clause.append({"created_at": {"order": "desc"}})

        from_idx = (page - 1) * size

        search_body = {
            "from": from_idx,
            "size": size,
            "query": {
                "bool": {
                    "must": must_clause,
                    "filter": filter_clause
                }
            }
        }
        if sort_clause:
            search_body["sort"] = sort_clause

        try:
            res = self.client.search(index=index_name, body=search_body)
            total = res["hits"]["total"]["value"]
            hits = [item["_source"] for item in res["hits"]["hits"]]
            return {"total": total, "hits": hits}
        except OpenSearchException as e:
            logger.error(f"OpenSearch query failed: {e}")
            return {"total": 0, "hits": []}

opensearch_manager = OpenSearchManager()
