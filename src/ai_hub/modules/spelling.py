from __future__ import annotations

import threading

from ..services.selection import get_selection, replace_selection
from ..ui.tabs.spelling_tab import SpellingTab
from .base import HubModule, ModuleAPI


def _build_spelling_tab(api: ModuleAPI) -> SpellingTab:
    return SpellingTab(api.context.client, api.context.prompts)


def _register_spelling_hotkey(api: ModuleAPI) -> None:
    settings = api.context.settings.hotkeys

    def run_spelling() -> None:
        try:
            prompt = api.context.prompts.get_by_slug("fix")
        except KeyError:
            return
        selection = get_selection().text
        if not selection.strip():
            return

        def worker() -> None:
            output = api.context.client.chat(
                prompt.system or None,
                prompt.build_message(selection),
                prompt.temperature,
            )
            if output.strip():
                replace_selection(output)

        threading.Thread(target=worker, daemon=True).start()

    api.hotkeys.register(settings.spelling, run_spelling)


def register(api: ModuleAPI) -> HubModule:
    def on_init(module_api: ModuleAPI) -> None:
        _register_spelling_hotkey(module_api)

    return HubModule(
        id="spelling",
        title="Spelling",
        factory=_build_spelling_tab,
        order=30,
        on_init=on_init,
    )
