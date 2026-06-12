FROM python:3.11-slim

WORKDIR /app

# Install docker CLI for orchestration and other dependencies
RUN apt-get update && apt-get install -y \
    curl \
    docker.io \
    docker-compose-v2 \
    bash \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port
EXPOSE 8000

# Start FastAPI application
CMD ["uvicorn", "main:socket_app", "--host", "0.0.0.0", "--port", "8000"]
