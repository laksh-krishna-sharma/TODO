import json
import multiprocessing
import os

# Detect Database Type
db_url = os.getenv("DATABASE_URL", "")
is_sqlite = db_url.startswith("sqlite")

# Environment Variables
workers_per_core_str = os.getenv("WORKERS_PER_CORE", "1")
max_workers_str = os.getenv("MAX_WORKERS", "10")
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)
host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "8000")
bind_env = os.getenv("BIND", None)
loglevel = os.getenv("LOG_LEVEL", "info")

# Set Binding
use_bind = bind_env if bind_env else f"{host}:{port}"

# Compute Worker Count
cores = multiprocessing.cpu_count()
workers_per_core = float(workers_per_core_str)
default_web_concurrency = max(int(workers_per_core * cores), 2)

# Determine Workers
if is_sqlite:
    web_concurrency = 1  # SQLite does not handle concurrency well
else:
    web_concurrency = int(web_concurrency_str) if web_concurrency_str else default_web_concurrency
    if max_workers_str:
        web_concurrency = min(web_concurrency, int(max_workers_str))

# Choose Worker Class
worker_class = "uvicorn.workers.UvicornWorker" if is_sqlite else "app.workers.ConfigurableWorker"

# Timeout & Logging Configuration
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", "60"))
timeout = int(os.getenv("TIMEOUT", "60"))
keepalive = int(os.getenv("KEEP_ALIVE", "5"))
accesslog = os.getenv("ACCESS_LOG", "-") or None
errorlog = os.getenv("ERROR_LOG", "-") or None
worker_tmp_dir = "/tmp/shm"

# Gunicorn Configuration Variables
log_data = {
    "loglevel": loglevel,
    "workers": web_concurrency,
    "worker_class": worker_class,
    "bind": use_bind,
    "graceful_timeout": graceful_timeout,
    "timeout": timeout,
    "keepalive": keepalive,
    "errorlog": errorlog,
    "accesslog": accesslog,
    "workers_per_core": workers_per_core,
    "host": host,
    "port": port,
    "database": "SQLite" if is_sqlite else "Other",
}

# Print Config for Debugging
print(json.dumps(log_data))

# Gunicorn Variables
bind = use_bind
workers = web_concurrency
