from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

import keyboard


HotkeyCallback = Callable[[], None]


@dataclass(slots=True)
class HotkeyRegistration:
    combo: str
    callback: HotkeyCallback
    suppress: bool = False
    trigger_on_release: bool = True


class HotkeyRegistry:
    """Collects hotkeys so modules can register before hooks are active."""

    def __init__(self) -> None:
        self._registrations: List[HotkeyRegistration] = []
        self._active = False

    def register(
        self,
        combo: str,
        callback: HotkeyCallback,
        *,
        suppress: bool = False,
        trigger_on_release: bool = True,
    ) -> None:
        if self._active:
            keyboard.add_hotkey(
                combo,
                callback,
                suppress=suppress,
                trigger_on_release=trigger_on_release,
            )
            return
        self._registrations.append(
            HotkeyRegistration(
                combo=combo,
                callback=callback,
                suppress=suppress,
                trigger_on_release=trigger_on_release,
            )
        )

    def activate(self) -> None:
        if self._active:
            return
        for registration in self._registrations:
            keyboard.add_hotkey(
                registration.combo,
                registration.callback,
                suppress=registration.suppress,
                trigger_on_release=registration.trigger_on_release,
            )
        self._active = True
