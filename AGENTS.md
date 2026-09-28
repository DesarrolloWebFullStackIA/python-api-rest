# Project Guidelines & Rules

## 1. Language & Naming Invariants
- **Code & Variables**: All variables, functions, classes, database columns, filenames, and internal identifiers MUST be named in English using standard Python conventions (snake_case for functions/variables, PascalCase for classes).
- **Docstrings & Comments**: All docstrings, inline comments, and module descriptions MUST be written in English.
- **Git Commits**: All commit messages MUST be written in English following Conventional Commits format (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
- **GitHub & Agile Artifacts**: Any GitHub issues, backlog cards, task descriptions, and pull request descriptions MUST be written in English.
- **Documentation**: `README.md`, API specification notes, and architectural docs MUST be written in English.

## 2. Technical & Architectural Standards
- **Backend Framework**: FastAPI (modern asynchronous/typed patterns, dependency injection).
- **ORM & Validation**: SQLAlchemy 2.0+ declarative models and Pydantic v2 schemas (`from_attributes = True`).
- **Relational Integrity**: Foreign keys, cascades, relationships, and index definitions must be explicitly configured.
- **Error Handling & HTTP Semantics**: Return semantic HTTP codes (`200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `404 Not Found`, `422 Unprocessable Entity`, `500 Internal Server Error`). All database operations must handle rollbacks upon exceptions.
- **Code Style**: Strictly follow PEP 8 and clean architecture boundaries (separation of routes, services, models, schemas, and database session lifecycle).
- **Testing**: Maintain unit and integration tests using `pytest` and `TestClient`.
