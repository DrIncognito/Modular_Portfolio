

import unittest
from modular_portfolio.flask_app.app import app

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Modular Portfolio Dashboard', response.data)

if __name__ == "__main__":
    unittest.main()
