---
name: docker-best-practices
description: Complete containerization guide covering Dockerfile patterns, Docker Compose, security, and networking
license: MIT
---

# Docker Best Practices

Comprehensive guide for containerization with focus on security, minimalism, and production readiness.

## Non-Negotiable Rules (STOP if violated)

| Rule | Violation = STOP |
|------|-----------------|
| Dockerfile has non-root USER | Block if missing |
| Docker Compose has read_only | Block if missing |
| No privileged: true | Block if detected |
| No secrets in ENV | Block if detected |
| AGENT must never read .env files | Block if attempted |

## Dockerfile Best Practices

### Non-Root User (REQUIRED)
```dockerfile
# BAD - runs as root
FROM python:3.11
COPY . /app
CMD ["python", "app.py"]

# GOOD - runs as non-root
FROM python:3.11

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and set permissions
COPY --chown=appuser:appuser . /app
WORKDIR /app

USER appuser
CMD ["python", "app.py"]
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
FROM python:3.11 AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY --chown=appuser:appuser . /app
WORKDIR /app
ENV PATH=/root/.local/bin:$PATH
USER appuser
CMD ["python", "app.py"]
```

### Security Hardening
```dockerfile
FROM python:3.11-slim

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
CMD ["python", "app.py"]
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

### AGENT Restrictions
- AGENT must never Read `.env` files
- Application code can load `.env` files
- Use Docker secrets for production secrets
- Never commit `.env` files

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
# BAD - use minimal official images
FROM python:3.11

# GOOD - use official minimal images
FROM python:3.11-slim
```

### Caching
```dockerfile
# BAD - breaks caching
COPY . /app
RUN pip install -r requirements.txt

# GOOD - leverages caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
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
FROM python:3.11-slim
COPY --chown=appuser:appuser . /app
USER appuser
WORKDIR /app

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["python", "app.py"]
```

## Docker Compose Example

```yaml
version: '3.8'

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

## Pre-Commit Hooks (OPTIONAL)

### Installation
If `setup-hooks.sh` is missing, ask user before installing:

```
"Pre-commit hooks are not configured. Would you like me to install them?
This will add Dockerfile linting (hadolint) and other quality checks."
```

Only run `curl -sSL https://raw.githubusercontent.com/joaomj/opencode/main/setup-hooks.sh | bash` if user confirms "yes".

### Before Committing
If hooks are installed, run: `pre-commit run --all-files`

## Completion Checklist

- [ ] Dockerfile uses non-root USER
- [ ] Dockerfile has minimal layers
- [ ] Docker Compose uses read_only filesystem
- [ ] No privileged: true in any service
- [ ] No secrets in ENV (use secrets:)
- [ ] AGENT never read `.env` files
- [ ] Internal networks for backend services
- [ ] Health checks defined
- [ ] Resource limits configured
- [ ] Pre-commit hooks installed only with user consent
