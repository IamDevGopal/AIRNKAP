# AIRNKAP

## Dev Tooling

This project is configured with:
- `ruff` for linting and formatting
- `mypy` for static type checks
- `pytest` for tests
- `pre-commit` for local quality gates

## Setup

```powershell
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
pre-commit install
```

## Run Checks

```powershell
ruff check .
ruff format .
mypy
pytest
pre-commit run --all-files
```

> Note: current `mypy` config runs on both `app/` and `tests/` from `pyproject.toml`.
