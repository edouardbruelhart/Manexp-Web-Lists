FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --locked --no-install-project

RUN uv run playwright install --with-deps chromium

COPY manexp_web_lists ./manexp_web_lists

CMD ["uv", "run", "manexp_web_lists/run.py"]
