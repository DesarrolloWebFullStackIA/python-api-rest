#!/usr/bin/env bash
# ==============================================================================
# VaporStore REST API - Quick Start Script for Linux & macOS
# ==============================================================================

set -e

# Terminal colors
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}${BOLD}======================================================================${NC}"
echo -e "${BLUE}${BOLD}          VaporStore Video Game REST API - Quick Start                ${NC}"
echo -e "${BLUE}${BOLD}======================================================================${NC}"
echo ""

# 1. Determine Python binary
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}[ERROR] Python was not found in your PATH.${NC}"
    echo "Please install Python 3.10+ from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo -e "${GREEN}[OK] Detected: ${PYTHON_VERSION}${NC}"

# 2. Check or create virtual environment
if [ ! -f ".venv/bin/python" ]; then
    echo -e "${YELLOW}[INFO] Virtual environment not detected. Creating .venv...${NC}"
    $PYTHON_CMD -m venv .venv
    echo -e "${GREEN}[OK] Virtual environment created.${NC}"
fi

# 3. Activate virtual environment
# shellcheck source=/dev/null
source .venv/bin/activate

# 4. Verify/Install dependencies
echo -e "${YELLOW}[INFO] Verifying Python dependencies...${NC}"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo -e "${GREEN}[OK] Dependencies are up to date.${NC}"

# 5. Ensure .env exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}[INFO] .env not found. Copying .env.example to .env...${NC}"
        cp .env.example .env
        echo -e "${GREEN}[OK] Created .env configuration.${NC}"
    fi
fi

echo ""
echo -e "${BLUE}${BOLD}======================================================================${NC}"
echo -e "${GREEN}${BOLD}  VaporStore API Server is starting!${NC}"
echo ""
echo -e "  * ${BOLD}Web Client UI:${NC}   http://127.0.0.1:8000/client/"
echo -e "  * ${BOLD}Swagger UI Docs:${NC} http://127.0.0.1:8000/docs"
echo -e "  * ${BOLD}ReDoc Specs:${NC}     http://127.0.0.1:8000/redoc"
echo -e "  * ${BOLD}Health Check:${NC}    http://127.0.0.1:8000/api/v1/health"
echo ""
echo -e "  Press ${YELLOW}CTRL+C${NC} in this terminal to stop the server at any time."
echo -e "${BLUE}${BOLD}======================================================================${NC}"
echo ""

# 6. Attempt to open browser in background
CLIENT_URL="http://127.0.0.1:8000/client/"
if command -v xdg-open &>/dev/null; then
    (sleep 1.5 && xdg-open "$CLIENT_URL") &>/dev/null &
elif command -v open &>/dev/null; then
    (sleep 1.5 && open "$CLIENT_URL") &>/dev/null &
fi

# 7. Start Uvicorn development server
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
