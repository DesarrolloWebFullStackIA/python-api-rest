# Welcome to the VaporStore Wiki

Welcome to the official developer documentation and technical wiki for **VaporStore**, a production-grade relational REST API developed in **FastAPI** with **SQLAlchemy 2.0**, **Pydantic v2**, and an integrated **Axios client application**.

---

## 🧭 Navigation & Documentation Guide

Use the sidebar or the index below to explore each area of the system architecture:

| Section | Description |
| :--- | :--- |
| [[Architecture-&-Design]] | High-level system architecture, Clean Architecture layers, lifespan, and dependency injection. |
| [[Database-&-ERD]] | Relational Entity-Relationship Diagram (1:N), SQLAlchemy models, migrations, and cascading integrity. |
| [[REST-API-Specification]] | Comprehensive endpoint specifications, request/response JSON schemas, query filters, and pagination. |
| [[Steam-API-Integration]] | Architecture of the public Steam Store & Web API integration (search, 1-click import, live player stats). |
| [[Frontend-Client]] | Client web portal architecture (HTML5 semantic markup, modern CSS3 dark theme, Axios instance, modal flows). |
| [[Testing-&-QA]] | Pytest automated test suite, in-memory SQLite fixtures, mocking patterns, and 23/23 passing test matrix. |
| [[Deployment-&-Getting-Started]] | Local installation, `.env` configuration, `start.bat` & `start.sh` quick start scripts, and production guidelines. |

---

## 🎯 Project Overview & Business Context

**VaporStore** was developed for **TechSolutions** to demonstrate a modern, scalable digital catalog service. The chosen business domain connects **Video Games** with **Categories** in a strict **1:N Relational Model**:
- A Category can classify multiple Video Games.
- Each Video Game belongs to exactly one Category.
- Deleting a Category automatically cascades and deletes all associated Games from the database (`ON DELETE CASCADE`), ensuring database referential integrity.

---

## ⚡ Quick Access Links

- **Web Client Application**: [http://127.0.0.1:8000/client/](http://127.0.0.1:8000/client/)
- **Interactive OpenAPI Documentation (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc Specification**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check Endpoint**: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)
