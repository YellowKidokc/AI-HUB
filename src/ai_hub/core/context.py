from __future__ import annotations

from dataclasses import dataclass

from ..config import AppSettings
from ..services.openai_client import OpenAIClient
from ..services.prompt_manager import PromptCatalog


@dataclass(slots=True)
class AppContext:
    """Shared application state exposed to modules."""

    settings: AppSettings
    client: OpenAIClient
    prompts: PromptCatalog
