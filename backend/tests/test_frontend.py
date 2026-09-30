def test_root_endpoint_metadata(client):
    """
    Test root endpoint returns service metadata, version, and links to docs and client.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "API" in data["service"]
    assert data["client_url"] == "/client/"
    assert data["docs_url"] == "/docs"


def test_frontend_client_index_serves_html(client):
    """
    Test that the mounted /client/ endpoint successfully serves the HTML index.
    """
    response = client.get("/client/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
    assert "VaporStore" in response.text
    assert "id=\"gamesGrid\"" in response.text


def test_frontend_static_assets_served(client):
    """
    Test that static CSS and JS client assets are properly served.
    """
    css_res = client.get("/client/css/styles.css")
    assert css_res.status_code == 200
    assert "--bg-primary" in css_res.text

    api_res = client.get("/client/js/api.js")
    assert api_res.status_code == 200
    assert "categoriesApi" in api_res.text
    assert "gamesApi" in api_res.text

    app_res = client.get("/client/js/app.js")
    assert app_res.status_code == 200
    assert "fetchGames" in app_res.text


def test_favicon_endpoints(client):
    """
    Test that favicon.ico and favicon.svg endpoints return 200 with appropriate media types.
    """
    ico_res = client.get("/favicon.ico")
    assert ico_res.status_code == 200

    svg_res = client.get("/client/favicon.svg")
    assert svg_res.status_code == 200
    assert "<svg" in svg_res.text

