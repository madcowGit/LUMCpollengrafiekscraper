
# LUMC Pollen Flask API

A minimal Flask web server that exposes the LUMC pollen data as a simple HTTP API and serves links/images to the historical graphs. It is a container-ready rewrite of your original script.

## Endpoints

- `GET /health` → health probe.
- `GET /pollen` → JSON array with all pollen rows: `{ name, columns, total }`.
- `GET /pollen/<name>/total` → `{ name, total }` for a given pollen name.
- `GET /pollen/<name>/history/url` → `{ name, url }` direct PNG graph URL.
- `GET /pollen/<name>/history/image` → streams the PNG image.

Name matching is case-insensitive.

## Local run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export FLASK_ENV=development
python app.py
# Then open http://localhost:8000/health
```

## Docker build & run

```bash
docker build -t lumc-pollen:local .
docker run --rm -p 8000:8000 lumc-pollen:local
```

## Configuration

- `LUMC_BASE_URL` (optional): Override the upstream base URL. Default: `https://sec.lumc.nl/pollenwebextern/`.
- `PORT` (optional): Port for the development server (`python app.py`). The container uses Gunicorn on port `8000`.

## GitHub Actions: build & publish to GHCR

This repo includes a workflow at `.github/workflows/docker-publish.yml` to automatically build and push the image to GitHub Container Registry (GHCR) on each push to `main` and on tag events.

**Prerequisites:**
- Make sure your repository visibility and package settings allow GHCR publishes.
- No extra secrets are required: the built-in `GITHUB_TOKEN` is used for `ghcr.io`.

After a successful run, the image will be available at:
`ghcr.io/<OWNER>/<REPO>:latest` and `ghcr.io/<OWNER>/<REPO>:<sha>`.

## Notes

- The upstream site structure can change. This scraper uses simple heuristics similar to the original script, so consider adding monitoring/logging.
- The server keeps an in-memory cache (15 minutes) to avoid hitting the upstream too often.
