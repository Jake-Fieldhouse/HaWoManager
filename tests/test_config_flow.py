import asyncio
import sys
import types

# Stub minimal homeassistant modules required for import
ha = types.ModuleType("homeassistant")
ha.config_entries = types.ModuleType("config_entries")
class DummyConfigFlow:
    def __init_subclass__(cls, **kwargs):
        pass
ha.config_entries.ConfigEntry = object
ha.config_entries.ConfigFlow = DummyConfigFlow
ha.core = types.ModuleType("core")
ha.core.HomeAssistant = object
ha.helpers = types.ModuleType("helpers")
ha.helpers.typing = types.ModuleType("typing")
ha.helpers.typing.ConfigType = dict
ha.components = types.ModuleType("components")
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
        return {"views": []}
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
sys.modules.setdefault("homeassistant.components.lovelace", lovelace)
sys.modules.setdefault("homeassistant.components.lovelace.const", lovelace.const)
sys.modules.setdefault("homeassistant.components.lovelace.dashboard", lovelace.dashboard)

from custom_components.womgr.config_flow import WoMgrConfigFlow


async def run_step(input_data):
    flow = WoMgrConfigFlow()

    def async_show_form(*args, **kwargs):
        return {"type": "form", "errors": kwargs.get("errors")}

    def async_create_entry(*args, **kwargs):
        return {"type": "create_entry", "data": kwargs.get("data")}

    flow.async_show_form = async_show_form
    flow.async_create_entry = async_create_entry
    return await flow.async_step_device(input_data)


def test_config_flow_mac_validation_error():
    invalid = {
        "device_name": "pc",
        "mac": "invalid",
        "ip": "1.2.3.4",
        "location": "lab",
        "os_type": "linux",
    }
    result = asyncio.run(run_step(invalid))
    assert result["type"] == "form"
    assert result["errors"] == {"mac": "invalid_mac"}


def test_config_flow_valid_device():
    valid = {
        "device_name": "pc",
        "mac": "AA:BB:CC:DD:EE:FF",
        "ip": "1.2.3.4",
        "location": "lab",
        "os_type": "linux",
    }
    result = asyncio.run(run_step(valid))
    assert result["type"] == "create_entry"
    assert result["data"] == valid
