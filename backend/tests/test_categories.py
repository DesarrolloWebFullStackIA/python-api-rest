def test_create_category_success(client):
    response = client.post("/api/v1/categories/", json={
        "name": "Role-Playing Game",
        "description": "Deep immersive narrative experiences."
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Role-Playing Game"
    assert data["description"] == "Deep immersive narrative experiences."
    assert "id" in data
    assert data["games_count"] == 0


def test_create_duplicate_category_fails(client):
    client.post("/api/v1/categories/", json={"name": "Action"})
    response = client.post("/api/v1/categories/", json={"name": "Action"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_get_all_categories(client):
    client.post("/api/v1/categories/", json={"name": "Shooter"})
    client.post("/api/v1/categories/", json={"name": "Simulator"})

    response = client.get("/api/v1/categories/")
    assert response.status_code == 200
    data = response.json()
    names = [c["name"] for c in data]
    assert "Shooter" in names
    assert "Simulator" in names


def test_get_category_by_id(client):
    create_res = client.post("/api/v1/categories/", json={"name": "Platformer"})
    cat_id = create_res.json()["id"]

    response = client.get(f"/api/v1/categories/{cat_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Platformer"


def test_get_nonexistent_category_returns_404(client):
    response = client.get("/api/v1/categories/99999")
    assert response.status_code == 404


def test_update_category(client):
    create_res = client.post("/api/v1/categories/", json={"name": "Horror"})
    cat_id = create_res.json()["id"]

    update_res = client.put(f"/api/v1/categories/{cat_id}", json={
        "name": "Survival Horror",
        "description": "Tense and scary gameplay."
    })
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Survival Horror"


def test_delete_category(client):
    create_res = client.post("/api/v1/categories/", json={"name": "Racing"})
    cat_id = create_res.json()["id"]

    delete_res = client.delete(f"/api/v1/categories/{cat_id}")
    assert delete_res.status_code == 204

    get_res = client.get(f"/api/v1/categories/{cat_id}")
    assert get_res.status_code == 404
