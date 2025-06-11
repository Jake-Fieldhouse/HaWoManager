import unittest
from unittest.mock import patch
import sys

from womgr.entities import PingBinarySensor


class TestPingArgs(unittest.TestCase):
    def test_linux_args(self):
        sensor = PingBinarySensor("dev", "1.2.3.4")
        with patch("shutil.which", return_value="ping"):
            original = sys.platform
            sys.platform = "linux"
            try:
                args = sensor._build_ping_args()
            finally:
                sys.platform = original
        self.assertEqual(args, ["ping", "-c", "1", "-W", "1", "1.2.3.4"])

    def test_windows_args(self):
        sensor = PingBinarySensor("dev", "1.2.3.4")
        with patch("shutil.which", return_value="ping.exe"):
            original = sys.platform
            sys.platform = "win32"
            try:
                args = sensor._build_ping_args()
            finally:
                sys.platform = original
        self.assertEqual(args, ["ping.exe", "-n", "1", "-w", "1000", "1.2.3.4"])


if __name__ == "__main__":
    unittest.main()
