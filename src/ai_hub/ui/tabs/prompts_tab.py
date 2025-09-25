from __future__ import annotations

import threading

from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from ...services.openai_client import OpenAIClient
from ...services.prompt_manager import Prompt
from ...services.selection import get_selection, replace_selection
from ..dialogs.result_popup import ResultPopup
from ..tabs.base import BaseTab


class PromptsTab(BaseTab):
    def __init__(self, client: OpenAIClient, prompts: list[Prompt]):
        super().__init__()
        self._client = client
        self._prompts = prompts
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Prompt Navigator — select text in any app, then choose a prompt:"))

        self.prompt_list = QListWidget(self)
        for prompt in self._prompts:
            QListWidgetItem(prompt.name, self.prompt_list)
        layout.addWidget(self.prompt_list)

        self.run_button = QPushButton("Run on Selection", self)
        self.run_button.clicked.connect(self._on_run_clicked)
        layout.addWidget(self.run_button)

    def _on_run_clicked(self) -> None:
        index = self.prompt_list.currentRow()
        if index < 0:
            return
        prompt = self._prompts[index]
        selection = get_selection().text
        if not selection.strip():
            return

        def run() -> None:
            output = self._client.chat(prompt.system or None, prompt.build_message(selection), prompt.temperature)
            if not output.strip():
                return
            if prompt.replace:
                replace_selection(output)
            else:
                ResultPopup.show_text(prompt.name, output)

        threading.Thread(target=run, daemon=True).start()
