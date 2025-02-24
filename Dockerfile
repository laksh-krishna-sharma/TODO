# Stage 1: Install dependencies using Poetry
FROM python:3.11-slim-bookworm AS requirements-stage

# Install required system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 curl && rm -rf /var/lib/apt/lists/*

# Install the latest Poetry (ensuring we get `poetry export`)
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy dependency files
COPY ./pyproject.toml ./poetry.lock /

# Ensure Poetry is using a new virtual environment inside the container
RUN poetry config virtualenvs.create false
RUN poetry self add poetry-plugin-export
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without=dev



# Export dependencies to requirements.txt (ensure correct version)
RUN poetry --version && poetry export -f requirements.txt --output requirements.txt --without-hashes --without=dev

# Stage 2: Application build
FROM python:3.11-slim-bookworm

# Install SQLite3 for database operations
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 && rm -rf /var/lib/apt/lists/*

# Copy exported dependencies
COPY --from=requirements-stage /requirements.txt /requirements.txt

# Install dependencies
RUN python3 -m venv /venv && /venv/bin/pip install --no-cache-dir --upgrade -r /requirements.txt

# Copy application files
COPY ./pyproject.toml ./gunicorn_conf.py /
COPY ./app /app

# Create required directories
RUN mkdir -p /tmp/shm /data && chmod -R 777 /tmp/shm /data

# Set environment variables for SQLite
ENV DATABASE_URL=sqlite:////data/database.db
ENV PORT 8000

# Expose port
EXPOSE 8000

# Set entrypoint to use venv
ENTRYPOINT ["/venv/bin/gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "gunicorn_conf.py", "app.main:app"]
