from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass

try:
    import win32clipboard as wcb
    import win32con
    HAVE_WIN32 = True
except Exception:  # pragma: no cover - fallback on non-Windows
    HAVE_WIN32 = False

try:
    import pyperclip
    HAVE_PYPERCLIP = True
except Exception:  # pragma: no cover - optional dependency
    HAVE_PYPERCLIP = False

try:
    import keyboard
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("The 'keyboard' package is required for selection helpers.") from exc


@dataclass(slots=True)
class SelectionResult:
    text: str


@contextmanager
def _preserve_clipboard():
    original = ""
    if HAVE_WIN32:
        try:
            wcb.OpenClipboard()
            if wcb.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                original = wcb.GetClipboardData(win32con.CF_UNICODETEXT)
        finally:
            wcb.CloseClipboard()
    elif HAVE_PYPERCLIP:
        original = pyperclip.paste()

    try:
        yield
    finally:
        if HAVE_WIN32:
            try:
                wcb.OpenClipboard()
                wcb.EmptyClipboard()
                wcb.SetClipboardText(original)
            finally:
                wcb.CloseClipboard()
        elif HAVE_PYPERCLIP:
            pyperclip.copy(original)


def _clear_clipboard():
    if HAVE_WIN32:
        try:
            wcb.OpenClipboard()
            wcb.EmptyClipboard()
        finally:
            wcb.CloseClipboard()
    elif HAVE_PYPERCLIP:
        pyperclip.copy("")


def _read_clipboard_text() -> str:
    if HAVE_WIN32:
        try:
            wcb.OpenClipboard()
            if wcb.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                return wcb.GetClipboardData(win32con.CF_UNICODETEXT)
        finally:
            wcb.CloseClipboard()
        return ""
    if HAVE_PYPERCLIP:
        return pyperclip.paste()
    return ""


def get_selection() -> SelectionResult:
    with _preserve_clipboard():
        _clear_clipboard()
        keyboard.send("ctrl+c")
        time.sleep(0.08)
        text = _read_clipboard_text()
        if text.strip():
            return SelectionResult(text)

        keyboard.send("ctrl+a")
        time.sleep(0.06)
        keyboard.send("ctrl+c")
        time.sleep(0.08)
        text = _read_clipboard_text()
        return SelectionResult(text)


def replace_selection(text: str) -> None:
    with _preserve_clipboard():
        if HAVE_WIN32:
            wcb.OpenClipboard()
            wcb.EmptyClipboard()
            wcb.SetClipboardText(text)
            wcb.CloseClipboard()
        elif HAVE_PYPERCLIP:
            pyperclip.copy(text)
        keyboard.send("ctrl+v")
        time.sleep(0.04)


def copy_to_clipboard(text: str) -> None:
    if HAVE_WIN32:
        wcb.OpenClipboard()
        wcb.EmptyClipboard()
        wcb.SetClipboardText(text)
        wcb.CloseClipboard()
    elif HAVE_PYPERCLIP:
        pyperclip.copy(text)
