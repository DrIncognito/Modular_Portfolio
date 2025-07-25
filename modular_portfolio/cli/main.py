
import sys
import os
# Ensure the parent directory is in sys.path for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modular_portfolio.modular_core.loader import PluginLoader
from rich.console import Console
from rich.table import Table

def launch_cli():
    loader = PluginLoader()
    plugins = loader.get_plugins('cli')
    console = Console()
    table = Table(title="Available CLI Plugins")
    table.add_column("Name")
    table.add_column("Description")
    for plugin in plugins:
        table.add_row(plugin['metadata']['name'], plugin['metadata'].get('description', ''))
    console.print(table)
    if not plugins:
        print("No CLI plugins found.")
        return
    name = input("Enter plugin name to run (or blank to exit): ").strip()
    for plugin in plugins:
        if plugin['metadata']['name'].lower() == name.lower():
            plugin['class']().run('cli')
            return
    if name:
        print("Plugin not found.")

def main():
    launch_cli()

if __name__ == "__main__":
    main()
