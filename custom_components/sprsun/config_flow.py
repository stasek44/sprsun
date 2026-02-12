"""Config flow for SPRSUN Heat Pump."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_SLAVE_ID, DOMAIN
from .modbus import SPRSUNModbusClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=502): int,
        vol.Optional(CONF_SLAVE_ID, default=1): int,
    }
)


async def validate_connection(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, Any]:
    """Validate the Modbus connection can be established."""
    client = SPRSUNModbusClient(
        host=data[CONF_HOST],
        port=data[CONF_PORT],
        slave_id=data.get(CONF_SLAVE_ID, 1),
        timeout=10,
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


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
