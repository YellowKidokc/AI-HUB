from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Callable

import keyboard

from ..services.openai_client import OpenAIClient
from ..services.prompt_manager import Prompt
from ..services.selection import get_selection, replace_selection
from ..ui.dialogs.prompt_navigator import PromptNavigator
from ..ui.dialogs.result_popup import ResultPopup


@dataclass(slots=True)
class HotkeyCallbacks:
    focus_hub_tab: Callable[[], None]


class GlobalHotkeys:
    def __init__(
        self,
        client: OpenAIClient,
        prompts: list[Prompt],
        spelling_prompt: Prompt,
        callbacks: HotkeyCallbacks,
        prompt_hotkey: str,
        spelling_hotkey: str,
        goto_hotkey: str | None,
    ) -> None:
        self._client = client
        self._prompts = prompts
        self._spelling_prompt = spelling_prompt
        self._callbacks = callbacks
        self._prompt_hotkey = prompt_hotkey
        self._spelling_hotkey = spelling_hotkey
        self._goto_hotkey = goto_hotkey
        self._navigator = PromptNavigator(client, prompts)

    def start(self) -> None:
        keyboard.add_hotkey(self._spelling_hotkey, self._run_spelling, suppress=False, trigger_on_release=True)
        keyboard.add_hotkey(self._prompt_hotkey, self._show_prompt_navigator, suppress=False, trigger_on_release=True)
        if self._goto_hotkey:
            keyboard.add_hotkey(self._goto_hotkey, self._callbacks.focus_hub_tab, suppress=False, trigger_on_release=True)

    def _show_prompt_navigator(self) -> None:
        self._navigator.show_near_cursor()

    def _run_spelling(self) -> None:
        selection = get_selection().text
        if not selection.strip():
            return

        def run() -> None:
            output = self._client.chat(self._spelling_prompt.system or None, self._spelling_prompt.build_message(selection), self._spelling_prompt.temperature)
            if output.strip():
                replace_selection(output)

        threading.Thread(target=run, daemon=True).start()

    def run_prompt_by_index(self, index: int) -> None:
        if index < 0 or index >= len(self._prompts):
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
