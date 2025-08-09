FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ./pyproject.toml               /app/pyproject.toml
COPY ./uv.lock                      /app/uv.lock
COPY ./README.md                    /app/README.md
COPY ./src/finnikacc/__init__.py    /app/src/finnikacc/__init__.py

COPY ./packages/finnikacc-api/pyproject.toml    /app/packages/finnikacc-api/pyproject.toml
COPY ./packages/finnikacc-api/README.md         /app/packages/finnikacc-api/README.md
COPY ./packages/finnikacc-api/src/finnikacc_api/__init__.py /app/packages/finnikacc-api/src/finnikacc_api/__init__.py

WORKDIR /app

RUN uv sync --frozen --no-cache

WORKDIR /app/packages/finnikacc-api

# CMD ["uv", "run", "uvicorn", "finnikacc_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
