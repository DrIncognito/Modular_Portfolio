# Modular Portfolio

A modular, pluggable Python application to showcase small tools and utilities in one place.

## Features
- Add tools as folders in `addons/`
- CLI / Web / GUI support
- Plugin-based architecture
- Drag-and-drop customizable dashboard
- Plugin scaffold generator
- Fully open source

## Getting Started

```bash
python start.py cli   # CLI mode
python start.py web   # Flask dashboard
python start.py gui   # GUI drag-and-drop
```

**Note:**
- The GUI mode (`python start.py gui`) requires a graphical environment. If you run this in a headless server or Codespaces, you may see errors like `no display name and no $DISPLAY environment variable`. To use the GUI, run on your local machine or set up a virtual display (e.g., with Xvfb).

---

## How It Works

- **Plugins**: Each tool is a folder in `addons/` with a `main.py` (must subclass `BasePlugin` and implement `run(mode)`), and a `metadata.json` describing the plugin.
- **Auto-discovery**: All plugins in `addons/` are auto-loaded and available in CLI, web, and GUI modes depending on their `type` in `metadata.json`.
- **Entrypoints**:
  - `python start.py cli` — Launches the CLI dashboard, lists plugins, and lets you run them interactively.
  - `python start.py web` — Starts a Flask web dashboard, where you can run plugins from your browser.
  - `python start.py gui` — Launches a PyQt5 GUI dashboard with plugin buttons (requires a graphical environment).

---

## Authoring Plugins

1. **Scaffold a new plugin:**
   ```bash
   python utils/plugin_creator.py --name MyTool
   ```
2. **Edit your plugin:**
   - Implement your logic in `addons/MyTool/main.py` by subclassing `BasePlugin` and defining `run(self, mode)`.
   - Update `metadata.json` with your plugin's name, description, version, and supported modes (`cli`, `web`, `gui`).
3. **Test your plugin:**
   - Run in CLI: `python start.py cli`
   - Run in Web: `python start.py web` (then open browser)
   - Run in GUI: `python start.py gui`

**Example:**
See `addons/example_tool/` for a complete demo plugin that shows different behavior in CLI, web, and GUI modes.

---

## Create New Plugin

```bash
python utils/plugin_creator.py --name MyTool
```

Then implement the logic in `main.py` and update `metadata.json`.
