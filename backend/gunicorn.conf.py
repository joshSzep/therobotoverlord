"""
Gunicorn configuration file for The Robot Overlord backend.
"""

import multiprocessing
import os

from gunicorn.arbiter import Arbiter

# Server socket configuration
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
backlog = 2048

# Worker processes
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = "therobotoverlord_backend"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'


# Server hooks
def on_starting(
    server: Arbiter,
) -> None:
    """Log when server starts."""
    if server.log is not None:
        server.log.info("Starting The Robot Overlord backend")


def on_exit(
    server: Arbiter,
) -> None:
    """Log when server exits."""
    if server.log is not None:
        server.log.info("Stopping The Robot Overlord backend")


# Application configuration
wsgi_app = "backend.app:app"
