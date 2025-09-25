from __future__ import annotations

import threading

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

from ...services.openai_client import OpenAIClient
from ...services.prompt_manager import Prompt
from ...services.selection import get_selection, replace_selection
from .result_popup import ResultPopup


class PromptNavigator(QDialog):
    def __init__(self, client: OpenAIClient, prompts: list[Prompt]):
        super().__init__()
        self._client = client
        self._prompts = prompts
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool | Qt.FramelessWindowHint)
        self.setWindowTitle("Prompt Navigator")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.prompt_list = QListWidget(self)
        for prompt in self._prompts:
            QListWidgetItem(prompt.name, self.prompt_list)
        layout.addWidget(self.prompt_list)
        layout.addWidget(QLabel("Enter to run • Esc to close"))
        self.prompt_list.itemDoubleClicked.connect(lambda _: self.run_selected())
        self.prompt_list.setCurrentRow(0)

    def show_near_cursor(self) -> None:
        pos = QCursor.pos()
        self.move(pos)
        self.show()
        self.raise_()
        self.activateWindow()
        self.prompt_list.setFocus()

    def keyPressEvent(self, event):  # pragma: no cover - Qt
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.run_selected()
            return
        if event.key() == Qt.Key_Escape:
            self.close()
            return
        super().keyPressEvent(event)

    def run_selected(self) -> None:
        index = self.prompt_list.currentRow()
        if index < 0:
            self.close()
            return
        prompt = self._prompts[index]
        selection = get_selection().text
        if not selection.strip():
            self.close()
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
        self.close()
