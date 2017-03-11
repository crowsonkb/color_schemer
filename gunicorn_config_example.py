# Gunicorn example configuration. Copy it to gunicorn_config.py and edit it as required. Refer
# to http://docs.gunicorn.org/en/latest/settings.html for documentation on gunicorn's settings.

import os
from pathlib import Path

# Server socket
bind = ['127.0.0.1:8000']

# Workers
workers = os.cpu_count()

# Server mechanics
daemon = True
chdir = str(Path(__file__).resolve())
pidfile = 'gunicorn.pid'

# Logging
accesslog = 'log/access.log'
errorlog = 'log/error.log'
loglevel = os.environ.get('LOGLEVEL', 'info')


def on_exit(server):
    """Clean up pid file on exit."""
    try:
        os.unlink(pidfile)
    except FileNotFoundError:
        pass
