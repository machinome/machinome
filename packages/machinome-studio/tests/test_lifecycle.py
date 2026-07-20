import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from shop_floor.lifecycle import ShopOpenError, ShopRunner


class ShopRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.state_file = Path(self.temporary_directory.name) / "shop-floor.pid"
        self.runner = ShopRunner(state_file=self.state_file)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    @patch("shop_floor.lifecycle.wait_until_available", return_value=True)
    @patch("shop_floor.lifecycle.subprocess.Popen")
    def test_open_starts_the_service_and_reports_its_stable_location(
        self, popen: Mock, _available: Mock
    ) -> None:
        process = Mock(pid=12345)
        popen.return_value = process

        location = self.runner.open()

        self.assertEqual(location, "http://127.0.0.1:9000")
        self.assertEqual(self.state_file.read_text(), "12345")
        command = popen.call_args.args[0]
        self.assertIn("uvicorn", command)
        self.assertIn("shop_floor.app:app", command)

    @patch("shop_floor.lifecycle.wait_until_available", return_value=False)
    @patch("shop_floor.lifecycle.subprocess.Popen")
    def test_open_reports_failure_when_service_never_becomes_available(
        self, popen: Mock, _available: Mock
    ) -> None:
        process = Mock(pid=12345)
        popen.return_value = process

        with self.assertRaises(ShopOpenError):
            self.runner.open()

        process.terminate.assert_called_once()
        self.assertFalse(self.state_file.exists())

    @patch("shop_floor.lifecycle.wait_until_unavailable", return_value=True)
    @patch("shop_floor.lifecycle.os.kill")
    def test_close_stops_the_recorded_service(
        self, kill: Mock, unavailable: Mock
    ) -> None:
        self.state_file.write_text("12345")

        self.runner.close()

        kill.assert_called_once()
        unavailable.assert_called_once_with("http://127.0.0.1:9000/health")
        self.assertFalse(self.state_file.exists())
