
def create_test_user(client, suffix="1"):
    payload = {
        "username": f"project_owner_{suffix}",
        "email": f"project_owner_{suffix}@example.com",
    }

    response = client.post("/users/", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_project(client):
    owner = create_test_user(client, "create")

    payload = {
        "name": "Jira Clone",
        "key": "JIRA",
        "description": "Project management platform",
        "owner_id": owner["id"],
    }

    response = client.post("/projects/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["key"] == payload["key"]
    assert data["owner_id"] == owner["id"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_list_projects(client):
    response = client.get("/projects/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_project_by_id(client):
    owner = create_test_user(client, "get")
    payload = {
        "name": "Get Project",
        "key": "GETP",
        "description": "Project retrieval test",
        "owner_id": owner["id"],
    }

    create_response = client.post("/projects/", json=payload)
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]

    response = client.get(f"/projects/{project_id}")

    assert response.status_code == 200
    assert response.json()["id"] == project_id
    assert response.json()["key"] == "GETP"


def test_update_project(client):
    owner = create_test_user(client, "update")
    payload = {
        "name": "Before Update",
        "key": "UPDT",
        "description": "Original description",
        "owner_id": owner["id"],
    }

    create_response = client.post("/projects/", json=payload)
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]

    response = client.patch(
        f"/projects/{project_id}",
        json={"name": "After Update"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "After Update"
    assert response.json()["key"] == "UPDT"


def test_delete_project(client):
    owner = create_test_user(client, "delete")
    payload = {
        "name": "Delete Project",
        "key": "DELP",
        "description": "Project deletion test",
        "owner_id": owner["id"],
    }

    create_response = client.post("/projects/", json=payload)
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]

    response = client.delete(f"/projects/{project_id}")

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(f"/projects/{project_id}")
    assert get_response.status_code == 404


def test_project_with_nonexistent_owner_returns_404(client):
    payload = {
        "name": "Invalid Owner Project",
        "key": "INVO",
        "description": "This owner does not exist",
        "owner_id": 999999,
    }

    response = client.post("/projects/", json=payload)

    assert response.status_code == 404


def test_duplicate_project_key_returns_409(client):
    owner = create_test_user(client, "duplicate")

    payload = {
        "name": "First Project",
        "key": "DUPL",
        "description": "First project with this key",
        "owner_id": owner["id"],
    }

    first_response = client.post("/projects/", json=payload)
    assert first_response.status_code == 201

    duplicate_payload = {
        "name": "Second Project",
        "key": "DUPL",
        "description": "Duplicate key",
        "owner_id": owner["id"],
    }

    response = client.post("/projects/", json=duplicate_payload)

    assert response.status_code == 409


def test_get_nonexistent_project_returns_404(client):
    response = client.get("/projects/999999")

    assert response.status_code == 404


def test_invalid_project_data_returns_422(client):
    response = client.post(
        "/projects/",
        json={
            "name": "Invalid Project",
            "key": "lowercase",
            "owner_id": 1,
        },
    )

    assert response.status_code == 422
