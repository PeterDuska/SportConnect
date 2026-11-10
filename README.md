# WTaM

FastAPI + Vue 3 + TypeScript starter with registration, login, logout, and a protected workspace. Registration signs you in automatically. SQLite stores accounts and revocable seven-day sessions; passwords use Argon2. Cookies are HTTP-only and requests use CSRF protection. No tokens are stored in localStorage.

## Development

Run these in two terminals from the repository root:

```powershell
cd backend
uv sync --cache-dir ../.cache/uv
uv run --cache-dir ../.cache/uv uvicorn main:app --reload
```

```powershell
cd frontend
npm install --cache ../.cache/npm
npm run dev
```

Open http://localhost:5173. API documentation: http://127.0.0.1:8000/docs. Vite proxies `/api` to FastAPI, keeping browser requests same-origin.

## Checks

Backend: `cd backend` then `uv run --cache-dir ../.cache/uv pytest`.

Frontend: `cd frontend` then `npm run build`.

## Deployment notes

Build the frontend before starting FastAPI; FastAPI serves `frontend/dist` when present. Use HTTPS and set `COOKIE_SECURE=true`. This starter creates tables automatically; add Alembic migrations as the schema evolves. Authentication endpoints still need deployment-level rate limiting. Email verification and password recovery are not included.

## Matchday UI prototype

After signing in, the workspace offers Matches, My picks, Communities, and Rankings. On mobile the main navigation stays at the bottom. Select a match, enter a final score and save it; picks can be edited until the sample kickoff time. Tap a match to open the score form and sample community member predictions with toggleable like/dislike reactions.

Fixtures, community views, and standings are illustrative frontend data. Picks, reactions, and newly created preview communities exist only in memory and reset on reload; backend prediction storage, results, scoring, invitations, and membership management are not implemented.

The prototype is football-only. Matches switches between Upcoming and Closed fixtures; My picks filters saved predictions by upcoming or closed kickoff. Both views can filter by league or team using the Filters control. Mobile uses a compact profile control and labeled bottom navigation.

Community detail includes preview members, rankings, and match-selectable predictions. Match details let you choose a community; your own prediction appears across communities. Creating a community opens its invite preview; entering a name only adds a temporary preview member and sends no invitation. Profile statistics show the current preview prediction count; scoring and rank are not connected.

The prototype also includes screens for example scoring rules, event attendance, competition creation, community privacy and membership management, and administration of fixtures, results, accounts, and issues. These are design previews: changes are temporary, no attendance or invitations are sent, and administration does not modify real data. Scoring and tie-break rules remain undecided.
