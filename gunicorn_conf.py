import os
import multiprocessing

# Environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()
HOST = os.getenv("HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", "8000"))

# Server socket
bind = f"{HOST}:{WEB_PORT}"
backlog = 2048

# Worker processes
# For CPU-bound: workers = cpu_count * 2 + 1
# For I/O-bound (FastAPI): workers = cpu_count + 1 (more conservative)
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = int(os.getenv("WORKER_CONNECTIONS", "1000"))
timeout = int(os.getenv("WORKER_TIMEOUT", "30"))
keepalive = int(os.getenv("KEEPALIVE", "2"))

# Restart workers after this many requests, to help prevent memory leaks
max_requests = int(os.getenv("MAX_REQUESTS", "1000"))
max_requests_jitter = int(os.getenv("MAX_REQUESTS_JITTER", "100"))

# Logging configuration
if DEBUG or ENVIRONMENT == "development":
    # Development: verbose logging
    accesslog = "-"  # stdout
    errorlog = "-"   # stderr
    loglevel = "debug"
    access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
else:
    # Production: structured logging
    accesslog = "/app/logs/gunicorn_access.log"
    errorlog = "/app/logs/gunicorn_error.log"
    loglevel = LOG_LEVEL
    access_log_format = '{"remote_ip":"%(h)s","request_id":"%({X-Request-ID}i)s","timestamp":"%(t)s","method":"%(m)s","url":"%(U)s","query":"%(q)s","protocol":"%(H)s","status":%(s)s,"response_length":%(b)s,"referer":"%(f)s","user_agent":"%(a)s","response_time":%(D)s}'

# Process naming
proc_name = "fastapi_users_api"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# Preload application for better performance
preload_app = True

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance tuning
worker_tmp_dir = "/dev/shm"  # Use memory for worker temp files

# Graceful shutdown
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", "30"))

# SSL configuration (for HTTPS)
keyfile = os.getenv("SSL_KEYFILE")
certfile = os.getenv("SSL_CERTFILE")
ca_certs = os.getenv("SSL_CA_CERTS")
cert_reqs = int(os.getenv("SSL_CERT_REQS", "0"))  # 0=CERT_NONE, 1=CERT_OPTIONAL, 2=CERT_REQUIRED

# Hooks for application lifecycle
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("🚀 Starting Gunicorn server...")
    server.log.info(f"🔧 Environment: {ENVIRONMENT}")
    server.log.info(f"🔧 Workers: {workers}")
    server.log.info(f"🔧 Worker class: {worker_class}")
    server.log.info(f"🔧 Bind: {bind}")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("🔄 Reloading Gunicorn server...")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info(f"👷 Worker {worker.pid} received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info(f"👷 Worker {worker.pid} about to be forked")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"👷 Worker {worker.pid} spawned")

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info(f"👷 Worker {worker.pid} initialized")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info(f"👷 Worker {worker.pid} received SIGABRT signal")

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("🔄 Pre-exec: New master process about to be forked")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("✅ Gunicorn server is ready. Listening on: %s", server.address)

def on_exit(server):
    """Called just before exiting."""
    server.log.info("🛑 Gunicorn server is shutting down...")

# Environment-specific configurations
if ENVIRONMENT == "development":
    # Development settings
    reload = True
    reload_extra_files = ["app/", "requirements.txt"]
    workers = 1  # Single worker for development
    loglevel = "debug"
elif ENVIRONMENT == "production":
    # Production settings
    reload = False
    preload_app = True
    workers = max(2, multiprocessing.cpu_count())  # At least 2 workers
    loglevel = "warning"
elif ENVIRONMENT == "testing":
    # Testing settings
    workers = 1
    loglevel = "error"
    accesslog = None  # Disable access logs in tests
