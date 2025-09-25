from __future__ import annotations

from typing import Callable

import qdarktheme
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget

from ..config import AppSettings
from ..hotkeys.global_hotkeys import GlobalHotkeys, HotkeyCallbacks
from ..hotkeys.hotstrings import AIHotstrings, HotstringEngine
from ..services.openai_client import OpenAIClient
from ..services.prompt_manager import Prompt, default_prompts
from ..ui.tabs.chat_tab import ChatTab
from ..ui.tabs.prompts_tab import PromptsTab
from ..ui.tabs.spelling_tab import SpellingTab


class MainWindow(QMainWindow):
    def __init__(self, settings: AppSettings):
        super().__init__()
        self.setWindowTitle("AI Hub")
        self.resize(1000, 720)

        qdarktheme.setup_theme("auto")

        self._settings = settings
        self._client = OpenAIClient(settings.openai)
        self._prompts = list(default_prompts())
        self._tabs = QTabWidget(self)
        self.setCentralWidget(self._tabs)

        self._chat_tab = ChatTab(self._client)
        self._prompts_tab = PromptsTab(self._client, self._prompts)
        self._spelling_tab = SpellingTab(self._client, self._prompts[0])

        self._tabs.addTab(self._chat_tab, "Chat")
        self._tabs.addTab(self._prompts_tab, "Prompts")
        self._tabs.addTab(self._spelling_tab, "Spelling")

        self._tabs.currentChanged.connect(self._on_tab_changed)

        self._hotkeys = GlobalHotkeys(
            client=self._client,
            prompts=self._prompts,
            spelling_prompt=self._prompts[0],
            callbacks=HotkeyCallbacks(focus_hub_tab=self.focus_hub_tab),
            prompt_hotkey=settings.hotkeys.prompt_navigator,
            spelling_hotkey=settings.hotkeys.spelling,
            goto_hotkey=settings.hotkeys.goto_hub,
        )
        self._hotkeys.start()

        self._hotstrings_engine = HotstringEngine(
            buffer_size=settings.hotstrings.buffer_size,
            enabled=settings.hotstrings.enabled_by_default,
        )
        self._register_default_hotstrings()
        self._hotstrings_engine.start()

        keyboard = __import__("keyboard")
        keyboard.add_hotkey(
            settings.hotkeys.toggle_hotstrings,
            self._toggle_hotstrings,
            suppress=False,
            trigger_on_release=True,
        )

    def _register_default_hotstrings(self) -> None:
        import time

        self._hotstrings_engine.register_text(";sig", "Best regards,\nYour Name")
        self._hotstrings_engine.register_text(";date", lambda: time.strftime("%Y-%m-%d"))
        self._hotstrings_engine.register_text(";time", lambda: time.strftime("%H:%M"))

        ai_hotstrings = AIHotstrings(self._client, self._prompts)
        self._hotstrings_engine.register_ai(";fix", ai_hotstrings.make_handler(0))
        self._hotstrings_engine.register_ai(";clar", ai_hotstrings.make_handler(1))
        self._hotstrings_engine.register_ai(";short", ai_hotstrings.make_handler(2))
        self._hotstrings_engine.register_ai(";long", ai_hotstrings.make_handler(3))

    def focus_hub_tab(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()
        self._tabs.setCurrentIndex(0)

    def _toggle_hotstrings(self) -> None:
        new_state = not self._hotstrings_engine.enabled
        self._hotstrings_engine.set_enabled(new_state)
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(self, "AI Hub", f"Hotstrings {'enabled' if new_state else 'disabled'}.")

    def _on_tab_changed(self, index: int) -> None:  # pragma: no cover - UI hook
        for i in range(self._tabs.count()):
            widget = self._tabs.widget(i)
            if hasattr(widget, "on_activate"):
                if i == index:
                    widget.on_activate()
                else:
                    widget.on_deactivate()


def run_app(settings: AppSettings) -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow(settings)
    window.show()
    app.exec()
