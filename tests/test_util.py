import unittest

from womgr.util import parse_mac_address

class TestParseMacAddress(unittest.TestCase):
    def test_valid_mac(self):
        self.assertEqual(
            parse_mac_address("AA:BB:CC:DD:EE:FF"),
            bytes.fromhex("aabbccddeeff"),
        )
        self.assertEqual(
            parse_mac_address("aa-bb-cc-dd-ee-ff"),
            bytes.fromhex("aabbccddeeff"),
        )

    def test_invalid_mac(self):
        with self.assertRaises(ValueError):
            parse_mac_address("invalid")
        with self.assertRaises(ValueError):
            parse_mac_address("00:11:22:33:44")

if __name__ == "__main__":
    unittest.main()
