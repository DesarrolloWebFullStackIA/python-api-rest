def test_create_game_success(client):
    cat_res = client.post("/api/v1/categories/", json={"name": "Action RPG"})
    cat_id = cat_res.json()["id"]

    game_payload = {
        "title": "Elden Ring",
        "description": "Rise, Tarnished, and be guided by grace.",
        "price": 59.99,
        "release_year": 2022,
        "rating": 9.6,
        "is_active": True,
        "category_id": cat_id
    }
    response = client.post("/api/v1/games/", json=game_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Elden Ring"
    assert data["price"] == 59.99
    assert data["category_id"] == cat_id
    assert data["category"]["name"] == "Action RPG"


def test_create_game_with_invalid_category_fails(client):
    game_payload = {
        "title": "Ghost Game",
        "category_id": 9999
    }
    response = client.post("/api/v1/games/", json=game_payload)
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"].lower()


def test_get_games_filtering_and_pagination(client):
    cat1_id = client.post("/api/v1/categories/", json={"name": "Sci-Fi"}).json()["id"]
    cat2_id = client.post("/api/v1/categories/", json={"name": "Fantasy"}).json()["id"]

    client.post("/api/v1/games/", json={"title": "Cyberpunk 2077", "price": 49.99, "rating": 8.7, "category_id": cat1_id})
    client.post("/api/v1/games/", json={"title": "Starfield", "price": 69.99, "rating": 7.0, "category_id": cat1_id})
    client.post("/api/v1/games/", json={"title": "The Witcher 3", "price": 29.99, "rating": 9.8, "category_id": cat2_id})

    # Filter by category
    res_cat1 = client.get(f"/api/v1/games/?category_id={cat1_id}")
    assert res_cat1.status_code == 200
    data = res_cat1.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2

    # Filter by search
    res_search = client.get("/api/v1/games/?search=witcher")
    assert res_search.status_code == 200
    assert res_search.json()["total"] == 1
    assert res_search.json()["items"][0]["title"] == "The Witcher 3"

    # Filter by price
    res_price = client.get("/api/v1/games/?max_price=30.00")
    assert res_price.status_code == 200
    assert res_price.json()["total"] == 1
    assert res_price.json()["items"][0]["title"] == "The Witcher 3"

    # Filter by rating
    res_rating = client.get("/api/v1/games/?min_rating=9.0")
    assert res_rating.status_code == 200
    assert res_rating.json()["total"] == 1


def test_update_game(client):
    cat_id = client.post("/api/v1/categories/", json={"name": "Arcade"}).json()["id"]
    game_res = client.post("/api/v1/games/", json={"title": "Pacman", "price": 4.99, "category_id": cat_id})
    game_id = game_res.json()["id"]

    update_res = client.put(f"/api/v1/games/{game_id}", json={
        "title": "Pac-Man Championship Edition",
        "price": 9.99,
        "rating": 8.5
    })
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["title"] == "Pac-Man Championship Edition"
    assert data["price"] == 9.99


def test_delete_game(client):
    cat_id = client.post("/api/v1/categories/", json={"name": "Retro"}).json()["id"]
    game_res = client.post("/api/v1/games/", json={"title": "Space Invaders", "category_id": cat_id})
    game_id = game_res.json()["id"]

    delete_res = client.delete(f"/api/v1/games/{game_id}")
    assert delete_res.status_code == 204

    get_res = client.get(f"/api/v1/games/{game_id}")
    assert get_res.status_code == 404


def test_cascade_delete_category_removes_games(client):
    cat_id = client.post("/api/v1/categories/", json={"name": "RTS"}).json()["id"]
    game1 = client.post("/api/v1/games/", json={"title": "StarCraft", "category_id": cat_id}).json()["id"]
    game2 = client.post("/api/v1/games/", json={"title": "Age of Empires", "category_id": cat_id}).json()["id"]

    # Delete category
    del_res = client.delete(f"/api/v1/categories/{cat_id}")
    assert del_res.status_code == 204

    # Verify both games were cascade-deleted
    assert client.get(f"/api/v1/games/{game1}").status_code == 404
    assert client.get(f"/api/v1/games/{game2}").status_code == 404
