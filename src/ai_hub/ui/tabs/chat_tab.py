from __future__ import annotations

import threading

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QLabel, QPushButton, QTextEdit, QVBoxLayout

from ...services.openai_client import OpenAIClient
from ..tabs.base import BaseTab


class ChatTab(BaseTab):
    request_started = Signal()
    request_finished = Signal(str)

    def __init__(self, client: OpenAIClient, system_default: str = "You are a helpful assistant."):
        super().__init__()
        self._client = client
        self._system_default = system_default
        self._build_ui()
        self.request_started.connect(self._on_request_started)
        self.request_finished.connect(self._on_request_finished)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("System (optional):"))
        self.system_input = QTextEdit(self)
        self.system_input.setFixedHeight(80)
        self.system_input.setPlainText(self._system_default)
        layout.addWidget(self.system_input)

        layout.addWidget(QLabel("Your message:"))
        self.user_input = QTextEdit(self)
        self.user_input.setFixedHeight(200)
        layout.addWidget(self.user_input)

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self._on_send_clicked)
        layout.addWidget(self.send_button)

        layout.addWidget(QLabel("Response:"))
        self.response_output = QTextEdit(self)
        self.response_output.setReadOnly(True)
        layout.addWidget(self.response_output)

    @Slot()
    def _on_send_clicked(self) -> None:
        message = self.user_input.toPlainText().strip()
        if not message:
            return
        system = self.system_input.toPlainText().strip() or None

        def run() -> None:
            self.request_started.emit()
            reply = self._client.chat(system, message)
            self.request_finished.emit(reply)

        threading.Thread(target=run, daemon=True).start()

    @Slot()
    def _on_request_started(self) -> None:
        self.response_output.setPlainText("Thinking...")
        self.send_button.setEnabled(False)

    @Slot(str)
    def _on_request_finished(self, reply: str) -> None:
        self.response_output.setPlainText(reply)
        self.send_button.setEnabled(True)
