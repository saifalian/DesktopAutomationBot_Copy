# Desktop Automation Bot Copy

Desktop Automation Bot Copy is another saved version of the Python desktop automation assistant.

The runnable code is inside the `omg` folder. It includes a desktop UI, screenshot tools, OCR helpers, grid overlays, agent memory, prompt files, and mouse action helpers.

This repo is useful if you want to compare this version with the main `DesktopAutomationBot` project or continue work from this copy separately.

## What This App Can Do

- Show a desktop bot interface.
- Capture screenshots.
- Prepare images for OCR or vision work.
- Display grid and overlay helpers.
- Store agent memory and session data.
- Use prompt files for AI task handling.
- Include helper code for mouse actions.
- Save logs while the app is running.

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

## Safety Notes

This is a desktop automation experiment. Run it first on safe apps or test windows.

Be careful before allowing any automation to control the mouse on important websites, private accounts, or payment pages.
