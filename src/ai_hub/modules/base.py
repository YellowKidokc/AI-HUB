from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtWidgets import QWidget

from ..core.context import AppContext
from ..hotkeys.hotstrings import HotstringEngine
from ..hotkeys.registry import HotkeyRegistry


@dataclass(slots=True)
class ModuleAPI:
    """Services exposed to module registration functions."""

    context: AppContext
    hotkeys: HotkeyRegistry
    hotstrings: HotstringEngine


TabFactory = Callable[[ModuleAPI], QWidget]
InitHook = Callable[[ModuleAPI], None]


@dataclass(slots=True)
class HubModule:
    """Represents a tab (and optional hooks) contributed by a module."""

    id: str
    title: str
    factory: TabFactory
    order: int = 100
    on_init: InitHook | None = None
