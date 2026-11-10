# WTaM project context

The user is experienced with Laravel and Vue and is exploring Python backend development. Keep solutions simple and explanations practical.

## Stack and commands

- Backend: Python 3.11+, FastAPI, SQLAlchemy, SQLite, pwdlib/Argon2. Dependencies: uv, `backend/uv.lock`.
- Frontend: Vue 3 Composition API, TypeScript, Vite. Dependencies: npm, `frontend/package-lock.json`.
- Backend dev: from `backend`, `uv run --cache-dir ../.cache/uv uvicorn main:app --reload`.
- Frontend dev: from `frontend`, `npm run dev`. Vite proxies `/api` to `http://127.0.0.1:8000`.
- Backend tests: from `backend`, `.\.venv\Scripts\python.exe -m pytest -q`.
- Frontend build/type check: from `frontend`, `npm run build`.
- Use workspace-local `.cache/uv` and `.cache/npm` for installs. Windows may restrict network access. Plain uvicorn avoids optional C++ build dependencies on Windows ARM.

## Design preferences explicitly requested by the user

- Very minimal, mobile-first UI inspired by the user's white, cool-gray, blue/violet UI-kit reference.
- Maintain palette variables in `frontend/src/style.css`: white surfaces `#FFFFFF`, cool-gray background `#EDF1F4`, dark ink `#252B3A`, muted text `#626B7B`, blue `#2587ED`, violet `#4934ED`. Use darker accent `#4437D9` for small accent text.
- Rounded white surfaces, generous whitespace, system sans-serif typography, subtle separators, and restrained shadows. Limit gradients to primary actions and the small brand mark.
- Keep screen copy short. Matches use a shared white list, with venue and guidance on the match prediction screen. Preview disclosure remains available on the profile screen.
- Narrow authentication form. Mobile: 16px inputs, 44px minimum touch targets, natural vertical scrolling, safe-area padding. Preserve visible labels, keyboard focus, and reduced-motion support.
- Apply the same visual language to authentication and the workspace.

## Authentication

- `backend/main.py`: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`, `/api/auth/logout`.
- Registration signs in automatically; `/me` restores sessions after reload. Workspace access requires authentication.
- Argon2 password hashing, random seven-day sessions in HTTP-only cookies, hashed session tokens in the database. Never store auth tokens in localStorage.
- Preserve `X-Requested-With: WTaM` for mutations and `X-CSRF-Token` for authenticated mutations. Cross-origin API access is disabled.
- Deployment: HTTPS and `COOKIE_SECURE=true`. Rate limiting, email verification, password recovery, and Alembic migrations are not implemented.
- FastAPI serves `frontend/dist` when present at startup; rebuild frontend changes when using that mode.
- Keep secrets, databases, caches, environments, dependencies, and build output out of version control.

## Continuity

- Preserve auth behavior during visual changes. Build after frontend edits; run auth tests after backend edits.
- Update this file as lasting project decisions change; keep setup instructions in README.md.

## Matchday prototype

- Authenticated workspace uses Matches, My picks, Communities, and Rankings, with bottom navigation on mobile.
- Predictions have their own match screen with one-step exact-score saving and sample community member picks with mutually exclusive like/dislike reactions scoped to the community and match; sample kickoff closes editing.
- Fixtures, standings, communities, and predictions are currently frontend preview data. In-memory picks and reactions reset on reload; keep the preview disclosure available on the profile screen until backend integration.


- Scope is football only. No sport selector or non-football fixtures. Matches filters Upcoming/Closed; My picks filters saved predictions into Upcoming and Closed by kickoff. Both lists support league and team filters behind a Filters control.
- The signed-in view has no brand/title header. Start with page controls; Profile is the rightmost bottom navigation item and opens account details, sign-out, and preview information. Mobile uses an inset bottom navigation bar with labeled line icons; preserve safe-area spacing.

- Groups has no visible heading and has a top-right plus button that opens a separate community creation screen. Creating a preview community opens its detail screen with an invite preview. Group detail has members, rankings, and match-selectable picks; match detail selects a community and shows its members. Your prediction appears across your communities. Invitations are not sent.

- Additional mobile-first preview screens cover scoring rules, matchday attendance, group competition creation, privacy and membership management, and administration of fixtures, results, accounts and issues. These do not implement backend operations or authorization; keep their preview labels explicit. Example scoring is not a decided rule.
