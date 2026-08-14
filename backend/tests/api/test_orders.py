import uuid

def test_idempotent_order_creation(client, customer_headers, admin_headers, db_session):
    # 1. Create Category & Product as Admin
    cat_res = client.post("/api/v1/products/categories", json={"name": "Electronics"}, headers=admin_headers)
    cat_id = cat_res.json()["id"]

    prod_res = client.post(
        "/api/v1/products",
        json={
            "sku": "SKU-ORDER-TEST-01",
            "name": "Test Laptop",
            "category_id": cat_id,
            "brand": "TechCorp",
            "price": 999.99,
            "initial_stock": 10
        },
        headers=admin_headers
    )
    product_id = prod_res.json()["id"]

    # 2. Place Order with Idempotency-Key
    idempotency_key = f"IDEM-{uuid.uuid4()}"
    order_payload = {
        "items": [
            {"product_id": product_id, "quantity": 2}
        ]
    }

    headers_with_key = {**customer_headers, "Idempotency-Key": idempotency_key}

    # First request
    res1 = client.post("/api/v1/orders", json=order_payload, headers=headers_with_key)
    assert res1.status_code == 201
    order1 = res1.json()
    assert order1["status"] == "PENDING"
    assert order1["total_amount"] == 1999.98

    # Second request with SAME Idempotency-Key -> MUST return same order without duplicate creation
    res2 = client.post("/api/v1/orders", json=order_payload, headers=headers_with_key)
    assert res2.status_code == 201
    order2 = res2.json()
    assert order2["id"] == order1["id"]

    # 3. Process Payment
    pay_res = client.post(f"/api/v1/payments/{order1['id']}/process", json={"simulate_failure": False}, headers=customer_headers)
    assert pay_res.status_code == 200
    assert pay_res.json()["status"] == "SUCCESS"
