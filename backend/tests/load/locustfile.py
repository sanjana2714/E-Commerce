import uuid
from locust import HttpUser, task, between

class EcommerceLoadTestUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Register and login a unique user for load testing
        self.email = f"loaduser_{uuid.uuid4().hex[:8]}@example.com"
        self.password = "LoadPass123!"
        
        self.client.post("/api/v1/auth/register", json={
            "email": self.email,
            "full_name": "Load Test User",
            "password": self.password,
            "role": "CUSTOMER"
        })

        res = self.client.post("/api/v1/auth/login", json={
            "email": self.email,
            "password": self.password
        })
        if res.status_code == 200:
            token = res.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}

    @task(4)
    def search_products(self):
        query = "laptop"
        self.client.get(f"/api/v1/products/search?q={query}&size=10")

    @task(3)
    def view_product(self):
        self.client.get("/api/v1/products/1")

    @task(2)
    def cart_operations(self):
        self.client.get("/api/v1/cart", headers=self.headers)
        self.client.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 1}, headers=self.headers)

    @task(1)
    def create_order(self):
        idempotency_key = f"LOCUST-{uuid.uuid4()}"
        headers = {**self.headers, "Idempotency-Key": idempotency_key}
        self.client.post("/api/v1/orders", json={"items": [{"product_id": 1, "quantity": 1}]}, headers=headers)
