# Testing & Quality Assurance

This document details the automated testing architecture, test fixtures, mocking strategy, and verification coverage of **VaporStore**.

---

## Testing Framework & Setup

- **Test Runner**: `pytest` (v8.0+)
- **HTTP Client**: `starlette.testclient.TestClient`
- **Database Engine**: In-memory SQLite (`sqlite:///:memory:`) using `StaticPool`

### Isolated In-Memory Fixtures (`backend/tests/conftest.py`)
To prevent test pollution and cross-test side effects, each test function executes within a completely isolated, fresh database schema:
```python
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

---

## Test Suite Breakdown (23 Tests)

### 1. Categories Management (`backend/tests/test_categories.py`) — 7 Tests
- `test_create_category_success`: Verifies creation returns HTTP 201 Created and defaults `games_count` to 0.
- `test_create_duplicate_category_fails`: Confirms unique constraint enforcement returning HTTP 400 Bad Request.
- `test_get_all_categories`: Validates retrieval of sorted category records.
- `test_get_category_by_id`: Verifies single record retrieval by ID.
- `test_get_nonexistent_category_returns_404`: Ensures missing IDs return HTTP 404 Not Found.
- `test_update_category`: Tests updating category names and descriptions.
- `test_delete_category`: Tests deletion returning HTTP 204 No Content.

### 2. Video Games Management (`backend/tests/test_games.py`) — 6 Tests
- `test_create_game_success`: Creates a game linked to a valid category, asserting joined category response.
- `test_create_game_with_invalid_category_fails`: Asserts foreign key validation fails with HTTP 400 Bad Request when category does not exist.
- `test_get_games_filtering_and_pagination`: Validates query filtering by `category_id`, `search`, `min_rating`, and `max_price`.
- `test_update_game`: Verifies updating game pricing and review scores.
- `test_delete_game`: Confirms game deletion returning HTTP 204.
- `test_cascade_delete_category_removes_games`: **Relational Cascade Test** confirming that deleting a category automatically removes all child games.

### 3. Frontend Static Mounting (`backend/tests/test_frontend.py`) — 3 Tests
- `test_root_endpoint_metadata`: Confirms `/` returns online status, version, and client links.
- `test_frontend_client_index_serves_html`: Asserts `/client/` serves `index.html`.
- `test_frontend_static_assets_served`: Verifies static delivery of `styles.css`, `api.js`, and `app.js`.

### 4. Steam API Integration (`backend/tests/test_steam.py`) — 7 Tests
- `test_steam_search_endpoint`: Tests catalog search with mocked Steam response.
- `test_steam_search_empty_query_fails`: Validates empty query strings trigger HTTP 422 Unprocessable Entity.
- `test_steam_import_game_auto_creates_category_and_game`: **1-Click Import Test** verifying auto-creation of Category and Game linked via foreign key.
- `test_steam_import_duplicate_fails`: Verifies duplicate AppID import attempts return HTTP 400.
- `test_steam_stats_success`: Tests live concurrent player endpoint with mocked player count.
- `test_steam_stats_game_not_found`: Asserts 404 for nonexistent games.
- `test_steam_stats_game_without_steam_id_fails`: Asserts 400 when game has no `steam_app_id`.

---

## Running Tests

Execute the full suite with verbose reporting:
```bash
pytest -v
```

Execution benchmark: **23 passed in ~0.85s (100% success rate)**.
