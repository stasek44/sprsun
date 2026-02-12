"""SPRSUN Heat Pump integration for Home Assistant.

Implements synchronous Modbus pattern based on modbus_integration_guide.md.
"""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_SLAVE_ID,
    DOMAIN,
    PLATFORMS,
)
from .modbus import SPRSUNModbusClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SPRSUN Heat Pump from a config entry.
    
    Creates synchronous Modbus client with persistent connection.
    """
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    slave_id = entry.data.get(CONF_SLAVE_ID, 1)
    
    # Create Modbus client (synchronous with Lock)
    client = SPRSUNModbusClient(
        host=host,
        port=port,
        slave_id=slave_id,
        timeout=10,  # Fail-fast timeout
    )
    
    # Connect once (via executor)
    connected = await hass.async_add_executor_job(client.connect)
    if not connected:
        raise ConfigEntryNotReady(f"Failed to connect to SPRSUN at {host}:{port}")
    
    # Store client in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client
    
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
        # Close Modbus connection
        client: SPRSUNModbusClient = hass.data[DOMAIN].pop(entry.entry_id)
        await hass.async_add_executor_job(client.close)
        
        _LOGGER.info("SPRSUN Heat Pump integration unloaded")
    
    return unload_ok
