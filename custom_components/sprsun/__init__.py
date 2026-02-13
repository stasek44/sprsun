"""SPRSUN Heat Pump integration for Home Assistant.

Uses DataUpdateCoordinator pattern for polling Modbus device.
All entities subscribe to coordinator for data updates.
"""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    CONF_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DEFAULT_TIMEOUT,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import SPRSUNDataUpdateCoordinator
from .modbus import SPRSUNModbusClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SPRSUN Heat Pump from a config entry.
    
    Creates Modbus client, initializes coordinator, and loads platforms.
    """
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    slave_id = entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)
    timeout = entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    
    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    # Create synchronous Modbus client
    client = SPRSUNModbusClient(
        host=host,
        port=port,
        slave_id=slave_id,
        timeout=timeout,
    )
    
    # Connect to device (via executor to avoid blocking)
    connected = await hass.async_add_executor_job(client.connect)
    if not connected:
        raise ConfigEntryNotReady(f"Failed to connect to SPRSUN at {host}:{port}")
    
    # Create coordinator for polling
    coordinator = SPRSUNDataUpdateCoordinator(hass, client, entry, scan_interval)
    
    # Fetch initial data (will raise ConfigEntryNotReady if fails)
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info(
        "SPRSUN Heat Pump integration loaded for %s:%s (slave %d)",
        host, port, slave_id
    )
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Get coordinator and close Modbus connection
        coordinator: SPRSUNDataUpdateCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await hass.async_add_executor_job(coordinator.client.close)
        
        _LOGGER.info("SPRSUN Heat Pump integration unloaded")
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
