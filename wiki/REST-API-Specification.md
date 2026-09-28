# REST API Specification

This document provides complete documentation of the **VaporStore REST API** endpoints, parameters, request/response formats, and semantic HTTP status codes.

---

## General Conventions

- **Base URL**: `/api/v1`
- **Content-Type**: `application/json`
- **Semantic HTTP Status Codes**:
  - `200 OK`: Successful read or update operation.
  - `201 Created`: Resource successfully created.
  - `204 No Content`: Successful deletion (no response body).
  - `400 Bad Request`: Business rule violation (e.g. duplicate category, invalid foreign key).
  - `404 Not Found`: Resource ID does not exist.
  - `422 Unprocessable Entity`: Schema/data validation failure.
  - `500 Internal Server Error`: Server or database failure.
  - `502 Bad Gateway`: External provider communication failure (e.g. Steam unreachable).

---

## 1. System Health

### `GET /api/v1/health`
Checks API service health and database connectivity.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "app_name": "Video Games API",
  "version": "1.0.0",
  "database": "connected"
}
```

---

## 2. Categories Resource (`/api/v1/categories`)

### `GET /api/v1/categories/`
Retrieves all categories ordered alphabetically, each annotated with its computed count of associated games.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Action",
    "description": "Fast-paced games focusing on combat and reflexes.",
    "created_at": "2026-09-28T10:47:55Z",
    "updated_at": "2026-09-28T10:47:55Z",
    "games_count": 3
  }
]
```

### `POST /api/v1/categories/`
Creates a new category. The name must be unique.

**Request Payload:**
```json
{
  "name": "Strategy",
  "description": "Tactical planning and decision making."
}
```
**Response (201 Created):**
```json
{
  "id": 3,
  "name": "Strategy",
  "description": "Tactical planning and decision making.",
  "created_at": "2026-09-28T11:00:00Z",
  "updated_at": "2026-09-28T11:00:00Z",
  "games_count": 0
}
```

### `GET /api/v1/categories/{id}`
Retrieves a single category by ID. Returns `404 Not Found` if missing.

### `PUT /api/v1/categories/{id}`
Updates category fields.

**Request Payload:**
```json
{
  "name": "Turn-Based Strategy",
  "description": "Tactical strategy with discrete turn phases."
}
```

### `DELETE /api/v1/categories/{id}`
Deletes the category. Automatically triggers a database `CASCADE` delete on all its associated games. Returns `204 No Content`.

---

## 3. Video Games Resource (`/api/v1/games`)

### `GET /api/v1/games/`
Queries video games with multi-criteria filtering and pagination.

**Supported Query Parameters:**
| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `page` | `integer` | `1` | Page number (&ge; 1) |
| `page_size` | `integer` | `10` | Number of items per page (1 to 100) |
| `category_id` | `integer` | `None` | Filter by relational Category foreign key |
| `search` | `string` | `None` | Case-insensitive search on title or description |
| `min_rating` | `float` | `None` | Filter by minimum rating (0.0 to 10.0) |
| `max_price` | `float` | `None` | Filter by maximum retail price |
| `is_active` | `boolean` | `None` | Filter by catalog availability status |

**Response (200 OK):**
```json
{
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1,
  "items": [
    {
      "id": 1,
      "title": "Elden Ring",
      "description": "Rise, Tarnished, and be guided by grace to brandish the power of the Elden Ring.",
      "price": 59.99,
      "release_year": 2022,
      "rating": 9.6,
      "is_active": true,
      "image_url": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1245620/header.jpg",
      "steam_app_id": 1245620,
      "category_id": 2,
      "created_at": "2026-09-28T10:47:55Z",
      "updated_at": "2026-09-28T10:47:55Z",
      "category": {
        "id": 2,
        "name": "Role-Playing (RPG)",
        "description": "Games emphasizing narrative choices and character progression."
      }
    }
  ]
}
```

### `POST /api/v1/games/`
Creates a new game record linked to an existing Category.

**Request Payload:**
```json
{
  "title": "Cyberpunk 2077",
  "description": "An open-world, action-adventure story set in Night City.",
  "price": 59.99,
  "release_year": 2020,
  "rating": 8.7,
  "steam_app_id": 1091500,
  "category_id": 2,
  "is_active": true
}
```
**Response (201 Created):** Returns the created game object with populated relational category. Returns `400 Bad Request` if `category_id` does not exist.

### `GET /api/v1/games/{id}`
Retrieves a single game by ID, including its joined relational category details.

### `PUT /api/v1/games/{id}`
Updates game details and/or category assignment.

### `DELETE /api/v1/games/{id}`
Deletes a game by ID. Returns `204 No Content`.
