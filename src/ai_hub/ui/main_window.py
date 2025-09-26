from __future__ import annotations

import qdarktheme
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget

from ..config import AppSettings
from ..core.context import AppContext
from ..hotkeys.hotstrings import HotstringEngine
from ..hotkeys.registry import HotkeyRegistry
from ..modules import discover_modules
from ..modules.base import ModuleAPI
from ..services.openai_client import OpenAIClient
from ..services.prompt_manager import PromptCatalog


class MainWindow(QMainWindow):
    def __init__(self, settings: AppSettings):
        super().__init__()
        self.setWindowTitle("AI Hub")
        self.resize(1000, 720)

        qdarktheme.setup_theme("auto")

        self._settings = settings
        client = OpenAIClient(settings.openai)
        prompts = PromptCatalog.from_path(settings.paths.prompts)
        self._context = AppContext(settings=settings, client=client, prompts=prompts)
        self._tabs = QTabWidget(self)
        self.setCentralWidget(self._tabs)

        self._hotkey_registry = HotkeyRegistry()
        self._hotstrings_engine = HotstringEngine(
            buffer_size=settings.hotstrings.buffer_size,
            enabled=settings.hotstrings.enabled_by_default,
        )

        module_api = ModuleAPI(
            context=self._context,
            hotkeys=self._hotkey_registry,
            hotstrings=self._hotstrings_engine,
        )
        self._modules = discover_modules(module_api)

        for module in self._modules:
            widget = module.factory(module_api)
            self._tabs.addTab(widget, module.title)

        self._tabs.currentChanged.connect(self._on_tab_changed)

        self._register_default_hotstrings()

        if settings.hotkeys.goto_hub:
            self._hotkey_registry.register(
                settings.hotkeys.goto_hub,
                self.focus_hub_tab,
            )

        for module in self._modules:
            if module.on_init:
                module.on_init(module_api)

        self._hotstrings_engine.start()
        self._hotkey_registry.activate()

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
