# PokePortfolio

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

Create the database tables after configuring `backend/.env`:

```powershell
python -m app.db.create_tables
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

The frontend uses client-side routes such as `/collection`, `/search`, and
`/settings`. Vite development and preview servers provide the required SPA
fallback. A future static host must rewrite unknown non-file routes to
`/index.html` while leaving `/api`, `/static`, `/uploads`, and real asset files
untouched.

## Configure the portfolio assistant

The collection page includes an AI portfolio analyst backed by the server-side
OpenAI Responses API. Before using it, replace the placeholder values in
`backend/.env` for `OPENAI_API_KEY` and `JUSTTCG_API_KEY`.
Set `JUSTTCG_USD_TO_CAD_RATE` to a current positive conversion rate. Both market
estimates and TCGPlayer reference prices use this rate before calculations.

The collection automatically refreshes card prices, and a refresh button can
request another update. Current prices are saved as CAD snapshots and used for
unit price, quantity-based market value, unrealized profit/loss and ROI. Identical
provider observations are not saved twice. All cards are attempted with bounded
concurrency; no 20-holding cutoff is applied. Provider rate limits still apply.

JustTCG v1 supplies raw-card estimates/history; v2 beta supplies exact company/grade
variants where available. A matching variant may still have no price. Unknown or
ambiguous printings are reported rather than assigned another printing's price.
Sealed products retain saved prices. Failed refreshes preserve older saved prices
and are explicitly marked; no raw price is used to value a slab.

The analyst fetches both market evidence and TCGdex's `pricing.tcgplayer` data on
each question. TCGPlayer raw-card reference prices (market, low, median, high) are
also shown on card details. Cardmarket data is intentionally ignored. Supported
history windows are 7/30/90/180 days and one year; answers distinguish requested
windows from actual observation coverage and personal ROI from market growth.
Chat returns refreshed assets so dashboard metrics update without a second fetch.

User-facing attribution is "Marketplace and verified store sales" for the blended
estimate and "TCGPlayer" for the reference. See [market source documentation](https://justtcg.com/features),
[graded coverage](https://justtcg.com/docs/api/cards-v2/graded), and
[TCGPlayer fields](https://tcgdex.dev/reference/card#tcgplayer-pricing).

## Checks

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

```powershell
cd frontend
npm test
npm run lint
npx tsc -b
npm run build
```

`npm test` runs the frontend unit and component tests once. Use `npm run
test:watch` while developing frontend changes.

## Current scope

This setup ticket includes the FastAPI and React application shells, database
configuration, and a health endpoint. Portfolio models and product features are
implemented in later tickets.
