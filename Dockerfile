FROM ghcr.io/astral-sh/uv:debian AS base

COPY . /app
WORKDIR /app

FROM base AS prod-deps
RUN uv sync --frozen --no-cache --no-dev

FROM base
COPY --from=prod-deps /app/.venv /app/.venv

CMD ["uv", "run", "src/app.py"]
