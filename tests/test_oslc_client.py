"""Integration tests for OSLC client."""

import unittest
from tests.mock_server import MockOSLCServer
from src.oslc_client import OSLCClient


class TestOSLCClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock = MockOSLCServer(port=9801)
        cls.mock.start()
        cls.client = OSLCClient("http://localhost:9801", "admin", "admin")

    @classmethod
    def tearDownClass(cls):
        cls.mock.stop()

    def test_authenticate(self):
        result = self.client.authenticate()
        self.assertTrue(result)

    def test_get_service_providers(self):
        providers = self.client.get_service_providers(
            "http://localhost:9801/rm/catalog"
        )
        self.assertGreater(len(providers), 0)
        self.assertEqual(providers[0]["title"], "Test Project")

    def test_query_resources(self):
        result = self.client.query_resources(
            "http://localhost:9801/rm/query",
            select="dcterms:title",
        )
        self.assertIn("oslc:results", result)
        self.assertEqual(len(result["oslc:results"]), 2)

    def test_query_with_filter(self):
        result = self.client.query_resources(
            "http://localhost:9801/rm/resources",
            where='dcterms:identifier="REQ-001"',
        )
        self.assertIn("oslc:results", result)


if __name__ == "__main__":
    unittest.main()
