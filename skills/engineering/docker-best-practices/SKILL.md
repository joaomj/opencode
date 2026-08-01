---
name: docker-best-practices
description: Complete containerization guide covering Dockerfile patterns, Docker Compose, security, and networking
license: MIT
---

# Docker Best Practices

Comprehensive guide for containerization with focus on security, minimalism, and production readiness.

## Non-Negotiable Rules (STOP if violated)

Core rules defined in AGENTS.md. Docker-specific additions:

| Rule | Violation = STOP |
|------|-----------------|
| Dockerfile has non-root USER | Block if missing |
| Docker Compose has read_only | Block if missing |
| No privileged: true | Block if detected |
| No secrets in ENV | Block if detected |

## Dockerfile Best Practices

### Non-Root User (REQUIRED)
```dockerfile
# BAD - runs as root
FROM python:3.11
COPY . /app
CMD ["python", "app.py"]

# GOOD - runs as non-root
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install dependencies
COPY requirements.txt .
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python --no-cache -r requirements.txt

# Copy app and set permissions
COPY --chown=appuser:appuser . /app
WORKDIR /app

USER appuser
CMD ["uv", "run", "python", "app.py"]
```

### Minimal Layers
```dockerfile
# BAD - many unnecessary layers
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git
RUN apt-get clean

# GOOD - combined layers
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        git && \
    rm -rf /var/lib/apt/lists/*
```

### Multi-Stage Builds
```dockerfile
# Build stage
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python --no-cache -r requirements.txt

# Runtime stage
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser . /app
WORKDIR /app
ENV PATH=/opt/venv/bin:$PATH
USER appuser
CMD ["uv", "run", "python", "app.py"]
```

### Security Hardening
```dockerfile
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Install only necessary system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set security defaults
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy with proper ownership
COPY --chown=appuser:appuser . /app
WORKDIR /app

USER appuser
CMD ["uv", "run", "python", "app.py"]
```

## Docker Compose Best Practices

### Read-Only Filesystem (REQUIRED)
```yaml
services:
  app:
    image: myapp:latest
    read_only: true
    tmpfs:
      - /tmp
      - /var/run
    volumes:
      - ./data:/app/data:ro
```

### Minimal Permissions
```yaml
services:
  app:
    image: myapp:latest
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    security_opt:
      - no-new-privileges:true
```

### Resource Limits
```yaml
services:
  app:
    image: myapp:latest
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Secrets Management
```yaml
services:
  app:
    image: myapp:latest
    secrets:
      - db_password
      - api_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    file: ./secrets/api_key.txt
```

**IMPORTANT:** Never use `environment:` for secrets. Always use `secrets:`.

## Security Rules

### No Privileged Mode
```yaml
# BAD - privileged mode
services:
  app:
    image: myapp:latest
    privileged: true

# GOOD - least privilege
services:
  app:
    image: myapp:latest
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
```

### No Secrets in ENV
```yaml
# BAD - secrets in environment
services:
  app:
    image: myapp:latest
    environment:
      - DB_PASSWORD=secret123
      - API_KEY=abc123

# GOOD - use Docker secrets
services:
  app:
    image: myapp:latest
    secrets:
      - db_password
      - api_key
```

## Security Scanning

### Trivy Image Scanning
```dockerfile
# Scan base images before using them
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Run Trivy from CI or the operator workstation.
# trivy image --severity HIGH,CRITICAL ghcr.io/astral-sh/uv:python3.11-bookworm-slim
```

### CI/CD Security Scanning
Add Trivy to your GitHub workflow to scan container images:

Action references in examples are intentionally time-sensitive. Before using
an example, resolve current supported releases and pin each action to a release
or commit SHA. Do not copy an old action reference unchanged.

```yaml
  trivy:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - name: Scan container image
        uses: aquasecurity/trivy-action@<verified-release-or-sha>
        with:
          image-ref: myapp:latest
          format: sarif
          output: trivy-results.sarif
          severity: HIGH,CRITICAL
      - name: Upload results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@<verified-release-or-sha>
        with:
          sarif_file: trivy-results.sarif
```

## Network Isolation

### Separate Networks
```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No internet access

services:
  web:
    image: nginx:latest
    networks:
      - frontend

  app:
    image: myapp:latest
    networks:
      - frontend
      - backend

  db:
    image: postgres:15
    networks:
      - backend
```

### Internal Networks
```yaml
networks:
  backend:
    internal: true  # Blocks internet access
    driver: bridge

services:
  db:
    image: postgres:15
    networks:
      - backend
```

### Firewall Rules
```yaml
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    networks:
      - frontend
```

## Image Optimization

### Use Official Images
```dockerfile
# BAD - use a larger base image without the project package workflow
FROM python:3.11

# GOOD - use the official uv image and the project package workflow
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
```

### Caching
```dockerfile
# BAD - breaks caching
COPY . /app
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python -r requirements.txt

# GOOD - leverages caching
COPY requirements.txt .
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python --no-cache -r requirements.txt
COPY . /app
```

### Multi-Stage for Size
```dockerfile
# Build stage (can include build tools)
FROM golang:1.21 AS builder
WORKDIR /build
COPY go.mod go.sum .
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o app

# Runtime stage (minimal)
FROM alpine:3.19
COPY --from=builder /build/app /app
CMD ["/app"]
```

## Health Checks

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
COPY --chown=appuser:appuser . /app
USER appuser
WORKDIR /app

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uv", "run", "python", "app.py"]
```

## Docker Compose Example

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    image: myapp:latest
    read_only: true
    tmpfs:
      - /tmp
      - /var/run
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    security_opt:
      - no-new-privileges:true
    secrets:
      - db_password
    environment:
      - DATABASE_URL=postgresql://user:${DB_PASSWORD}@db:5432/mydb
    networks:
      - frontend
      - backend
    depends_on:
      db:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  frontend:
    driver: bridge
  backend:
    internal: true
    driver: bridge

volumes:
  postgres_data:

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

## Completion Checklist

- [ ] Dockerfile uses non-root USER
- [ ] Dockerfile has minimal layers
- [ ] Docker Compose uses read_only filesystem
- [ ] No privileged: true in any service
- [ ] No secrets in ENV (use secrets:)
- [ ] Internal networks for backend services
- [ ] Health checks defined
- [ ] Resource limits configured
- [ ] Trivy or similar scanner used for image vulnerability scanning
