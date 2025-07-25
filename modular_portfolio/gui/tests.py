

import unittest
from modular_portfolio.gui.dashboard import launch_gui

class TestGUI(unittest.TestCase):
    def test_gui_runs(self):
        # This is a smoke test; actual GUI interaction would require integration testing
        try:
            launch_gui()
        except Exception as e:
            self.fail(f"GUI launch failed: {e}")

if __name__ == "__main__":
    unittest.main()
