import unittest

from womgr.util import parse_mac_address, pastel_color, slugify

class TestParseMacAddress(unittest.TestCase):
    def test_valid_mac(self):
        valid_cases = [
            "AA:BB:CC:DD:EE:FF",
            "aa:bb:cc:dd:ee:ff",
            "AA-BB-CC-DD-EE-FF",
            "aa-bb-cc-dd-ee-ff",
            "AA-BB:CC-DD:EE-FF",
        ]
        for mac in valid_cases:
            with self.subTest(mac=mac):
                self.assertEqual(
                    parse_mac_address(mac),
                    bytes.fromhex("aabbccddeeff"),
                )

    def test_invalid_mac(self):
        with self.assertRaises(ValueError):
            parse_mac_address("invalid")
        with self.assertRaises(ValueError):
            parse_mac_address("00:11:22:33:44")


class TestPastelColor(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(pastel_color("dev"), pastel_color("dev"))

    def test_format(self):
        color = pastel_color("dev")
        self.assertRegex(color, r"rgb\(\d{1,3}, \d{1,3}, \d{1,3}\)")


class TestSlugify(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(slugify("My Device"), "my_device")

    def test_strip_invalid(self):
        self.assertEqual(slugify("Dev!@# Name"), "dev_name")

if __name__ == "__main__":
    unittest.main()
