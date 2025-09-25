from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QPushButton, QTextEdit, QVBoxLayout

from ...services.selection import copy_to_clipboard


class ResultPopup:
    @staticmethod
    def show_text(title: str, content: str) -> None:
        dialog = QDialog()
        dialog.setWindowTitle(title)
        dialog.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        layout = QVBoxLayout(dialog)

        text = QTextEdit(dialog)
        text.setReadOnly(True)
        text.setPlainText(content)
        layout.addWidget(text)

        button = QPushButton("Copy & Close", dialog)
        layout.addWidget(button)

        def on_copy() -> None:
            copy_to_clipboard(content)
            dialog.accept()

        button.clicked.connect(on_copy)
        dialog.resize(680, 420)
        dialog.exec()
