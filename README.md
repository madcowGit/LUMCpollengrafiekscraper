
# LUMC Pollen Flask API

A minimal Flask web server that scrapes the LUMC pollen data and exposes it as a simple HTTP API and serves links/images to the historical graphs. 
The server keeps an in-memory cache (15 minutes) to avoid hitting the upstream too often.

## Endpoints

- `GET /health` → health probe.
- `GET /pollen` → JSON array with all pollen rows: `{ name, columns, total }`.
- `GET /pollen/<name>/total` → `{ name, total }` for a given pollen name.
- `GET /pollen/<name>/history/url` → `{ name, url }` direct PNG graph URL.
- `GET /pollen/<name>/history/image` → streams the PNG image.

Name matching is case-insensitive.

# Install

## Local run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export FLASK_ENV=development
python app.py
# Then open http://localhost:8000/health
```

## Docker compose

```
version: "3.9"
services:
 lumcpollengrafiekscraper:
  image: ghcr.io/madcowgit/lumcpollengrafiekscraper:main
  ports:
    - "8001:8000"
  environment:
    LUMC_BASE_URL: "https://sec.lumc.nl/pollenwebextern/"
    PORT: "8000"
  restart: always    
```

## Configuration

- `LUMC_BASE_URL` (optional): Override the upstream base URL. Default: `https://sec.lumc.nl/pollenwebextern/`.
- `PORT` (optional): Port for the development server (`python app.py`). The container uses Gunicorn on port `8000`.


