# AI Hub (Python Desktop)

A modular PySide6 desktop application that brings together chat, writing prompts, spelling correction, global hotkeys, and hotstrings – all backed by the OpenAI Chat Completions API. The interface is dark-themed via [pyqtdarktheme 2.1.0](https://github.com/5yutan5/PyQtDarkTheme) and is designed so new capability tabs can be added over time without touching the core plumbing.

## Features

- **Three core tabs**
  - **Chat** – send system + user messages to OpenAI and view responses
  - **Prompts** – run curated prompts on any text selection; replace in place or show popup results
  - **Spelling** – one-click spelling & grammar fixes on selected text
- **Global hotkeys** (via `keyboard`) available from any Windows application
  - `Ctrl+Shift+J` – fix spelling (replace selection)
  - `Ctrl+Shift+K` – open prompt navigator near the mouse
  - `Ctrl+Alt+Shift+K` – bring the hub window to the foreground (configurable)
- **Hotstrings** for quick snippets and AI-powered rewrites (toggle with `Ctrl+Alt+H`)
  - `;sig` signature, `;date`, `;time`
  - AI-driven `;fix`, `;clar`, `;short`, `;long` on the current selection
- **Clipboard-safe selection helpers** preserve the user’s clipboard
- **Configurable via environment variables or `settings.ini`**
- **Modular architecture** ready for additional tabs, prompts, or backends

## Getting Started

### 1. Create and activate a virtual environment

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
```

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -e .
```

This installs PySide6, pyqtdarktheme 2.1.0, requests, keyboard, and the platform-specific clipboard helpers (pywin32 on Windows, pyperclip elsewhere).

### 3. Configure OpenAI access

Set an environment variable for the API key (recommended):

```powershell
setx OPENAI_API_KEY "sk-your-key"
```

Optional overrides:

- `OPENAI_ENDPOINT` (defaults to `https://api.openai.com/v1/chat/completions`)
- `OPENAI_MODEL` (defaults to `gpt-4o-mini`)
- `AI_HUB_TIMEOUT` (seconds, defaults to `120`)

You can also create a `settings.ini` next to the executable with the same keys under `[openai]`, plus `[hotkeys]` and `[hotstrings]` sections for overrides.

### 4. Run the desktop app

```bash
ai-hub
```

## Auto-start on Windows

To launch AI Hub automatically at login:

1. Run `pyinstaller --noconfirm --onefile -w -n AIHubLauncher src/ai_hub/app.py` (optional) to package as a single EXE, or simply use the `ai-hub` console script inside your virtual environment.
2. Press `Win + R`, type `shell:startup`, and press Enter to open the Startup folder.
3. Create a shortcut to either the generated EXE or to `python.exe <path>\ai_hub\app.py` with the virtual environment activated.
4. The hub will now launch at every logon.

Alternatively, create a Scheduled Task (Task Scheduler → Create Task → Trigger “At log on”) that runs your chosen command.

## Extending the Hub

The application is structured for incremental growth:

- **Tabs** live under `src/ai_hub/ui/tabs/`. Subclass `BaseTab` and add to the `QTabWidget` in `MainWindow`.
- **Prompts** are defined in `src/ai_hub/services/prompt_manager.py`. Add more prompt definitions or load from disk.
- **Global hotkeys** live in `src/ai_hub/hotkeys/global_hotkeys.py`. Add new bindings or per-prompt hotkeys.
- **Hotstrings** are registered in `MainWindow._register_default_hotstrings`. Swap in a JSON loader or UI editor later.
- **Backend services** (OpenAI client, future FastAPI server, vector search, etc.) live under `src/ai_hub/services/`.

Keep adding modules and attach them as new tabs or dialog workflows—no need to rewrite the main window.

## Roadmap Ideas

- Prompt profiles and tagging, saved per user
- FastAPI/HTTP backend for advanced workflows and background jobs
- Document ingestion (PDF, DOCX) with summarization
- Audio capture and Whisper transcription tab
- Local model routing (Ollama, GPT4All) with fallback
- Tray icon with quick actions and notifications
- Hotstring editor UI stored in JSON/SQLite

## Development Tips

- Use `settings.ini` during development to experiment with hotkey/hotstring mappings without touching code.
- Wrap long-running operations in threads (as shown) to keep the UI responsive.
- When adding new dependencies, update `pyproject.toml`.
- Consider adding a `tests/` folder with Qt unit tests as new logic is added.

Happy building!
