

import unittest
from modular_portfolio.cli.main import launch_cli

class TestCLI(unittest.TestCase):
    def test_cli_runs(self):
        # This is a smoke test; actual CLI interaction would require integration testing
        try:
            launch_cli()
        except Exception as e:
            self.fail(f"CLI launch failed: {e}")

if __name__ == "__main__":
    unittest.main()
