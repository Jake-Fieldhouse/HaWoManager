import asyncio
import sys
import types
from dataclasses import dataclass
from types import SimpleNamespace

# Stub minimal homeassistant modules required for import
ha = types.ModuleType("homeassistant")
ha.config_entries = types.ModuleType("config_entries")
ha.config_entries.ConfigEntry = object
class DummyConfigFlow:
    def __init_subclass__(cls, **kwargs):
        pass

    def async_show_form(self, *, step_id: str, data_schema=None, errors=None):
        return {"type": "form", "step_id": step_id, "errors": errors or {}}

    def async_create_entry(self, *, title: str, data: dict):
        return {"type": "create_entry", "title": title, "data": data}

    def async_abort(self, **kwargs):
        return {"type": "abort", **kwargs}

ha.config_entries.ConfigFlow = DummyConfigFlow
ha.core = types.ModuleType("core")
ha.core.HomeAssistant = object
ha.helpers = types.ModuleType("helpers")
ha.helpers.typing = types.ModuleType("typing")
ha.helpers.typing.ConfigType = dict
ha.components = types.ModuleType("components")
ha.components.http = types.ModuleType("http")

@dataclass
class StaticPathConfig:
    url_path: str
    path: str
    cache_headers: bool = True

ha.components.http.StaticPathConfig = StaticPathConfig
lovelace = types.ModuleType("lovelace")
lovelace.const = types.SimpleNamespace(
    CONF_ALLOW_SINGLE_WORD="allow_single_word",
    CONF_ICON="icon",
    CONF_TITLE="title",
    CONF_URL_PATH="url_path",
)

class DummyDashboardsCollection:
    pass

class DummyLovelaceStorage:
    async def async_load(self, *args, **kwargs):
        raise Exception
    async def async_save(self, *args, **kwargs):
        pass

class ConfigNotFound(Exception):
    pass

lovelace.dashboard = types.SimpleNamespace(
    DashboardsCollection=DummyDashboardsCollection,
    LovelaceStorage=DummyLovelaceStorage,
    ConfigNotFound=ConfigNotFound,
)
ha.components.lovelace = lovelace

sys.modules.setdefault("homeassistant", ha)
sys.modules.setdefault("homeassistant.config_entries", ha.config_entries)
sys.modules.setdefault("homeassistant.core", ha.core)
sys.modules.setdefault("homeassistant.helpers", ha.helpers)
sys.modules.setdefault("homeassistant.helpers.typing", ha.helpers.typing)
sys.modules.setdefault("homeassistant.components", ha.components)
sys.modules.setdefault("homeassistant.components.http", ha.components.http)
sys.modules.setdefault("homeassistant.components.lovelace", lovelace)
sys.modules.setdefault("homeassistant.components.lovelace.const", lovelace.const)
sys.modules.setdefault("homeassistant.components.lovelace.dashboard", lovelace.dashboard)

import unittest
from custom_components.womgr.config_flow import WoMgrConfigFlow


def _valid_input(**overrides):
    data = {
        "device_name": "dev1",
        "mac": "AA:BB:CC:DD:EE:FF",
        "ip": "192.168.1.100",
        "location": "lab",
        "os_type": "linux",
        "username": "",
        "password": "",
        "color": "",
        "dashboard": "",
    }
    data.update(overrides)
    return data


class TestConfigFlow(unittest.TestCase):
    def test_step_device_invalid_ip(self):
        flow = WoMgrConfigFlow()
        result = asyncio.run(flow.async_step_device(_valid_input(ip="invalid")))
        self.assertEqual(result["type"], "form")
        self.assertEqual(result["errors"], {"ip": "invalid_ip"})

    def test_step_device_duplicate_device_name(self):
        flow = WoMgrConfigFlow()
        flow._async_current_entries = lambda: [SimpleNamespace(data=_valid_input())]
        result = asyncio.run(flow.async_step_device(_valid_input()))
        self.assertEqual(result["type"], "abort")
        self.assertEqual(result["reason"], "duplicate_device_name")

    def test_step_device_duplicate_mac(self):
        flow = WoMgrConfigFlow()
        flow._async_current_entries = lambda: [SimpleNamespace(data=_valid_input())]
        result = asyncio.run(flow.async_step_device(_valid_input(device_name="dev2")))
        self.assertEqual(result["type"], "abort")
        self.assertEqual(result["reason"], "duplicate_mac")

