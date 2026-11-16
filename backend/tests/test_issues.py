
def create_test_user(client, suffix="1"):
    payload = {
        "username": f"issue_user_{suffix}",
        "email": f"issue_user_{suffix}@example.com",
    }
    response = client.post("/users/", json=payload)
    assert response.status_code == 201
    return response.json()




def create_test_project(client, owner_id, suffix="1"):
    import uuid

    unique_key = f"T{uuid.uuid4().hex[:8].upper()}"

    payload = {
        "name": f"Issue Test Project {suffix}",
        "key": unique_key,
        "description": "Project for issue API tests",
        "owner_id": owner_id,
    }

    response = client.post("/projects/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()



def create_test_issue(client, suffix="1"):
    user = create_test_user(client, suffix)
    project = create_test_project(client, user["id"], suffix)

    payload = {
        "title": f"Test issue {suffix}",
        "description": "Issue created by automated tests",
        "issue_type": "bug",
        "status": "todo",
        "priority": "high",
        "project_id": project["id"],
        "reporter_id": user["id"],
        "assignee_id": None,
        "due_date": "2026-11-05",
    }

    response = client.post("/issues/", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_issue(client):
    issue = create_test_issue(client)

    assert issue["title"] == "Test issue 1"
    assert issue["issue_type"] == "bug"
    assert issue["status"] == "todo"
    assert issue["priority"] == "high"
    assert issue["assignee_id"] is None
    assert issue["id"] is not None
    assert issue["created_at"] is not None


def test_list_issues(client):
    create_test_issue(client)

    response = client.get("/issues/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test issue 1"


def test_get_issue_by_id(client):
    issue = create_test_issue(client)

    response = client.get(f"/issues/{issue['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == issue["id"]


def test_update_issue(client):
    issue = create_test_issue(client)

    response = client.patch(
        f"/issues/{issue['id']}",
        json={
            "status": "in_progress",
            "priority": "critical",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    assert response.json()["priority"] == "critical"
    assert response.json()["title"] == issue["title"]


def test_clear_issue_assignee(client):
    user = create_test_user(client, "assign")
    project = create_test_project(client, user["id"], "assign")

    payload = {
        "title": "Assigned issue",
        "project_id": project["id"],
        "reporter_id": user["id"],
        "assignee_id": user["id"],
    }

    create_response = client.post("/issues/", json=payload)
    assert create_response.status_code == 201
    issue_id = create_response.json()["id"]

    response = client.patch(
        f"/issues/{issue_id}",
        json={"assignee_id": None},
    )

    assert response.status_code == 200
    assert response.json()["assignee_id"] is None


def test_delete_issue(client):
    issue = create_test_issue(client)

    response = client.delete(f"/issues/{issue['id']}")

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(f"/issues/{issue['id']}")
    assert get_response.status_code == 404


def test_get_nonexistent_issue_returns_404(client):
    response = client.get("/issues/999999")

    assert response.status_code == 404


def test_create_issue_with_nonexistent_project_returns_404(client):
    user = create_test_user(client, "no_project")

    response = client.post(
        "/issues/",
        json={
            "title": "Issue with missing project",
            "project_id": 999999,
            "reporter_id": user["id"],
        },
    )

    assert response.status_code == 404


def test_create_issue_with_nonexistent_reporter_returns_404(client):
    user = create_test_user(client, "reporter")
    project = create_test_project(client, user["id"], "reporter")

    response = client.post(
        "/issues/",
        json={
            "title": "Issue with missing reporter",
            "project_id": project["id"],
            "reporter_id": 999999,
        },
    )

    assert response.status_code == 404


def test_create_issue_with_nonexistent_assignee_returns_404(client):
    user = create_test_user(client, "assignee")
    project = create_test_project(client, user["id"], "assignee")

    response = client.post(
        "/issues/",
        json={
            "title": "Issue with missing assignee",
            "project_id": project["id"],
            "reporter_id": user["id"],
            "assignee_id": 999999,
        },
    )

    assert response.status_code == 404


def test_create_issue_with_invalid_type_returns_422(client):
    user = create_test_user(client, "invalid")
    project = create_test_project(client, user["id"], "invalid")

    response = client.post(
        "/issues/",
        json={
            "title": "Invalid issue type",
            "issue_type": "feature_request",
            "project_id": project["id"],
            "reporter_id": user["id"],
        },
    )

    assert response.status_code == 422


def test_delete_nonexistent_issue_returns_404(client):
    response = client.delete("/issues/999999")

    assert response.status_code == 404
