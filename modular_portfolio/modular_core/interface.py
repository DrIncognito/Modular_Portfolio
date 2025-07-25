class BasePlugin:
    def run(self, mode: str):
        raise NotImplementedError("Each plugin must implement a run() method.")
