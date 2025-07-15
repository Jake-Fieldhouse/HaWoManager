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

class DummyLovelaceStorage:
    def __init__(self):
        self.config = None

    async def async_load(self, *args, **kwargs):
        if self.config is None:
            raise ConfigNotFound
        return self.config

    async def async_save(self, cfg):
        self.config = cfg

class DummyDashboardsCollection:
    def __init__(self, dashboards):
        self.dashboards = dashboards

    async def async_create_item(self, cfg):
        path = cfg["url_path"]
        self.dashboards[path] = DummyLovelaceStorage()
        return self.dashboards[path]

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

from custom_components.womgr import async_setup_entry
from custom_components.womgr.const import DOMAIN

class DummyConfigEntries:
    async def async_forward_entry_setups(self, entry, platforms):
        pass

def test_no_duplicate_cards_when_setup_called_twice():
    async def run_test():
        dashboards = {}
        lovelace_data = {
            "dashboards": dashboards,
            "dashboards_collection": DummyDashboardsCollection(dashboards),
        }
        tasks = []

        def async_create_task(coro):
            task = asyncio.create_task(coro)
            tasks.append(task)
            return task

        hass = SimpleNamespace(
            data={DOMAIN: {}, "lovelace": lovelace_data},
            config_entries=DummyConfigEntries(),
            async_create_task=async_create_task,
        )

        entry = SimpleNamespace(
            data={
                "device_name": "server",
                "mac": "00:11:22:33:44:55",
                "ip": "0.0.0.0",
                "location": "here",
                "os_type": "linux",
                "dashboard": "",
            },
            entry_id="1",
        )

        await asyncio.gather(
            async_setup_entry(hass, entry),
            async_setup_entry(hass, entry),
        )

        await asyncio.gather(*tasks)

        path = entry.data["dashboard"] or "womgr"
        dashboard = dashboards[path]
        config = await dashboard.async_load(False)
        view = next(v for v in config.get("views", []) if v.get("path") == path)
        cards = [c for c in view.get("cards", []) if c.get("title") == "server"]
        assert len(cards) == 1

    asyncio.run(run_test())


def test_custom_dashboard_path():
    async def run_test():
        dashboards = {}
        lovelace_data = {
            "dashboards": dashboards,
            "dashboards_collection": DummyDashboardsCollection(dashboards),
        }
        tasks = []

        def async_create_task(coro):
            task = asyncio.create_task(coro)
            tasks.append(task)
            return task

        hass = SimpleNamespace(
            data={DOMAIN: {}, "lovelace": lovelace_data},
            config_entries=DummyConfigEntries(),
            async_create_task=async_create_task,
        )

        entry = SimpleNamespace(
            data={
                "device_name": "server",
                "mac": "00:11:22:33:44:55",
                "ip": "0.0.0.0",
                "location": "here",
                "os_type": "linux",
                "dashboard": "customdash",
            },
            entry_id="1",
        )

        await async_setup_entry(hass, entry)
        await asyncio.gather(*tasks)

        dashboard = dashboards["customdash"]
        config = await dashboard.async_load(False)
        view = next(v for v in config.get("views", []) if v.get("path") == "customdash")
        assert view is not None

    asyncio.run(run_test())
