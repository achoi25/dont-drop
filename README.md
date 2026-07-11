# dont-drop
don't drop !<br>
Help is available<br>
Speak with someone today<br>
988 Suicide and Crisis Lifeline

## setup

install dependencies via the nix dev shell:

```sh
nix develop
```

install the git hooks (one-time, per clone):

```sh
scripts/install-hooks.sh
```

## running

**backend** (from `backend/`):

```sh
cd backend
uv sync
uv run uvicorn src.main:app --reload
```

the first startup will download the embedding model (~80MB) into `backend/.model_cache/`. subsequent starts are instant.

**frontend** (from `frontend/`):

```sh
cd frontend
npm install
npm run dev
```

open `http://localhost:5173` in your browser. the backend must be running at `http://localhost:8000`.

## architecture

```
backend/   FastAPI + sentence-transformers (semantic similarity)
frontend/  SvelteKit
```

person data lives in `backend/PERSON.json` — swap it out to change who you're trying to save.
