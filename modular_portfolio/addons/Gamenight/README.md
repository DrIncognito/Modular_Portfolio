# Plugin Template

This is a template for creating new plugins for Modular Portfolio.

## How to Use
1. Copy this folder to `addons/YourPluginName`
2. Edit `main.py` to implement your plugin logic (subclass `BasePlugin` and implement `run(self, mode)`)
3. Fill out `metadata.json` with your plugin's name, description, version, and supported modes (`cli`, `web`, `gui`)
4. Add a README.md describing your plugin

## Example
See `addons/example_tool/` for a complete demo plugin.
