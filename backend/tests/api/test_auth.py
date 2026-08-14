def test_register_and_login_flow(client):
    # 1. Register User
    reg_payload = {
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "Password123!",
        "role": "CUSTOMER"
    }
    response = client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "CUSTOMER"

    # 2. Login User
    login_payload = {
        "email": "newuser@example.com",
        "password": "Password123!"
    }
    login_res = client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 3. Get /me
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "newuser@example.com"
