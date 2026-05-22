#!/bin/sh
set -e

echo ">>> Creating tables and seeding database..."
.venv/bin/python seed.py

echo ">>> Starting server..."
exec .venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
