import unittest

from womgr.entities import setup_device, remove_device, SystemCommandSwitch, _existing_devices

class DummyProcess:
    def __init__(self):
        self.terminated = False
    def poll(self):
        return None
    def terminate(self):
        self.terminated = True
    def wait(self, timeout=None):
        pass

class TestDeviceManagement(unittest.TestCase):
    def tearDown(self):
        _existing_devices.clear()

    def test_ip_validation_and_duplicates(self):
        entry = setup_device("dev1", "AA:BB:CC:DD:EE:FF", "192.0.2.1", "office", "linux")
        with self.assertRaises(ValueError):
            setup_device("dev1", "AA:BB:CC:DD:EE:F0", "192.0.2.2", "office", "linux")
        with self.assertRaises(ValueError):
            setup_device("dev2", "AA:BB:CC:DD:EE:F1", "not-an-ip", "office", "linux")
        remove_device(entry)

    def test_remove_device_terminates_process(self):
        entry = setup_device("dev2", "AA:BB:CC:DD:EE:F2", "192.0.2.3", "office", "linux")
        system = next(e for e in entry.entities if isinstance(e, SystemCommandSwitch))
        system.process = DummyProcess()
        remove_device(entry)
        self.assertTrue(system.process.terminated)

if __name__ == "__main__":
    unittest.main()
