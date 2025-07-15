import asyncio
import sys
import types
from dataclasses import dataclass
from types import SimpleNamespace

# Stub minimal homeassistant modules required for import
ha = types.ModuleType("homeassistant")
ha.config_entries = types.ModuleType("config_entries")
ha.config_entries.ConfigEntry = object
ha.core = types.ModuleType("core")
ha.core.HomeAssistant = object
ha.helpers = types.ModuleType("helpers")
ha.helpers.typing = types.ModuleType("typing")
ha.helpers.typing.ConfigType = dict
ha.helpers.device_registry = types.ModuleType("device_registry")
ha.helpers.device_registry.async_get = lambda hass: types.SimpleNamespace(
    async_get_or_create=lambda **kw: types.SimpleNamespace(id="dev"),
    async_update_device=lambda *a, **k: None,
)
ha.components = types.ModuleType("components")
ha.components.http = types.ModuleType("http")
class DummyView:
    name = "dummy"
    url = "/"
    requires_auth = False
    def __init__(self, hass=None):
        pass
ha.components.http.HomeAssistantView = DummyView

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

from custom_components.womgr import async_unload_entry
from custom_components.womgr.const import DOMAIN

class DummyConfigEntries:
    async def async_unload_platforms(self, entry, platforms):
        raise AssertionError("unload should not be called")

def test_unload_entry_without_data():
    hass = SimpleNamespace(data={DOMAIN: {}}, config_entries=DummyConfigEntries())
    entry = SimpleNamespace(data={}, entry_id="dummy")
    assert asyncio.run(async_unload_entry(hass, entry))

