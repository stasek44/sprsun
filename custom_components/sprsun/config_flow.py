"""Config flow for SPRSUN Heat Pump."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    CONF_TIMEOUT,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DEFAULT_TIMEOUT,
    DOMAIN,
)
from .modbus import SPRSUNModbusClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): int,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): vol.All(
            vol.Coerce(int), vol.Range(min=3, max=60)
        ),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=300)
        ),
    }
)


async def validate_connection(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, Any]:
    """Validate the Modbus connection can be established."""
    client = SPRSUNModbusClient(
        host=data[CONF_HOST],
        port=data[CONF_PORT],
        slave_id=data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID),
        timeout=data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
    )
    
    # Test connection
    connected = await hass.async_add_executor_job(client.connect)
    if not connected:
        raise CannotConnect(f"Failed to connect to {data[CONF_HOST]}:{data[CONF_PORT]}")
    
    # Test a simple read (unit status register)
    try:
        result = await hass.async_add_executor_job(client.read_batch, 0x0000, 1)
        if result is None:
            raise CannotConnect("Connection established but unable to read data")
    finally:
        await hass.async_add_executor_job(client.close)
    
    return {"title": f"SPRSUN Heat Pump ({data[CONF_HOST]})"}


class SPRSUNConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SPRSUN Heat Pump."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SPRSUNOptionsFlow:
        """Get the options flow for this handler."""
        return SPRSUNOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_connection(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during validation")
                errors["base"] = "unknown"
            else:
                # Create unique ID from host:port
                await self.async_set_unique_id(
                    f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
                )
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class SPRSUNOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for SPRSUN Heat Pump."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update config entry with new values
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input},
            )
            return self.async_create_entry(title="", data={})

        # Get current values from config_entry
        current_timeout = self.config_entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
        current_scan_interval = self.config_entry.data.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_TIMEOUT,
                    default=current_timeout,
                ): vol.All(vol.Coerce(int), vol.Range(min=3, max=60)),
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=current_scan_interval,
                ): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
