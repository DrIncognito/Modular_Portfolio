from core.interface import BasePlugin

class PluginTemplate(BasePlugin):
    def run(self, mode: str):
        print(f"Running PluginTemplate in {mode} mode!")
