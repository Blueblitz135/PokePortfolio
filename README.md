# PokéPortfolio

<<<<<<< HEAD
PokéPortfolio is a local, full-stack portfolio tracker for Pokémon cards and
sealed products. It records what you own, each purchase lot, current market
prices, and collection performance in CAD.

The application currently supports:

- Raw cards, graded cards, and sealed products as separate asset types
- Multiple purchase lots per asset, with purchase date, quantity, and unit cost
- Quantity, total cost, average cost, market value, profit/loss, and ROI
- TCGdex card search and images, with structured card and set numbers
- Manual sealed-product entry and upload-first product images
- JPEG, PNG, and WebP uploads up to 5 MB for sealed-product images; the backend
  image API supports every asset type
- Code-rendered grading labels over card images
- Manual market-price snapshots for every asset type
- JustTCG card-price refreshes and TCGPlayer reference prices normalized to CAD
- A portfolio assistant powered by the OpenAI Responses API
- A collection dashboard, asset filters, detail pages, and browser-local settings

This is currently a single-user MVP. It has no authentication, cloud sync,
alerts, scraping, eBay integration, advanced charts, or automatic sealed-product
pricing.

## Technology

- **Backend:** FastAPI, Pydantic, SQLAlchemy, SQLite by default, PostgreSQL-ready
- **Frontend:** React 19, TypeScript, Vite, React Router
- **Tests:** pytest and Vitest/Testing Library
- **External services:** TCGdex, optional JustTCG, and optional OpenAI
=======
A Pokemon investment portfolio manager.
>>>>>>> 43e2cd44a5b051809710c11b897a529abd02dcae

## Prerequisites

- Python 3.11 or newer
- Node.js 20.19 or newer
- npm 10 or newer

PostgreSQL is optional. The default configuration uses a local SQLite database.

## Quick start

### 1. Start the backend

From the repository root in PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -m app.db.create_tables
uvicorn app.main:app --reload
```

The backend runs at <http://localhost:8000>. Useful endpoints include:

- Health check: <http://localhost:8000/api/health>
- Interactive API documentation: <http://localhost:8000/docs>
- Alternative API documentation: <http://localhost:8000/redoc>

Verify the API from another PowerShell session:

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

Run database commands from the `backend` directory so the default SQLite file
and `.env` resolve consistently. `create_tables` creates missing tables; this
project does not currently include a migration workflow.

### 2. Start the frontend

In a second terminal, from the repository root:

```powershell
cd frontend
npm ci
npm run dev
```

Open <http://localhost:5173>. The Vite development server proxies `/api`,
`/static`, and `/uploads` to the backend at `http://localhost:8000`.

Set `BACKEND_PROXY_TARGET` before starting Vite if the backend uses another
address:

```powershell
$env:BACKEND_PROXY_TARGET = "http://localhost:9000"
npm run dev
```

## Configuration

Backend settings are read from environment variables and `backend/.env`. Start
with [`backend/.env.example`](backend/.env.example).

The app works without paid integrations: TCGdex search requires no key, and
manual market prices remain available. Replace placeholder API keys only for the
features you intend to enable.

| Setting | Purpose | Required |
| --- | --- | --- |
| `DATABASE_URL` | SQLAlchemy database URL; defaults to local SQLite | No |
| `UPLOAD_DIR` | Directory for user-uploaded images | No |
| `TCGDEX_BASE_URL` | Card metadata, images, and TCGPlayer reference endpoint | No |
| `TCGDEX_TIMEOUT_SECONDS` | TCGdex request timeout | No |
| `TCGDEX_SEARCH_LIMIT` | Maximum normalized card-search results | No |
| `JUSTTCG_API_KEY` | Enables automatic card market-price lookups | For JustTCG |
| `JUSTTCG_BASE_URL` | JustTCG API base URL | No |
| `JUSTTCG_TIMEOUT_SECONDS` | JustTCG request timeout | No |
| `JUSTTCG_USD_TO_CAD_RATE` | Positive USD-to-CAD rate used before storing JustTCG and TCGPlayer values | For external CAD prices |
| `OPENAI_API_KEY` | Enables the portfolio assistant | For assistant |
| `OPENAI_BASE_URL` | OpenAI-compatible Responses API base URL | No |
| `OPENAI_MODEL` | Model used by the assistant; defaults to `gpt-5-mini` | No |
| `OPENAI_TIMEOUT_SECONDS` | Assistant request timeout | No |
| `PORTFOLIO_CHAT_HISTORY_DURATION` | Default external price-history window | No |

