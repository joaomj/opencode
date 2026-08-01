---
name: docker-best-practices
description: Apply secure, minimal Dockerfile and Docker Compose practices for containerized applications.
---

# Docker Best Practices

Use this skill for Dockerfiles, Compose files, container security, image
optimization, and container networking.

## Stop Conditions

- The image runs as root without a documented reason.
- Compose lacks a read-only filesystem where the service permits it.
- `privileged: true` is present.
- Secrets are stored in an image, Dockerfile, or environment value.
- A container has broader capabilities or network access than required.

## Dockerfile

- Use a small maintained base image that matches the project package workflow.
- Use the official uv image for Python projects when uv is the repository tool.
- Create and use a non-root user.
- Install only required packages and remove package-manager caches.
- Copy dependency manifests before application code to preserve cache reuse.
- Use multi-stage builds when build tools are not needed at runtime.
- Pin or verify base images according to the repository's supply-chain policy.
- Set `WORKDIR`, explicit environment defaults, and a predictable entrypoint.
- Add a health check when the service exposes a reliable health boundary.

## Compose

- Set `read_only: true` where the application supports it.
- Mount only required writable paths as `tmpfs` or explicit volumes.
- Drop all capabilities and add back only required capabilities.
- Set `no-new-privileges:true`.
- Define CPU and memory limits for services with operational impact.
- Separate frontend, backend, and internal networks.
- Add health checks and health-based dependencies.
- Use Docker secrets or an external secret manager. Do not put secrets in
  `environment:` or committed files.

## Networking

- Keep databases and internal services on an internal backend network.
- Expose only the ports that users or required peer services need.
- Document each external connection and its trust boundary.
- Do not use network access as a substitute for service authorization.

## Security Scanning

Read `../references/container-scanning.md` for the shared Trivy and action
pinning guidance. Resolve current action versions before copying a workflow.

## Verification

- Build the image with the expected target.
- Inspect the image user, entrypoint, exposed ports, and filesystem.
- Validate Compose configuration.
- Run the service with the intended read-only and network restrictions.
- Scan the image and report high or critical findings.
- Verify health checks and graceful shutdown behavior.

## Completion Checklist

- Non-root user is configured.
- Layers and base image are minimal for the workload.
- Filesystem and capabilities follow least privilege.
- No privileged mode or committed secrets exists.
- Internal networks and health checks are defined where needed.
- Resource limits and vulnerability scanning are configured.
