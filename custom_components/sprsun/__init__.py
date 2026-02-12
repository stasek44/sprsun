"""The SPRSUN Heat Pump integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import SPRSUNDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# List of platforms to support
PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SPRSUN Heat Pump from a config entry."""
    
    # Create the data update coordinator
    coordinator = SPRSUNDataUpdateCoordinator(hass, entry)
    
    # Fetch initial data so we have data when entities subscribe
    # This will also connect to the device
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Disconnect from device
        coordinator: SPRSUNDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.client.disconnect()
        
        # Remove coordinator from hass.data
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
