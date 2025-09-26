from __future__ import annotations

import threading

from ..hotkeys.hotstrings import AIHotstrings
from ..services.selection import get_selection, replace_selection
from ..ui.dialogs.prompt_navigator import PromptNavigator
from ..ui.dialogs.result_popup import ResultPopup
from ..ui.tabs.prompts_tab import PromptsTab
from .base import HubModule, ModuleAPI


PROMPT_HOTSTRINGS = {
    ";fix": "fix",
    ";clar": "clarity",
    ";short": "shorten",
    ";long": "lengthen",
}


def _build_prompts_tab(api: ModuleAPI) -> PromptsTab:
    return PromptsTab(api.context.client, api.context.prompts)


def _register_prompt_navigator(api: ModuleAPI) -> None:
    settings = api.context.settings.hotkeys
    navigator = PromptNavigator(api.context.client, api.context.prompts)

    def show() -> None:
        navigator.show_near_cursor()

    api.hotkeys.register(settings.prompt_navigator, show)


def _register_prompt_hotstrings(api: ModuleAPI) -> None:
    ai_hotstrings = AIHotstrings(api.context.client, api.context.prompts)
    for trigger, slug in PROMPT_HOTSTRINGS.items():
        api.hotstrings.register_ai(trigger, ai_hotstrings.make_handler(slug))


def _register_prompt_shortcuts(api: ModuleAPI) -> None:
    catalog = api.context.prompts

    def make_runner(slug: str):
        def run() -> None:
            try:
                prompt = catalog.get_by_slug(slug)
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
                if not output.strip():
                    return
                if prompt.replace:
                    replace_selection(output)
                else:
                    ResultPopup.show_text(prompt.name, output)

            threading.Thread(target=worker, daemon=True).start()

        return run

    # Optional quick shortcuts for summarize/explain/action items
    shortcut_map = {
        "ctrl+alt+1": "summarize",
        "ctrl+alt+2": "explain",
        "ctrl+alt+3": "action_items",
    }
    for combo, slug in shortcut_map.items():
        api.hotkeys.register(combo, make_runner(slug))


def register(api: ModuleAPI) -> HubModule:
    def on_init(module_api: ModuleAPI) -> None:
        _register_prompt_navigator(module_api)
        _register_prompt_hotstrings(module_api)
        _register_prompt_shortcuts(module_api)

    return HubModule(
        id="prompts",
        title="Prompts",
        factory=_build_prompts_tab,
        order=20,
        on_init=on_init,
    )
