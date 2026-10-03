# Desktop Automation Bot Copy

Desktop Automation Bot Copy is a preserved copy of the desktop automation assistant project. The runnable source lives under the `omg` directory and includes UI panels, agent memory, LLM prompt handling, OCR helpers, screenshot capture, grid overlays, and mouse actions.

This repository is useful for comparing or continuing a later variant of the original `DesktopAutomationBot` codebase without mixing runtime logs and screenshots into version control.

## Features

- PyQt-style dashboard and bot interaction UI
- Screenshot capture, preprocessing, and OCR modules
- Grid and overlay UI helpers
- Agent memory/session modules
- LLM client and prompt definitions
- Mouse action helpers
- Runtime logging utilities

## Project Structure

```text
omg/
├── actions/
├── agent/
├── config/
├── llm/
├── ui/
├── utils/
├── vision/
└── main.py
```

## Setup

```powershell
cd omg
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Safety

This is a desktop automation tool. Run it first against non-sensitive applications and verify any generated action plan before allowing automation to control the mouse.

