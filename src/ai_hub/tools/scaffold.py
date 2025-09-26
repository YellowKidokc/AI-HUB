from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

TEMPLATE = """from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ..modules.base import HubModule, ModuleAPI


class _PlaceholderTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("{title} module ready!"))


def _build_tab(api: ModuleAPI) -> QWidget:
    return _PlaceholderTab()


def register(api: ModuleAPI) -> HubModule:
    return HubModule(
        id="{module_id}",
        title="{title}",
        factory=_build_tab,
        order={order},
    )
"""


def generate_module(module_name: str, title: str, order: int) -> Path:
    target = Path(__file__).resolve().parents[1] / "modules" / f"{module_name}.py"
    if target.exists():
        raise SystemExit(f"Module '{module_name}' already exists at {target}.")
    content = TEMPLATE.format(module_id=module_name, title=title, order=order)
    target.write_text(content, encoding="utf-8")
    return target


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-hub-scaffold",
        description="Generate a new AI Hub module skeleton.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Examples:
              ai-hub-scaffold research "Research Tools" --order 40
            """
        ),
    )
    parser.add_argument("name", help="Python-friendly module name (used as file + module id).")
    parser.add_argument("title", help="Tab title shown in the UI.")
    parser.add_argument(
        "--order",
        type=int,
        default=50,
        help="Tab order (lower numbers appear earlier).",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    path = generate_module(args.name, args.title, args.order)
    print(f"Created module at {path}")


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
