# TODO: Write a production-ready Dockerfile
#
# All of these are tested by the grader:
#
# [ ] Multi-stage build (2+ FROM instructions)
# [ ] Base image: python:3.14-slim (pinned version, no :latest)
# [ ] Copy requirements.txt and pip install BEFORE copying source code (layer caching)
# [ ] Run as a non-root USER
# [ ] EXPOSE 8080
# [ ] HEALTHCHECK instruction
# [ ] No hardcoded secrets (no ENV PASSWORD=..., no ENV SECRET_KEY=...)
# [ ] Final image under 200MB
#
# Start command: uvicorn src.app:app --host 0.0.0.0 --port 8080

# Stage 1: Build stage for dependencies
# FROM python:3.14.0-alpine AS builder
FROM python@sha256:8373231e1e906ddfb457748bfc032c4c06ada8c759b7b62d9c73ec2a3c56e710 AS builder
WORKDIR /build
COPY requirements.txt . 
RUN pip install --target=/deps --no-cache-dir --no-compile -r requirements.txt && \
    find /deps -type d -name "__pycache__" -exec rm -r {} + && \
    find /deps -type f -name "*.pyc" -delete && \
    find /deps -type d -name "tests" -exec rm -r {} + && \
    find /deps -type d -name "*.dist-info" -exec rm -r {} +

# Stage 2: Runtime stage
FROM python@sha256:8373231e1e906ddfb457748bfc032c4c06ada8c759b7b62d9c73ec2a3c56e710 AS runtime
WORKDIR /app

# Labels OCI
ARG VERSION=1.0.0

LABEL org.opencontainers.image.title="Ejercicio 01 - Node Registry"
LABEL org.opencontainers.image.authors="Juan M. Brero <brerojuanm@gmail.com>"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.source="https://github.com/Juanbrero/exercise-01-node-registry.git"
LABEL app.environment="Production"

RUN addgroup -g 1001 -S appgroup && \
    adduser -S -u 1001 -G appgroup appuser

COPY --from=builder --chown=appuser:appgroup /deps /deps
COPY --chown=appuser:appgroup src/ /app/src/

# Enviroments
ENV PYTHONPATH=/deps:/app/src
ENV PYTHONDONTWRITEBYTECODE=1

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request; r=urllib.request.urlopen('http://localhost:8080/health'); exit(0 if r.status==200 else 1)"]

USER appuser
EXPOSE 8080

ENTRYPOINT ["python", "-m"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
