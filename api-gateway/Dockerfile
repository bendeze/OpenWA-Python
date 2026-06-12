FROM docker:cli AS docker-cli
FROM ghcr.io/astral-sh/uv:latest AS uv

FROM python:3.11-slim

WORKDIR /app

# 1. Copy the Docker CLI and uv package manager directly (No apt-get required!)
COPY --from=docker-cli /usr/local/bin/docker /usr/local/bin/
COPY --from=uv /uv /uvx /bin/

# 2. Download the Docker Compose plugin
RUN apt-get update && apt-get install -y curl \
    && mkdir -p /usr/local/lib/docker/cli-plugins \
    && curl -SL https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose \
    && chmod +x /usr/local/lib/docker/cli-plugins/docker-compose \
    && apt-get remove -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# 3. Use uv for blazing fast Python installations
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

COPY . .

# Expose port
EXPOSE 8000

# Start FastAPI application
CMD ["uvicorn", "main:socket_app", "--host", "0.0.0.0", "--port", "8000"]
