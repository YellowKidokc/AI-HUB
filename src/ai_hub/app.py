from __future__ import annotations

from pathlib import Path

from .config import load_settings
from .ui.main_window import run_app


def main() -> None:
    settings = load_settings()
    run_app(settings)


if __name__ == "__main__":
    main()
