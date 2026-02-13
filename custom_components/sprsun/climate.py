"""Climate platform for SPRSUN Heat Pump.

Climate entity for HVAC control. Reads data from coordinator.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    REG_COOLING_SETPOINT,
    REG_HEATING_SETPOINT,
    REG_HOTWATER_SETPOINT,
    REG_OUTLET_TEMP,
    REG_UNIT_MODE,
    UNIT_MODE_COOLING,
    UNIT_MODE_COOLING_DHW,
    UNIT_MODE_DHW,
    UNIT_MODE_HEATING,
    UNIT_MODE_HEATING_DHW,
)
from .coordinator import SPRSUNDataUpdateCoordinator
from .modbus import decode_temperature, encode_temperature

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SPRSUN climate entity."""
    coordinator: SPRSUNDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SPRSUNClimate(coordinator)])


class SPRSUNClimate(CoordinatorEntity[SPRSUNDataUpdateCoordinator], ClimateEntity):
    """Representation of SPRSUN heat pump climate entity.
    
    Subscribes to coordinator for automatic updates every 30 seconds.
    """

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.HEAT,
        HVACMode.COOL,
    ]

    def __init__(self, coordinator: SPRSUNDataUpdateCoordinator) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        
        # Device info
        self._attr_unique_id = f"{coordinator.entry.entry_id}_climate"
        self._attr_device_info = coordinator.device_info

    @property
    def current_temperature(self) -> float | None:
        """Return current temperature from outlet sensor."""
        if REG_OUTLET_TEMP in self.coordinator.data:
            return decode_temperature(
                self.coordinator.data[REG_OUTLET_TEMP], scale=0.1
            )
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return target temperature based on current mode."""
        if REG_UNIT_MODE not in self.coordinator.data:
            return None
        
        unit_mode = self.coordinator.data[REG_UNIT_MODE]
        
        # Map unit mode to appropriate setpoint register
        if unit_mode in (UNIT_MODE_HEATING, UNIT_MODE_HEATING_DHW):
            reg = REG_HEATING_SETPOINT
        elif unit_mode in (UNIT_MODE_COOLING, UNIT_MODE_COOLING_DHW):
            reg = REG_COOLING_SETPOINT
        elif unit_mode == UNIT_MODE_DHW:
            reg = REG_HOTWATER_SETPOINT
        else:
            return None
        
        if reg in self.coordinator.data:
            return decode_temperature(self.coordinator.data[reg], scale=0.1, signed=True)
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        if REG_UNIT_MODE not in self.coordinator.data:
            return HVACMode.OFF
        
        unit_mode = self.coordinator.data[REG_UNIT_MODE]
        return self._map_unit_mode_to_hvac(unit_mode)

    def _map_unit_mode_to_hvac(self, unit_mode: int) -> HVACMode:
        """Map device unit mode to HVAC mode."""
        if unit_mode == UNIT_MODE_DHW:
            return HVACMode.OFF  # DHW only, no heating/cooling
        elif unit_mode in (UNIT_MODE_HEATING, UNIT_MODE_HEATING_DHW):
            return HVACMode.HEAT
        elif unit_mode in (UNIT_MODE_COOLING, UNIT_MODE_COOLING_DHW):
            return HVACMode.COOL
        return HVACMode.OFF

    def _map_hvac_to_unit_mode(self, hvac_mode: HVACMode) -> int:
        """Map HVAC mode to device unit mode."""
        mode_map = {
            HVACMode.OFF: UNIT_MODE_DHW,
            HVACMode.HEAT: UNIT_MODE_HEATING_DHW,
            HVACMode.COOL: UNIT_MODE_COOLING_DHW,
        }
        return mode_map.get(hvac_mode, UNIT_MODE_DHW)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        
        if REG_UNIT_MODE not in self.coordinator.data:
            _LOGGER.error("Cannot set temperature: unit mode unknown")
            return
        
        unit_mode = self.coordinator.data[REG_UNIT_MODE]
        
        # Determine which setpoint register to write
        if unit_mode in (UNIT_MODE_HEATING, UNIT_MODE_HEATING_DHW):
            register = REG_HEATING_SETPOINT
        elif unit_mode in (UNIT_MODE_COOLING, UNIT_MODE_COOLING_DHW):
            register = REG_COOLING_SETPOINT
        elif unit_mode == UNIT_MODE_DHW:
            register = REG_HOTWATER_SETPOINT
        else:
            _LOGGER.warning("Cannot set temperature in current mode")
            return
        
        # Encode temperature (scale 0.1, signed)
        encoded = encode_temperature(temperature, scale=0.1, signed=True)
        
        # Write to Modbus (via executor to avoid blocking)
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_register, register, encoded
        )
        
        if success:
            # Request immediate coordinator refresh to propagate to all entities
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set temperature to %.1f°C", temperature)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        # Map HVAC mode to unit mode value
        unit_mode = self._map_hvac_to_unit_mode(hvac_mode)
        
        # Write to Modbus (via executor to avoid blocking)
        success = await self.hass.async_add_executor_job(
            self.coordinator.client.write_register, REG_UNIT_MODE, unit_mode
        )
        
        if success:
            # Request immediate coordinator refresh to propagate to all entities
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set HVAC mode to %s", hvac_mode)
