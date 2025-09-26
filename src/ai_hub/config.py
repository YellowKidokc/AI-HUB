from __future__ import annotations

import configparser
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


DEFAULT_SETTINGS_PATH = Path("settings.ini")


@dataclass(slots=True)
class OpenAISettings:
    api_key: Optional[str]
    endpoint: str
    model: str
    timeout: int


@dataclass(slots=True)
class HotkeySettings:
    spelling: str = "ctrl+shift+j"
    prompt_navigator: str = "ctrl+shift+k"
    goto_hub: Optional[str] = "ctrl+alt+shift+k"
    toggle_hotstrings: str = "ctrl+alt+h"


@dataclass(slots=True)
class HotstringSettings:
    enabled_by_default: bool = True
    buffer_size: int = 64


@dataclass(slots=True)
class AppSettings:
    openai: OpenAISettings
    hotkeys: HotkeySettings
    hotstrings: HotstringSettings
    paths: "PathSettings"


@dataclass(slots=True)
class PathSettings:
    prompts: Optional[Path]


_DEFAULT_ENDPOINT = "https://api.openai.com/v1/chat/completions"
_DEFAULT_MODEL = "gpt-4o-mini"
_DEFAULT_TIMEOUT = 120


def _load_settings_file(path: Path) -> configparser.ConfigParser:
    parser = configparser.ConfigParser()
    if path.exists():
        parser.read(path)
    return parser


def _read_ini_value(parser: configparser.ConfigParser, section: str, option: str, fallback: Optional[str]) -> Optional[str]:
    if parser.has_option(section, option):
        return parser.get(section, option)
    return fallback


def load_settings(settings_path: Path | None = None) -> AppSettings:
    path = settings_path or DEFAULT_SETTINGS_PATH
    parser = _load_settings_file(path)

    api_key = os.environ.get("OPENAI_API_KEY") or _read_ini_value(parser, "openai", "api_key", None)
    endpoint = os.environ.get("OPENAI_ENDPOINT") or _read_ini_value(parser, "openai", "endpoint", _DEFAULT_ENDPOINT) or _DEFAULT_ENDPOINT
    model = os.environ.get("OPENAI_MODEL") or _read_ini_value(parser, "openai", "model", _DEFAULT_MODEL) or _DEFAULT_MODEL
    timeout_str = os.environ.get("AI_HUB_TIMEOUT") or _read_ini_value(parser, "openai", "timeout", str(_DEFAULT_TIMEOUT)) or str(_DEFAULT_TIMEOUT)

    hotkey_spelling = _read_ini_value(parser, "hotkeys", "spelling", HotkeySettings().spelling) or HotkeySettings().spelling
    hotkey_prompt = _read_ini_value(parser, "hotkeys", "prompt_navigator", HotkeySettings().prompt_navigator) or HotkeySettings().prompt_navigator
    hotkey_goto = _read_ini_value(parser, "hotkeys", "goto_hub", HotkeySettings().goto_hub)
    hotkey_toggle = _read_ini_value(parser, "hotkeys", "toggle_hotstrings", HotkeySettings().toggle_hotstrings) or HotkeySettings().toggle_hotstrings

    hotstrings_enabled = _read_ini_value(parser, "hotstrings", "enabled", None)
    hotstrings_buffer = _read_ini_value(parser, "hotstrings", "buffer_size", str(HotstringSettings().buffer_size)) or str(HotstringSettings().buffer_size)

    prompts_path_env = os.environ.get("AI_HUB_PROMPTS")
    prompts_path_ini = _read_ini_value(parser, "paths", "prompts", prompts_path_env)
    prompts_path = Path(prompts_path_ini).expanduser() if prompts_path_ini else None

    openai_settings = OpenAISettings(
        api_key=api_key,
        endpoint=endpoint,
        model=model,
        timeout=int(timeout_str),
    )
    hotkey_settings = HotkeySettings(
        spelling=hotkey_spelling,
        prompt_navigator=hotkey_prompt,
        goto_hub=hotkey_goto,
        toggle_hotstrings=hotkey_toggle,
    )
    hotstring_settings = HotstringSettings(
        enabled_by_default=(hotstrings_enabled.lower() == "true") if isinstance(hotstrings_enabled, str) else HotstringSettings().enabled_by_default,
        buffer_size=int(hotstrings_buffer),
    )
    path_settings = PathSettings(prompts=prompts_path)

    return AppSettings(
        openai=openai_settings,
        hotkeys=hotkey_settings,
        hotstrings=hotstring_settings,
        paths=path_settings,
    )
