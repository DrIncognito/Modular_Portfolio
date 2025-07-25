

import unittest
from modular_portfolio.modular_core.loader import PluginLoader
from modular_portfolio.modular_core.interface import BasePlugin

class TestPluginSystem(unittest.TestCase):
    def test_plugin_discovery(self):
        loader = PluginLoader()
        plugins = loader.get_plugins()
        self.assertTrue(any(p['metadata']['name'] == 'ExampleTool' for p in plugins))

    def test_plugin_interface(self):
        loader = PluginLoader()
        plugins = loader.get_plugins()
        for plugin in plugins:
            # Compare by class name and module to avoid import identity issues
            self.assertTrue(
                plugin['class'].__name__ == 'ExampleTool' and hasattr(plugin['class'], 'run'),
                f"Plugin class {plugin['class']} does not match interface requirements"
            )

if __name__ == "__main__":
    unittest.main()
