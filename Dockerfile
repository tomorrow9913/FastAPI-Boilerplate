FROM python:3.12-slim

ENV USER=fastapi \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd -m -s /bin/bash $USER

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc=4:14.2.0-1 \
    libpq-dev=* \
    pkg-config=1.8.1-4 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.5.5 /uv /bin/uv
RUN chown -R "$USER":"$USER" /bin/uv

ENV APP_DIR=/home/$USER/app
ENV PYTHONPATH=$APP_DIR

WORKDIR $APP_DIR

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --no-dev

COPY main.py ./main.py
COPY src/ ./src/

RUN chown -R "$USER":"$USER" $APP_DIR

USER $USER

CMD ["uv", "run", "main.py"]
