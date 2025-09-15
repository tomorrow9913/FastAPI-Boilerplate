# =================================================================
# 1. Builder Stage: Install dependencies and build the virtual environment
# =================================================================
FROM python:3.12-slim as builder

# 시스템 환경 변수 설정
# Setting environment variables to prevent Python from writing .pyc files and to ensure stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
# using --no-install-recommends to minimize unnecessary package installations
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential=* \
    libpq-dev=* \
    && rm -rf /var/lib/apt/lists/*

# Install 'uv' from the specified image
COPY --from=ghcr.io/astral-sh/uv:0.5.5 /uv /usr/local/bin/uv

# Setting up the working directory, creating a virtual environment, and installing dependencies
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv venv && \
    . .venv/bin/activate && \
    uv sync --no-dev

# =================================================================
# 2. Final Stage: Set up the runtime environment
# =================================================================
FROM python:3.12-slim as final

# 시스템 사용자 생성
ENV USER=fastapi
RUN useradd -m -s /bin/bash $USER

# Installing only the necessary runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5=* \
    && rm -rf /var/lib/apt/lists/*

# Setting Application Directory
ENV APP_DIR=/home/$USER/app
WORKDIR $APP_DIR

# Copy the virtual environment from the builder stage
COPY --from=builder --chown=$USER:$USER /app/.venv ./.venv
COPY --from=builder --chown=$USER:$USER /app/pyproject.toml ./pyproject.toml

# Copy application code
COPY --chown=$USER:$USER main.py ./main.py
COPY --chown=$USER:$USER src/ ./src/

# Switch to the system user
USER $USER

# Set the path to use uv within the virtual environment and run the application
CMD ["./.venv/bin/python", "main.py"]
