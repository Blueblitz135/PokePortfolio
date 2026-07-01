# Pokemon Portfolio

Initial full-stack scaffold for a Pokemon portfolio investment app.

## Prerequisites

- Python 3.11 or newer
- Node.js 20.19 or newer
- npm 10 or newer

PostgreSQL is supported through `DATABASE_URL`. Local development defaults to a
SQLite database, so PostgreSQL is not required to run this initial scaffold.

## Run the backend

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The API runs at <http://localhost:8000>. Verify it with:

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

To use PostgreSQL, set `DATABASE_URL` in `backend/.env`, for example:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/pokemon_portfolio
```

## Run the frontend

In a second terminal, from the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. The Vite development server proxies `/api`
requests to the backend at port 8000.

## Checks

```powershell
cd backend
pytest
```

```powershell
cd frontend
npm run lint
npm run build
```

## Current scope

This setup ticket includes the FastAPI and React application shells, database
configuration, and a health endpoint. Portfolio models and product features are
implemented in later tickets.
