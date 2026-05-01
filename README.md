# AI-native-portfolio

Working implementation: **Clinical Prior Authorization Copilot**.

## Run API
```bash
make bootstrap
make install-runtime
make run
```

## Run worker (separate process)
```bash
make worker
```

## Test
```bash
pytest -q
```

## Environment
- `DATABASE_URL` (default: sqlite:///./app.db)
- `S3_BUCKET` (optional, if set uses AWS S3 via boto3)
- `LLM_PROVIDER` (`openai` | `anthropic` | `none`)
- `OPENAI_API_KEY`, `OPENAI_MODEL`
- `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`

## Implemented
- REST API: create case, enqueue draft generation, fetch case.
- GraphQL query endpoint for case retrieval.
- Queue/job table + separate worker loop.
- SQLModel persistence (SQLite default; Postgres via `DATABASE_URL`).
- S3-backed storage option with local fallback.
- LLM-backed drafting with deterministic fallback if provider not configured.


## Install targets
- `pip install -e .[dev]` is the offline-safe editable install path.
- `make install-runtime` installs full runtime dependencies with `--no-build-isolation` when package-index access is available.
- If your environment blocks package index access entirely, configure an internal mirror (`PIP_INDEX_URL`) or pre-populate a wheelhouse before running `make install-runtime`.


## Why `pip install -e .[dev]` fails here
- Pip defaults to build isolation for editable installs and tries to create an isolated build env.
- That bootstrap step fetches `setuptools` from the configured index/proxy.
- In this environment, the proxy/index is blocked, so bootstrap fails before dependency resolution.

## Code-level fix included
- Use `scripts/bootstrap_env.sh` (or `make bootstrap`) which runs `pip install --no-build-isolation -e .[dev]` to bypass isolated build bootstrap.
