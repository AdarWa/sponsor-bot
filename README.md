# Sponsor Bot starter

A minimal FastAPI + Vue starter project with built-in authentication powered by [`fastapi-users`](https://fastapi-users.github.io/fastapi-users/).

## Backend

Located in `backend/`, the API exposes JWT authentication routes (register/login) via `fastapi-users` and a `/api/me` profile route protected by the JWT dependency.

### Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Env vars (see `backend/app/config.py`) can be overridden with a `.env` file.

#### Azure Database for PostgreSQL

You can connect to Azure Database for PostgreSQL either by providing a `DATABASE_URL` (e.g. `postgresql+asyncpg://...@...postgres.database.azure.com/db?sslmode=require`) or by setting the split credentials below:

```bash
export AZURE_PG_HOST=myserver.postgres.database.azure.com:5432
export AZURE_PG_USER=myadmin
export AZURE_PG_PASSWORD='strong-password'
export AZURE_PG_DATABASE=sponsorbot
# Optional: point to the DigiCert CA bundle provided by Azure
export AZURE_PG_SSL_CERT=/path/to/DigiCertGlobalRootCA.crt.pem
```

SSL is enforced by default; disable it only for local emulation with `AZURE_PG_REQUIRE_SSL=false`.

## Frontend

The Vue 3 app (Vite) lives in `frontend/` and provides a simple UI for registration/login/profile retrieval.

```bash
cd frontend
npm install
npm run dev # served at http://localhost:5173
```

For production, build the frontend (`npm run build`) and FastAPI will automatically serve files from `frontend/dist`.

## Development notes

- Default API base URL for the frontend is `http://localhost:8000`. Override via `VITE_API_BASE`.
- Vite dev server proxies `/api` calls to `localhost:8000`.
- Authentication relies wholly on `fastapi-users` so token refresh/reset flows can be extended through that library's routers.
