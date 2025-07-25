
import importlib.util
import os
import json
import sys
from modular_portfolio.modular_core.interface import BasePlugin

ADDONS_PATH = os.path.join(os.path.dirname(__file__), '..', 'addons')

class PluginLoader:
    def __init__(self, addons_path=ADDONS_PATH):
        self.addons_path = os.path.abspath(addons_path)
        self.plugins = []
        self.load_plugins()

    def load_plugins(self):
        self.plugins = []
        for item in os.listdir(self.addons_path):
            plugin_dir = os.path.join(self.addons_path, item)
            if os.path.isdir(plugin_dir):
                main_py = os.path.join(plugin_dir, 'main.py')
                meta_json = os.path.join(plugin_dir, 'metadata.json')
                if os.path.exists(main_py) and os.path.exists(meta_json):
                    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
                    sys.path.insert(0, plugin_dir)
                    spec = importlib.util.spec_from_file_location(item, main_py)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    with open(meta_json) as f:
                        metadata = json.load(f)
                    for attr in dir(module):
                        obj = getattr(module, attr)
                        if isinstance(obj, type):
                            # Debug: print BasePlugin identity
                            try:
                                is_sub = issubclass(obj, BasePlugin)
                            except Exception as e:
                                is_sub = str(e)
                            print(f"DEBUG: {item}.{attr} is_subclass: {is_sub}, obj: {obj}, BasePlugin: {BasePlugin}, obj.__module__: {getattr(obj, '__module__', None)}")
                            if is_sub and obj is not BasePlugin:
                                self.plugins.append({'name': item, 'class': obj, 'metadata': metadata})
                    sys.path.pop(0)

    def get_plugins(self, mode=None):
        if mode:
            return [p for p in self.plugins if mode in p['metadata'].get('type', [])]
        return self.plugins
