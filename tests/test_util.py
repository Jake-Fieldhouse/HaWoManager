import unittest

from womgr.util import parse_mac_address

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

if __name__ == "__main__":
    unittest.main()
