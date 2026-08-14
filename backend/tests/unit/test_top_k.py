import pytest
from app.algorithms.top_k import TopKHeap

def test_top_k_empty_list():
    result = TopKHeap.get_top_k_products([], k=5)
    assert result == []

def test_top_k_basic():
    items = [
        {"id": 1, "name": "Item A", "sales_count": 10},
        {"id": 2, "name": "Item B", "sales_count": 50},
        {"id": 3, "name": "Item C", "sales_count": 30},
        {"id": 4, "name": "Item D", "sales_count": 5},
        {"id": 5, "name": "Item E", "sales_count": 100},
    ]
    top_3 = TopKHeap.get_top_k_products(items, k=3, metric_key="sales_count")
    assert len(top_3) == 3
    assert top_3[0]["id"] == 5  # 100 sales
    assert top_3[1]["id"] == 2  # 50 sales
    assert top_3[2]["id"] == 3  # 30 sales

def test_top_k_larger_k_than_elements():
    items = [
        {"id": 1, "sales_count": 20},
        {"id": 2, "sales_count": 40},
    ]
    top_5 = TopKHeap.get_top_k_products(items, k=5)
    assert len(top_5) == 2
    assert top_5[0]["id"] == 2
    assert top_5[1]["id"] == 1
