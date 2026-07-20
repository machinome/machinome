import asyncio
import unittest

from fastapi.testclient import TestClient

from shop_floor.app import app, lifecycle_events, lifecycle_status


class ShopFloorAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_reports_when_the_shop_is_available(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "open"})

    def test_browser_page_monitors_lifecycle_with_sse(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Shop is open", response.text)
        self.assertIn("new EventSource('/events/lifecycle')", response.text)
        self.assertIn("Shop is closed", response.text)

    def test_lifecycle_stream_announces_open_and_remains_an_sse_response(self) -> None:
        response = lifecycle_status()
        first_chunk = asyncio.run(anext(lifecycle_events()))

        self.assertEqual(response.media_type, "text/event-stream")
        self.assertIn("event: lifecycle", first_chunk)
        self.assertIn("data: open", first_chunk)
