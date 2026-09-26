"""Read-only probe for Paperclip tools in the existing Assist pipeline."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Load the UI-configured integration and its LLM platform."""
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the UI-configured integration."""
    return True
