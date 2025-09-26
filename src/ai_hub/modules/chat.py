from __future__ import annotations

from ..ui.tabs.chat_tab import ChatTab
from .base import HubModule, ModuleAPI


def _build_chat_tab(api: ModuleAPI) -> ChatTab:
    return ChatTab(api.context.client)


def register(api: ModuleAPI) -> HubModule:
    return HubModule(
        id="chat",
        title="Chat",
        factory=_build_chat_tab,
        order=10,
    )
