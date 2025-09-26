from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable

import keyboard

from ..services.openai_client import OpenAIClient
from ..services.prompt_manager import PromptCatalog
from ..services.selection import get_selection, replace_selection


HotstringCallback = Callable[[], None]


@dataclass(slots=True)
class HotstringDefinition:
    trigger: str
    action: Callable[[], None]


class HotstringEngine:
    """Simple keystroke buffer for text expanders and AI actions."""

    def __init__(self, *, buffer_size: int, enabled: bool = True) -> None:
        self._buffer_size = buffer_size
        self._enabled = enabled
        self._buffer: list[str] = []
        self._text_hotstrings: dict[str, Callable[[], None]] = {}
        self._ai_hotstrings: dict[str, Callable[[], None]] = {}

    @property
    def enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, value: bool) -> None:
        self._enabled = value

    def register_text(self, trigger: str, replacer: Callable[[], str] | str) -> None:
        def action() -> None:
            text = replacer() if callable(replacer) else replacer
            replace_selection(text)

        self._text_hotstrings[trigger] = action

    def register_ai(self, trigger: str, callback: HotstringCallback) -> None:
        self._ai_hotstrings[trigger] = callback

    def start(self) -> None:
        keyboard.hook(self._on_key_event)

    def _on_key_event(self, event) -> None:  # pragma: no cover - relies on OS events
        if not self._enabled or event.event_type != "down":
            return

        key = event.name
        if len(key) == 1:
            self._buffer.append(key)
        elif key == "space":
            self._buffer.append(" ")
        elif key == "backspace":
            if self._buffer:
                self._buffer.pop()
            return
        else:
            return

        if len(self._buffer) > self._buffer_size:
            self._buffer = self._buffer[-self._buffer_size:]

        buffer_text = "".join(self._buffer)

        for trigger, action in {**self._ai_hotstrings, **self._text_hotstrings}.items():
            if buffer_text.endswith(trigger):
                for _ in range(len(trigger)):
                    keyboard.send("backspace")
                    time.sleep(0.005)
                action()
                self._buffer.clear()
                break


class AIHotstrings:
    def __init__(self, client: OpenAIClient, catalog: PromptCatalog):
        self._client = client
        self._catalog = catalog

    def make_handler(self, slug: str) -> Callable[[], None]:
        def handler() -> None:
            try:
                prompt = self._catalog.get_by_slug(slug)
            except KeyError:
                return
            selection = get_selection().text
            if not selection.strip():
                return

            def run() -> None:
                output = self._client.chat(prompt.system or None, prompt.build_message(selection), prompt.temperature)
                if output.strip():
                    replace_selection(output)

            threading.Thread(target=run, daemon=True).start()

        return handler
