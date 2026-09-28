# Architecture & Design

This document details the architectural principles, design patterns, and structural decisions implemented in the **VaporStore** REST API.

---

## Clean Architecture & Layered Structure

The project strictly follows Clean Architecture separation of concerns, decoupling transport/HTTP logic, business domain services, database persistence, and data validation:

```text
                  +--------------------------------+
                  |         HTTP Request           |
                  +--------------------------------+
                                  |
                                  v
                  +--------------------------------+
                  |         Routes Layer           |  (FastAPI Routers, HTTP semantics,
                  |      (backend/app/routes)      |   status codes, dependency injection)
                  +--------------------------------+
                                  |
                                  v
                  +--------------------------------+
                  |        Services Layer          |  (Business logic, transactional DB
                  |     (backend/app/services)     |   commit/rollback, Steam HTTP client)
                  +--------------------------------+
                                  |
                   +--------------+--------------+
                   |                             |
                   v                             v
+------------------------------------+  +------------------------------------+
|            Schemas Layer           |  |            Models Layer            |
|       (backend/app/schemas)        |  |        (backend/app/models)        |
| (Pydantic v2 input/output schemas, |  | (SQLAlchemy 2.0 ORM Declarative,   |
|     validation, from_attributes)   |  |   Foreign Keys, Cascade, Indexes)  |
+------------------------------------+  +------------------------------------+
                   |                             |
                   +--------------+--------------+
                                  |
                                  v
                  +--------------------------------+
                  |         Database Engine        |  (SessionLocal, Engine, SQLite/
                  |     (backend/app/database)     |   PostgreSQL, Connection Pooling)
                  +--------------------------------+
```

---

## Core Components

### 1. Application Lifespan (`backend/app/main.py`)
FastAPI's modern `@asynccontextmanager` pattern manages startup and shutdown routines:
- **Startup**:
  - Automatically executes `Base.metadata.create_all(bind=engine)` to ensure database tables are created.
  - Automatically seeds 5 initial categories (`Action`, `Role-Playing (RPG)`, `Strategy`, `Adventure`, `Indie`) if the database is newly initialized.
- **Shutdown**:
  - Ensures clean teardown of database connections and background tasks.

### 2. Dependency Injection (`get_db`)
Database sessions are managed using Python generators injected into route handlers via FastAPI `Depends(get_db)`:
```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
This guarantees that:
- Every HTTP request receives an isolated database session.
- Database connections are guaranteed to close upon request completion, preventing connection leaks.

### 3. Centralized Settings (`backend/app/config/settings.py`)
Application configuration uses Pydantic's `BaseSettings` (`pydantic-settings`):
- Reads strongly-typed variables from `.env`.
- Supports environment switching (`development`, `testing`, `production`).
- Dynamically parses comma-separated CORS origins into lists.

### 4. Transactional Integrity & Rollbacks
All database write operations within `CategoryService` and `GameService` are wrapped in `try/except` blocks:
```python
try:
    db.add(entity)
    db.commit()
    db.refresh(entity)
except Exception:
    db.rollback()
    raise HTTPException(status_code=500, detail="Database operation failed.")
```
This guarantees that failed transactions never leave the database in an inconsistent or locked state.

### 5. Static Files Mounting
The client web application is delivered directly through FastAPI:
```python
frontend_path = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_path.is_dir():
    app.mount("/client", StaticFiles(directory=str(frontend_path), html=True), name="client")
```
When accessing `http://127.0.0.1:8000/client/`, the client is served on the same origin, eliminating cross-origin complications during evaluation.