The repository also contains an experimental PokeTrace adapter and related
settings. It is tested in isolation but is not connected to the current user
workflow or portfolio calculations.

To use PostgreSQL, install and start PostgreSQL, create a database, and set for
example:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/pokemon_portfolio
```

Then rerun `python -m app.db.create_tables` from `backend`.

## How pricing works

- All normalized purchase and market values are stored and displayed in CAD.
- The latest price snapshot supplies an asset's unit market price.
- Market value is unit market price multiplied by total quantity across lots.
- Profit/loss is market value minus total cost; ROI is profit/loss divided by
  total cost.
- Manual snapshots support raw cards, graded cards, and sealed products.
- Automatic refreshes attempt card assets through JustTCG and preserve the last
  saved price when a provider is unavailable or cannot find an exact match.
- Raw-card condition, graded-card company/grade, printing, and card identity are
  matched separately. A raw-card quote is never used to value a graded card.
- TCGPlayer values from TCGdex are shown as raw-card reference evidence, not as
  graded or condition-specific valuations.
- Repeated observations from JustTCG are not stored twice.

The collection page refreshes card prices after loading and also provides a
manual refresh button. Sealed products retain their latest manually entered
price.

## Main workflows

- **Collection:** review portfolio totals, filter by asset type, refresh card
  prices, open asset details, and ask the portfolio assistant questions.
- **Search:** find a card through TCGdex, choose raw or graded ownership details,
  review the data, and create the asset with its first purchase lot.
- **Sealed products:** create products manually, manage lots and prices, and
  upload a primary image.
- **Asset details:** inspect metadata and calculations; add, edit, or delete
  purchase lots; and record a market price. Card images currently come from
  TCGdex; card uploads are available through the API but not exposed in the UI.
- **Settings:** choose the default collection filter. Preferences are stored in
  the current browser only. CAD is the only selectable display currency.

## Data and local files

With the default configuration:

- Portfolio data is stored in `backend/pokemon_portfolio.db`.
- Uploaded images are stored in `backend/uploads/` and served from `/uploads`.
- Bundled placeholders are served from `/static`.
- Display preferences are stored in browser `localStorage` and do not sync.

Treat the database and uploads directory as a pair when backing up or moving a
collection. Do not commit `.env`, the SQLite database, uploaded images, or API
keys.

## Checks

Run backend tests from `backend` with the virtual environment installed:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Run frontend tests and quality checks from `frontend`:

```powershell
npm test
npm run lint
npx tsc -b
npm run build
```

`npm test` runs the frontend tests once. Use `npm run test:watch` during active
frontend development.

## Project structure

```text
backend/
  app/
    adapters/     External service clients
    api/routes/   Thin FastAPI route modules
    db/           Engine, sessions, and table creation
    models/       SQLAlchemy models and enums
    schemas/      Pydantic request and response models
    services/     Portfolio business logic
    tests/        Backend tests
frontend/
  src/
    api/          Backend API clients
    components/   Reusable UI components
    pages/        Route-level screens
    preferences/  Browser-local settings
    types/        Shared frontend types
    utils/        Formatting and payload helpers
docs/             Product, architecture, and ticket documentation
```

Additional design context is in [`docs/00_project_overview.md`](docs/00_project_overview.md),
and the API contract is documented in [`docs/03_api_contract.md`](docs/03_api_contract.md).

## Deployment notes

`npm run build` writes the frontend production bundle to `frontend/dist`. A
production deployment must serve that bundle, run FastAPI separately, route the
backend paths (`/api`, `/static`, and `/uploads`) correctly, and rewrite unknown
frontend routes to `index.html`. It should also use persistent storage for the
database and uploads.

## License

This project is available under the terms in [`LICENSE`](LICENSE).
