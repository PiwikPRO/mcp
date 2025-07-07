FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock* .
COPY README.md .

COPY src ./src

# Create a least-privileged user and group, and give ownership of the app directory
RUN groupadd -r app && useradd -r -g app -u 10001 -m app && chown -R app:app /app

# Switch to non-root user for install and runtime
USER app

ENV PATH="/home/app/.local/bin:$PATH"
# Install uv as regular user so it's under /home/app/.local/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

RUN uv sync --frozen --no-dev


CMD ["uv", "run", "--no-dev", "--frozen", "--no-sync", "python", "-m", "piwik_pro_mcp.server"]