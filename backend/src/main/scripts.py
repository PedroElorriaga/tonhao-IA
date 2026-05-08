import os
import uvicorn

# src/ directory — one level up from this file (src/main/ → src/)
_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def dev():
    uvicorn.run(
        "main.main:app",
        host="localhost",
        port=8000,
        reload=True,
        reload_dirs=[_SRC_DIR],
        app_dir=_SRC_DIR,
    )


def start():
    uvicorn.run(
        "main.main:app",
        host="0.0.0.0",
        port=8000,
        app_dir=_SRC_DIR,
    )
