
import sys
import os
# Ensure the parent directory is in sys.path for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Add calc_module to the path for core imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'calc_module')))

from modular_portfolio.cli.main import launch_cli
from modular_portfolio.flask_app.app import launch_web
from modular_portfolio.gui.dashboard import launch_gui

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "cli"
    if mode == "cli":
        launch_cli()
    elif mode == "web":
        launch_web()
    elif mode == "gui":
        launch_gui()
    else:
        print("Unknown mode: cli, web, gui")
