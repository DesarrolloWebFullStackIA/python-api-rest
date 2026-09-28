from unittest.mock import patch
from app.services.steam_service import SteamService


def test_steam_search_endpoint(client):
    """
    Test Steam catalog search endpoint with mocked Steam service response.
    """
    mock_response = {
        "total": 2,
        "query": "Hades",
        "items": [
            {"id": 1145360, "name": "Hades", "price": 24.99, "image_url": "https://steam.cdn/hades.jpg"},
            {"id": 1145350, "name": "Hades II", "price": 29.99, "image_url": "https://steam.cdn/hades2.jpg"}
        ]
    }

    with patch.object(SteamService, "search_steam_games", return_value=mock_response):
        response = client.get("/api/v1/steam/search?query=Hades")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["name"] == "Hades"
        assert data["items"][0]["id"] == 1145360


def test_steam_search_empty_query_fails(client):
    """
    Test that searching with an empty query triggers validation error.
    """
    response = client.get("/api/v1/steam/search?query=")
    assert response.status_code == 422


def test_steam_import_game_auto_creates_category_and_game(client):
    """
    Test 1-click Steam import auto-creates relational category and game.
    """
    mock_steam_details = {
        "name": "Portal 2",
        "short_description": "The 'Perpetual Testing Initiative' has been expanded to allow you to design co-op puzzles!",
        "header_image": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/620/header.jpg",
        "is_free": False,
        "price_overview": {"final": 999, "currency": "USD"},
        "release_date": {"date": "Apr 19, 2011"},
        "metacritic": {"score": 95},
        "genres": [{"id": "2", "description": "Puzzle"}]
    }

    with patch.object(SteamService, "get_app_details", return_value=mock_steam_details):
        response = client.post("/api/v1/games/steam/620")
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Portal 2"
        assert data["price"] == 9.99
        assert data["release_year"] == 2011
        assert data["rating"] == 9.5
        assert data["steam_app_id"] == 620
        assert data["category"]["name"] == "Puzzle"

    # Verify category was created and persists in database
    categories_res = client.get("/api/v1/categories/")
    cat_names = [c["name"] for c in categories_res.json()]
    assert "Puzzle" in cat_names


def test_steam_import_duplicate_fails(client):
    """
    Test that attempting to import an already existing Steam game returns 400 Bad Request.
    """
    mock_steam_details = {
        "name": "Terraria",
        "short_description": "Dig, fight, explore, build!",
        "is_free": False,
        "price_overview": {"final": 999},
        "release_date": {"date": "May 16, 2011"},
        "genres": [{"id": "1", "description": "Action"}]
    }

    with patch.object(SteamService, "get_app_details", return_value=mock_steam_details):
        # First import succeeds
        res1 = client.post("/api/v1/games/steam/105600")
        assert res1.status_code == 201

        # Second import of same AppID fails with 400
        res2 = client.post("/api/v1/games/steam/105600")
        assert res2.status_code == 400
        assert "already imported" in res2.json()["detail"].lower()


def test_steam_stats_success(client):
    """
    Test fetching live concurrent players for a game linked with Steam.
    """
    # Create category and game with steam_app_id
    cat_res = client.post("/api/v1/categories/", json={"name": "Tactical"})
    cat_id = cat_res.json()["id"]

    game_res = client.post("/api/v1/games/", json={
        "title": "Counter-Strike 2",
        "steam_app_id": 730,
        "category_id": cat_id
    })
    game_id = game_res.json()["id"]

    with patch.object(SteamService, "get_concurrent_players", return_value=1254300):
        response = client.get(f"/api/v1/games/{game_id}/steam-stats")
        assert response.status_code == 200
        data = response.json()
        assert data["game_id"] == game_id
        assert data["steam_app_id"] == 730
        assert data["player_count"] == 1254300
        assert data["is_online"] is True


def test_steam_stats_game_not_found(client):
    """
    Test fetching stats for nonexistent game returns 404.
    """
    response = client.get("/api/v1/games/99999/steam-stats")
    assert response.status_code == 404


def test_steam_stats_game_without_steam_id_fails(client):
    """
    Test fetching stats for a game that has no steam_app_id returns 400 Bad Request.
    """
    cat_res = client.post("/api/v1/categories/", json={"name": "Board Games"})
    cat_id = cat_res.json()["id"]

    game_res = client.post("/api/v1/games/", json={
        "title": "Chess Master",
        "category_id": cat_id
    })
    game_id = game_res.json()["id"]

    response = client.get(f"/api/v1/games/{game_id}/steam-stats")
    assert response.status_code == 400
    assert "not linked to a steam" in response.json()["detail"].lower()
