# Build stage
FROM python:3.12-slim AS builder

ENV POETRY_VIRTUALENVS_CREATE=false
WORKDIR /workspace

# Build args
ARG GITHUB_TOKEN
ARG ACCESS_GUARD_BRANCH=developer

# Install build dependencies
RUN apt-get update \
    && apt-get -y install gcc libpq-dev git \
    && apt-get clean

# Install Poetry
RUN pip install poetry

# Create expected structure
RUN mkdir -p /workspace/access-manager-api

# Set working directory to access-manager-api
WORKDIR /workspace/access-manager-api

# Copy current context (access-manager-api/)
COPY . .

# Clone access-guard as sibling directory
WORKDIR /workspace
RUN git clone --branch ${ACCESS_GUARD_BRANCH} https://${GITHUB_TOKEN}@github.com/yuriscom/access_guard.git access-guard

# Go back into access-manager-api and install
WORKDIR /workspace/access-manager-api
RUN poetry install --no-interaction --no-ansi --no-root

# Runtime stage
FROM python:3.12-slim

ENV POETRY_VIRTUALENVS_CREATE=false
WORKDIR /workspace/access-manager-api

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

# Install runtime deps
RUN apt-get update \
    && apt-get -y install libpq-dev \
    && apt-get install --only-upgrade libexpat1 \
    && apt-get clean

# Copy installed packages and binaries
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code and config
COPY --from=builder /workspace /workspace

EXPOSE 8080
