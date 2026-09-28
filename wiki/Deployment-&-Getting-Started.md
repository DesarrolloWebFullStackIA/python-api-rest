# Deployment & Getting Started

This guide covers local environment initialization, automated quick-start scripts, configuration options, and production deployment recommendations for **VaporStore**.

---

## ⚡ 1-Click Quick Start

The repository includes pre-configured automation scripts that create the virtual environment, install requirements, set up configuration, launch the server, and open your browser automatically:

### Windows
Double-click `start.bat` or run in terminal:
```cmd
start.bat
```

### Linux & macOS
Run in terminal:
```bash
chmod +x start.sh
./start.sh
```

---

## Manual Installation Guide

### 1. Clone Repository
```bash
git clone https://github.com/DesarrolloWebFullStackIA/python-api-rest.git
cd python-api-rest
```

### 2. Virtual Environment
- **Windows**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **Linux / macOS**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
```bash
cp .env.example .env
```

### 5. Run Server
```bash
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

---

## Environment Variables Reference

| Variable | Type | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `APP_NAME` | `str` | `Video Games API` | Service name in OpenAPI docs |
| `APP_VERSION` | `str` | `1.0.0` | Application semantic version |
| `ENVIRONMENT` | `str` | `development` | `development` / `production` |
| `DEBUG` | `bool` | `True` | Enable/disable debug traces |
| `DATABASE_URL` | `str` | `sqlite:///./games.db` | SQLAlchemy connection URI |
| `CORS_ORIGINS` | `str` | `*` | Allowed CORS origins (comma-separated) |

---

## Production Deployment Recommendations

For production deployments (e.g. AWS EC2, DigitalOcean, Render, or Railway):

1. **Database Migration to PostgreSQL**:
   Update `DATABASE_URL` in `.env`:
   ```text
   DATABASE_URL=postgresql+psycopg2://user:password@host:5432/vaporstore_db
   ```
   Install PostgreSQL driver: `pip install psycopg2-binary`.

2. **Gunicorn Process Manager**:
   Run multiple worker processes behind Gunicorn with Uvicorn workers:
   ```bash
   gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

3. **CORS Lockdown**:
   Set `CORS_ORIGINS` to your production domain:
   ```text
   CORS_ORIGINS=https://vaporstore.yourdomain.com
   ```

---

## How to Sync this Wiki to GitHub

GitHub Wikis are Git repositories. To publish this `wiki/` directory to your GitHub Wiki:

1. Enable the **Wiki** tab in your repository settings on GitHub if not already enabled.
2. Clone your repository's wiki:
   ```bash
   git clone https://github.com/DesarrolloWebFullStackIA/python-api-rest.wiki.git
   ```
3. Copy all markdown files from `wiki/` into the cloned wiki directory:
   - On Windows:
     ```cmd
     xcopy /Y /S wiki\* python-api-rest.wiki\
     ```
   - On Linux / macOS:
     ```bash
     cp -r wiki/* python-api-rest.wiki/
     ```
4. Commit and push the wiki repository:
   ```bash
   cd python-api-rest.wiki
   git add .
   git commit -m "docs(wiki): publish complete documentation suite"
   git push origin master
   ```
