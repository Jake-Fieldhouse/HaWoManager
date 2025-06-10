"""WoMgr integration initialization."""

from homeassistant.core import HomeAssistant

DOMAIN = "womgr"

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the WoMgr component."""
    hass.data.setdefault(DOMAIN, {})
    return True
