# AI Hub Desktop

AI Hub is a PySide6 desktop companion that lives on your machine, styles itself with `pyqtdarktheme 2.1.0`, and wires global hotkeys, hotstrings, and modular AI workflows into a single window. Every capability (chat, prompts, spelling, future research tools, etc.) is packaged as its own module so you can keep stacking tabs without rewriting the core.

## Highlights

- **Modular tab system** – drop new modules into `src/ai_hub/modules/` (or scaffold them with `ai-hub-scaffold`) and they appear automatically.
- **Prompt catalog with slugs** – prompts live in code or an external JSON file, can be addressed by slug, and power hotkeys, hotstrings, and the prompt navigator dialog.
- **Global reach** – keyboard hooks run from anywhere: `Ctrl+Shift+J` fixes spelling, `Ctrl+Shift+K` opens the prompt navigator near your cursor, and `Ctrl+Alt+H` toggles hotstrings.
- **Clipboard-safe selection helpers** – selections are copied, transformed, and pasted back without losing the user’s clipboard contents.
- **Auto-start ready** – package with PyInstaller or register a shortcut/Scheduled Task to launch on login.

## Quick Start

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -e .
setx OPENAI_API_KEY "sk-your-key"
ai-hub
```

On macOS/Linux swap the virtual environment commands for the usual `python3 -m venv` / `source .venv/bin/activate`. The OpenAI key can also be provided through `settings.ini` (see below).

### Configuration

`settings.ini` (optional, stored next to the executable) understands:

```ini
[openai]
api_key = sk-your-key
endpoint = https://api.openai.com/v1/chat/completions
model = gpt-4o-mini
timeout = 120

[hotkeys]
spelling = ctrl+shift+j
prompt_navigator = ctrl+shift+k
goto_hub = ctrl+alt+shift+k
toggle_hotstrings = ctrl+alt+h

[hotstrings]
enabled = true
buffer_size = 64

[paths]
prompts = C:\\path\\to\\prompts.json
```

Environment variable overrides are also supported:

- `OPENAI_API_KEY`, `OPENAI_ENDPOINT`, `OPENAI_MODEL`, `AI_HUB_TIMEOUT`
- `AI_HUB_PROMPTS` – alternate prompt catalog JSON

The prompt file expects a list of objects with `slug`, `name`, `prefix`, `suffix`, `replace`, and optional `system`, `temperature`, `order` fields.

### Autostart on Windows

1. Optionally package as a single EXE: `pyinstaller --noconfirm --onefile -w -n AIHub src/ai_hub/app.py`
2. Open `shell:startup` and drop a shortcut to either the EXE or the `ai-hub` console script.
3. Alternatively, create a Scheduled Task set to trigger “At log on” and point it at the same command.

## Modules & Extensibility

Modules are regular Python files that export a `register(api: ModuleAPI) -> HubModule`. At runtime the loader imports every module under `src/ai_hub/modules/`, builds the tab widget, and lets the module register hotkeys/hotstrings during its `on_init` hook.

### Scaffold a new module

```bash
ai-hub-scaffold research "Research Tools" --order 40
```

This command creates `src/ai_hub/modules/research.py` with a ready-to-edit template. The `order` decides where the tab appears (lower numbers float to the left). Drop your UI in the generated factory and register any keyboard automation inside the returned `HubModule`.

### Prompt-driven automation

- **Prompt Navigator** – instant list of catalog prompts, bound to `Ctrl+Shift+K` by default.
- **Hotstrings** – `;fix`, `;clar`, `;short`, and `;long` call into the catalog by slug; define new ones by adding entries to the catalog or your own module.
- **Shortcut bindings** – `Ctrl+Alt+1/2/3` run summarize, explain, and action-item prompts. Extend via `ModuleAPI.hotkeys.register`.

### Selection helpers

Global operations all route through `ai_hub.services.selection`: `get_selection()` safely grabs the user’s highlight (retrying with `Ctrl+A` if empty) and `replace_selection()` pastes the result back while restoring the clipboard. Use them in your modules to stay consistent.

## Roadmap Ideas

- Hotstring editor tab backed by JSON/SQLite
- FastAPI backend for long-running jobs and local model routing
- PDF/Doc/Audio ingestion workflows
- Tray icon with quick actions and status indicators
- Workspace-aware profiles that switch prompts/hotkeys per app

Build iteratively—add a module for each new capability, and keep your Python + UI work decoupled from the window chrome.
