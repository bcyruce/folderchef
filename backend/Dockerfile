# ============================================================
# FolderChef Backend -- Docker Image
# ============================================================
# Used by Railway for deployment. Supports two run modes:
#
#   WEB SERVER (default):
#     docker run -p 8000:8000 folderchef-backend
#
#   SCRAPER CLI:
#     docker run folderchef-backend python -m app.cli scrape --week 6 --year 2026
#
# ============================================================

FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr (see logs in real time)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default: run the web server
# Override CMD for the cron service to run the CLI instead
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
