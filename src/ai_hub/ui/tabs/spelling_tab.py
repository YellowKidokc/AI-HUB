from __future__ import annotations

import threading

from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout

from ...services.openai_client import OpenAIClient
from ...services.prompt_manager import PromptCatalog
from ...services.selection import get_selection, replace_selection
from ..tabs.base import BaseTab


class SpellingTab(BaseTab):
    def __init__(self, client: OpenAIClient, catalog: PromptCatalog, slug: str = "fix"):
        super().__init__()
        self._client = client
        self._catalog = catalog
        self._slug = slug
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select text in any window, then click to fix spelling:"))
        button = QPushButton("Fix Spelling Now", self)
        button.clicked.connect(self._on_fix_clicked)
        layout.addWidget(button)
        layout.addStretch(1)

    def _on_fix_clicked(self) -> None:
        selection = get_selection().text
        if not selection.strip():
            return

        def run() -> None:
            try:
                prompt = self._catalog.get_by_slug(self._slug)
            except KeyError:
                return
            output = self._client.chat(prompt.system or None, prompt.build_message(selection), prompt.temperature)
            if output.strip():
                replace_selection(output)

        threading.Thread(target=run, daemon=True).start()
