
def test_list_users(client):
    response = client.get("/users/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_user(client):
    payload = {
        "username": "pytest_user",
        "email": "pytest_user@example.com",
    }

    response = client.post("/users/", json=payload)

    assert response.status_code == 201
    assert response.json()["username"] == payload["username"]
    assert response.json()["email"] == payload["email"]
    assert "id" in response.json()


def test_duplicate_username_returns_409(client):
    payload = {
        "username": "duplicate_user",
        "email": "first@example.com",
    }

    first_response = client.post("/users/", json=payload)
    assert first_response.status_code == 201

    duplicate_payload = {
        "username": "duplicate_user",
        "email": "second@example.com",
    }

    response = client.post("/users/", json=duplicate_payload)

    assert response.status_code == 409


def test_invalid_user_data_returns_422(client):
    response = client.post(
        "/users/",
        json={"username": "missing_email"},
    )

    assert response.status_code == 422


def test_get_nonexistent_user_returns_404(client):
    response = client.get("/users/999999")

    assert response.status_code == 404


def test_update_user(client):
    payload = {
        "username": "before_update",
        "email": "before@example.com",
    }

    create_response = client.post("/users/", json=payload)
    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    updated_payload = {
        "username": "after_update",
        "email": "after@example.com",
    }

    response = client.put(
        f"/users/{user_id}",
        json=updated_payload,
    )

    assert response.status_code == 200
    assert response.json()["username"] == "after_update"
    assert response.json()["email"] == "after@example.com"


def test_update_nonexistent_user_returns_404(client):
    payload = {
        "username": "updated_user",
        "email": "updated@example.com",
    }

    response = client.put("/users/999999", json=payload)

    assert response.status_code == 404


def test_delete_user(client):
    payload = {
        "username": "delete_me",
        "email": "delete_me@example.com",
    }

    create_response = client.post("/users/", json=payload)
    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    response = client.delete(f"/users/{user_id}")

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_user_returns_404(client):
    response = client.delete("/users/999999")

    assert response.status_code == 404
